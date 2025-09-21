# 动植物和工具系统扩展模块
# 用于补全现有的动植物种类，新增工具系统
# 支持双规律协作：识别规律 + 工具效用规律

import random
from typing import Dict, List, Optional, Tuple

# ==================== 新增动物类 ====================

class Pheasant:
    """野鸡 - 鸟类，需要弓箭捕获"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "Pheasant"
        self.hp = 15
        self.attack = 0
        self.food = 15
        self.alive = True
        self.chase_steps = 0
        self.chase_target = None
        self.vision_range = 6
        self.flight_height = random.randint(1, 3)  # 飞行高度，影响捕获难度
        self.visible_info = {
            "体型": "小",
            "羽毛": "彩色",
            "爪子": "细爪",
            "速度": 3,
            "颜色": "棕",
            "叫声": "咯咯",
            "飞行": "会飞"
        }
    
    def move(self, game_map, players=None):
        """野鸡的移动逻辑 - 受惊时会飞行逃离"""
        if not self.alive:
            return
            
        # 检查周围是否有玩家，如果有则飞行逃离
        if players:
            for player in players:
                if player.is_alive():
                    distance = abs(self.x - player.x) + abs(self.y - player.y)
                    if distance <= 3:  # 警觉距离
                        # 飞行逃离
                        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]  # 飞行距离更远
                        dx, dy = random.choice(directions)
                        new_x = self.x + dx
                        new_y = self.y + dy
                        if game_map.is_within_bounds(new_x, new_y):
                            self.x = new_x
                            self.y = new_y
                        return
        
        # 正常随机移动
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        dx, dy = random.choice(directions)
        new_x = self.x + dx
        new_y = self.y + dy
        if game_map.is_within_bounds(new_x, new_y):
            self.x = new_x
            self.y = new_y


class Dove:
    """斑鸠 - 鸟类，需要弓箭捕获"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "Dove"
        self.hp = 12
        self.attack = 0
        self.food = 12
        self.alive = True
        self.chase_steps = 0
        self.chase_target = None
        self.vision_range = 5
        self.flight_height = random.randint(1, 2)  # 比野鸡飞得低一些
        self.visible_info = {
            "体型": "小",
            "羽毛": "灰色",
            "爪子": "细爪",
            "速度": 2,
            "颜色": "灰",
            "叫声": "咕咕",
            "飞行": "会飞"
        }
    
    def move(self, game_map, players=None):
        """斑鸠的移动逻辑 - 比野鸡稍微温顺一些"""
        if not self.alive:
            return
            
        # 检查周围是否有玩家
        if players:
            for player in players:
                if player.is_alive():
                    distance = abs(self.x - player.x) + abs(self.y - player.y)
                    if distance <= 2:  # 警觉距离比野鸡小
                        # 飞行逃离
                        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1)]
                        dx, dy = random.choice(directions)
                        new_x = self.x + dx
                        new_y = self.y + dy
                        if game_map.is_within_bounds(new_x, new_y):
                            self.x = new_x
                            self.y = new_y
                        return
        
        # 正常随机移动
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        dx, dy = random.choice(directions)
        new_x = self.x + dx
        new_y = self.y + dy
        if game_map.is_within_bounds(new_x, new_y):
            self.x = new_x
            self.y = new_y


# ==================== 新增植物类 ====================

class Potato:
    """土豆 - 地下植物，需要铁锹挖掘"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "Potato"
        self.collected = False
        self.alive = True
        self.underground_depth = random.randint(1, 3)  # 埋藏深度，影响挖掘难度
        self.visible_info = {
            "颜色": "棕色",
            "形状": "椭圆形", 
            "硬度": "坚硬",
            "气味": "泥土味",
            "位置": "地下",
            "大小": "中等"
        }
        self.food = 8
        self.toxic = False
    
    def update(self):
        pass


class SweetPotato:
    """红薯 - 地下植物，需要铁锹挖掘"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "SweetPotato"
        self.collected = False
        self.alive = True
        self.underground_depth = random.randint(1, 2)  # 比土豆稍浅
        self.visible_info = {
            "颜色": "红色",
            "形状": "长椭圆",
            "硬度": "较软",
            "气味": "甜味",
            "位置": "地下", 
            "大小": "大"
        }
        self.food = 10
        self.toxic = False
    
    def update(self):
        pass


