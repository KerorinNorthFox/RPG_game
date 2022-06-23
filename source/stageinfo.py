from source.character import *


stage_num: int = 2


# ステージ1-1
def one_one() -> list[object | int]:
    Enemy: list[object] = []
    Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, False, 0))
    now_stage: int = 1
    exp: int = 100
    skill_point: int = 10
    return Enemy, now_stage, exp, skill_point

# ステージ1-2
def one_two() -> list[object | int]:
    Enemy: list[object] = []
    Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, False, 0))
    Enemy.append(EnemyClass("敵B", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, False, 0))
    now_stage: int = 2
    exp: int = 300
    skill_point: int = 20
    return Enemy, now_stage, exp, skill_point

# ステージ1-3
def one_three() -> list[object | int]:
    Enemy: list[object] = []
    Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, False, 0))
    Enemy.append(EnemyClass("敵B", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, True, 0))
    Enemy.append(EnemyClass("敵C", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, False, 0))
    Enemy.append(EnemyClass("敵D", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, True, 0))
    now_stage: int = 3
    exp: int = 500
    skill_point: int = 40
    return Enemy, now_stage, exp, skill_point


# EnemyClss(name, job, hp, mp, strg, vtl, mana, aatk, amana, 
#           speed, alive, element, way_type)