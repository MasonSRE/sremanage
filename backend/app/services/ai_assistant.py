"""
AI助手服务
支持OpenAI兼容的API格式，可配置不同的AI服务
"""

import os
import requests
import json
from typing import Dict, Any, Optional
from app.utils.logger import logger

class AIAssistant:
    def __init__(self):
        self.enabled = os.getenv('AI_ENABLED', 'false').lower() == 'true'
        self.base_url = os.getenv('AI_BASE_URL', 'https://api.openai.com/v1')
        self.api_key = os.getenv('AI_API_KEY', '')
        self.model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
        
        # 确保base_url以正确格式结尾
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        if not self.base_url.endswith('v1/'):
            self.base_url = self.base_url.rstrip('/') + '/v1/'
        
        # 记录配置状态
        self._log_configuration()
    
    def _log_configuration(self):
        """记录AI配置状态"""
        logger.info(f"AI助手配置状态:")
        logger.info(f"  - 启用状态: {self.enabled}")
        logger.info(f"  - API基础URL: {self.base_url}")
        logger.info(f"  - API密钥: {'已配置' if self.api_key else '未配置'}")
        logger.info(f"  - 模型: {self.model}")
        
        # 验证配置
        validation_result = self.validate_configuration()
        if not validation_result['valid']:
            logger.warning(f"AI配置验证失败: {', '.join(validation_result['errors'])}")
    
    def validate_configuration(self) -> Dict[str, Any]:
        """验证AI配置"""
        errors = []
        
        if not self.enabled:
            errors.append("AI助手未启用 (AI_ENABLED=false)")
        
        if not self.api_key:
            errors.append("未配置API密钥 (AI_API_KEY)")
        elif len(self.api_key) < 20:
            errors.append("API密钥格式可能不正确")
        
        if not self.base_url:
            errors.append("未配置API基础URL (AI_BASE_URL)")
        elif not (self.base_url.startswith('http://') or self.base_url.startswith('https://')):
            errors.append("API基础URL格式不正确，应以http://或https://开头")
        
        if not self.model:
            errors.append("未配置AI模型 (AI_MODEL)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def is_available(self) -> bool:
        """检查AI服务是否可用"""
        return self.enabled and bool(self.api_key)
    
    def generate_compose(self, user_prompt: str) -> Dict[str, Any]:
        """生成docker-compose配置"""
        if not self.is_available():
            return self._fallback_response(user_prompt)
        
        try:
            # 构建AI提示词
            system_prompt = """你是一个Docker专家，专门生成docker-compose.yml配置。

要求：
1. 只返回docker-compose.yml内容，不要其他解释
2. 使用 version: '3.8'
3. 包含合理的默认配置
4. 添加必要的环境变量
5. 配置数据持久化（volumes）
6. 设置 restart: unless-stopped
7. 使用合适的端口映射
8. 添加时区设置 TZ=Asia/Shanghai
9. 确保安全性（不使用privileged等危险配置）

示例格式：
version: '3.8'
services:
  应用名:
    image: 镜像:版本
    container_name: 容器名
    environment:
      - 环境变量=值
      - TZ=Asia/Shanghai
    ports:
      - "主机端口:容器端口"
    volumes:
      - ./data:/容器内路径
    restart: unless-stopped"""

            # 调用AI API
            response = self._call_ai_api(system_prompt, user_prompt)
            
            if response['success']:
                compose_content = response['content'].strip()
                
                # 清理AI响应（移除markdown代码块标记）
                if compose_content.startswith('```'):
                    lines = compose_content.split('\n')
                    # 移除第一行的```yaml或```
                    if lines[0].startswith('```'):
                        lines = lines[1:]
                    # 移除最后一行的```
                    if lines[-1].strip() == '```':
                        lines = lines[:-1]
                    compose_content = '\n'.join(lines)
                
                return {
                    'success': True,
                    'compose': compose_content,
                    'message': '🤖 AI已为你生成配置',
                    'source': 'ai'
                }
            else:
                logger.warning(f"AI API调用失败: {response['error']}")
                return self._fallback_response(user_prompt)
                
        except Exception as e:
            logger.error(f"AI助手生成配置失败: {str(e)}")
            return self._fallback_response(user_prompt)
    
    def generate_sre_response(self, user_prompt: str) -> Dict[str, Any]:
        """生成SRE助手响应"""
        if not self.is_available():
            return self._fallback_sre_response(user_prompt)
        
        try:
            # 构建SRE专用提示词
            system_prompt = """你是一个经验丰富的SRE（Site Reliability Engineering）专家，专门帮助解决运维和可靠性问题。

你的职责包括：
1. 系统监控和告警分析
2. 故障排查和根因分析
3. 性能优化建议
4. 容量规划
5. 灾难恢复策略
6. 自动化运维建议
7. 服务可用性改进

回答要求：
- 提供专业、实用的建议
- 包含具体的操作步骤
- 推荐相关工具和最佳实践
- 考虑成本和可行性
- 提供监控和指标建议

请用中文回答，语言专业但易懂。"""

            # 调用AI API
            response = self._call_ai_api(system_prompt, user_prompt)
            
            if response['success']:
                content = response['content'].strip()
                
                # 解析响应，提取建议列表
                suggestions = self._extract_suggestions_from_content(content)
                
                return {
                    'success': True,
                    'content': content,
                    'suggestions': suggestions,
                    'message': '🤖 SRE专家为你提供建议',
                    'source': 'ai'
                }
            else:
                logger.warning(f"SRE AI调用失败: {response['error']}")
                return self._fallback_sre_response(user_prompt)
                
        except Exception as e:
            logger.error(f"SRE助手响应失败: {str(e)}")
            return self._fallback_sre_response(user_prompt)
    
    def _extract_suggestions_from_content(self, content: str) -> list:
        """从AI响应中提取建议列表"""
        suggestions = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # 匹配各种列表格式
            if (line.startswith('- ') or 
                line.startswith('• ') or 
                line.startswith('* ') or
                any(line.startswith(f'{i}. ') for i in range(1, 20))):
                # 清理格式符号
                clean_line = line.lstrip('- •*0123456789. ').strip()
                if clean_line and len(clean_line) > 10:  # 过滤太短的内容
                    suggestions.append(clean_line)
        
        # 如果没有找到列表，尝试按句号分割
        if not suggestions:
            sentences = content.split('。')
            for sentence in sentences[:6]:  # 限制最多6个建议
                sentence = sentence.strip()
                if len(sentence) > 20:  # 过滤太短的句子
                    suggestions.append(sentence + '。')
        
        return suggestions[:8]  # 最多返回8个建议
    
    def _fallback_sre_response(self, user_prompt: str) -> Dict[str, Any]:
        """SRE助手的备用响应"""
        # SRE相关的预设响应
        sre_templates = {
            'monitoring': {
                'keywords': ['监控', '告警', 'monitor', 'alert', '指标', 'metrics'],
                'content': '关于系统监控和告警，我建议从以下几个方面进行完善：',
                'suggestions': [
                    '建立完整的监控体系，包括基础设施、应用和业务指标',
                    '配置合理的告警阈值，避免告警疲劳',
                    '实施分层告警策略，区分不同严重级别',
                    '建立告警响应流程和值班制度',
                    '定期回顾和优化监控策略',
                    '使用Prometheus、Grafana等开源监控工具'
                ]
            },
            'performance': {
                'keywords': ['性能', '优化', 'performance', '延迟', 'latency', '慢', '卡顿'],
                'content': '针对系统性能优化，建议从以下维度进行分析和改进：',
                'suggestions': [
                    '进行性能基准测试，建立性能基线',
                    '识别系统瓶颈：CPU、内存、磁盘I/O、网络',
                    '优化数据库查询性能，添加合适的索引',
                    '实施缓存策略，减少重复计算和数据访问',
                    '优化应用程序代码，减少不必要的资源消耗',
                    '考虑水平扩展和负载均衡方案'
                ]
            },
            'incident': {
                'keywords': ['故障', '事故', 'incident', '问题', '异常', '报错', 'error'],
                'content': '故障处理和根因分析的标准流程如下：',
                'suggestions': [
                    '立即响应：确认故障范围和影响程度',
                    '临时修复：优先恢复服务，保证业务连续性',
                    '根因分析：使用日志、监控数据定位问题根源',
                    '永久修复：制定并实施长期解决方案',
                    '事后总结：编写故障报告，提取经验教训',
                    '预防措施：改进监控、测试和部署流程'
                ]
            },
            'capacity': {
                'keywords': ['容量', '扩容', 'capacity', '资源', '规划', 'scale'],
                'content': '容量规划和资源管理的最佳实践包括：',
                'suggestions': [
                    '定期评估当前资源使用情况和增长趋势',
                    '建立容量预测模型，提前规划资源需求',
                    '实施自动扩缩容策略，应对流量波动',
                    '优化资源利用率，避免过度配置',
                    '制定容量应急预案，应对突发流量',
                    '定期进行容量压测，验证系统承载能力'
                ]
            }
        }
        
        # 简单的关键词匹配
        user_prompt_lower = user_prompt.lower()
        for category, template in sre_templates.items():
            for keyword in template['keywords']:
                if keyword in user_prompt_lower:
                    return {
                        'success': True,
                        'content': template['content'],
                        'suggestions': template['suggestions'],
                        'message': f'🛠️ 为你提供了{category}相关的专业建议（AI助手暂不可用）',
                        'source': 'template'
                    }
        
        # 如果没有匹配到，返回通用SRE建议
        return {
            'success': True,
            'content': '作为SRE专家，我建议从以下几个核心领域来提升系统可靠性：',
            'suggestions': [
                '建立完善的监控和告警体系',
                '制定详细的故障响应流程',
                '实施自动化运维和部署',
                '定期进行灾难恢复演练',
                '优化系统性能和容量规划',
                '建立SLI/SLO指标体系',
                '推行DevOps文化和最佳实践',
                '持续改进和学习'
            ],
            'message': '🛠️ AI助手暂不可用，提供通用SRE建议',
            'source': 'generic'
        }
    
    def _call_ai_api(self, system_prompt: str, user_prompt: str, stream: bool = False) -> Dict[str, Any]:
        """调用AI API（OpenAI兼容格式）"""
        url = f"{self.base_url}chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'max_tokens': 2000,
            'temperature': 0.3,
            'stream': stream
        }
        
        # 配置session以提高稳定性
        session = requests.Session()
        session.headers.update(headers)
        
        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.debug(f"AI API请求尝试 {attempt + 1}/{max_retries}: {url}")
                
                # 增加连接超时和读取超时
                response = session.post(url, json=data, timeout=(10, 30), verify=True, stream=stream)
                
                logger.debug(f"AI API响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    if stream:
                        return {
                            'success': True,
                            'response': response
                        }
                    else:
                        result = response.json()
                        content = result['choices'][0]['message']['content']
                        logger.info(f"AI API调用成功，响应长度: {len(content)}")
                        return {
                            'success': True,
                            'content': content
                        }
                elif response.status_code == 429:
                    # 速率限制错误，等待更长时间重试
                    logger.warning(f"AI API速率限制，等待重试...")
                    import time
                    time.sleep(min(2 ** attempt, 10))  # 指数退避，最多等待10秒
                    continue
                else:
                    error_msg = f"API返回错误: {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail}"
                    except:
                        error_msg += f" - {response.text[:200]}"
                    
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg
                    }
                    
            except requests.exceptions.SSLError as e:
                logger.warning(f"SSL错误，尝试第{attempt + 1}次: {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': f"SSL连接失败: {str(e)}"
                    }
                # SSL错误时等待一下再重试
                import time
                time.sleep(1)
                continue
                
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"连接错误，尝试第{attempt + 1}次: {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': f"连接失败: {str(e)}"
                    }
                # 连接错误时等待更长时间
                import time
                time.sleep(min(2 ** attempt, 5))
                continue
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"超时错误，尝试第{attempt + 1}次: {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': f"请求超时: {str(e)}"
                    }
                continue
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求错误，尝试第{attempt + 1}次: {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': f"请求失败: {str(e)}"
                    }
                continue
        
        return {
            'success': False,
            'error': "所有重试均失败"
        }
    
    def stream_generate_compose(self, user_prompt: str):
        """流式生成docker-compose配置"""
        if not self.is_available():
            yield "data: " + json.dumps({
                'type': 'error',
                'content': 'AI服务不可用，请检查配置'
            }) + "\n\n"
            return
        
        try:
            # 构建AI提示词
            system_prompt = """你是一个Docker专家，专门生成docker-compose.yml配置。

要求：
1. 只返回docker-compose.yml内容，不要其他解释
2. 使用 version: '3.8'
3. 包含合理的默认配置
4. 添加必要的环境变量
5. 配置数据持久化（volumes）
6. 设置 restart: unless-stopped
7. 使用合适的端口映射
8. 添加时区设置 TZ=Asia/Shanghai
9. 确保安全性（不使用privileged等危险配置）

示例格式：
version: '3.8'
services:
  应用名:
    image: 镜像:版本
    container_name: 容器名
    environment:
      - 环境变量=值
      - TZ=Asia/Shanghai
    ports:
      - "主机端口:容器端口"
    volumes:
      - ./data:/容器内路径
    restart: unless-stopped"""

            # 调用AI API（流式）
            response = self._call_ai_api(system_prompt, user_prompt, stream=True)
            
            if response['success']:
                # 发送开始信号
                yield "data: " + json.dumps({
                    'type': 'start',
                    'content': '🤖 AI正在为你生成配置...'
                }) + "\n\n"
                
                content_buffer = ""
                
                # 处理流式响应
                for line in response['response'].iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]
                            if data_str.strip() == '[DONE]':
                                break
                            
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        chunk = delta['content']
                                        content_buffer += chunk
                                        yield "data: " + json.dumps({
                                            'type': 'chunk',
                                            'content': chunk
                                        }) + "\n\n"
                            except json.JSONDecodeError:
                                continue
                
                # 清理最终内容
                compose_content = content_buffer.strip()
                if compose_content.startswith('```'):
                    lines = compose_content.split('\n')
                    if lines[0].startswith('```'):
                        lines = lines[1:]
                    if lines[-1].strip() == '```':
                        lines = lines[:-1]
                    compose_content = '\n'.join(lines)
                
                # 发送完成信号
                yield "data: " + json.dumps({
                    'type': 'complete',
                    'content': compose_content,
                    'message': '🤖 AI已为你生成配置'
                }) + "\n\n"
                
            else:
                yield "data: " + json.dumps({
                    'type': 'error',
                    'content': f'AI服务调用失败: {response["error"]}'
                }) + "\n\n"
                
        except Exception as e:
            logger.error(f"流式AI生成配置失败: {str(e)}")
            yield "data: " + json.dumps({
                'type': 'error',
                'content': f'生成配置时发生错误: {str(e)}'
            }) + "\n\n"
    
    def _fallback_response(self, user_prompt: str) -> Dict[str, Any]:
        """AI不可用时的备用响应"""
        # 预设的模板配置
        templates = {
            'mysql': {
                'keywords': ['mysql', '数据库', 'database'],
                'compose': '''version: '3.8'
services:
  mysql:
    image: mysql:8.0
    container_name: mysql-instance
    environment:
      - MYSQL_ROOT_PASSWORD=changeme123
      - TZ=Asia/Shanghai
    ports:
      - "3306:3306"
    volumes:
      - ./data:/var/lib/mysql
      - ./config:/etc/mysql/conf.d
    restart: unless-stopped'''
            },
            'redis': {
                'keywords': ['redis', '缓存', 'cache'],
                'compose': '''version: '3.8'
services:
  redis:
    image: redis:7
    container_name: redis-instance
    environment:
      - TZ=Asia/Shanghai
    ports:
      - "6379:6379"
    volumes:
      - ./data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes'''
            },
            'nginx': {
                'keywords': ['nginx', 'web', '网站', '反向代理'],
                'compose': '''version: '3.8'
services:
  nginx:
    image: nginx:latest
    container_name: nginx-instance
    environment:
      - TZ=Asia/Shanghai
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./html:/usr/share/nginx/html
      - ./conf:/etc/nginx/conf.d
      - ./logs:/var/log/nginx
    restart: unless-stopped'''
            },
            'postgres': {
                'keywords': ['postgres', 'postgresql', 'pg'],
                'compose': '''version: '3.8'
services:
  postgres:
    image: postgres:15
    container_name: postgres-instance
    environment:
      - POSTGRES_PASSWORD=changeme123
      - TZ=Asia/Shanghai
    ports:
      - "5432:5432"
    volumes:
      - ./data:/var/lib/postgresql/data
    restart: unless-stopped'''
            }
        }
        
        # 简单的关键词匹配
        user_prompt_lower = user_prompt.lower()
        for app_name, template in templates.items():
            for keyword in template['keywords']:
                if keyword in user_prompt_lower:
                    return {
                        'success': True,
                        'compose': template['compose'],
                        'message': f'🛠️ 为你提供了{app_name}的默认配置（AI助手暂不可用）',
                        'source': 'template'
                    }
        
        # 如果没有匹配到，返回通用模板
        return {
            'success': True,
            'compose': '''version: '3.8'
services:
  app:
    image: your-image:latest
    container_name: your-app
    environment:
      - TZ=Asia/Shanghai
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
    restart: unless-stopped''',
            'message': '🛠️ AI助手暂不可用，请手动编辑配置',
            'source': 'generic'
        }

# 创建全局实例
ai_assistant = AIAssistant()