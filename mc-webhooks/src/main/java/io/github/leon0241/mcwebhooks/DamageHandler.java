package io.github.leon0241.mcwebhooks;

import org.bukkit.entity.EntityType;
import org.bukkit.entity.LivingEntity;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDamageEvent;
import org.json.simple.JSONObject;

import static org.bukkit.Bukkit.getLogger;

public final class DamageHandler implements Listener {
    public Webhook webhook = new Webhook();

    @EventHandler(priority = EventPriority.MONITOR)
    public void onPlayerDamage(EntityDamageEvent event) {
        // Only player events, and only non-entity attack events
        if (!event.getEntityType().equals(EntityType.PLAYER)) {
            return;
        }

        // Redefine living entity to get health
        if (!(event.getEntity() instanceof LivingEntity)) return;
        LivingEntity entity = (LivingEntity) event.getEntity();

        String damagedPlayer = entity.getName();
        double damage = event.getFinalDamage();
        String source;

        if (event instanceof EntityDamageByEntityEvent) {
            EntityDamageByEntityEvent entityEvent = (EntityDamageByEntityEvent) event;
            source = entityEvent.getDamager().getName();
            // entity-caused damage logic
        } else {
            EntityDamageEvent otherEvent = event;
            source = otherEvent.getCause().toString();
        }

        JSONObject jsonString = new JSONObject();

        String string = "";

        jsonString.put("Player", damagedPlayer);
        jsonString.put("Source", source);


        if (event.getFinalDamage() > entity.getHealth()) {
            // On Death
            string = damagedPlayer + " died from " + source;

            jsonString.put("Death", "true");

        } else {
            // On not death
            string = damagedPlayer + " took " + damage + " damage from " + source;

            jsonString.put("Death", "false");
            jsonString.put("Damage", damage);
        }

        getLogger().info(jsonString.toJSONString());
        webhook.sendWebhook(jsonString);
        getLogger().info(string);
        getLogger().info("");
    }
}