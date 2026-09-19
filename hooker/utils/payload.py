from typing import Any


class Payload:
    player: str = ""
    death: bool = False
    damage: int = 0
    source: str = ""

    def unpack_json(self, data: dict[str, Any]):
        self.player = data["Player"]
        self.death = data["Death"] == "true"
        self.damage = data["Damage"] if "Damage" in data else 99
        self.source = data["Source"]
        return

    def get_player(self) -> str:
        return self.player

    def get_death(self) -> bool:
        return self.death

    def get_damage(self) -> int:
        return self.damage

    def get_source(self) -> str:
        return self.source
