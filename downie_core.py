#!/usr/bin/env python

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from urllib.parse import quote

logger = logging.getLogger(__name__)

def downie_download(url, format_type="mp4", destination=None):
    """
    Downie的视频下载功能
    :param url: 要下载的视频URL
    :param format_type: 视频格式，默认为mp4
    :param destination: 下载目标文件夹路径，可选
    :return: bool, str 下载是否成功的标志和相关信息
    """
    logger.info(f"开始Downie下载功能，URL: {url}")
    logger.info(f"指定格式: {format_type}")
    if destination:
        logger.info(f"下载目标路径: {destination}")

    try:
        # 确保URL中的特殊字符被正确编码
        encoded_url = quote(url, safe='')
        
        # 构建基本的URL Scheme
        action_url = f"downie://XUOpenURL?url={encoded_url}"
        
        # 添加可选参数
        if format_type:
            action_url += f"&postprocessing={format_type}"
        
        # 如果提供了目标文件夹，展开并编码路径
        if destination:
            # 确保路径被展开为绝对路径
            expanded_path = os.path.expanduser(os.path.expandvars(destination))
            # 编码路径
            action_url += f"&destination={quote(expanded_path, safe='')}"

        # 发送到Downie进行下载
        subprocess.run(['open', action_url])
        logger.info("已发送下载请求到Downie")

        # 等待下载开始
        time.sleep(5)

        return True, "下载请求已成功发送到Downie"

    except Exception as e:
        error_msg = f"下载失败: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def main():
    if len(sys.argv) < 2:
        print("请提供要下载的视频URL")
        print("用法: python downie_test.py <URL> [目标文件夹路径] [格式]")
        print("示例: python downie_test.py https://example.com/video ~/Downloads/Videos mp4")
        return

    url = sys.argv[1]
    destination = None
    format_type = "mp4"
    # 解析命令行参数
    if len(sys.argv) > 2:
        destination = os.path.expanduser(sys.argv[2])
        # 检查目标路径是否存在
        if not os.path.exists(destination):
            print(f"错误: 目标文件夹不存在: {destination}")
            return
        elif not os.path.isdir(destination):
            print(f"错误: 指定路径不是文件夹: {destination}")
            return

    # 如果提供了格式参数
    if len(sys.argv) > 3:
        format_type = sys.argv[3]

    success, message = downie_download(url, format_type=format_type, destination=destination)
    
    if success:
        print("\n测试结果: 成功")
        print(f"详细信息: {message}")
    else:
        print("\n测试结果: 失败")
        print(f"错误信息: {message}")

if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    main()