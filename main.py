from enum import Enum
import json
import random
import re
from typing import TypedDict
import pulp

from stats import Stat, Stats

# Define the problem
prob = pulp.LpProblem("Equipment_Optimization", pulp.LpMinimize)


stat_matchers = {
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
        re.compile(r"^\+(\d+)% chance to Suppress Spell Damage")
    ]
}


def parse_item(item) -> Stats:
    stats = {stat: 0 for stat in Stat}
    for modtype in ["implicitMods", "explicitMods", "craftedMods"]:
        for line in item["item"].get(modtype, []):
            for stat, matchers in stat_matchers.items():
                for matcher in matchers:
                    match = matcher.match(line)
                    if match:
                        stats[stat] += int(match.group(1))
    return stats


possible_mods = {
    "prefix": {
        "life": {Stat.LIFE: 70},
    },
    "suffix": {
        "fire":  {Stat.FIRE_RESISTANCE: 35},
        "cold":  {Stat.COLD_RESISTANCE: 35},
        "lightning":  {Stat.LIGHTNING_RESISTANCE: 35},
        "cold_fire":  {Stat.FIRE_RESISTANCE: 20, Stat.COLD_RESISTANCE: 20},
        "fire_lightning":  {Stat.FIRE_RESISTANCE: 20, Stat.LIGHTNING_RESISTANCE: 20},
        "cold_lightning":  {Stat.COLD_RESISTANCE: 20, Stat.LIGHTNING_RESISTANCE: 20},
        "chaos_cold":  {Stat.CHAOS_RESISTANCE: 15, Stat.COLD_RESISTANCE: 15},
        "chaos_lightning":  {Stat.CHAOS_RESISTANCE: 15, Stat.LIGHTNING_RESISTANCE: 15},
        "chaos_fire":  {Stat.CHAOS_RESISTANCE: 15, Stat.FIRE_RESISTANCE: 15},
        "all_attributes":  {Stat.DEXTERITY: 13, Stat.INTELLIGENCE: 13, Stat.STRENGTH: 13},
        "all_resistances":  {Stat.FIRE_RESISTANCE: 12, Stat.COLD_RESISTANCE: 12, Stat.LIGHTNING_RESISTANCE: 12},
        "dex_int":  {Stat.DEXTERITY: 25, Stat.INTELLIGENCE: 25},
        "dex_str":  {Stat.DEXTERITY: 25, Stat.STRENGTH: 25},
        "int_str":  {Stat.INTELLIGENCE: 25, Stat.STRENGTH: 25},
        "dex":  {Stat.DEXTERITY: 30},
        "int":  {Stat.INTELLIGENCE: 30},
        "str":  {Stat.STRENGTH: 30},
    }
}

