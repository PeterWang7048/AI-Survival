#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能规律内容增强器
解决规律中unknown、none、True等模糊值问题
提供清晰、具体、有意义的规律描述

问题解决：
1. [unknown] -> 具体的对象/环境/特征名称
2. none -> 具体的工具名称或"徒手"
3. True -> 具体的结果描述
4. 增强规律的可读性和实用性

作者：AI生存游戏项目组
版本：1.0.0
"""

import re
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """内容类型枚举"""
    ENVIRONMENT = "environment"
    OBJECT = "object"
    CHARACTERISTIC = "characteristic"
    ACTION = "action"
    TOOL = "tool"
    RESULT = "result"


@dataclass
class EnhancedContent:
    """增强内容"""
    original: str
    enhanced: str
    content_type: ContentType
    confidence: float
    enhancement_method: str


class ContentEnhancer:
    """内容增强器 - 将模糊值转换为具体描述"""
    
    def __init__(self):
        self.enhancement_rules = self._initialize_enhancement_rules()
        self.context_patterns = self._initialize_context_patterns()
        self.enhancement_stats = {
            'total_enhancements': 0,
            'unknown_fixed': 0,
            'none_fixed': 0,
            'boolean_fixed': 0,
            'generic_enhanced': 0
        }
    
    def _initialize_enhancement_rules(self) -> Dict[str, Dict[str, str]]:
        """初始化增强规则库"""
        return {
            # 环境增强
            'environment': {
                'unknown': '未知环境',
                'open_field': '开阔地',
                'forest': '森林',
                'mountain': '山地',
                'river': '河流',
                'cave': '洞穴',
                'desert': '沙漠',
                'grassland': '草原',
                'swamp': '沼泽'
            },
            
            # 对象增强
            'object': {
                'unknown': '未知目标',
                'berry': '浆果',
                'animal': '动物',
                'tree': '树木',
                'stone': '石头',
                'water': '水源',
                'food': '食物',
                'plant': '植物',
                'fruit': '果实',
                'herb': '草药',
                'meat': '肉类',
                'fish': '鱼类',
                'bird': '鸟类',
                'rabbit': '兔子',
                'deer': '鹿',
                'wolf': '狼',
                'bear': '熊'
            },
            
            # 特征增强
            'characteristic': {
                'unknown': '常规特征',
                'red_color': '红色',
                'big_size': '大型',
                'small_size': '小型',
                'dangerous': '危险',
                'safe': '安全',
                'edible': '可食用',
                'poisonous': '有毒',
                'ripe': '成熟',
                'fresh': '新鲜',
                'dry': '干燥',
                'wet': '湿润',
                'hard': '坚硬',
                'soft': '柔软'
            },
            
            # 动作增强
            'action': {
                'unknown': '未知动作',
                'collect': '采集',
                'hunt': '狩猎',
                'explore': '探索',
                'move': '移动',
                'eat': '进食',
                'drink': '饮水',
                'rest': '休息',
                'attack': '攻击',
                'defend': '防御',
                'build': '建造',
                'craft': '制作',
                'search': '搜索',
                'climb': '攀爬',
                'swim': '游泳',
                'run': '奔跑',
                'walk': '行走'
            },
            
            # 工具增强
            'tool': {
                'none': '徒手',
                'no_tool': '徒手',
                '无': '徒手',
                'stone_tool': '石制工具',
                'wooden_stick': '木棍',
                'sharp_stone': '尖石',
                'rope': '绳索',
                'container': '容器',
                'spear': '长矛',
                'knife': '刀具',
                'bow': '弓箭',
                'trap': '陷阱',
                'fire': '火焰',
                'net': '网具',
                'hook': '钩子'
            },
            
            # 结果增强
            'result': {
                'True': '成功',
                'False': '失败',
                'true': '成功',
                'false': '失败',
                'success': '成功',
                'failure': '失败',
                'unknown': '未知结果',
                'food_obtained': '获得食物',
                'water_obtained': '获得水源',
                'tool_obtained': '获得工具',
                'injured': '受伤',
                'safe': '安全',
                'lost': '迷失',
                'tired': '疲劳',
                'energized': '精力充沛'
            }
        }
    
    def _initialize_context_patterns(self) -> Dict[str, List[str]]:
        """初始化上下文模式，用于智能推断"""
        return {
            'collection_context': [
                '采集', 'collect', '收集', '获取', '拾取'
            ],
            'hunting_context': [
                '狩猎', 'hunt', '捕获', '攻击', '追踪'
            ],
            'exploration_context': [
                '探索', 'explore', '搜索', 'search', '发现'
            ],
            'survival_context': [
                '生存', 'survival', '求生', '维持', '保持'
            ],
            'crafting_context': [
                '制作', 'craft', '建造', 'build', '创造'
            ]
        }
    
    def enhance_content(self, content: str, content_type: ContentType, 
                       context: Dict[str, Any] = None) -> EnhancedContent:
        """增强单个内容"""
        if context is None:
            context = {}
        
        # 获取原始内容
        original = str(content).strip()
        
        # 如果已经是具体内容，直接返回
        if self._is_already_specific(original, content_type):
            return EnhancedContent(
                original=original,
                enhanced=original,
                content_type=content_type,
                confidence=1.0,
                enhancement_method='no_enhancement_needed'
            )
        
        # 进行增强
        enhanced, method, confidence = self._perform_enhancement(
            original, content_type, context
        )
        
        # 更新统计
        self._update_stats(original, enhanced, method)
        
        return EnhancedContent(
            original=original,
            enhanced=enhanced,
            content_type=content_type,
            confidence=confidence,
            enhancement_method=method
        )
    
    def _is_already_specific(self, content: str, content_type: ContentType) -> bool:
        """判断内容是否已经足够具体"""
        generic_terms = ['unknown', 'none', 'True', 'False', 'true', 'false', 'no_tool', '无', '未知', '未知资源']
        
        # 如果是通用术语，需要增强
        if content.lower() in [term.lower() for term in generic_terms]:
            return False
        
        # 如果是单个字符或过短，需要增强
        if len(content) <= 2:
            return False
        
        # 如果包含"未知"等词汇，需要增强
        vague_patterns = ['未知', '不明', '不详', '模糊']
        if any(pattern in content for pattern in vague_patterns):
            return False
        
        return True
    
    def _perform_enhancement(self, content: str, content_type: ContentType, 
                           context: Dict[str, Any]) -> tuple[str, str, float]:
        """执行具体的增强操作"""
        type_key = content_type.value
        
        # 方法1: 直接规则匹配
        if type_key in self.enhancement_rules:
            rule_dict = self.enhancement_rules[type_key]
            if content in rule_dict:
                return rule_dict[content], 'direct_rule_match', 0.95
        
        # 方法2: 上下文智能推断
        enhanced, confidence = self._context_based_enhancement(
            content, content_type, context
        )
        if enhanced != content:
            return enhanced, 'context_inference', confidence
        
        # 方法3: 模式化增强
        enhanced = self._pattern_based_enhancement(content, content_type)
        if enhanced != content:
            return enhanced, 'pattern_enhancement', 0.7
        
        # 方法4: 默认增强
        return self._default_enhancement(content, content_type), 'default_enhancement', 0.5
    
    def _context_based_enhancement(self, content: str, content_type: ContentType, 
                                 context: Dict[str, Any]) -> tuple[str, float]:
        """基于上下文的智能增强"""
        
        # 获取上下文信息
        action = str(context.get('action', '') or '')
        environment = str(context.get('environment', '') or '')
        object_name = str(context.get('object', '') or '')
        tool_name = str(context.get('tool', '') or '')
        result_desc = str(context.get('result', '') or '')
        
        # 根据动作上下文推断
        if content_type == ContentType.OBJECT and str(content).strip().lower() in {'unknown', 'unknown_object', 'unknown_resource', '未知', '未知目标', '未知资源'}:
            # 1) 动作上下文优先
            if '采集' in action or 'collect' in action:
                if '开阔地' in environment:
                    return '野生浆果', 0.85
                elif '森林' in environment:
                    return '森林果实', 0.85
                else:
                    return '可采集植物', 0.75
            if '狩猎' in action or 'hunt' in action or 'attack' in action:
                return '猎物', 0.8
            if '探索' in action or 'explore' in action:
                return '未知区域', 0.75

            # 2) 无动作时，使用工具与结果推断
            if tool_name:
                tool_lower = tool_name.lower()
                if any(k in tool_lower for k in ['bow', '弓', '箭', 'ranged', 'trap']):
                    return '猎物', 0.75
                if any(k in tool_lower for k in ['shovel', 'dig', '铁锹', '篮', 'basket', 'container', 'knife', '采集']):
                    if '开阔地' in environment:
                        return '野生浆果', 0.8
                    elif '森林' in environment:
                        return '森林果实', 0.8
                    return '可采集植物', 0.7

            if result_desc:
                if '食物' in result_desc or 'food' in result_desc:
                    # 再根据工具偏好二分
                    if any(k in tool_name.lower() for k in ['bow', '弓', '箭', 'trap']):
                        return '猎物', 0.7
                    return '可食用资源', 0.65
        
        # 根据环境上下文推断工具
        if content_type == ContentType.TOOL and content in ['none', 'no_tool']:
            if '采集' in action:
                return '采集工具', 0.7
            elif '狩猎' in action:
                return '狩猎工具', 0.7
            elif '探索' in action:
                return '徒手', 0.9  # 探索通常不需要工具
        
        # 根据动作推断结果
        if content_type == ContentType.RESULT and content in ['True', 'true']:
            if '采集' in action:
                return '成功采集', 0.8
            elif '探索' in action:
                return '探索成功', 0.8
            elif '移动' in action:
                return '移动顺利', 0.8
        
        return content, 0.0
    
    def _pattern_based_enhancement(self, content: str, content_type: ContentType) -> str:
        """基于模式的增强"""
        
        # 处理布尔值
        if content_type == ContentType.RESULT:
            if content.lower() in ['true', '1', 'yes']:
                return '成功'
            elif content.lower() in ['false', '0', 'no']:
                return '失败'
        
        # 处理None值
        if content.lower() in ['none', 'null', '', '无']:
            if content_type == ContentType.TOOL:
                return '徒手'
            elif content_type == ContentType.OBJECT:
                return '目标物体'
            elif content_type == ContentType.ENVIRONMENT:
                return '当前环境'
        
        # 处理unknown
        if content.lower() in ['unknown', '未知', '未知资源', 'unknown_resource', 'unknown_object']:
            type_defaults = {
                ContentType.ENVIRONMENT: '未知环境',
                ContentType.OBJECT: '未知目标', 
                ContentType.CHARACTERISTIC: '常规特征',
                ContentType.ACTION: '未知动作',
                ContentType.TOOL: '徒手',
                ContentType.RESULT: '未知结果'
            }
            return type_defaults.get(content_type, content)
        
        return content
    
    def _default_enhancement(self, content: str, content_type: ContentType) -> str:
        """默认增强方案"""
        
        # 为每种类型提供默认的友好描述
        defaults = {
            ContentType.ENVIRONMENT: f'{content}环境',
            ContentType.OBJECT: f'{content}目标',
            ContentType.CHARACTERISTIC: f'{content}特征',
            ContentType.ACTION: f'{content}行为',
            ContentType.TOOL: f'{content}工具',
            ContentType.RESULT: f'{content}结果'
        }
        
        return defaults.get(content_type, content)
    
    def _update_stats(self, original: str, enhanced: str, method: str):
        """更新增强统计"""
        if enhanced != original:
            self.enhancement_stats['total_enhancements'] += 1
            
            if 'unknown' in original.lower():
                self.enhancement_stats['unknown_fixed'] += 1
            elif 'none' in original.lower():
                self.enhancement_stats['none_fixed'] += 1
            elif original.lower() in ['true', 'false']:
                self.enhancement_stats['boolean_fixed'] += 1
            else:
                self.enhancement_stats['generic_enhanced'] += 1


class IntelligentRuleFormatter:
    """智能规律格式化器"""
    
    def __init__(self):
        self.content_enhancer = ContentEnhancer()
        self.formatting_stats = {
            'rules_formatted': 0,
            'elements_enhanced': 0,
            'clarity_improvements': 0
        }
    
    def format_rule(self, rule_data: Dict[str, Any]) -> str:
        """智能格式化规律"""
        try:
            # 提取规律元素
            conditions = rule_data.get('conditions', {})
            expected_result = rule_data.get('expected_result', 'unknown')
            pattern_name = rule_data.get('pattern_name', 'unknown_pattern')
            
            # 解析模式名称
            elements = self._parse_pattern_elements(pattern_name)
            
            # 构建上下文
            context = {
                'action': conditions.get('A', ''),
                'environment': conditions.get('E', ''),
                'object': conditions.get('O', ''),
                'tool': conditions.get('T', ''),
                'result': expected_result
            }
            
            # 增强各个元素
            enhanced_elements = {}
            for key, value in conditions.items():
                content_type = self._map_key_to_content_type(key)
                enhanced = self.content_enhancer.enhance_content(
                    value, content_type, context
                )
                enhanced_elements[key] = enhanced.enhanced
            
            # 增强结果
            result_enhanced = self.content_enhancer.enhance_content(
                expected_result, ContentType.RESULT, context
            )
            
            # 构建格式化字符串
            formatted_rule = self._build_formatted_string(
                enhanced_elements, result_enhanced.enhanced, elements
            )
            
            # 更新统计
            self.formatting_stats['rules_formatted'] += 1
            self.formatting_stats['elements_enhanced'] += len(enhanced_elements)
            
            return formatted_rule
            
        except Exception as e:
            return f"规律格式化失败: {str(e)}"
    
    def _parse_pattern_elements(self, pattern_name: str) -> List[str]:
        """解析模式元素"""
        # 去掉'-R'后缀，分割元素
        if pattern_name.endswith('-R'):
            pattern_name = pattern_name[:-2]
        
        return pattern_name.split('-')
    
    def _map_key_to_content_type(self, key: str) -> ContentType:
        """映射键到内容类型"""
        mapping = {
            'E': ContentType.ENVIRONMENT,
            'O': ContentType.OBJECT,
            'C': ContentType.CHARACTERISTIC,
            'A': ContentType.ACTION,
            'T': ContentType.TOOL,
            'R': ContentType.RESULT
        }
        return mapping.get(key, ContentType.OBJECT)
    
    def _build_formatted_string(self, elements: Dict[str, str], 
                              result: str, pattern_elements: List[str]) -> str:
        """构建格式化字符串"""
        
        # 根据模式元素构建描述
        parts = []
        
        # 处理环境
        if 'E' in elements:
            parts.append(f"在{elements['E']}中")
        
        # 处理对象和特征
        object_part = ""
        if 'O' in elements:
            object_part = elements['O']
            if 'C' in elements:
                object_part = f"{elements['C']}的{object_part}"
        
        # 处理动作和工具
        action_part = ""
        if 'A' in elements:
            action_part = elements['A']
            if 'T' in elements:
                tool_name = elements['T']
                if tool_name == '徒手':
                    action_part = f"{tool_name}{action_part}"
                else:
                    action_part = f"使用{tool_name}进行{action_part}"
        elif 'T' in elements:
            action_part = f"使用{elements['T']}"
        
        # 组合描述
        if object_part and action_part:
            description = f"对{object_part}{action_part}"
        elif action_part:
            description = action_part
        elif object_part:
            description = f"面对{object_part}"
        else:
            description = "执行动作"
        
        # 添加位置信息
        if parts:
            full_description = f"{parts[0]}，{description}"
        else:
            full_description = description
        
        # 添加结果
        return f"{full_description}，预期结果：{result}"
    
    def get_enhancement_stats(self) -> Dict[str, Any]:
        """获取增强统计信息"""
        return {
            'formatting_stats': self.formatting_stats.copy(),
            'content_enhancement_stats': self.content_enhancer.enhancement_stats.copy()
        }


def main():
    """测试函数"""
    formatter = IntelligentRuleFormatter()
    
    # 测试规律数据
    test_rule = {
        'pattern_name': 'E-A-R',
        'conditions': {
            'E': 'open_field',
            'A': 'explore'
        },
        'expected_result': 'True'
    }
    
    print("🧪 测试智能规律格式化器")
    print("=" * 40)
    
    # 格式化前
    print("原始规律:")
    print(f"  模式: {test_rule['pattern_name']}")
    print(f"  条件: {test_rule['conditions']}")
    print(f"  结果: {test_rule['expected_result']}")
    
    # 格式化后
    formatted = formatter.format_rule(test_rule)
    print(f"\n增强后规律:")
    print(f"  {formatted}")
    
    # 统计信息
    stats = formatter.get_enhancement_stats()
    print(f"\n📊 增强统计:")
    for key, value in stats['content_enhancement_stats'].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
