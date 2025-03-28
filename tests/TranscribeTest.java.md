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