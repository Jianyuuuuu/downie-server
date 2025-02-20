#!/usr/bin/env python

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from downie_core import downie_download

logger = logging.getLogger(__name__)

def get_video_id_from_url(url):
    """从YouTube URL中提取视频ID"""
    logger.debug(f"正在解析URL: {url}")
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            video_id = parse_qs(parsed_url.query)['v'][0]
            logger.debug(f"成功提取视频ID: {video_id}")
            return video_id
    elif parsed_url.hostname == 'youtu.be':
        video_id = parsed_url.path[1:]
        logger.debug(f"成功提取视频ID: {video_id}")
        return video_id
    logger.warning(f"无法从URL提取视频ID: {url}")
    return None

def extract_text_from_srt(srt_file):
    """从SRT文件中提取纯文本内容"""
    logger.info(f"开始从SRT文件提取文本: {srt_file}")
    text_parts = []
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            logger.debug(f"读取到 {len(lines)} 行内容")
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or '-->' in line or line.isdigit():
                    continue
                text_parts.append(line)
                logger.debug(f"处理第 {i} 行: {line[:50]}...")
        
        if not text_parts:
            logger.error("未从字幕文件中提取到任何文本内容")
            return ""
        
        text = ' '.join(text_parts)
        logger.info(f"成功提取文本，长度: {len(text)}字符")
        logger.debug(f"提取的文本内容前100个字符: {text[:100]}...")
        return text
    except Exception as e:
        logger.error(f"提取SRT文本时出错: {str(e)}")
        raise

# 默认下载目录配置
DEFAULT_DOWNLOAD_DIR = os.path.expanduser("~/Downloads/Downie_Transcripts")

# 确保下载目录存在
if not os.path.exists(DEFAULT_DOWNLOAD_DIR):
    os.makedirs(DEFAULT_DOWNLOAD_DIR)
    logger.info(f"创建下载目录: {DEFAULT_DOWNLOAD_DIR}")

def find_downloaded_files(video_id, download_dir=DEFAULT_DOWNLOAD_DIR, target_url=None):
    """查找下载的音频和字幕文件
    Args:
        video_id: YouTube视频ID
        download_dir: 下载目录路径，默认为DEFAULT_DOWNLOAD_DIR
        target_url: 目标YouTube URL，用于匹配文件元数据
    Returns:
        tuple: (音频文件路径, 字幕文件路径列表)
    """
    # 记录开始查找文件的日志
    logger.info(f"开始查找下载文件，视频ID: {video_id}")
    # 展开下载目录路径（处理~等路径符号）
    download_dir = os.path.expanduser(download_dir)
    # 初始化音频文件和字幕文件列表为空
    audio_file = None
    srt_files = []
    
    try:
        # 遍历下载目录中的所有文件
        for file in os.listdir(download_dir):
            # 获取完整的文件路径
            file_path = os.path.join(download_dir, file)
            # 检查是否为音频文件（mp3或m4a格式）
            if file.endswith(('.mp3', '.m4a')):
                try:
                    # 使用mdls命令获取文件的元数据（来源URL）
                    result = subprocess.run(['mdls', '-name', 'kMDItemWhereFroms', file_path], 
                                          capture_output=True, text=True)
                    # 如果成功获取元数据
                    if result.returncode == 0:
                        # 解析元数据输出行
                        metadata_lines = result.stdout.strip().split('\n')
                        for line in metadata_lines:
                            # 清理元数据行的多余字符
                            line = line.strip().strip('"() ')
                            # 如果提供了目标URL且在元数据中找到匹配
                            if target_url and target_url in line:
                                # 记录找到的音频文件
                                audio_file = file_path
                                # 获取音频文件的基本名称（不包含扩展名）
                                audio_base_name = os.path.splitext(os.path.basename(file_path))[0]
                                # 在同一目录下查找匹配的srt字幕文件
                                for srt_file_name in os.listdir(download_dir):
                                    # 检查是否为srt字幕文件
                                    if srt_file_name.endswith('.srt'):
                                        # 获取字幕文件的基本名称（移除.srt后缀）
                                        clean_srt_name = srt_file_name.split('.srt')[0]
                                        clean_audio_name = audio_base_name
                                        # 修改匹配逻辑：检查字幕文件名是否以音频文件名开头
                                        if clean_srt_name.startswith(clean_audio_name):
                                            # 找到匹配的字幕文件，添加到列表
                                            srt_file = os.path.join(download_dir, srt_file_name)
                                            srt_files.append(srt_file)
                                            logger.info(f"找到字幕文件: {srt_file}")
                                # 记录找到的音频和字幕文件信息
                                if audio_file:
                                    logger.info(f"找到音频文件: {audio_file}")
                                    logger.info(f"找到 {len(srt_files)} 个匹配的字幕文件")
                                    break
                        # 如果找到了音频文件，跳出外层循环
                        if audio_file:
                            break
                except Exception as e:
                    # 记录读取文件元数据时的错误，继续处理下一个文件
                    logger.warning(f"读取文件元数据时出错: {str(e)}")
                    continue
    except Exception as e:
        # 记录并抛出查找文件过程中的错误
        logger.error(f"查找下载文件时出错: {str(e)}")
        raise
    
    # 返回找到的音频文件路径和字幕文件路径列表
    return audio_file, srt_files

