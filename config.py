from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 飞书应用配置
    FEISHU_APP_ID = environ.get('FEISHU_APP_ID')
    FEISHU_APP_SECRET = environ.get('FEISHU_APP_SECRET')
    
    # 多维表格配置
    BASE_ID = environ.get('BASE_ID')
    TABLE_ID = environ.get('TABLE_ID')