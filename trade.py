import json
import pprint
import re
from typing import TypedDict
import requests

from enum import Enum

import request_lib


class Stat(Enum):
    FIRE_RESISTANCE = "pseudo.pseudo_total_fire_resistance"
    COLD_RESISTANCE = "pseudo.pseudo_total_cold_resistance"
    LIGHTNING_RESISTANCE = "pseudo.pseudo_total_lightning_resistance"
    CHAOS_RESISTANCE = "pseudo.pseudo_total_chaos_resistance"
    LIFE = "pseudo.pseudo_total_life"
    STRENGTH = "pseudo.pseudo_total_strength"
    DEXTERITY = "pseudo.pseudo_total_dexterity"
    INTELLIGENCE = "pseudo.pseudo_total_intelligence"
    MOVEMENT_SPEED = "pseudo.pseudo_increased_movement_speed"
    SPELL_SUPPRESSION = "explicit.stat_3680664274"


class Weight(TypedDict):
    stat: Stat
    value: float


class Trade:
    request_handler = request_lib.RequestHandler()

    def get_items(self, weights: list[Weight], max_price: int, category: str):
        query = {
            "query": {
                "status": {
                    "option": "online"
                },
                "stats": [
                    {
                        "type": "weight",
                        "filters": [
                            {
                                "id": weight["stat"].value,
                                "value": {
                                    "weight": weight["value"]
                                },
                                "disabled": False
                            }
                            for weight in weights
                        ],
                        "value": {
                            "min": 1
                        },
                        "disabled": False
                    }
                ],
                "filters": {
                    "trade_filters": {
                        "filters": {
                            "price": {
                                "max": max_price
                            }
                        }
                    },
                    "type_filters": {
                        "filters": {
                            "category": {
                                "option": category
                            }
                        }
                    }
                }
            },
            "sort": {
                "statgroup.0": "desc"
            }
        }
        # pprint.pprint(query)

        for item in self.request_handler.iterate_trade(query):
            yield item


class Stats(TypedDict):
    Stat.FIRE_RESISTANCE: int
    Stat.COLD_RESISTANCE: int
    Stat.LIGHTNING_RESISTANCE: int
    Stat.CHAOS_RESISTANCE: int
    Stat.LIFE: int
    Stat.STRENGTH: int
    Stat.DEXTERITY: int
    Stat.INTELLIGENCE: int
    Stat.MOVEMENT_SPEED: int


['+55 to Dexterity',
 'Adds 13 to 21 Cold Damage to Attacks',
 '41% increased Evasion Rating',
 '+119 to maximum Life',
 '+42% to Fire Resistance',
 '+44% to Lightning Resistance',
 '16% increased Stun and Block Recovery']
matchers = {
    Stat.FIRE_RESISTANCE:    [
        re.compile(r"^\+(\d+)% to Fire Resistance$"),
        re.compile(r"^\+(\d+)% to Fire and Chaos Resistances$"),
        re.compile(r"^\+(\d+)% to Fire and Cold Resistances$"),
        re.compile(r"^\+(\d+)% to Fire and Lightning Resistances$"),
        re.compile(r"^\+(\d+)% to all Elemental Resistances$"),
    ],
    Stat.COLD_RESISTANCE:    [
        re.compile(r"^\+(\d+)% to Cold Resistance$"),
        re.compile(r"^\+(\d+)% to Cold and Chaos Resistances$"),
        re.compile(r"^\+(\d+)% to Fire and Cold Resistances$"),
        re.compile(r"^\+(\d+)% to Cold and Lightning Resistances$"),
        re.compile(r"^\+(\d+)% to all Elemental Resistances$"),
    ],
    Stat.LIGHTNING_RESISTANCE: [
        re.compile(r"^\+(\d+)% to Lightning Resistance$"),
        re.compile(r"^\+(\d+)% to Lightning and Chaos Resistances$"),
        re.compile(r"^\+(\d+)% to Fire and Lightning Resistances$"),
        re.compile(r"^\+(\d+)% to Cold and Lightning Resistances$"),
        re.compile(r"^\+(\d+)% to all Elemental Resistances$"),
    ],
    Stat.CHAOS_RESISTANCE:   [
        re.compile(r"^\+(\d+)% to Chaos Resistance$"),
        re.compile(r"^\+(\d+)% to Fire and Chaos Resistances$"),
        re.compile(r"^\+(\d+)% to Cold and Chaos Resistances$"),
        re.compile(r"^\+(\d+)% to Lightning and Chaos Resistances$"),
    ],
    Stat.LIFE:               [
        re.compile(r"^\+(\d+) to maximum Life$"),
    ],
    Stat.STRENGTH:           [
        re.compile(r"^\+(\d+) to Strength$"),
        re.compile(r"^\+(\d+) to Strength and Dexterity$"),
        re.compile(r"^\+(\d+) to Strength and Intelligence$"),
        re.compile(r"^\+(\d+) to all Attributes$"),
    ],
    Stat.DEXTERITY:          [
        re.compile(r"^\+(\d+) to Dexterity$"),
        re.compile(r"^\+(\d+) to Strength and Dexterity$"),
        re.compile(r"^\+(\d+) to Dexterity and Intelligence$"),
        re.compile(r"^\+(\d+) to all Attributes$"),
    ],
    Stat.INTELLIGENCE:       [
        re.compile(r"^\+(\d+) to Intelligence$"),
        re.compile(r"^\+(\d+) to Strength and Intelligence$"),
        re.compile(r"^\+(\d+) to Dexterity and Intelligence$"),
        re.compile(r"^\+(\d+) to all Attributes$"),
    ],
    Stat.MOVEMENT_SPEED:     [
        re.compile(r"^(\d+)% increased Movement Speed$"),
    ],
    Stat.SPELL_SUPPRESSION:  [
        re.compile(r"^(\d+)% chance to Suppress Spell Damage")
    ]
}


