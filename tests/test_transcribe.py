import requests
import os
import time

def test_transcribe_api():
    """测试音频转写接口"""
    # API配置
    BASE_URL = "http://127.0.0.1:8080"
    ENDPOINT = "/transcribe"
    
    # 测试音频文件路径
    # audio_file_path = "tests/test_files/test_audio.mp3"
    audio_file_path = "让我来告诉你吧——是手心啊，哈哈哈.wav"

    # 确保测试文件存在
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"测试音频文件不存在: {audio_file_path}")
    
    try:
        # 准备请求数据
        files = {
            'file': ('test_audio.mp3', open(audio_file_path, 'rb'), 'audio/mpeg')
        }
        data = {
            'language_code': 'zh-CN',
            'model': 'latest_long'
        }
        
        # 发送请求
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            files=files,
            data=data
        )
        end_time = time.time()
        
        # 打印测试结果
        print("\n=== 转写接口测试结果 ===")
        print(f"请求耗时: {end_time - start_time:.2f}秒")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        # 检查响应
        assert response.status_code == 200, "请求失败"
        assert "transcription" in response.json(), "响应格式错误"
        
        print("\n✓ 测试通过！")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
    
if __name__ == "__main__":
    test_transcribe_api()