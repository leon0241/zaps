package io.github.leon0241.mcwebhooks;

public class WebhookErrorException extends Exception {

    public WebhookErrorException(String message) {
        super("Error trying to send webhook" + message);
    }
}