def parse_item(item) -> Stats:
    stats = {
        Stat.FIRE_RESISTANCE: 0,
        Stat.COLD_RESISTANCE: 0,
        Stat.LIGHTNING_RESISTANCE: 0,
        Stat.CHAOS_RESISTANCE: 0,
        Stat.LIFE: 0,
        Stat.STRENGTH: 0,
        Stat.DEXTERITY: 0,
        Stat.INTELLIGENCE: 0,
        Stat.MOVEMENT_SPEED: 0,
        Stat.SPELL_SUPPRESSION: 0
    }
    for line in item["item"]["explicitMods"]:
        for stat in matchers:
            for matcher in matchers[stat]:
                match = matcher.match(line)
                if match:
                    stats[stat] += int(match.group(1))

    return stats


def get_weight_sum(stats: Stats, weights: list[Weight]) -> float:
    sum = 0
    for weight in weights:
        sum += stats[weight["stat"]] * weight["value"]
        if weight["stat"] == Stat.LIFE:
            sum += stats[Stat.STRENGTH] / 2
    return sum


if __name__ == "__main__":
    trade = Trade()
    weights = [
        {"stat": Stat.FIRE_RESISTANCE, "value": 1},
        {"stat": Stat.COLD_RESISTANCE, "value": 1},
        {"stat": Stat.LIGHTNING_RESISTANCE, "value": 1},
        {"stat": Stat.CHAOS_RESISTANCE, "value": 4},
        {"stat": Stat.LIFE, "value": 2},
        {"stat": Stat.STRENGTH, "value": 1},
        {"stat": Stat.DEXTERITY, "value": 1},
        {"stat": Stat.INTELLIGENCE, "value": 1},
        {"stat": Stat.MOVEMENT_SPEED, "value": 5},
        {"stat": Stat.SPELL_SUPPRESSION, "value": 10},
    ]
    items = {}
    for slot in ["armour.gloves", "armour.boots", "accessory.ring", "accessory.belt", "accessory.amulet"]:
        print(slot)
        items[slot] = []
        for item in trade.get_items(weights, 100, slot):
            items[slot].append(item)
    with open("items.json", "w") as f:
        f.write(json.dumps(items, indent=4))
        # stats = parse_item(item)
        # sum = get_weight_sum(stats, weights)
        # items[item["item"]["name"]] = sum

    #     for item in trade.get_items(weights, 10, f"{slot}.gloves"):
    #         stats = parse_item(item)
    #         sum = get_weight_sum(stats, weights)
    #         items[item["item"]["name"]] = sum
    # for item in trade.get_items(weights, 10, "armour.gloves"):
    #     stats = parse_item(item)
    #     sum = get_weight_sum(stats, weights)
    #     with open("item.json", "w") as f:
    #         f.write(str(item))
    #     break
    #     print(item["item"]["name"], sum)
