# Downie YouTube 文本提取服务

这是一个基于 Downie4 的 YouTube 视频文本提取服务，可以自动从 YouTube 视频中提取字幕文本内容。该服务支持命令行工具和 HTTP API 两种使用方式。
可以对接N8N,Zapiers,dify等平台，用来获取youtube的视频文本内容。

后续开发目标：

- 增加纯下载功能
- 其他拓展功能

## 功能特点

- 支持从 YouTube 视频中提取字幕文本
- 自动使用 Downie 下载视频并获取字幕
- 提供命令行工具和 HTTP API 接口
- 支持日志记录和错误处理
- 自动清理下载的临时文件

## 工作机制

1. 接收 YouTube 视频 URL
2. 使用 Downie 的 URL Scheme 触发下载
3. 监控下载目录等待音频和字幕文件
4. 提取字幕文件中的文本内容
5. 清理临时文件并返回文本结果

## 环境要求

- macOS 系统
- Python 3.8 或更高版本
- [Downie 4](https://software.charliemonroe.net/downie/) 已安装
- 确保 Downie 已配置好 YouTube 下载功能

## 安装配置

1. 克隆项目并安装依赖：

```bash
git clone <repository_url>
cd downie-server
pip install -r requirements.txt
```

2. 配置下载目录：
   - 默认下载目录为 `~/Downloads/Downie_Transcripts`
   - 可以通过修改 `downie_youtube_transcript.py` 文件中的 `DEFAULT_DOWNLOAD_DIR` 变量来更改下载目录
   - 程序会自动创建下载目录（如果不存在）

## 使用方法

### 命令行工具

1. 使用核心下载功能：

```bash
python downie_core.py <YouTube-URL> [目标文件夹路径] [格式]
```

示例：
```bash
# 基本下载
python downie_core.py "https://www.youtube.com/watch?v=xxxxx"

# 指定下载路径和格式
python downie_core.py "https://www.youtube.com/watch?v=xxxxx" "~/Downloads/Videos" mp4
```

2. 提取视频文本：

```bash
python downie_youtube_transcript.py <YouTube-URL>
```

### HTTP API 服务

1. 启动服务器：

```bash
python downie_youtube_transcript_server.py
```

服务器将在 http://0.0.0.0:3200 启动

2. API 接口：

- 健康检查：
  ```
  GET /
  ```
  响应示例：
  ```json
  {
      "status": "running",
      "message": "YouTube文本提取服务（Downie）正在运行"
  }
  ```

- 提取文本：
  ```
  POST /extract
  Content-Type: application/json
  
  {
      "url": "https://www.youtube.com/watch?v=xxxxx"
  }
  ```

  响应示例：
  ```json
  {
      "text": "提取的文本内容...",
      "status": "success",
      "timestamp": "2024-01-01T12:00:00",
      "request_id": "202401011200-123456"
  }
  ```

## 项目结构

主要模块说明：

- `downie_core.py`: 核心下载功能
  - 提供 URL Scheme 方式调用 Downie 进行视频下载
  - 支持指定下载格式和目标文件夹
  - 提供同步的下载请求接口

- `downie_youtube_transcript.py`: 文本提取核心功能
  - 处理 YouTube URL 并提取视频 ID
  - 使用 Downie 下载视频并获取字幕
  - 提供字幕文本提取功能
  - 管理下载目录和临时文件清理

- `downie_youtube_transcript_server.py`: HTTP API 服务
  - 提供 RESTful API 接口
  - 支持异步请求处理
  - 包含请求日志和错误处理

## 日志

- 服务运行日志保存在 `youtube_text_api.log`
- 包含详细的操作记录和错误信息
- 日志格式：时间 - 日志级别 - 消息内容

## 错误处理

常见错误及解决方案：

1. "无效的 YouTube URL"：检查输入的 URL 格式是否正确
2. "Downie 下载失败"：确认 Downie 是否正常运行
3. "下载超时"：检查网络连接和 Downie 设置
4. "无法获取字幕文件"：确认视频是否包含字幕

## 注意事项

1. 确保 Downie 已正确安装，并能正常下载你想要的视频。如果是Youtube，可能需要用户登录。
2. 使用Transcript功能的时候，视频必须包含字幕，否则无法提取文本
3. 下载目录默认为 `~/Downloads/Downie_Transcripts`，可在 `downie_youtube_transcript.py` 中第58行修改
4. API 服务默认端口为 3200，可在 `downie_youtube_transcript_server.py` 中修改
5. 程序会自动清理下载的临时文件（音频和字幕文件）

## 贡献

欢迎提交 Issue 和 Pull Request

## 许可证

[添加许可证信息]