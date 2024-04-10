import base64

encoded_string = "5oCO5LmI5L2/55SodXNi6ZKl5YyZ"
decoded_string = base64.b64decode(encoded_string).decode("utf-8")
print(decoded_string)


import base64

def is_base64(s):
    try:
        # 尝试解码字符串
        decoded = base64.b64decode(s)
        # 如果解码成功，返回True
        return True
    except:
        # 如果解码失败，返回False
        return False

# 测试字符串是否为Base64编码
encoded_string = "5oCO5LmI5L2/55SodXNi6ZKl5YyZ"
print(is_base64(encoded_string))  # 输出：True

encoded_string = "怎么使用usb钥匙"
print(is_base64(encoded_string))  # 输出：False

encoded_string = "How to use usb key"
print(is_base64(encoded_string))  # 输出：False