blocks = {
    "of the Whelpling": {"fire"},
    "of the Salamander": {"fire"},
    "of the Drake": {"fire"},
    "of the Kiln": {"fire"},
    "of the Furnace": {"fire"},
    "of the Volcano": {"fire"},
    "of the Magma": {"fire"},
    "of Tzteosh": {"fire"},
    "of the Inuit": {"cold"},
    "of the Seal": {"cold"},
    "of the Penguin": {"cold"},
    "of the Yeti": {"cold"},
    "of the Walrus": {"cold"},
    "of the Polar Bear": {"cold"},
    "of the Ice": {"cold"},
    "of Haast": {"cold"},
    "of the Cloud": {"lightning"},
    "of the Squall": {"lightning"},
    "of the Storm": {"lightning"},
    "of the Thunderhead": {"lightning"},
    "of the Tempest": {"lightning"},
    "of the Maelstrom": {"lightning"},
    "of the Lightning": {"lightning"},
    "of Ephij": {"lightning"},
    "of the Mongoose": {"dex", "dex_int", "dex_str"},
    "of the Lynx": {"dex", "dex_int", "dex_str"},
    "of the Fox": {"dex", "dex_int", "dex_str"},
    "of the Falcon": {"dex", "dex_int", "dex_str"},
    "of the Panther": {"dex", "dex_int", "dex_str"},
    "of the Leopard": {"dex", "dex_int", "dex_str"},
    "of the Jaguar": {"dex", "dex_int", "dex_str"},
    "of the Phantom": {"dex", "dex_int", "dex_str"},
    "of the Wind": {"dex", "dex_int", "dex_str"},
    "of the Brute": {"str", "dex_str", "int_str"},
    "of the Wrestler": {"str", "dex_str", "int_str"},
    "of the Bear": {"str", "dex_str", "int_str"},
    "of the Lion": {"str", "dex_str", "int_str"},
    "of the Gorilla": {"str", "dex_str", "int_str"},
    "of the Goliath": {"str", "dex_str", "int_str"},
    "of the Leviathan": {"str", "dex_str", "int_str"},
    "of the Titan": {"str", "dex_str", "int_str"},
    "of the Gods": {"str", "dex_str", "int_str"},
    "of the Pupil": {"int", "dex_int", "int_str"},
    "of the Student": {"int", "dex_int", "int_str"},
    "of the Prodigy": {"int", "dex_int", "int_str"},
    "of the Augur": {"int", "dex_int", "int_str"},
    "of the Philosopher": {"int", "dex_int", "int_str"},
    "of the Sage": {"int", "dex_int", "int_str"},
    "of the Savant": {"int", "dex_int", "int_str"},
    "of the Virtuoso": {"int", "dex_int", "int_str"},
    "of the Genius": {"int", "dex_int", "int_str"},
    "Hale": {"life"},
    "Healthy": {"life"},
    "Sanguine": {"life"},
    "Stalwart": {"life"},
    "Stout": {"life"},
    "Robust": {"life"},
    "Rotund": {"life"},
    "Virile": {"life"},
    "Athlete's": {"life"},
    "of the Crystal": {"all_resistances"},
    "of the Prism": {"all_resistances"},
    "of the Kaleidoscope": {"all_resistances"},
    "of Variegation": {"all_resistances"},
    "of the Rainbow": {"all_resistances"},
    "of the Clouds": {"all_attributes"},
    "of the Sky": {"all_attributes"},
    "of the Meteor": {"all_attributes"},
    "of the Comet": {"all_attributes"},
    # "full_prefixes": set(possible_mods["prefix"].keys()),
    # "full_suffixes": set(possible_mods["suffix"].keys()),
}


def get_crafting_options(item):
    options = []
    mods = item["item"]["extended"]["mods"]["explicit"]
    prefix_count = 0
    suffix_count = 0
    craft_possibilities = []
    blocked_mods = set()
    for mod in mods:
        if mod["name"] in blocks:
            blocked_mods |= set(blocks[mod["name"]])
        if mod["tier"].startswith("P"):
            prefix_count += 1
        elif mod["tier"].startswith("S"):
            suffix_count += 1
    if prefix_count < 3:
        for mod in possible_mods["prefix"]:
            if mod not in blocked_mods:
                craft_possibilities.append(mod)
    if suffix_count < 3:
        for mod in possible_mods["suffix"]:
            if mod not in blocked_mods:
                craft_possibilities.append(mod)

    return craft_possibilities


# Define the slots and items
# slots = ["helmet", "gloves", "chest", "pants"]
num_items = 100
slots = ["armour.gloves", "armour.boots", "accessory.ring1", "accessory.ring2",
         "accessory.belt", "accessory.amulet"]

input = {}
with open("items.json") as f:
    i = json.load(f)
    for slot, items in i.items():
        input[slot] = []
        for item in items:
            stats = parse_item(item)
            input[slot].append(tuple(stats[stat] for stat in Stat))

if "accessory.ring" in input:
    input["accessory.ring1"] = input["accessory.ring"]
    input["accessory.ring2"] = input["accessory.ring"]
    del input["accessory.ring"]

# Define the decision variables
v = {}
v["x"] = pulp.LpVariable.dicts(
    "x", ((slot, item) for slot in slots for item in range(num_items)), cat='Binary')