def process_youtube_url(url):
    """处理YouTube URL，返回文本内容"""
    logger.info(f"开始处理YouTube URL: {url}")
    video_id = get_video_id_from_url(url)
    if not video_id:
        logger.error(f"无效的YouTube URL: {url}")
        raise ValueError("无效的YouTube URL")
    
    logger.info("正在使用Downie下载视频...")
    success, message = downie_download(url, format_type="mp3", destination=DEFAULT_DOWNLOAD_DIR)
    if not success:
        logger.error(f"Downie下载失败: {message}")
        raise Exception(f"Downie下载失败: {message}")
    
    logger.info("等待下载完成...")
    max_attempts = 60  # 2分钟等待时间
    audio_file = None
    srt_files = []
    audio_found_time = None
    
    for attempt in range(max_attempts):
        time.sleep(2)
        audio_file, current_srt_files = find_downloaded_files(video_id, target_url=url)
        if audio_file:
            if not audio_found_time:  # 记录首次找到音频文件的时间
                audio_found_time = time.time()
                logger.info("找到音频文件，开始等待字幕文件...")
            
            if current_srt_files:  # 找到字幕文件
                srt_files = current_srt_files
                logger.info(f"找到 {len(srt_files)} 个字幕文件")
                break
            elif time.time() - audio_found_time >= 6:  # 从找到音频文件后等待6秒
                logger.warning("已找到音频文件但未找到字幕文件，可能该视频没有字幕")
                break
            logger.debug(f"等待字幕文件... (已等待 {int(time.time() - audio_found_time)} 秒)")
        else:
            logger.debug(f"等待下载... ({(attempt + 1) * 2}秒)")
    else:
        logger.error("下载超时：120秒内未找到匹配的音频文件")
        raise FileNotFoundError("下载超时：120秒内未找到匹配的音频文件")
    
    if not srt_files:
        logger.error("未找到字幕文件")
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)
            logger.info(f"已删除音频文件: {audio_file}")
        raise ValueError("无法获取字幕文件，请确保视频包含字幕")
    
    try:
        # 处理所有字幕文件并合并文本
        # 修改：只处理第一个字幕文件
        text = extract_text_from_srt(srt_files[0])
        if not text:
            logger.error("提取的文本内容为空")
            raise ValueError("提取的文本内容为空，请检查字幕文件是否有效")
        
        logger.info(f"成功处理字幕文件: {srt_files[0]}")
        logger.info(f"提取的文本长度: {len(text)} 字符")
        logger.debug(f"提取的文本内容前100个字符: {text[:100]}...")
        
        # 清理下载的文件
        files_to_delete = [(audio_file, "音频文件")] + [(srt_file, "字幕文件") for srt_file in srt_files]
        
        for file_path, file_type in files_to_delete:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"已删除{file_type}: {file_path}")
                except Exception as delete_error:
                    logger.error(f"删除{file_type}时出错: {str(delete_error)}")
        
        return text
    except Exception as e:
        # 发生错误时也要清理文件
        files_to_clean = [(audio_file, "音频文件")] + [(srt_file, "字幕文件") for srt_file in srt_files]
        for file_path, _ in files_to_clean:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as delete_error:
                    logger.error(f"清理文件时出错: {str(delete_error)}")
        raise

def main():
    if len(sys.argv) != 2:
        print("请提供YouTube视频URL")
        print("用法: python extract_youtube_text.py <YouTube-URL>")
        return
    
    url = sys.argv[1]
    try:
        text = process_youtube_url(url)
        print("\n提取的文本内容：")
        print(text)
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")

if __name__ == '__main__':
    main()