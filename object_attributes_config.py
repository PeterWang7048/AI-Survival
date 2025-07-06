"""
五库系统对象和属性配置文件
基于main3.0.py的完整移植方案
"""

# ========== 环境对象配置 ==========
ENVIRONMENT_TYPES = {
    'plain': {
        'type': '平原', 
        'safety': 0.1, 
        'resources': 'low',
        'description': '开阔的平原地带，资源稀少但视野良好'
    },
    'big_tree': {
        'type': '大树', 
        'safety': 0.3, 
        'resources': 'tree_plants',
        'description': '高大的树木，可能有树上植物，提供一定遮蔽'
    },
    'bush': {
        'type': '灌木', 
        'safety': 0.2, 
        'resources': 'ground_plants',
        'description': '低矮的灌木丛，地面植物丰富'
    },
    'rock': {
        'type': '岩石', 
        'safety': 0.2, 
        'resources': 'none',
        'description': '坚硬的岩石地带，无资源但可作掩护'
    },
    'cave': {
        'type': '洞穴', 
        'safety': 0.8, 
        'resources': 'shelter',
        'description': '天然洞穴，安全的避难所'
    },
    'river': {
        'type': '河流', 
        'safety': 0.3, 
        'resources': 'water',
        'description': '流动的河水，重要的水源'
    },
    'puddle': {
        'type': '水坑', 
        'safety': 0.4, 
        'resources': 'water',
        'description': '小型水坑，临时水源'
    }
}

# ========== 动物对象配置 ==========
ANIMAL_CHARACTERISTICS = {
    'Tiger': {
        # 外观特征
        "体型": "大", "牙齿": "尖牙", "爪子": "利爪", "速度": 2,
        "颜色": "黄", "毛发": "短毛", "叫声": "嗷",
        # 游戏属性
        "hp": 500, "attack": 50, "food": 500, 
        "is_predator": True, "vision_range": 8,
        # 分类
        "category": "predator", "size_class": "large"
    },
    'BlackBear': {
        # 外观特征
        "体型": "大", "牙齿": "尖牙", "爪子": "利爪", "速度": 2,
        "颜色": "黑", "毛发": "长毛", "叫声": "哼",
        # 游戏属性
        "hp": 300, "attack": 30, "food": 300, 
        "is_predator": True, "vision_range": 6,
        # 分类
        "category": "predator", "size_class": "large"
    },
    'Rabbit': {
        # 外观特征
        "体型": "小", "牙齿": "平牙", "爪子": "利爪", "速度": 2,
        "颜色": "黄", "毛发": "短毛", "叫声": "哼",
        # 游戏属性
        "hp": 10, "attack": 0, "food": 10, 
        "is_predator": False, "vision_range": 3,
        # 分类
        "category": "prey", "size_class": "small"
    },
    'Boar': {
        # 外观特征
        "体型": "中", "牙齿": "尖牙", "爪子": "蹄", "速度": 2,
        "颜色": "棕", "毛发": "短毛", "叫声": "哼",
        # 游戏属性
        "hp": 50, "attack": 10, "food": 50, 
        "is_predator": False, "vision_range": 4,
        # 分类
        "category": "prey", "size_class": "medium"
    },
    'Pheasant': {
        # 外观特征
        "体型": "小", "牙齿": "尖嘴", "爪子": "细爪", "速度": 2,
        "颜色": "彩", "羽毛": "长羽", "叫声": "咯咯",
        # 游戏属性
        "hp": 8, "attack": 0, "food": 8, 
        "is_predator": False, "vision_range": 5,
        # 特殊属性
        "飞行": "会飞",
        # 分类
        "category": "bird", "size_class": "small"
    },
    'Dove': {
        # 外观特征
        "体型": "小", "牙齿": "尖嘴", "爪子": "细爪", "速度": 2,
        "颜色": "白", "羽毛": "短羽", "叫声": "咕咕",
        # 游戏属性
        "hp": 12, "attack": 0, "food": 12, 
        "is_predator": False, "vision_range": 4,
        # 特殊属性
        "飞行": "会飞",
        # 分类
        "category": "bird", "size_class": "small"
    }
}