class Acorn:
    """橡果 - 树上植物，需要棍子敲打"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "Acorn"
        self.collected = False
        self.alive = True
        self.tree_height = random.randint(2, 4)  # 树的高度，影响敲打难度
        self.visible_info = {
            "颜色": "棕色",
            "形状": "椭圆形",
            "硬度": "坚硬",
            "气味": "木质味",
            "位置": "树上",
            "大小": "小"
        }
        self.food = 6
        self.toxic = False
    
    def update(self):
        pass


class Chestnut:
    """栗子 - 树上植物，需要棍子敲打"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "Chestnut"
        self.collected = False
        self.alive = True
        self.tree_height = random.randint(3, 5)  # 比橡果高一些
        self.has_spikes = True  # 有刺，增加收集难度
        self.visible_info = {
            "颜色": "深棕色",
            "形状": "圆形",
            "硬度": "坚硬",
            "气味": "坚果味",
            "位置": "树上",
            "大小": "中等",
            "外壳": "有刺"
        }
        self.food = 8
        self.toxic = False
    
    def update(self):
        pass


# ==================== 工具系统 ====================

class Tool:
    """工具基类"""
    def __init__(self, name: str, tool_type: str, durability: int = 100):
        self.name = name
        self.tool_type = tool_type
        self.durability = durability
        self.max_durability = durability
        self.effective_targets = []  # 有效目标列表
        self.usage_count = 0
        
    def use(self, target) -> Tuple[bool, str]:
        """使用工具，返回(是否成功, 结果描述)"""
        if self.durability <= 0:
            return False, f"{self.name}已经损坏，无法使用"
            
        # 检查目标兼容性
        target_type = target.type if hasattr(target, 'type') else str(type(target).__name__)
        is_effective = target_type in self.effective_targets
        
        # 消耗耐久度
        durability_cost = 1 if is_effective else 2  # 无效使用消耗更多耐久度
        self.durability = max(0, self.durability - durability_cost)
        self.usage_count += 1
        
        if is_effective:
            return True, f"成功使用{self.name}对{target_type}，效果良好"
        else:
            return False, f"使用{self.name}对{target_type}效果不佳"
    
    def repair(self, amount: int = 10):
        """修理工具"""
        self.durability = min(self.max_durability, self.durability + amount)
    
    def get_condition(self) -> str:
        """获取工具状态描述"""
        ratio = self.durability / self.max_durability
        if ratio > 0.8:
            return "完好"
        elif ratio > 0.5:
            return "轻微磨损"
        elif ratio > 0.2:
            return "严重磨损"
        else:
            return "即将损坏"


class Spear(Tool):
    """长矛 - 对付猛兽类（老虎、黑熊）"""
    def __init__(self):
        super().__init__("长矛", "weapon", 80)
        self.effective_targets = ["Tiger", "BlackBear"]
        self.attack_power = 60  # 攻击力
        self.range = 2  # 攻击范围
        self.visible_info = {
            "材质": "木杆铁头",
            "长度": "长",
            "重量": "中等",
            "锋利度": "尖锐",
            "用途": "刺击"
        }


class Stone(Tool):
    """石头 - 对付猎物类（兔子、野猪）"""
    def __init__(self):
        super().__init__("石头", "projectile", 50)
        self.effective_targets = ["Rabbit", "Boar"]
        self.attack_power = 25
        self.range = 4  # 投掷范围
        self.visible_info = {
            "材质": "岩石",
            "大小": "手掌大小",
            "重量": "重",
            "形状": "不规则",
            "用途": "投掷"
        }


