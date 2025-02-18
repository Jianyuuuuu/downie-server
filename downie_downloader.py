import subprocess
import sys
from urllib.parse import quote

def send_to_downie(url, postprocessing=None):
    """
    将URL发送到Downie进行下载
    """
    try:
        # 构建正确的 URL Scheme
        action_url = f"downie://XUOpenLink?url={quote(url)}"
        if postprocessing:
            action_url += f"&postprocessing={postprocessing}"
            
        subprocess.run(['open', action_url])
        return True
    except Exception as e:
        print(f"发送失败: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        # 默认下载音频
        send_to_downie(url, postprocessing="audio")
    else:
        print("请提供要下载的URL")
        print("用法: python downie_downloader.py <URL>")
        print("注意: 此脚本将自动设置为仅下载音频模式")