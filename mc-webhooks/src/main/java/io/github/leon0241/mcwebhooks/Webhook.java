package io.github.leon0241.mcwebhooks;

import org.json.simple.JSONObject;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import static org.bukkit.Bukkit.getLogger;

public class Webhook {

    public void sendWebhook(JSONObject request) {
        var url = "http://192.168.0.81:5000/webhook";
        var url2 = "http://192.168.0.81:8080/webhook";
        getLogger().info(url);
        getLogger().info(request.toJSONString());

        HttpClient httpClient = HttpClient.newHttpClient();
//            String json = new DiscordWebhookRequestDto(request).toJson();
        HttpRequest httpRequest = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .method("POST", HttpRequest.BodyPublishers.ofString(request.toJSONString()))
                .build();
        httpClient.sendAsync(
                httpRequest, HttpResponse.BodyHandlers.ofString()
        ).exceptionally(ex -> {
            getLogger().warning("Webhook failed: " + ex.getMessage());
            return null;
        });
    }
}