#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可见属性规范与映射（仅底层原始属性，不包含抽象属性）

输出统一为 characteristic_ 前缀的键，供 C 特征使用。
"""
from typing import Dict, Any


def get_visible_characteristics(entity_type: str) -> Dict[str, Any]:
    """根据实体类型返回规范化的可见属性字典（characteristic_*）。

    entity_type 支持的值（大小写不敏感）：
    - 动物: Tiger, BlackBear, Boar, Rabbit, Pheasant, Dove
    - 植物: Strawberry, ToxicStrawberry, Mushroom, ToxicMushroom,
            Potato, SweetPotato, Acorn, Chestnut
    """
    t = (entity_type or "").strip()
    key = t.lower()

    # 动物
    if key == "tiger":
        return {
            "characteristic_size": "large",
            "characteristic_teeth_type": "sharp",
            "characteristic_claws_type": "sharp",
            "characteristic_speed": 2,
            "characteristic_flight": "no_fly",
        }
    if key == "blackbear":
        return {
            "characteristic_size": "large",
            "characteristic_teeth_type": "sharp",
            "characteristic_claws_type": "sharp",
            "characteristic_speed": 2,
            "characteristic_flight": "no_fly",
        }
    if key == "boar":
        return {
            "characteristic_size": "large",
            "characteristic_teeth_type": "sharp",
            "characteristic_claws_type": "blunt",
            "characteristic_speed": 2,
            "characteristic_flight": "no_fly",
        }
    if key == "rabbit":
        return {
            "characteristic_size": "large",
            "characteristic_teeth_type": "flat",
            "characteristic_claws_type": "sharp",
            "characteristic_speed": 2,
            "characteristic_flight": "no_fly",
        }
    if key == "pheasant":
        return {
            "characteristic_size": "small",
            "characteristic_color": "brown",
            "characteristic_claws_type": "sharp",
            "characteristic_speed": 3,
            "characteristic_sound": "cluck",
            "characteristic_flight": "fly",
            "characteristic_flight_height": 2,
        }
    if key == "dove":
        return {
            "characteristic_size": "small",
            "characteristic_color": "gray",
            "characteristic_claws_type": "sharp",
            "characteristic_speed": 2,
            "characteristic_sound": "coo",
            "characteristic_flight": "fly",
            "characteristic_flight_height": 2,
        }

    # 植物（地表 / 地下 / 树上）
    if key == "strawberry":
        return {
            "characteristic_color": "bright_red",
            "characteristic_shape": "round",
            "characteristic_hardness": "soft",
            "characteristic_smell": "sweet",
            "characteristic_position": "ground",
        }
    if key == "toxicstrawberry":
        return {
            "characteristic_color": "dark_red",
            "characteristic_shape": "round",
            "characteristic_hardness": "soft",
            "characteristic_smell": "bitter",
            "characteristic_position": "ground",
        }
    if key == "mushroom":
        return {
            "characteristic_color": "brown",
            "characteristic_shape": "umbrella",
            "characteristic_hardness": "soft",
            "characteristic_smell": "earthy",
            "characteristic_position": "ground",
        }
    if key == "toxicmushroom":
        return {
            "characteristic_color": "red_brown",
            "characteristic_shape": "umbrella",
            "characteristic_hardness": "soft",
            "characteristic_smell": "musty",
            "characteristic_position": "ground",
        }
    if key == "potato":
        return {
            "characteristic_color": "brown",
            "characteristic_shape": "oval",
            "characteristic_hardness": "hard",
            "characteristic_smell": "earthy",
            "characteristic_position": "underground",
            "characteristic_size": "medium",
            "characteristic_underground_depth": 2,
        }
    if key == "sweetpotato":
        return {
            "characteristic_color": "red",
            "characteristic_shape": "long_oval",
            "characteristic_hardness": "softer",
            "characteristic_smell": "sweet",
            "characteristic_position": "underground",
            "characteristic_size": "large",
            "characteristic_underground_depth": 2,
        }
    if key == "acorn":
        return {
            "characteristic_color": "brown",
            "characteristic_shape": "oval",
            "characteristic_hardness": "hard",
            "characteristic_smell": "woody",
            "characteristic_position": "tree",
            "characteristic_size": "small",
            "characteristic_tree_height": 3,
            "characteristic_shell": "none",
        }
    if key == "chestnut":
        return {
            "characteristic_color": "deep_brown",
            "characteristic_shape": "circle",
            "characteristic_hardness": "hard",
            "characteristic_smell": "nutty",
            "characteristic_position": "tree",
            "characteristic_size": "medium",
            "characteristic_tree_height": 4,
            "characteristic_shell": "spiky",
        }

    return {}


