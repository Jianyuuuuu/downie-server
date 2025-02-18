# Downie YouTube 文本提取服务

这是一个基于 Downie 的 YouTube 视频文本提取服务，可以自动从 YouTube 视频中提取字幕文本内容。该服务支持命令行工具和 HTTP API 两种使用方式。

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
- 确保 Downie 已配置好 YouTube 下载功能，并设置好下载目录。

## 安装配置

1. 克隆项目并安装依赖：

```bash
git clone <repository_url>
cd downie-server
pip install -r requirements.txt
```

2. 确保 Downie 的下载目录设置为默认位置（~/Downloads/Downie）

## 使用方法

### 命令行工具

1. 直接下载视频：

```bash
python downie_downloader.py <YouTube-URL>
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

## 注意事项

1. 确保 Downie 已正确安装并能正常下载 YouTube 视频
2. 视频必须包含字幕，否则无法提取文本
3. 下载目录默认为 ~/Downloads/Downie，如需修改请更新代码中的路径
4. API 服务默认端口为 3200，可在代码中修改

## 日志

- 服务运行日志保存在 `youtube_text_api.log`
- 包含详细的操作记录和错误信息

## 错误处理

常见错误及解决方案：

1. "无效的 YouTube URL"：检查输入的 URL 格式是否正确
2. "Downie 下载失败"：确认 Downie 是否正常运行
3. "下载超时"：检查网络连接和 Downie 设置
4. "无法获取字幕文件"：确认视频是否包含字幕

## 开发说明

主要模块说明：

- `downie_downloader.py`: Downie 下载工具
- `downie_youtube_transcript.py`: 文本提取核心功能
- `downie_youtube_transcript_server.py`: HTTP API 服务

## 许可证

[添加许可证信息]

## 贡献

欢迎提交 Issue 和 Pull Request