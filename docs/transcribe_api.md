# 音频转写 API 文档

## 接口说明
该接口用于将音频文件转写为文本。支持多种音频格式和语言。

### 基本信息
- **接口URL**: `/transcribe`
- **请求方式**: POST
- **Content-Type**: multipart/form-data

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | 音频文件，支持格式：mp3, wav, m4a, flac |
| language_code | String | 是 | 音频语言代码，如：zh-CN（中文）, en-US（英文） |
| model | String | 否 | 转写模型，可选值：latest_long（默认）, latest_short |

### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| transcription | String | 转写结果文本 |
| error | String | 错误信息（仅在发生错误时返回） |

### 响应示例

成功响应：
```json
{
    "transcription": "这是转写的文本内容..."
}

错误响应
错误响应示例：
```json
{
    "error": "Invalid file type. Only audio files are allowed."
}
```
### 状态码说明
状态码 说明
200 请求成功 
400 请求参数错误 
500 服务器内部错误
### 使用示例
Python:

```python
import requests

# 准备请求数据
url = "http://your-domain.com/transcribe"
files = {
    'file': ('audio.mp3', open('path/to/audio.mp3', 'rb'), 'audio/mpeg')
}
data = {
    'language_code': 'zh-CN',
    'model': 'latest_long'
}

# 发送请求
response = requests.post(url, files=files, data=data)

# 处理响应
if response.status_code == 200:
    result = response.json()
    print(f"转写结果: {result['transcription']}")
else:
    print(f"请求失败: {response.json()['error']}")
```

### 注意事项
1. 音频文件大小限制：50MB
2. 支持的音频格式：mp3, wav, m4a, flac
3. 建议音频时长不超过4小时
4. 请确保音频质量清晰，背景噪音较小

3. 创建测试音频文件夹：
```bash
mkdir d:\vs-program\google\py\web-cloud\tests\test_files
```


使用说明：

1. 将测试音频文件放入 tests/test_files 目录
2. 运行测试：
```bash
python tests/test_transcribe.py
 ```

## js版本
### js测试代码
```java
import java.io.File;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import okhttp3.*;

public class TranscribeTest {
    private static final String BASE_URL = "http://127.0.0.1:8080";
    private static final String ENDPOINT = "/transcribe";

    public static void main(String[] args) {
        testTranscribeApi();
    }

    public static void testTranscribeApi() {
        // 测试音频文件
        File audioFile = new File("tests/test_files/test_audio.mp3");
        if (!audioFile.exists()) {
            System.out.println("测试音频文件不存在: " + audioFile.getPath());
            return;
        }

        try {
            OkHttpClient client = new OkHttpClient();

            // 构建multipart请求
            RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", "test_audio.mp3",
                    RequestBody.create(MediaType.parse("audio/mpeg"), audioFile))
                .addFormDataPart("language_code", "zh-CN")
                .addFormDataPart("model", "latest_long")
                .build();

            Request request = new Request.Builder()
                .url(BASE_URL + ENDPOINT)
                .post(requestBody)
                .build();

            // 记录开始时间
            Instant start = Instant.now();

            // 发送请求
            Response response = client.newCall(request).execute();
            String responseBody = response.body().string();

            // 计算耗时
            Duration duration = Duration.between(start, Instant.now());

            // 打印测试结果
            System.out.println("\n=== 转写接口测试结果 ===");
            System.out.println("请求耗时: " + duration.toMillis() / 1000.0 + "秒");
            System.out.println("状态码: " + response.code());
            System.out.println("响应内容: " + responseBody);

            if (response.code() == 200) {
                System.out.println("\n✓ 测试通过！");
            } else {
                System.out.println("\n✗ 测试失败！");
            }

        } catch (IOException e) {
            System.out.println("\n✗ 测试失败: " + e.getMessage());
        }
    }
}
```

### 添加 OkHttp 依赖
```java
## java版本
### 测试代码
```java
import java.io.File;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import okhttp3.*;

public class TranscribeTest {
    private static final String BASE_URL = "http://127.0.0.1:8080";
    private static final String ENDPOINT = "/transcribe";

    public static void main(String[] args) {
        testTranscribeApi();
    }

    public static void testTranscribeApi() {
        // 测试音频文件
        File audioFile = new File("tests/test_files/test_audio.mp3");
        if (!audioFile.exists()) {
            System.out.println("测试音频文件不存在: " + audioFile.getPath());
            return;
        }

        try {
            OkHttpClient client = new OkHttpClient();

            // 构建multipart请求
            RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", "test_audio.mp3",
                    RequestBody.create(MediaType.parse("audio/mpeg"), audioFile))
                .addFormDataPart("language_code", "zh-CN")
                .addFormDataPart("model", "latest_long")
                .build();

            Request request = new Request.Builder()
                .url(BASE_URL + ENDPOINT)
                .post(requestBody)
                .build();

            // 记录开始时间
            Instant start = Instant.now();

            // 发送请求
            Response response = client.newCall(request).execute();
            String responseBody = response.body().string();

            // 计算耗时
            Duration duration = Duration.between(start, Instant.now());

            // 打印测试结果
            System.out.println("\n=== 转写接口测试结果 ===");
            System.out.println("请求耗时: " + duration.toMillis() / 1000.0 + "秒");
            System.out.println("状态码: " + response.code());
            System.out.println("响应内容: " + responseBody);

            if (response.code() == 200) {
                System.out.println("\n✓ 测试通过！");
            } else {
                System.out.println("\n✗ 测试失败！");
            }

        } catch (IOException e) {
            System.out.println("\n✗ 测试失败: " + e.getMessage());
        }
    }
}
```

### 添加 OkHttp 依赖
```java
<dependency>
    <groupId>com.squareup.okhttp3</groupId>
    <artifactId>okhttp</artifactId>
    <version>4.9.1</version>
</dependency>
```