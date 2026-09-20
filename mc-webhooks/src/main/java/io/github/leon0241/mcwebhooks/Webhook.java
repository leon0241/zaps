package io.github.leon0241.mcwebhooks;

import org.json.simple.JSONObject;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import static org.bukkit.Bukkit.getLogger;

public class Webhook {

    private final HttpClient httpClient = HttpClient.newHttpClient();

    public void sendWebhook(JSONObject request) {
        sendTo("http://127.0.0.1:5000/webhook", request);
        sendTo("http://192.168.0.81:8080/webhook", request); // second request
    }

    private void sendTo(String url, JSONObject request) {
        HttpRequest httpRequest = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(request.toJSONString()))
                .build();

        httpClient.sendAsync(httpRequest, HttpResponse.BodyHandlers.ofString())
                .exceptionally(ex -> {
                    getLogger().warning("Webhook to " + url + " failed: " + ex.getMessage());
                    return null;
                });
    }
}