class Bow(Tool):
    """弓箭 - 对付鸟类（野鸡、斑鸠）"""
    def __init__(self):
        super().__init__("弓箭", "ranged_weapon", 60)
        self.effective_targets = ["Pheasant", "Dove"]
        self.attack_power = 30
        self.range = 6  # 射程
        self.accuracy = 0.7  # 命中率
        self.visible_info = {
            "材质": "木弓竹箭",
            "长度": "中等",
            "重量": "轻",
            "精度": "高",
            "用途": "远程射击"
        }


class Basket(Tool):
    """篮子 - 收集地面植物（草莓、蘑菇）"""
    def __init__(self):
        super().__init__("篮子", "container", 100)
        self.effective_targets = ["Strawberry", "Mushroom", "ToxicStrawberry", "ToxicMushroom"]
        self.capacity = 20  # 容量
        self.current_load = 0
        self.visible_info = {
            "材质": "藤条编织",
            "大小": "中等",
            "重量": "轻",
            "容量": "较大",
            "用途": "收集"
        }
    
    def use(self, target) -> Tuple[bool, str]:
        """篮子的特殊使用逻辑"""
        if self.current_load >= self.capacity:
            return False, f"{self.name}已满，无法收集更多"
        
        success, message = super().use(target)
        if success:
            self.current_load += 1
            return True, f"成功收集{target.type}到{self.name}中"
        return success, message


class Shovel(Tool):
    """铁锹 - 挖掘地下植物（土豆、红薯）"""
    def __init__(self):
        super().__init__("铁锹", "digging_tool", 70)
        self.effective_targets = ["Potato", "SweetPotato"]
        self.digging_power = 3  # 挖掘力度
        self.visible_info = {
            "材质": "铁头木柄",
            "长度": "中等",
            "重量": "重",
            "锋利度": "锐利",
            "用途": "挖掘"
        }


class Stick(Tool):
    """棍子 - 敲打树上植物（橡果、栗子）"""
    def __init__(self):
        super().__init__("棍子", "striking_tool", 90)
        self.effective_targets = ["Acorn", "Chestnut"]
        self.striking_power = 2  # 敲打力度
        self.length = 1.5  # 长度，影响敲打范围
        self.visible_info = {
            "材质": "硬木",
            "长度": "长",
            "重量": "轻",
            "硬度": "坚硬",
            "用途": "敲打"
        }


# ==================== 工具效用规律数据库 ====================

