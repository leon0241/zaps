package io.github.leon0241.mcwebhooks;

import org.bukkit.entity.EntityType;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDamageEvent;

import static org.bukkit.Bukkit.getLogger;

public final class DamageHandler implements Listener {
    public Webhook webhook = new Webhook();

    @EventHandler(priority = EventPriority.MONITOR)
    public void onPlayerDamage(EntityDamageEvent event) {
//        getLogger().info("Type1");
//        getLogger().info(event.getCause().toString());

        // Only player events, and only non-entity attack events
        if(!event.getEntityType().equals(EntityType.PLAYER)) {
            return;
        } else if (event.getCause().toString().startsWith("ENTITY")){
//            getLogger().info("entity");
            return;
        }

        var damagedPlayer = event.getEntity().getName();
        var source = event.getCause().toString();
        var damage = event.getFinalDamage();

        var string = damagedPlayer + " took " + damage + " damage from " + source;

        webhook.sendWebhook(string);
        getLogger().info(string);
        getLogger().info("");
    }

    @EventHandler(priority = EventPriority.MONITOR)
    public void onEntityEntityDamage(EntityDamageByEntityEvent event) {
//        getLogger().info("Type2");
        if(!event.getEntityType().equals(EntityType.PLAYER)) {
            return;
        }

        var damagedPlayer = event.getEntity().getName();
        var damageeEntity = event.getDamager();
        var damage = event.getFinalDamage();

        var string = damagedPlayer + " took " + damage + " damage from " + damageeEntity;

        webhook.sendWebhook(string);

        getLogger().info(string);
        getLogger().info("");
    }
}