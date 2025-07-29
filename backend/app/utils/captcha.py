import base64
from PIL import Image, ImageDraw, ImageFont
import random
import string
from io import BytesIO

def generate_captcha(size=(120, 40), length=4):
    """生成验证码图片和base64编码
    
    Returns:
        (base64_str, text): 返回base64编码的图片和验证码文本
    """
    # 生成随机字符
    chars = string.ascii_uppercase + string.digits
    text = ''.join(random.choices(chars, k=length))
    
    # 创建图片
    image = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(image)
    
    # 使用默认字体
    font = ImageFont.load_default()
    
    # 计算文本位置使其居中
    text_width = font.getsize(text)[0]
    text_height = font.getsize(text)[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # 添加干扰线
    for _ in range(5):
        x1 = random.randint(0, size[0])
        y1 = random.randint(0, size[1])
        x2 = random.randint(0, size[0])
        y2 = random.randint(0, size[1])
        draw.line(((x1, y1), (x2, y2)), fill='gray')
    
    # 绘制文字
    draw.text((x, y), text, font=font, fill='black')
    
    # 转换为base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}", text 