# ========== 植物对象配置 ==========
PLANT_CHARACTERISTICS = {
    'Strawberry': {
        # 外观特征
        "颜色": "红", "形状": "圆形", "硬度": "柔软", "气味": "香甜",
        "位置": "地面", "大小": "小",
        # 游戏属性
        "food": 5, "toxic": False, "location_type": "ground",
        # 分类
        "category": "ground_plant", "edible": True
    },
    'Mushroom': {
        # 外观特征
        "颜色": "棕", "形状": "伞形", "硬度": "柔软", "气味": "无",
        "位置": "地面", "大小": "小",
        # 游戏属性
        "food": 5, "toxic": False, "location_type": "ground",
        # 分类
        "category": "ground_plant", "edible": True
    },
    'ToxicStrawberry': {
        # 外观特征
        "颜色": "红", "形状": "圆形", "硬度": "柔软", "气味": "异味",
        "位置": "地面", "大小": "小",
        # 游戏属性
        "food": 5, "toxic": True, "location_type": "ground",
        # 分类
        "category": "ground_plant", "edible": False
    },
    'ToxicMushroom': {
        # 外观特征
        "颜色": "紫", "形状": "伞形", "硬度": "柔软", "气味": "刺鼻",
        "位置": "地面", "大小": "小",
        # 游戏属性
        "food": 5, "toxic": True, "location_type": "ground",
        # 分类
        "category": "ground_plant", "edible": False
    },
    'Potato': {
        # 外观特征
        "颜色": "棕", "形状": "椭圆", "硬度": "坚硬", "气味": "土味",
        "位置": "地下", "大小": "中",
        # 游戏属性
        "food": 10, "toxic": False, "location_type": "underground",
        # 分类
        "category": "underground_plant", "edible": True
    },
    'SweetPotato': {
        # 外观特征
        "颜色": "橙", "形状": "长条", "硬度": "坚硬", "气味": "甜味",
        "位置": "地下", "大小": "中",
        # 游戏属性
        "food": 12, "toxic": False, "location_type": "underground",
        # 分类
        "category": "underground_plant", "edible": True
    },
    'Acorn': {
        # 外观特征
        "颜色": "棕", "形状": "椭圆", "硬度": "坚硬", "气味": "坚果味",
        "位置": "树上", "大小": "小",
        # 游戏属性
        "food": 3, "toxic": False, "location_type": "tree",
        # 分类
        "category": "tree_plant", "edible": True
    },
    'Chestnut': {
        # 外观特征
        "颜色": "棕", "形状": "圆形", "硬度": "坚硬", "气味": "坚果味",
        "位置": "树上", "大小": "中",
        # 游戏属性
        "food": 8, "toxic": False, "location_type": "tree",
        # 分类
        "category": "tree_plant", "edible": True
    }
}

# ========== 工具对象配置 ==========
TOOL_CHARACTERISTICS = {
    'Spear': {
        # 物理属性
        "reach": 3, "penetration": 4, "precision": 3, "speed": 2,
        # 外观特征
        "材质": "木头", "长度": "长", "重量": "中",
        # 功能属性
        "type": "weapon", "target_type": "predator",
        # 分类
        "category": "weapon", "effectiveness_class": "high_damage"
    },
    'Stone': {
        # 物理属性
        "reach": 2, "penetration": 2, "precision": 2, "speed": 4,
        # 外观特征
        "材质": "石头", "长度": "短", "重量": "重",
        # 功能属性
        "type": "weapon", "target_type": "prey",
        # 分类
        "category": "weapon", "effectiveness_class": "fast_attack"
    },
    'Bow': {
        # 物理属性
        "reach": 5, "penetration": 3, "precision": 5, "speed": 3,
        # 外观特征
        "材质": "木头", "长度": "中", "重量": "轻",
        # 功能属性
        "type": "weapon", "target_type": "bird",
        # 分类
        "category": "weapon", "effectiveness_class": "long_range"
    },
    'Basket': {
        # 物理属性
        "reach": 1, "penetration": 1, "precision": 1, "speed": 1,
        # 外观特征
        "材质": "藤条", "长度": "短", "重量": "轻",
        # 功能属性
        "type": "tool", "target_type": "ground_plant",
        # 分类
        "category": "collection_tool", "effectiveness_class": "ground_gather"
    },
    'Shovel': {
        # 物理属性
        "reach": 2, "penetration": 4, "precision": 2, "speed": 2,
        # 外观特征
        "材质": "木头", "长度": "中", "重量": "中",
        # 功能属性
        "type": "tool", "target_type": "underground_plant",
        # 分类
        "category": "collection_tool", "effectiveness_class": "dig_tool"
    },
    'Stick': {
        # 物理属性
        "reach": 3, "penetration": 2, "precision": 2, "speed": 3,
        # 外观特征
        "材质": "木头", "长度": "长", "重量": "轻",
        # 功能属性
        "type": "tool", "target_type": "tree_plant",
        # 分类
        "category": "collection_tool", "effectiveness_class": "reach_tool"
    }
}

