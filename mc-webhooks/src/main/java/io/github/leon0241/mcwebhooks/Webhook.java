package io.github.leon0241.mcwebhooks;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import static org.bukkit.Bukkit.getLogger;

public class Webhook {

    public void sendWebhook(String request) {
        HttpClient httpClient = HttpClient.newHttpClient();
//            String json = new DiscordWebhookRequestDto(request).toJson();
        HttpRequest httpRequest = HttpRequest.newBuilder()
                .uri(URI.create("https://webhook.site/e9c14e38-82ea-4abb-892c-8cec0ded591f"))
                .header("Content-Type", "application/json")
                .method("POST", HttpRequest.BodyPublishers.ofString(request))
                .build();
        httpClient.sendAsync(
                httpRequest, HttpResponse.BodyHandlers.ofString()
        ).exceptionally(ex -> {
            getLogger().warning("Webhook failed: " + ex.getMessage());
            return null;
        });
    }
}