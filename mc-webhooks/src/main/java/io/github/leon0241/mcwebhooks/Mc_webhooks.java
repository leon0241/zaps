package io.github.leon0241.mcwebhooks;

import org.bukkit.Bukkit;
import org.bukkit.event.Listener;
import org.bukkit.plugin.java.JavaPlugin;

public final class Mc_webhooks extends JavaPlugin implements Listener {

    @Override
    public void onEnable() {
        saveResource("config.yml", false);

        saveDefaultConfig();

        // Plugin startup logic
        Bukkit.getPluginManager().registerEvents(new DamageHandler(), this);
    }

    @Override
    public void onDisable() {
        // Plugin shutdown logic
    }
}