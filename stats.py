from enum import Enum
from typing import TypedDict


class Stat(Enum):
    FIRE_RESISTANCE = 0
    COLD_RESISTANCE = 1
    LIGHTNING_RESISTANCE = 2
    CHAOS_RESISTANCE = 3
    LIFE = 4
    STRENGTH = 5
    DEXTERITY = 6
    INTELLIGENCE = 7
    MOVEMENT_SPEED = 8
    SPELL_SUPPRESSION = 9


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
