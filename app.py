from flask import Flask, render_template, request, jsonify
import requests
import json
from config import Config
from flask_caching import Cache

app = Flask(__name__)

# 配置缓存
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# 获取飞书访问令牌
@cache.memoize(timeout=7000)  # 缓存约2小时，飞书token有效期为2小时
def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": Config.FEISHU_APP_ID,
        "app_secret": Config.FEISHU_APP_SECRET
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json().get("tenant_access_token")

# 获取多维表格数据
@cache.memoize(timeout=300)  # 缓存5分钟
def get_bitable_data():
    token = get_tenant_access_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{Config.BASE_ID}/tables/{Config.TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", {}).get("items", [])
    else:
        print(f"获取数据失败: {response.text}")
        return []

# 首页路由
@app.route('/')
def index():
    articles = []
    items = get_bitable_data()
    
    for item in items:
        fields = item.get("fields", {})
        article = {
            "id": item.get("record_id"),
            "title": fields.get("标题", ""),
            "quote": fields.get("金句输出", ""),
            "comment": fields.get("黄叔点评", ""),
            "content": fields.get("概要内容输出", "")
        }
        articles.append(article)
    
    return render_template('index.html', articles=articles)

# 文章详情路由
@app.route('/article/<article_id>')
def article_detail(article_id):
    items = get_bitable_data()
    article = None
    
    for item in items:
        if item.get("record_id") == article_id:
            fields = item.get("fields", {})
            article = {
                "id": item.get("record_id"),
                "title": fields.get("标题", ""),
                "quote": fields.get("金句输出", ""),
                "comment": fields.get("黄叔点评", ""),
                "content": fields.get("概要内容输出", "")
            }
            break
    
    if article:
        return render_template('detail.html', article=article)
    else:
        return "文章不存在", 404

if __name__ == '__main__':
    app.run(debug=True)