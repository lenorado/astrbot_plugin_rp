from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import random
from datetime import datetime
 
@register("daily_luck_plugin", "Your Name", "每日人品插件", "1.0.0", "repo url")
class DailyLuckPlugin(Star):
  def __init__(self, context: Context):
      super().__init__(context)
      self.luck_scores = {}  # 存储每个用户的今日人品值
      self.probability_weights = [7, 8, 20, 30, 20, 8, 7]  # 默认概率分布
      self.current_date = datetime.now().date()  # 当天日期
 
  @filter.command("rp")
  async def rp(self, event: AstrMessageEvent):
      user_id = event.get_sender_id()
      user_name = event.get_sender_name()  # 获取用户名
      # 检查日期是否变化
      if datetime.now().date() != self.current_date:
          self.luck_scores = {}  # 清除之前的人品值
          self.current_date = datetime.now().date()  # 更新日期
 
      if user_id not in self.luck_scores:
          # 生成随机人品值，并按概率分布
          expanded_weights = self.expand_weights(self.probability_weights, 101)
          luck_score = random.choices(range(101), weights=expanded_weights)[0]
          self.luck_scores[user_id] = luck_score
 
      luck_score = self.luck_scores[user_id]
      description = self.get_luck_description(luck_score)
      yield event.plain_result(f"{user_name}今日人品：{luck_score}，{description}")
 
  @filter.command("set_probability")
  async def set_probability(self, event: AstrMessageEvent, *weights):
      if len(weights) != 7:
          yield event.plain_result("请输入 7 个概率权重值，用空格分隔。")
          return
 
      try:
          weights = [int(w) for w in weights]
          if sum(weights) != 100:
              yield event.plain_result("概率权重值之和必须为 100。")
              return
          self.probability_weights = weights
          yield event.plain_result("概率分布已更新。")
      except ValueError:
          yield event.plain_result("概率权重值必须是整数。")
 
  def get_luck_description(self, score):
      if score == 0:
          return "大寄！"
      elif 1 <= score <= 30:
          return "你快要寄了。"
      elif 31 <= score <= 60:
          return "小寄。"
      elif 61 <= score <= 80:
          return "小吉。"
      elif 81 <= score <= 90:
          return "中吉！"
      elif 91 <= score < 100:
          return "大吉！"
      elif score == 100:
          return "你人品爆炸！"
 
  def expand_weights(self, weights, total):
      # 确保权重列表的长度与 total 相匹配
      expanded_weights = []
      weight_sum = sum(weights)
      segment_size = total // len(weights)
      remainder = total % len(weights)
 
      for i, weight in enumerate(weights):
          # 分配每个权重段的大小
          segment_weight = weight / weight_sum
          # 如果是最后一个权重，加上余数
          if i == len(weights) - 1:
              segment_size += remainder
          # 生成权重列表
          expanded_weights.extend([segment_weight] * segment_size)
 
      # 将权重转换为整数
      expanded_weights = [int(round(weight * total)) for weight in expanded_weights]
      return expanded_weights