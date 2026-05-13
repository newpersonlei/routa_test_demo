# routa_test_demo

多人对战俄罗斯方块项目。

## 项目结构

```
├── app.py              # 应用入口
├── config.py           # 配置
├── requirements.txt    # 依赖列表
├── static/             # 静态资源（CSS、JS）
├── templates/          # HTML 模板
├── game/               # 游戏逻辑
└── routes/             # 路由蓝图
```

## 启动方式

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 启动应用：

```bash
flask run
```

或：

```bash
python app.py
```

应用默认监听 `http://localhost:5000`。
