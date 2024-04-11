import base64

# 输入要编码的汉字字符串
chinese_text:str = input("请输入要编码的汉字字符串：")

# 将汉字字符串编码为 UTF-8 格式，然后进行 Base64 编码
encoded_data = base64.b64encode(chinese_text.encode('utf-8')).decode('utf-8')

print("Base64 编码后的结果：", encoded_data)