class ToolEffectivenessDatabase:
    """工具效用数据库 - 存储工具与目标的有效性关系"""
    
    def __init__(self):
        # 工具-目标有效性映射（隐藏在系统中，玩家需要通过尝试来发现）
        self.effectiveness_map = {
            # 工具类型 : {目标类型: 效用分数}
            "长矛": {
                "Tiger": 0.9,      # 长矛对老虎很有效
                "BlackBear": 0.85, # 长矛对黑熊很有效
                "Rabbit": 0.3,     # 长矛对兔子效果一般（太笨重）
                "Boar": 0.6,       # 长矛对野猪中等效果
                "Pheasant": 0.1,   # 长矛对野鸡几乎无效
                "Dove": 0.1,       # 长矛对斑鸠几乎无效
            },
            "石头": {
                "Rabbit": 0.8,     # 石头对兔子很有效
                "Boar": 0.75,      # 石头对野猪很有效
                "Tiger": 0.2,      # 石头对老虎效果差
                "BlackBear": 0.15, # 石头对黑熊效果差
                "Pheasant": 0.4,   # 石头对野鸡中等效果
                "Dove": 0.35,      # 石头对斑鸠中等效果
            },
            "弓箭": {
                "Pheasant": 0.9,   # 弓箭对野鸡很有效
                "Dove": 0.85,      # 弓箭对斑鸠很有效
                "Rabbit": 0.5,     # 弓箭对兔子中等效果
                "Boar": 0.3,       # 弓箭对野猪效果一般
                "Tiger": 0.1,      # 弓箭对老虎几乎无效
                "BlackBear": 0.1,  # 弓箭对黑熊几乎无效
            },
            "篮子": {
                "Strawberry": 0.95,     # 篮子对草莓非常有效
                "Mushroom": 0.9,        # 篮子对蘑菇很有效
                "ToxicStrawberry": 0.95, # 篮子对毒草莓非常有效
                "ToxicMushroom": 0.9,    # 篮子对毒蘑菇很有效
                "Potato": 0.2,          # 篮子对土豆效果差（需要挖掘）
                "SweetPotato": 0.2,     # 篮子对红薯效果差
                "Acorn": 0.3,           # 篮子对橡果效果一般
                "Chestnut": 0.3,        # 篮子对栗子效果一般
            },
            "铁锹": {
                "Potato": 0.9,          # 铁锹对土豆很有效
                "SweetPotato": 0.85,    # 铁锹对红薯很有效
                "Strawberry": 0.2,      # 铁锹对草莓效果差（会损坏）
                "Mushroom": 0.2,        # 铁锹对蘑菇效果差
                "Acorn": 0.1,           # 铁锹对橡果几乎无效
                "Chestnut": 0.1,        # 铁锹对栗子几乎无效
            },
            "棍子": {
                "Acorn": 0.85,      # 棍子对橡果很有效
                "Chestnut": 0.9,    # 棍子对栗子很有效
                "Strawberry": 0.1,  # 棍子对草莓几乎无效
                "Mushroom": 0.1,    # 棍子对蘑菇几乎无效
                "Potato": 0.3,      # 棍子对土豆效果一般（可以松土）
                "SweetPotato": 0.3, # 棍子对红薯效果一般
                "Rabbit": 0.4,      # 棍子对兔子中等效果
                "Boar": 0.2,        # 棍子对野猪效果差
            }
        }
    
    def get_effectiveness(self, tool_type: str, target_type: str) -> float:
        """获取工具对目标的有效性分数"""
        return self.effectiveness_map.get(tool_type, {}).get(target_type, 0.1)
    
    def is_highly_effective(self, tool_type: str, target_type: str) -> bool:
        """判断工具对目标是否高效（>0.7）"""
        return self.get_effectiveness(tool_type, target_type) > 0.7
    
    def get_best_tool_for_target(self, target_type: str) -> str:
        """为特定目标找到最佳工具"""
        best_tool = None
        best_score = 0
        
        for tool_type, targets in self.effectiveness_map.items():
            score = targets.get(target_type, 0)
            if score > best_score:
                best_score = score
                best_tool = tool_type
        
        return best_tool
    
    def get_tool_target_pairs(self, min_effectiveness: float = 0.7) -> List[Tuple[str, str, float]]:
        """获取所有高效的工具-目标配对"""
        pairs = []
        for tool_type, targets in self.effectiveness_map.items():
            for target_type, effectiveness in targets.items():
                if effectiveness >= min_effectiveness:
                    pairs.append((tool_type, target_type, effectiveness))
        return pairs


# ==================== 工具管理系统 ====================

