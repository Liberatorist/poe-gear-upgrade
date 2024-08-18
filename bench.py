import json
from RePoE import mods, crafting_bench_options

from stats import Stat

relevant_stat_ids = {
    "fire_and_chaos_damage_resistance_%": [Stat.FIRE_RESISTANCE, Stat.CHAOS_RESISTANCE],
    "cold_and_chaos_damage_resistance_%": [Stat.COLD_RESISTANCE, Stat.CHAOS_RESISTANCE],
    "lightning_and_chaos_damage_resistance_%": [Stat.LIGHTNING_RESISTANCE, Stat.CHAOS_RESISTANCE],
    "base_cold_damage_resistance_%": [Stat.COLD_RESISTANCE],
    "base_fire_damage_resistance_%": [Stat.FIRE_RESISTANCE],
    "base_lightning_damage_resistance_%": [Stat.LIGHTNING_RESISTANCE],
    "cold_and_lightning_damage_resistance_%": [Stat.COLD_RESISTANCE, Stat.LIGHTNING_RESISTANCE],
    "fire_and_cold_damage_resistance_%": [Stat.FIRE_RESISTANCE, Stat.COLD_RESISTANCE],
    "fire_and_lightning_damage_resistance_%": [Stat.FIRE_RESISTANCE, Stat.LIGHTNING_RESISTANCE],
    "base_resist_all_elements_%": [Stat.FIRE_RESISTANCE, Stat.COLD_RESISTANCE, Stat.LIGHTNING_RESISTANCE],
    "additional_strength_and_intelligence": [Stat.STRENGTH, Stat.INTELLIGENCE],
    "additional_dexterity_and_intelligence": [Stat.DEXTERITY, Stat.INTELLIGENCE],
    "additional_strength_and_dexterity": [Stat.STRENGTH, Stat.DEXTERITY],
    "additional_strength": [Stat.STRENGTH],
    "additional_intelligence": [Stat.INTELLIGENCE],
    "additional_dexterity": [Stat.DEXTERITY],
    "additional_all_attributes": [Stat.STRENGTH, Stat.INTELLIGENCE, Stat.DEXTERITY],
    "base_maximum_life": [Stat.LIFE],
    "base_movement_velocity_+%": [Stat.MOVEMENT_SPEED],
    "base_spell_suppression_chance_%": [Stat.SPELL_SUPPRESSION],
}

crafts = {}
# item_class = "Ring"
for item_class in ["Ring", "Amulet", "Belt", "Body Armour", "Boots", "Gloves", "Helmet", "Shield"]:
    crafts[item_class] = []
    craftable_mods = [
        option["actions"]["add_explicit_mod"] for option in crafting_bench_options if item_class in option["item_classes"] and "add_explicit_mod" in option["actions"]
    ]

    relevant_crafts = []
    relevant_groups = set()
    for relevant_stat_id, stats in relevant_stat_ids.items():
        max_value = 0
        groups = set()
        for mod in craftable_mods:
            for stat in mods[mod]["stats"]:
                if stat["id"] == relevant_stat_id:
                    if stat["max"] > max_value:
                        max_value = stat["max"]
                        groups = set(mods[mod]["groups"])
        if max_value > 0:
            relevant_groups.update(groups)
            relevant_crafts.append(
                {"stat_id": relevant_stat_id, "value": max_value, "groups": groups, "blocked_by": set()})

    blocks = {group: set() for group in relevant_groups}
    for mod in mods.values():
        for group in set(mod["groups"]) & relevant_groups:
            if mod["name"] != "":
                blocks[group].add(mod["name"])

    for craft in relevant_crafts:
        for group in craft["groups"]:
            craft["blocked_by"] |= blocks[group]
        crafts[item_class].append(craft)


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


print(crafts)
with open("crafts.json", "w") as f:
    f.write(json.dumps(crafts, indent=4, cls=SetEncoder))
# print(crafts)
# bench_mods = {


# }

# for mod_id, mod in mods.items():
#     if mod["domain"] == "crafted":
#         if "IncreasedLife" in mod["groups"]:
#             print(mod_id)
