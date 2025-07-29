from alibabacloud_ecs20140526.client import Client as EcsClient
from alibabacloud_ecs20140526 import models as ecs_models
from alibabacloud_domain20180129.client import Client as DomainClient  
from alibabacloud_domain20180129 import models as domain_models
from alibabacloud_cdn20180510.client import Client as CdnClient
from alibabacloud_cdn20180510 import models as cdn_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class AliyunService:
    def __init__(self, access_key_id: str, access_key_secret: str, region: str = 'cn-hangzhou'):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region = region
        
        self.config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        
    def _get_ecs_client(self) -> EcsClient:
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret
        )
        config.endpoint = f'ecs.{self.region}.aliyuncs.com'
        return EcsClient(config)
    
    def _get_domain_client(self) -> DomainClient:
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret
        )
        config.endpoint = 'domain.aliyuncs.com'
        return DomainClient(config)
    
    def _get_cdn_client(self) -> CdnClient:
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret
        )
        config.endpoint = 'cdn.aliyuncs.com'
        return CdnClient(config)
    
    def get_ecs_instances(self, region: str = None) -> List[Dict]:
        """获取ECS实例列表"""
        try:
            if region:
                config = open_api_models.Config(
                    access_key_id=self.access_key_id,
                    access_key_secret=self.access_key_secret
                )
                config.endpoint = f'ecs.{region}.aliyuncs.com'
                client = EcsClient(config)
            else:
                client = self._get_ecs_client()
            
            request = ecs_models.DescribeInstancesRequest()
            request.page_number = 1
            request.page_size = 100
            # 设置必需的RegionId参数
            if region:
                request.region_id = region
            else:
                request.region_id = self.region
            runtime = util_models.RuntimeOptions()
            
            response = client.describe_instances_with_options(request, runtime)
            instances = []
            
            if response.body.instances and response.body.instances.instance:
                for instance in response.body.instances.instance:
                    # 获取公网IP
                    public_ip = ''
                    if hasattr(instance, 'public_ip_address') and instance.public_ip_address and hasattr(instance.public_ip_address, 'ip_address'):
                        public_ip = instance.public_ip_address.ip_address[0] if instance.public_ip_address.ip_address else ''
                    elif hasattr(instance, 'eip_address') and instance.eip_address and hasattr(instance.eip_address, 'ip_address'):
                        public_ip = instance.eip_address.ip_address or ''
                    
                    # 获取私网IP
                    private_ip = ''
                    if hasattr(instance, 'inner_ip_address') and instance.inner_ip_address and hasattr(instance.inner_ip_address, 'ip_address'):
                        private_ip = instance.inner_ip_address.ip_address[0] if instance.inner_ip_address.ip_address else ''
                    elif hasattr(instance, 'vpc_attributes') and instance.vpc_attributes and hasattr(instance.vpc_attributes, 'private_ip_address'):
                        if hasattr(instance.vpc_attributes.private_ip_address, 'ip_address'):
                            private_ip = instance.vpc_attributes.private_ip_address.ip_address[0] if instance.vpc_attributes.private_ip_address.ip_address else ''
                        else:
                            private_ip = getattr(instance.vpc_attributes, 'private_ip_address', '')
                    
                    instances.append({
                        'id': getattr(instance, 'instance_id', ''),
                        'name': getattr(instance, 'instance_name', ''),
                        'hostname': getattr(instance, 'hostname', '') or getattr(instance, 'instance_name', ''),
                        'status': getattr(instance, 'status', ''),
                        'instance_type': getattr(instance, 'instance_type', ''),
                        'image_id': getattr(instance, 'image_id', ''),
                        'public_ip': public_ip,
                        'private_ip': private_ip,
                        'region': getattr(instance, 'region_id', region or self.region),
                        'zone': getattr(instance, 'zone_id', ''),
                        'creation_time': getattr(instance, 'creation_time', ''),
                        'os_type': getattr(instance, 'ostype', ''),
                        'cpu': getattr(instance, 'cpu', 0),
                        'memory': getattr(instance, 'memory', 0),
                        'provider': 'aliyun'
                    })
            
            return instances
            
        except Exception as e:
            logger.error(f"获取ECS实例失败: {str(e)}")
            raise Exception(f"获取ECS实例失败: {str(e)}")
    
    def get_all_regions_instances(self) -> List[Dict]:
        """获取所有区域的ECS实例"""
        # 基于阿里云官网2024年最新区域列表
        # 来源: https://help.aliyun.com/zh/ecs/regions-and-zones
        regions = [
            # 中国地区 (15个)
            'cn-qingdao',       # 华北1（青岛）
            'cn-beijing',       # 华北2（北京）
            'cn-zhangjiakou',   # 华北3（张家口）
            'cn-huhehaote',     # 华北5（呼和浩特）
            'cn-wulanchabu',    # 华北6（乌兰察布）
            'cn-hangzhou',      # 华东1（杭州）
            'cn-shanghai',      # 华东2（上海）
            'cn-nanjing',       # 华东5（南京）
            'cn-fuzhou',        # 华东6（福州）
            'cn-wuhan-lr',      # 华中1（武汉）
            'cn-shenzhen',      # 华南1（深圳）
            'cn-heyuan',        # 华南2（河源）
            'cn-guangzhou',     # 华南3（广州）
            'cn-chengdu',       # 西南1（成都）
            'cn-hongkong',      # 中国香港
            
            # 海外地区 (14个)
            'ap-southeast-1',   # 新加坡
            'ap-southeast-3',   # 马来西亚（吉隆坡）
            'ap-southeast-5',   # 印度尼西亚（雅加达）
            'ap-southeast-6',   # 菲律宾（马尼拉）
            'ap-southeast-7',   # 泰国（曼谷）
            'ap-northeast-1',   # 日本（东京）
            'ap-northeast-2',   # 韩国（首尔）
            'us-west-1',        # 美国（硅谷）
            'us-east-1',        # 美国（弗吉尼亚）
            'eu-central-1',     # 德国（法兰克福）
            'eu-west-1',        # 英国（伦敦）
            'me-east-1',        # 阿联酋（迪拜）
            'me-central-1',     # 沙特（利雅得）
            'na-south-1'        # 墨西哥
        ]
        
        all_instances = []
        for region in regions:
            try:
                instances = self.get_ecs_instances(region)
                all_instances.extend(instances)
            except Exception as e:
                logger.warning(f"获取区域 {region} ECS实例失败: {str(e)}")
                continue
        
        return all_instances
    
    def get_domains(self) -> List[Dict]:
        """获取域名列表"""
        try:
            client = self._get_domain_client()
            request = domain_models.QueryDomainListRequest()
            request.page_num = 1
            request.page_size = 50
            runtime = util_models.RuntimeOptions()
            
            response = client.query_domain_list_with_options(request, runtime)
            domains = []
            
            if response.body.data and response.body.data.domain:
                for domain in response.body.data.domain:
                    domains.append({
                        'domain_name': getattr(domain, 'domain_name', ''),
                        'domain_status': getattr(domain, 'domain_status', ''),
                        'registration_date': getattr(domain, 'registration_date', ''),
                        'expiration_date': getattr(domain, 'expiration_date', ''),
                        'domain_type': getattr(domain, 'domain_type', ''),
                        'product_id': getattr(domain, 'product_id', ''),
                        'premium': getattr(domain, 'premium', False)
                    })
            
            return domains
            
        except Exception as e:
            logger.error(f"获取域名列表失败: {str(e)}")
            raise Exception(f"获取域名列表失败: {str(e)}")
    
    def refresh_cdn_cache(self, urls: List[str]) -> Dict:
        """刷新CDN缓存"""
        try:
            client = self._get_cdn_client()
            request = cdn_models.RefreshObjectCachesRequest()
            request.object_path = '\n'.join(urls)
            request.object_type = 'File'
            
            runtime = util_models.RuntimeOptions()
            response = client.refresh_object_caches_with_options(request, runtime)
            
            return {
                'success': True,
                'task_id': response.body.refresh_task_id,
                'request_id': response.body.request_id
            }
            
        except Exception as e:
            logger.error(f"CDN缓存刷新失败: {str(e)}")
            raise Exception(f"CDN缓存刷新失败: {str(e)}")
    
    def preload_cdn_cache(self, urls: List[str]) -> Dict:
        """CDN缓存预热"""
        try:
            client = self._get_cdn_client()
            request = cdn_models.PushObjectCacheRequest()
            request.object_path = '\n'.join(urls)
            
            runtime = util_models.RuntimeOptions()
            response = client.push_object_cache_with_options(request, runtime)
            
            return {
                'success': True,
                'task_id': response.body.push_task_id,
                'request_id': response.body.request_id
            }
            
        except Exception as e:
            logger.error(f"CDN缓存预热失败: {str(e)}")
            raise Exception(f"CDN缓存预热失败: {str(e)}")
    
    def get_cdn_domains(self) -> List[Dict]:
        """获取CDN域名列表"""
        try:
            client = self._get_cdn_client()
            request = cdn_models.DescribeUserDomainsRequest()
            request.page_number = 1
            request.page_size = 50
            runtime = util_models.RuntimeOptions()
            
            response = client.describe_user_domains_with_options(request, runtime)
            domains = []
            
            if response.body.domains and response.body.domains.page_data:
                for domain in response.body.domains.page_data:
                    domains.append({
                        'domain_name': getattr(domain, 'domain_name', ''),
                        'domain_status': getattr(domain, 'domain_status', ''),
                        'cdn_type': getattr(domain, 'cdn_type', ''),
                        'gmt_created': getattr(domain, 'gmt_created', ''),
                        'gmt_modified': getattr(domain, 'gmt_modified', ''),
                        'cname': getattr(domain, 'cname', ''),
                        'ssl_protocol': getattr(domain, 'ssl_protocol', 'off'),
                        'sandbox': getattr(domain, 'sandbox', ''),
                        'description': getattr(domain, 'description', '')
                    })
            
            return domains
            
        except Exception as e:
            logger.error(f"获取CDN域名列表失败: {str(e)}")
            raise Exception(f"获取CDN域名列表失败: {str(e)}")

def get_aliyun_service(access_key_id: str, access_key_secret: str, region: str = 'cn-hangzhou') -> AliyunService:
    """获取阿里云服务实例"""
    return AliyunService(access_key_id, access_key_secret, region)