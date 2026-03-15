# Daily Bible Django App (Updated)

这个版本已更新：
- 每一页顶部固定使用提供的图片
- 灵修内容补为完整多段文本
- 新增“今日祷告”内容区块
- 支持一页多条读经超链接

## 启动步骤

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo --clear
python manage.py runserver
```

访问：
- 首页: http://127.0.0.1:8000/
- 后台: http://127.0.0.1:8000/admin/

如果你已经有旧的 `db.sqlite3`，建议先删除后再执行：

```bash
python manage.py migrate
python manage.py seed_demo --clear
```
