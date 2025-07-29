from flask import Blueprint, request, jsonify, session, current_app
from app.services.auth import AuthService
from app.services.captcha import CaptchaService
from app.utils.logger import get_logger
import random
import string
import uuid
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import os
import time
from flask_cors import cross_origin

logger = get_logger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/test-session', methods=['GET'])
@cross_origin(origins=["http://127.0.0.1:5173", "http://localhost:5173"], supports_credentials=True)
def test_session():
    """测试会话是否正常工作"""
    try:
        # 记录原始请求信息
        logger.info(f"Request cookies: {request.cookies}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Session before: {dict(session)}")
        
        # 设置一个测试值
        if 'test_value' not in session:
            session['test_value'] = f"test-{time.time()}"
        else:
            session['test_value'] = f"updated-{time.time()}"
            
        session.modified = True
        logger.info(f"Session after: {dict(session)}")
        
        return jsonify({
            'success': True,
            'message': '会话测试',
            'session_data': dict(session),
            'cookies': dict(request.cookies)
        })
    except Exception as e:
        logger.error(f"会话测试失败: {str(e)}")
        logger.exception("详细错误：")
        return jsonify({
            'success': False,
            'message': f'会话测试失败: {str(e)}'
        }), 500

@auth_bp.route('/api/captcha', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://127.0.0.1:5173", "http://localhost:5173"], supports_credentials=True)
def get_captcha():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # 生成验证码并获取图片
        code, image = generate_captcha()
        
        # 使用验证码服务保存验证码
        captcha_id = CaptchaService.save_captcha(code)
        
        logger.info(f"生成验证码: {code}, ID: {captcha_id}")
        
        # 返回响应
        response = jsonify({
            'success': True,
            'data': {
                'image': image,
                'expires': 300,
                'captcha_id': captcha_id
            }
        })
        
        return response
    except Exception as e:
        logger.error(f"生成验证码失败: {str(e)}")
        logger.exception("详细错误：")
        return jsonify({
            'success': False,
            'message': '生成验证码失败'
        }), 500

@auth_bp.route('/api/login', methods=['POST', 'OPTIONS'])
@cross_origin(origins=["http://127.0.0.1:5173", "http://localhost:5173"], supports_credentials=True)
def login():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        logger.info(f"收到登录请求数据: {data}")
        
        captcha = data.get('captcha', '')
        username = data.get('username')
        password = data.get('password')
        captcha_id = data.get('captcha_id')
        
        # 如果没有提供验证码相关信息，跳过验证码验证（用于测试）
        if not captcha_id and not captcha:
            logger.info("跳过验证码验证（测试模式）")
        else:
            # 使用验证码服务验证
            is_valid, message = CaptchaService.validate_captcha(captcha_id, captcha)
            
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        # 验证码验证通过，调用登录服务
        try:
            result = AuthService.login({
                'username': username,
                'password': password
            })
            logger.info(f"登录服务结果: {result}")
            return jsonify(result)
        except Exception as e:
            logger.error(f"登录服务错误: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"登录路由错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@auth_bp.route('/api/login-test', methods=['POST', 'OPTIONS'])
@cross_origin(origins=["http://127.0.0.1:5173", "http://localhost:5173"], supports_credentials=True)
def login_test():
    """测试登录接口，跳过验证码验证"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        logger.info(f"收到测试登录请求数据: {data}")
        
        username = data.get('username')
        password = data.get('password')
        
        # 直接调用登录服务，跳过验证码验证
        try:
            result = AuthService.login({
                'username': username,
                'password': password
            })
            logger.info(f"测试登录服务结果: {result}")
            return jsonify(result)
        except Exception as e:
            logger.error(f"测试登录服务错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
    except Exception as e:
        logger.error(f"测试登录路由错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@auth_bp.route('/verify-token', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://127.0.0.1:5173", "http://localhost:5173"], supports_credentials=True)
def verify_token():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
            
        token = auth_header.split(' ')[1]
        AuthService.verify_token(token)
        
        return jsonify({
            'success': True,
            'message': 'Token is valid'
        })
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 401

@auth_bp.route('/api/test-captcha', methods=['GET'])
@cross_origin(origins=["http://127.0.0.1:5173", "http://localhost:5173"], supports_credentials=True)
def test_captcha():
    """测试验证码信息是否正确存储"""
    try:
        # 查看内存中的验证码存储
        from app.services.captcha import captcha_store
        
        return jsonify({
            'success': True,
            'data': {
                'captcha_count': len(captcha_store),
                'captcha_ids': list(captcha_store.keys())
            }
        })
    except Exception as e:
        logger.error(f"测试验证码失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'测试验证码失败: {str(e)}'
        }), 500

@auth_bp.route('/api/test-cookie', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://127.0.0.1:5173", "http://localhost:5173"], supports_credentials=True)
def test_cookie():
    """测试Cookie设置和读取（仅用于调试）"""
    try:
        # 记录原始请求信息
        logger.info(f"Request cookies: {request.cookies}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # 创建一个简单的测试验证码
        test_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        test_id = CaptchaService.save_captcha(test_code)
        
        logger.info(f"创建测试验证码: {test_code}, ID: {test_id}")
        
        # 创建一个响应
        response = jsonify({
            'success': True,
            'message': '测试验证码已创建',
            'data': {
                'test_code': test_code,
                'test_id': test_id
            }
        })
        
        return response
    except Exception as e:
        logger.error(f"验证码测试失败: {str(e)}")
        logger.exception("详细错误：")
        return jsonify({
            'success': False,
            'message': f'测试失败: {str(e)}'
        }), 500

def generate_captcha():
    # 生成验证码文本
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    logger.info(f"Generated captcha code: {code}")
    
    # 创建图片
    width = 280
    height = 120
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 添加背景干扰点
    for i in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill='lightgrey')
    
    # 添加柔和的干扰线
    for i in range(2):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='lightgray', width=1)
    
    # 尝试加载多个字体，确保至少一个可用
    font = None
    font_size = 95
    try:
        # 尝试多个常见字体
        font_names = ['arial.ttf', 'Arial.ttf', 'DejaVuSans-Bold.ttf', 'FreeSans.ttf']
        for font_name in font_names:
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except:
                continue
    except:
        pass
    
    # 如果所有字体都失败，创建一个基于默认字体的大字体
    if font is None:
        default_font = ImageFont.load_default()
        # 创建更大的默认字体图像
        font_size = 95
        logger.warning("Using default font with size scaling")
    
    # 绘制验证码字符
    colors = ['black', 'darkblue', 'darkred', 'darkgreen']
    char_spacing = width // 5  # 调整字符间距
    
    for i, char in enumerate(code):
        # 计算每个字符的位置，确保字符间距合适
        x = char_spacing * i + 30  # 增加左边距，使字符分布更均匀
        y = random.randint(10, 35)  # 适当的垂直位置范围
        
        # 随机选择颜色
        color = random.choice(colors)
        
        # 随机旋转角度（保持小角度以确保可读性）
        angle = random.randint(-5, 5)
        
        # 创建更大的单个字符图片
        char_img = Image.new('RGBA', (100, 100), (255, 255, 255, 0))  # 增加字符图片大小
        char_draw = ImageDraw.Draw(char_img)
        
        if font:
            # 使用TrueType字体
            char_draw.text((20, 10), char, font=font, fill=color)
        else:
            # 使用放大的默认字体
            char_draw.text((20, 10), char, fill=color)
            char_img = char_img.resize((100, 100), Image.LANCZOS)
        
        # 旋转字符
        char_img = char_img.rotate(angle, expand=True, resample=Image.BICUBIC)
        
        # 将旋转后的字符粘贴到主图片上
        try:
            image.paste(char_img, (x, y), char_img)
        except Exception as e:
            # 如果透明通道粘贴失败，尝试不使用透明通道
            logger.warning(f"Error pasting with alpha channel: {e}, trying without alpha")
            image.paste(char_img, (x, y))
    
    # 转换为base64
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    logger.info('Captcha image generated successfully')
    
    return code, img_str 