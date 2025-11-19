from datetime import datetime, timedelta

# 给定日期字符串
date_str = "2025-10-21"

# 将字符串转换为 datetime 对象
date_obj = datetime.strptime(date_str, "%Y-%m-%d")

# 计算30天之后的日期
new_date = date_obj + timedelta(days=30)

# 转换回字符串格式
new_date_str = new_date.strftime("%Y-%m-%d")

print("30天之后的日期是:", new_date_str)