class ToolManager:
    """工具管理系统 - 处理工具的创建、使用、损坏等"""
    
    def __init__(self):
        self.effectiveness_db = ToolEffectivenessDatabase()
        self.available_tools = {
            "长矛": Spear,
            "石头": Stone, 
            "弓箭": Bow,
            "篮子": Basket,
            "铁锹": Shovel,
            "棍子": Stick
        }
    
    def create_tool(self, tool_type: str) -> Optional[Tool]:
        """创建指定类型的工具"""
        if tool_type in self.available_tools:
            return self.available_tools[tool_type]()
        return None
    
    def evaluate_tool_use(self, tool: Tool, target) -> dict:
        """评估工具使用结果"""
        target_type = target.type if hasattr(target, 'type') else str(type(target).__name__)
        effectiveness = self.effectiveness_db.get_effectiveness(tool.name, target_type)
        
        success, message = tool.use(target)
        
        return {
            "success": success,
            "message": message,
            "effectiveness": effectiveness,
            "tool_condition": tool.get_condition(),
            "durability_remaining": tool.durability,
            "is_optimal_choice": effectiveness > 0.7
        }
    
    def suggest_tool_for_target(self, target_type: str) -> str:
        """为目标建议最佳工具（仅用于测试，游戏中不提供）"""
        return self.effectiveness_db.get_best_tool_for_target(target_type)
    
    def get_learning_data(self) -> dict:
        """获取供AI学习的工具效用数据"""
        return {
            "tool_types": list(self.available_tools.keys()),
            "high_effectiveness_pairs": self.effectiveness_db.get_tool_target_pairs(0.7),
            "total_combinations": sum(len(targets) for targets in self.effectiveness_db.effectiveness_map.values())
        }


# ==================== EOCATR经验生成工具 ====================

def generate_tool_usage_eocar_examples():
    """生成工具使用的EOCATR经验示例，供BPM学习"""
    examples = [
        # 成功案例
        {
            "E": {"terrain": "forest", "target_present": "Tiger", "distance": 2},
            "O": {"player_hp": 80, "has_tool": "长矛", "tool_durability": 70},
            "C": {"courage": 7, "strength": 6, "tool_skill": 5},
            "A": "use_spear_on_tiger",
            "R": {"success": True, "tiger_defeated": True, "food_gained": 50, "tool_durability": 65}
        },
        {
            "E": {"terrain": "grassland", "target_present": "Strawberry", "quantity": 5},
            "O": {"player_hp": 90, "has_tool": "篮子", "basket_capacity": 15},
            "C": {"gathering_skill": 8, "patience": 6},
            "A": "use_basket_on_strawberry",
            "R": {"success": True, "strawberry_collected": 5, "food_gained": 25, "basket_filled": 5}
        },
        
        # 失败案例
        {
            "E": {"terrain": "forest", "target_present": "Tiger", "distance": 2},
            "O": {"player_hp": 80, "has_tool": "篮子", "tool_durability": 90},
            "C": {"courage": 7, "strength": 6, "tool_skill": 3},
            "A": "use_basket_on_tiger",
            "R": {"success": False, "damage_taken": 30, "tool_damaged": True, "tool_durability": 70}
        },
        {
            "E": {"terrain": "forest", "target_present": "Potato", "depth": 2},
            "O": {"player_hp": 90, "has_tool": "棍子", "tool_durability": 80},
            "C": {"digging_skill": 3, "strength": 5},
            "A": "use_stick_on_potato",
            "R": {"success": False, "potato_collected": 0, "tool_durability": 75, "effort_wasted": True}
        }
    ]
    
    return examples


if __name__ == "__main__":
    # 测试代码
    tool_manager = ToolManager()
    
    # 测试工具创建
    spear = tool_manager.create_tool("长矛")
    basket = tool_manager.create_tool("篮子")
    
    print("工具系统测试:")
    print(f"长矛: {spear.name}, 耐久度: {spear.durability}")
    print(f"篮子: {basket.name}, 容量: {basket.capacity}")
    
    # 测试有效性数据库
    effectiveness_db = ToolEffectivenessDatabase()
    print("\n工具效用测试:")
    print(f"长矛对老虎的效用: {effectiveness_db.get_effectiveness('长矛', 'Tiger')}")
    print(f"篮子对草莓的效用: {effectiveness_db.get_effectiveness('篮子', 'Strawberry')}")
    print(f"老虎的最佳工具: {effectiveness_db.get_best_tool_for_target('Tiger')}")
    
    # 生成示例EOCATR经验
    eocar_examples = generate_tool_usage_eocar_examples()
    print(f"\n生成了 {len(eocar_examples)} 个EOCATR经验示例") 