# 看图推荐音乐项目

## 项目简介
本项目实现"看图推荐音乐"功能，用户上传图片后，系统自动分析图片内容、情感、场景等，并推荐合适的音乐，支持直接在网页端通过Spotify播放器播放。

## 目录结构
```
/mucis_project
  ├── backend/         # 后端代码（FastAPI）
  ├── frontend/        # 前端代码（React）
  ├── README.md
  └── 流程图.txt
```

## 启动方式

### 后端
1. 进入 backend 目录：`cd backend`
2. 安装依赖：`pip install -r requirements.txt`
3. 启动服务：`uvicorn main:app --reload`

### 前端
1. 进入 frontend 目录：`cd frontend`
2. 安装依赖：`npm install`
3. 启动服务：`npm start`

---

如需详细开发文档和API说明，请参考各子目录下的README。 