# ========== 目标类型映射 ==========
TARGET_TYPE_MAPPING = {
    # 动物映射
    'Tiger': 'predator',
    'BlackBear': 'predator', 
    'Rabbit': 'prey',
    'Boar': 'prey',
    'Pheasant': 'bird',
    'Dove': 'bird',
    # 植物映射
    'Strawberry': 'ground_plant',
    'Mushroom': 'ground_plant',
    'ToxicStrawberry': 'ground_plant',
    'ToxicMushroom': 'ground_plant',
    'Potato': 'underground_plant',
    'SweetPotato': 'underground_plant',
    'Acorn': 'tree_plant',
    'Chestnut': 'tree_plant'
}

# ========== 工具有效性计算系统 ==========
def calculate_tool_effectiveness(tool_name, target_name):
    """
    计算工具对目标的有效性
    移植自main3.0.py的工具有效性算法
    """
    if tool_name not in TOOL_CHARACTERISTICS:
        return 0.1
    if target_name not in TARGET_TYPE_MAPPING:
        return 0.1
    
    tool_props = TOOL_CHARACTERISTICS[tool_name]
    target_type = TARGET_TYPE_MAPPING[target_name]
    
    # 基础匹配度
    if tool_props['target_type'] == target_type:
        base_effectiveness = 0.8
    else:
        base_effectiveness = 0.3
    
    # 物理属性加成
    if target_type == 'predator':
        # 对付猛兽需要高穿透力
        effectiveness = base_effectiveness + (tool_props['penetration'] * 0.1)
    elif target_type == 'bird':
        # 对付鸟类需要高精确度
        effectiveness = base_effectiveness + (tool_props['precision'] * 0.1)
    elif target_type == 'underground_plant':
        # 挖掘地下植物需要高穿透力
        effectiveness = base_effectiveness + (tool_props['penetration'] * 0.1)
    elif target_type == 'tree_plant':
        # 采集树上植物需要长触及距离
        effectiveness = base_effectiveness + (tool_props['reach'] * 0.1)
    else:
        # 其他情况看速度
        effectiveness = base_effectiveness + (tool_props['speed'] * 0.05)
    
    return min(1.0, max(0.1, effectiveness))

def get_best_tool_for_target(target_name, available_tools=None):
    """
    为特定目标找到最佳工具
    """
    if available_tools is None:
        available_tools = list(TOOL_CHARACTERISTICS.keys())
    
    best_tool = None
    best_effectiveness = 0.0
    
    for tool_name in available_tools:
        effectiveness = calculate_tool_effectiveness(tool_name, target_name)
        if effectiveness > best_effectiveness:
            best_effectiveness = effectiveness
            best_tool = tool_name
    
    return best_tool, best_effectiveness

def get_tool_target_compatibility_matrix():
    """
    生成工具-目标兼容性矩阵
    用于智能体学习参考
    """
    matrix = {}
    for tool_name in TOOL_CHARACTERISTICS.keys():
        matrix[tool_name] = {}
        for target_name in TARGET_TYPE_MAPPING.keys():
            matrix[tool_name][target_name] = calculate_tool_effectiveness(tool_name, target_name)
    
    return matrix

