const fs = require('fs');
const axios = require('axios');
const FormData = require('form-data');

const BASE_URL = 'http://127.0.0.1:8080';
const ENDPOINT = '/transcribe';

async function testTranscribeApi() {
    // 测试音频文件路径
    const audioFilePath = 'tests/test_files/test_audio.mp3';

    try {
        // 检查文件是否存在
        if (!fs.existsSync(audioFilePath)) {
            throw new Error(`测试音频文件不存在: ${audioFilePath}`);
        }

        // 准备表单数据
        const formData = new FormData();
        formData.append('file', fs.createReadStream(audioFilePath));
        formData.append('language_code', 'zh-CN');
        formData.append('model', 'latest_long');

        // 记录开始时间
        const startTime = Date.now();

        // 发送请求
        const response = await axios.post(`${BASE_URL}${ENDPOINT}`, formData, {
            headers: {
                ...formData.getHeaders()
            }
        });

        // 计算耗时
        const duration = (Date.now() - startTime) / 1000;

        // 打印测试结果
        console.log('\n=== 转写接口测试结果 ===');
        console.log(`请求耗时: ${duration.toFixed(2)}秒`);
        console.log(`状态码: ${response.status}`);
        console.log(`响应内容:`, response.data);

        if (response.status === 200 && response.data.transcription) {
            console.log('\n✓ 测试通过！');
        } else {
            console.log('\n✗ 测试失败：响应格式错误');
        }

    } catch (error) {
        console.log('\n✗ 测试失败:', error.message);
        if (error.response) {
            console.log('错误响应:', error.response.data);
        }
    }
}

// 运行测试
testTranscribeApi();