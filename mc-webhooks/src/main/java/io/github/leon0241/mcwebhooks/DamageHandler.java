package io.github.leon0241.mcwebhooks;

import org.bukkit.entity.EntityType;
import org.bukkit.entity.LivingEntity;
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
        // Only player events, and only non-entity attack events
        if(!event.getEntityType().equals(EntityType.PLAYER)) {
            return;
        } else if (event.getCause().toString().startsWith("ENTITY")){
            return;
        }

        // Redefine living entity to get health
        if (!(event.getEntity() instanceof LivingEntity)) return;
        LivingEntity entity = (LivingEntity) event.getEntity();

        // Extract info
        var damagedPlayer = entity.getName();
        var source = event.getCause().toString();
        var damage = event.getFinalDamage();

        var string = "";
        // On Death
        if (event.getFinalDamage() > entity.getHealth()) {
            string = damagedPlayer + " died from " + source;
        // On not death
        } else {
            string = damagedPlayer + " took " + damage + " damage from " + source;
        }

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

        // Redefine living entity and get health - if higher than final damage then death.
        if (!(event.getEntity() instanceof LivingEntity)) return;
        LivingEntity entity = (LivingEntity) event.getEntity();

        var damagedPlayer = entity.getName();
        var damageeEntity = event.getDamager();
        var damage = event.getFinalDamage();

        var string = "";
        // On Death
        if (event.getFinalDamage() > entity.getHealth()) {
            string = damagedPlayer + " died from " + damageeEntity;
            // On not death
        } else {
            string = damagedPlayer + " took " + damage + " damage from " + damageeEntity;
        }

        webhook.sendWebhook(string);

        getLogger().info(string);
        getLogger().info("");
    }
}