for stat in Stat:
    v[stat] = pulp.LpVariable.dicts(
        str(stat.value), ((slot, item) for slot in slots for item in range(num_items)), cat='Binary')

# Objective function: minimize weighted sum of optional stats
prob += pulp.lpSum(
    -v["x"][slot, item] * input[slot][item][Stat.LIFE.value]
    - v["x"][slot, item] * 5 * input[slot][item][Stat.SPELL_SUPPRESSION.value]
    for slot in slots for item in range(num_items))

# Constraints: Each slot must have exactly one item chosen
for slot in slots:
    prob += pulp.lpSum(v["x"][slot, item] for item in range(num_items)) == 1

# Constraints: The sum of the resistances must be at least 100


def constraint(slots, input, v, stat: Stat, min_val: int):
    return pulp.lpSum(v["x"][slot, item_id] * input[slot][item_id][stat.value]
                      for slot in slots for item_id in range(len(input[slot]))) >= min_val


prob += constraint(slots, input, v, Stat.FIRE_RESISTANCE, 79)
prob += constraint(slots, input, v, Stat.COLD_RESISTANCE, 35)
prob += constraint(slots, input, v, Stat.LIGHTNING_RESISTANCE, 21)
prob += constraint(slots, input, v, Stat.CHAOS_RESISTANCE, 100)
prob += constraint(slots, input, v, Stat.DEXTERITY, 20)
prob += constraint(slots, input, v, Stat.INTELLIGENCE, 29)
prob += constraint(slots, input, v, Stat.MOVEMENT_SPEED, 25)
# prob += constraint(slots, input, v, Stat.SPELL_SUPPRESSION, 21)

# Constraint: The two chosen rings must be different
for item in range(num_items):
    prob += v["x"]["accessory.ring1", item] + \
        v["x"]["accessory.ring2", item] <= 1

# # Constraints: Each wildcard can be allocated to at most one type of resistance
# for slot in slots:
#     for item in range(num_items):
#         # prob += y_f[slot, item] + y_c[slot, item] + y_l[slot, item] <= 1

#         prob += v[Stat.FIRE_RESISTANCE][slot, item] <= v["x"][slot, item]
#         prob += v[Stat.COLD_RESISTANCE][slot, item] <= v["x"][slot, item]
#         prob += v[Stat.LIGHTNING_RESISTANCE][slot, item] <= v["x"][slot, item]


def print_item(item):
    print("Rarity:", item["item"]["rarity"])
    print(item["item"]["name"])
    print(item["item"]["typeLine"])
    if "implicitMods" in item["item"]:
        print("--------")
        for mod in item["item"]["implicitMods"]:
            print(mod, "(implicit)")
    if "explicitMods" in item["item"]:
        print("--------")
        for mod in item["item"]["explicitMods"]:
            print(mod)
    if "craftedMods" in item["item"]:
        for mod in item["item"]["craftedMods"]:
            print(mod, "(crafted)")


# Solve the problem
prob.solve()

# Print the results
stat_sums = {stat: 0 for stat in Stat}
for slot in slots:
    s = "accessory.ring" if slot.startswith("accessory.ring") else slot
    for idx, item in enumerate(i[s]):
        if pulp.value(v["x"][slot, idx]) == 1:
            print()
            # print("Slot:", slot, "Item:", item["item"]["name"])
            stats = parse_item(item)
            print_item(item)
            # for stat in Stat:
            #     print(stat.name, stats[stat])
            for stat in Stat:
                stat_sums[stat] += stats[stat]
print()
print("Total stats:", stat_sums)


# print(f"""{slot}: Item {item} with price {input[slot][item][Stat.LIFE]}, fire resistance {input[slot][item][Stat.FIRE_RESISTANCE]}, cold resistance {input[slot][item][Stat.COLD_RESISTANCE]}, lightning resistance {
#       input[slot][item][Stat.LIGHTNING_RESISTANCE]}, """)