# ========== 属性查询工具 ==========
def get_object_attributes(object_name):
    """获取对象的所有属性"""
    if object_name in ANIMAL_CHARACTERISTICS:
        return ANIMAL_CHARACTERISTICS[object_name]
    elif object_name in PLANT_CHARACTERISTICS:
        return PLANT_CHARACTERISTICS[object_name]
    elif object_name in TOOL_CHARACTERISTICS:
        return TOOL_CHARACTERISTICS[object_name]
    elif object_name in ENVIRONMENT_TYPES:
        return ENVIRONMENT_TYPES[object_name]
    else:
        return {}

def get_objects_by_category(category):
    """根据类别获取对象列表"""
    objects = []
    
    # 搜索动物
    for name, attrs in ANIMAL_CHARACTERISTICS.items():
        if attrs.get('category') == category:
            objects.append(name)
    
    # 搜索植物
    for name, attrs in PLANT_CHARACTERISTICS.items():
        if attrs.get('category') == category:
            objects.append(name)
    
    # 搜索工具
    for name, attrs in TOOL_CHARACTERISTICS.items():
        if attrs.get('category') == category:
            objects.append(name)
    
    return objects

def get_all_object_names():
    """获取所有对象名称"""
    all_objects = []
    all_objects.extend(ANIMAL_CHARACTERISTICS.keys())
    all_objects.extend(PLANT_CHARACTERISTICS.keys())
    all_objects.extend(TOOL_CHARACTERISTICS.keys())
    all_objects.extend(ENVIRONMENT_TYPES.keys())
    return all_objects

def get_attribute_values(attribute_name):
    """获取某个属性的所有可能值"""
    values = set()
    
    # 搜索所有对象的属性值
    for obj_dict in [ANIMAL_CHARACTERISTICS, PLANT_CHARACTERISTICS, TOOL_CHARACTERISTICS, ENVIRONMENT_TYPES]:
        for obj_attrs in obj_dict.values():
            if attribute_name in obj_attrs:
                values.add(obj_attrs[attribute_name])
    
    return list(values)

# ========== 统计信息 ==========
def get_object_statistics():
    """获取对象统计信息"""
    stats = {
        'total_objects': len(get_all_object_names()),
        'animals': len(ANIMAL_CHARACTERISTICS),
        'plants': len(PLANT_CHARACTERISTICS),
        'tools': len(TOOL_CHARACTERISTICS),
        'environments': len(ENVIRONMENT_TYPES),
        'categories': {
            'predators': len([a for a in ANIMAL_CHARACTERISTICS.values() if a.get('category') == 'predator']),
            'prey': len([a for a in ANIMAL_CHARACTERISTICS.values() if a.get('category') == 'prey']),
            'birds': len([a for a in ANIMAL_CHARACTERISTICS.values() if a.get('category') == 'bird']),
            'ground_plants': len([p for p in PLANT_CHARACTERISTICS.values() if p.get('category') == 'ground_plant']),
            'underground_plants': len([p for p in PLANT_CHARACTERISTICS.values() if p.get('category') == 'underground_plant']),
            'tree_plants': len([p for p in PLANT_CHARACTERISTICS.values() if p.get('category') == 'tree_plant']),
            'weapons': len([t for t in TOOL_CHARACTERISTICS.values() if t.get('category') == 'weapon']),
            'collection_tools': len([t for t in TOOL_CHARACTERISTICS.values() if t.get('category') == 'collection_tool'])
        }
    }
    return stats

if __name__ == "__main__":
    # 测试代码
    print("🎯 五库系统对象和属性配置")
    print("=" * 50)
    
    stats = get_object_statistics()
    print(f"总对象数: {stats['total_objects']}")
    print(f"动物: {stats['animals']}, 植物: {stats['plants']}, 工具: {stats['tools']}, 环境: {stats['environments']}")
    
    print("\n🔧 工具有效性测试:")
    print(f"长矛对老虎: {calculate_tool_effectiveness('Spear', 'Tiger'):.2f}")
    print(f"弓箭对鸽子: {calculate_tool_effectiveness('Bow', 'Dove'):.2f}")
    print(f"铁锹对土豆: {calculate_tool_effectiveness('Shovel', 'Potato'):.2f}")
    print(f"篮子对草莓: {calculate_tool_effectiveness('Basket', 'Strawberry'):.2f}")