#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
emrs_parameter_fix.py
EMRS奖励系统参数错误修复模块

解决AI生存系统中EMRS相关的参数错误问题，包括：
1. 调用参数不匹配修复
2. 方法名称统一
3. 参数验证和自动转换
4. 向后兼容性支持
5. 错误处理增强

作者：AI生存游戏项目组 - 问题4解决方案
版本：1.0.0
"""

import inspect
import warnings
from typing import Dict, List, Any, Optional, Union, Callable
from functools import wraps
import traceback
import logging

class EMRSParameterValidator:
    """EMRS参数验证器"""
    
    def __init__(self):
        self.validation_rules = {
            'action_result': {
                'type': dict,
                'required_keys': [],
                'optional_keys': ['health_change', 'food_gained', 'water_gained', 'damage_dealt', 'success']
            },
            'context': {
                'type': dict,
                'required_keys': [],
                'optional_keys': ['current_health', 'current_food', 'current_water', 'position', 'phase']
            },
            'development_stage': {
                'type': str,
                'valid_values': ['infant', 'child', 'adolescent', 'adult'],
                'default': 'child'
            }
        }
    
    def validate_parameter(self, param_name: str, param_value: Any) -> bool:
        """验证单个参数"""
        if param_name not in self.validation_rules:
            return True  # 未定义验证规则的参数默认通过
        
        rule = self.validation_rules[param_name]
        
        # 类型检查
        if 'type' in rule and not isinstance(param_value, rule['type']):
            return False
        
        # 值范围检查
        if 'valid_values' in rule and param_value not in rule['valid_values']:
            return False
        
        # 字典键检查
        if isinstance(param_value, dict) and 'required_keys' in rule:
            for key in rule['required_keys']:
                if key not in param_value:
                    return False
        
        return True
    
    def auto_fix_parameter(self, param_name: str, param_value: Any) -> Any:
        """自动修复参数"""
        if param_name not in self.validation_rules:
            return param_value
        
        rule = self.validation_rules[param_name]
        
        # 类型自动转换
        if 'type' in rule:
            if rule['type'] == dict and not isinstance(param_value, dict):
                if param_value is None:
                    return {}
                try:
                    # 尝试转换为字典
                    if hasattr(param_value, '__dict__'):
                        return param_value.__dict__
                    elif isinstance(param_value, (list, tuple)) and len(param_value) % 2 == 0:
                        return dict(zip(param_value[::2], param_value[1::2]))
                    else:
                        return {'raw_value': param_value}
                except:
                    return {'raw_value': param_value}
            
            elif rule['type'] == str and not isinstance(param_value, str):
                return str(param_value)
        
        # 设置默认值
        if 'default' in rule and (param_value is None or param_value == ''):
            return rule['default']
        
        # 值范围修复
        if 'valid_values' in rule and param_value not in rule['valid_values']:
            return rule['valid_values'][0] if rule['valid_values'] else rule.get('default')
        
        return param_value

class EMRSParameterMapper:
    """EMRS参数映射器"""
    
    def __init__(self):
        self.parameter_mappings = {
            # 旧参数名 -> 新参数名
            'current_state': 'context',
            'action_taken': 'action_result',
            'game_context': 'context',
            'state': 'context',
            'action': 'action_result',
            'developmental_stage': 'development_stage',
            'stage': 'development_stage'
        }
        
        self.method_mappings = {
            # 旧方法名 -> 新方法名
            'calculate_enhanced_reward': 'calculate_multi_dimensional_reward',
            'calculate_reward': 'calculate_multi_dimensional_reward',
            'get_reward_analysis': 'calculate_multi_dimensional_reward',
            'compute_rewards': 'calculate_multi_dimensional_reward'
        }
    
    def map_parameters(self, original_params: Dict[str, Any]) -> Dict[str, Any]:
        """映射参数名称"""
        mapped_params = {}
        
        for param_name, param_value in original_params.items():
            # 检查是否需要映射
            if param_name in self.parameter_mappings:
                new_name = self.parameter_mappings[param_name]
                mapped_params[new_name] = param_value
            else:
                mapped_params[param_name] = param_value
        
        return mapped_params
    
    def map_method_name(self, method_name: str) -> str:
        """映射方法名称"""
        return self.method_mappings.get(method_name, method_name)

class EMRSCompatibilityWrapper:
    """EMRS兼容性包装器"""
    
    def __init__(self, emrs_instance):
        self.emrs = emrs_instance
        self.validator = EMRSParameterValidator()
        self.mapper = EMRSParameterMapper()
        self.call_statistics = {
            'total_calls': 0,
            'successful_calls': 0,
            'fixed_calls': 0,
            'failed_calls': 0,
            'parameter_fixes': {},
            'method_redirects': {}
        }
    
    def __getattr__(self, name):
        """动态方法包装"""
        # 检查是否需要方法映射
        mapped_name = self.mapper.map_method_name(name)
        
        if hasattr(self.emrs, mapped_name):
            original_method = getattr(self.emrs, mapped_name)
            
            # 记录方法重定向
            if name != mapped_name:
                self.call_statistics['method_redirects'][name] = mapped_name
            
            return self._wrap_method(original_method, name)
        else:
            raise AttributeError(f"'{type(self.emrs).__name__}' object has no attribute '{name}'")
    
    def _wrap_method(self, method: Callable, original_name: str) -> Callable:
        """包装方法以添加参数修复功能"""
        
        @wraps(method)
        def wrapper(*args, **kwargs):
            self.call_statistics['total_calls'] += 1
            
            try:
                # 获取方法签名
                sig = inspect.signature(method)
                
                # 将位置参数转换为关键字参数
                bound_args = sig.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()
                
                # 映射参数名称
                mapped_params = self.mapper.map_parameters(bound_args.arguments)
                
                # 验证和修复参数
                fixed_params = {}
                parameters_fixed = False
                
                for param_name, param_value in mapped_params.items():
                    if param_name == 'self':
                        continue
                    
                    # 验证参数
                    if not self.validator.validate_parameter(param_name, param_value):
                        # 尝试修复参数
                        fixed_value = self.validator.auto_fix_parameter(param_name, param_value)
                        fixed_params[param_name] = fixed_value
                        parameters_fixed = True
                        
                        # 记录修复统计
                        if param_name not in self.call_statistics['parameter_fixes']:
                            self.call_statistics['parameter_fixes'][param_name] = 0
                        self.call_statistics['parameter_fixes'][param_name] += 1
                    else:
                        fixed_params[param_name] = param_value
                
                if parameters_fixed:
                    self.call_statistics['fixed_calls'] += 1
                
                # 重新绑定修复后的参数
                try:
                    result = method(**fixed_params)
                    self.call_statistics['successful_calls'] += 1
                    return result
                except TypeError as e:
                    # 参数不匹配，尝试智能适配
                    return self._smart_parameter_adaptation(method, fixed_params, e)
                
            except Exception as e:
                self.call_statistics['failed_calls'] += 1
                warnings.warn(f"EMRS方法调用失败 {original_name}: {str(e)}")
                
                # 返回默认结果避免程序崩溃
                if 'calculate' in original_name.lower() or 'reward' in original_name.lower():
                    return self._get_default_reward_result()
                else:
                    return None
        
        return wrapper
    
    def _smart_parameter_adaptation(self, method: Callable, params: Dict[str, Any], error: Exception) -> Any:
        """智能参数适配"""
        try:
            sig = inspect.signature(method)
            method_params = list(sig.parameters.keys())
            
            # 移除self参数
            if 'self' in method_params:
                method_params.remove('self')
            
            # 尝试只传递方法接受的参数
            adapted_params = {}
            for param_name in method_params:
                if param_name in params:
                    adapted_params[param_name] = params[param_name]
                elif param_name == 'action_result' and 'action' in params:
                    # 特殊处理：将action转换为action_result
                    action_data = params['action']
                    if isinstance(action_data, str):
                        adapted_params['action_result'] = {'action_type': action_data, 'success': True}
                    elif isinstance(action_data, dict):
                        adapted_params['action_result'] = action_data
                    else:
                        adapted_params['action_result'] = {'action_type': str(action_data), 'success': True}
                elif param_name == 'context' and any(key in params for key in ['current_state', 'state', 'game_context']):
                    # 合并多个上下文参数
                    context = {}
                    for context_key in ['current_state', 'state', 'game_context', 'context']:
                        if context_key in params and isinstance(params[context_key], dict):
                            context.update(params[context_key])
                    adapted_params['context'] = context
            
            result = method(**adapted_params)
            self.call_statistics['successful_calls'] += 1
            self.call_statistics['fixed_calls'] += 1
            return result
            
        except Exception as e:
            self.call_statistics['failed_calls'] += 1
            warnings.warn(f"智能参数适配失败: {str(e)}")
            return self._get_default_reward_result()
    
    def _get_default_reward_result(self) -> Dict[str, Any]:
        """获取默认奖励结果"""
        return {
            'total_reward': 0.0,
            'detailed_rewards': {
                'survival': 0.0,
                'resource': 0.0,
                'social': 0.0,
                'exploration': 0.0,
                'learning': 0.0
            },
            'reward_breakdown': {
                'survival': {'value': 0.0, 'percentage': 20.0, 'contribution_level': '默认'},
                'resource': {'value': 0.0, 'percentage': 20.0, 'contribution_level': '默认'},
                'social': {'value': 0.0, 'percentage': 20.0, 'contribution_level': '默认'},
                'exploration': {'value': 0.0, 'percentage': 20.0, 'contribution_level': '默认'},
                'learning': {'value': 0.0, 'percentage': 20.0, 'contribution_level': '默认'}
            },
            'weights_applied': {
                'survival_weight': 0.4,
                'resource_weight': 0.25,
                'social_weight': 0.15,
                'exploration_weight': 0.1,
                'learning_weight': 0.1
            },
            'status': 'default_fallback'
        }
    
    def get_compatibility_statistics(self) -> Dict[str, Any]:
        """获取兼容性统计信息"""
        success_rate = 0.0
        if self.call_statistics['total_calls'] > 0:
            success_rate = self.call_statistics['successful_calls'] / self.call_statistics['total_calls']
        
        fix_rate = 0.0
        if self.call_statistics['total_calls'] > 0:
            fix_rate = self.call_statistics['fixed_calls'] / self.call_statistics['total_calls']
        
        return {
            'total_calls': self.call_statistics['total_calls'],
            'successful_calls': self.call_statistics['successful_calls'],
            'fixed_calls': self.call_statistics['fixed_calls'],
            'failed_calls': self.call_statistics['failed_calls'],
            'success_rate': success_rate,
            'fix_rate': fix_rate,
            'parameter_fixes': dict(self.call_statistics['parameter_fixes']),
            'method_redirects': dict(self.call_statistics['method_redirects'])
        }

class EMRSParameterFixer:
    """EMRS参数修复主类"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.active_wrappers = {}
        self.global_statistics = {
            'wrappers_created': 0,
            'total_fixes_applied': 0,
            'successful_integrations': 0,
            'failed_integrations': 0
        }
    
    def wrap_emrs_instance(self, emrs_instance, instance_name: str = None) -> EMRSCompatibilityWrapper:
        """包装EMRS实例以提供兼容性"""
        if instance_name is None:
            instance_name = f"emrs_instance_{len(self.active_wrappers)}"
        
        try:
            wrapper = EMRSCompatibilityWrapper(emrs_instance)
            self.active_wrappers[instance_name] = wrapper
            self.global_statistics['wrappers_created'] += 1
            self.global_statistics['successful_integrations'] += 1
            
            if self.logger:
                self.logger.log(f"EMRS实例已包装: {instance_name}")
            
            return wrapper
            
        except Exception as e:
            self.global_statistics['failed_integrations'] += 1
            if self.logger:
                self.logger.log(f"EMRS实例包装失败 {instance_name}: {str(e)}")
            raise
    
    def create_parameter_adapter(self, original_params: Dict[str, Any]) -> Dict[str, Any]:
        """创建参数适配器"""
        mapper = EMRSParameterMapper()
        validator = EMRSParameterValidator()
        
        # 映射参数
        mapped_params = mapper.map_parameters(original_params)
        
        # 修复参数
        fixed_params = {}
        for param_name, param_value in mapped_params.items():
            fixed_params[param_name] = validator.auto_fix_parameter(param_name, param_value)
        
        return fixed_params
    
    def fix_method_call(self, emrs_instance, method_name: str, *args, **kwargs) -> Any:
        """修复方法调用"""
        try:
            # 获取或创建包装器
            wrapper_key = f"temp_{id(emrs_instance)}"
            if wrapper_key not in self.active_wrappers:
                self.active_wrappers[wrapper_key] = EMRSCompatibilityWrapper(emrs_instance)
            
            wrapper = self.active_wrappers[wrapper_key]
            
            # 获取包装后的方法
            method = getattr(wrapper, method_name)
            
            # 调用方法
            result = method(*args, **kwargs)
            
            self.global_statistics['total_fixes_applied'] += 1
            return result
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"方法调用修复失败 {method_name}: {str(e)}")
            raise
    
    def validate_emrs_integration(self, emrs_instance) -> Dict[str, Any]:
        """验证EMRS集成状态"""
        validation_result = {
            'instance_valid': False,
            'methods_available': [],
            'missing_methods': [],
            'parameter_compatibility': {},
            'recommendations': []
        }
        
        try:
            # 检查实例是否有效
            validation_result['instance_valid'] = emrs_instance is not None
            
            # 检查关键方法
            required_methods = [
                'calculate_multi_dimensional_reward',
                'get_reward_system_status',
                'predict_reward_trends',
                'get_optimization_suggestions'
            ]
            
            for method_name in required_methods:
                if hasattr(emrs_instance, method_name):
                    validation_result['methods_available'].append(method_name)
                else:
                    validation_result['missing_methods'].append(method_name)
            
            # 检查参数兼容性
            if hasattr(emrs_instance, 'calculate_multi_dimensional_reward'):
                method = getattr(emrs_instance, 'calculate_multi_dimensional_reward')
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                validation_result['parameter_compatibility']['calculate_multi_dimensional_reward'] = params
            
            # 生成建议
            if validation_result['missing_methods']:
                validation_result['recommendations'].append(
                    f"缺失方法: {', '.join(validation_result['missing_methods'])}, 建议使用兼容性包装器"
                )
            
            if len(validation_result['methods_available']) == len(required_methods):
                validation_result['recommendations'].append("EMRS实例完全兼容")
            
        except Exception as e:
            validation_result['validation_error'] = str(e)
            validation_result['recommendations'].append(f"验证过程中出现错误: {str(e)}")
        
        return validation_result
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """获取全局统计信息"""
        # 汇总所有包装器的统计信息
        total_calls = sum(wrapper.call_statistics['total_calls'] for wrapper in self.active_wrappers.values())
        total_successful = sum(wrapper.call_statistics['successful_calls'] for wrapper in self.active_wrappers.values())
        total_fixed = sum(wrapper.call_statistics['fixed_calls'] for wrapper in self.active_wrappers.values())
        total_failed = sum(wrapper.call_statistics['failed_calls'] for wrapper in self.active_wrappers.values())
        
        overall_success_rate = (total_successful / total_calls) if total_calls > 0 else 0.0
        overall_fix_rate = (total_fixed / total_calls) if total_calls > 0 else 0.0
        
        return {
            'global_statistics': dict(self.global_statistics),
            'active_wrappers': len(self.active_wrappers),
            'total_method_calls': total_calls,
            'total_successful_calls': total_successful,
            'total_fixed_calls': total_fixed,
            'total_failed_calls': total_failed,
            'overall_success_rate': overall_success_rate,
            'overall_fix_rate': overall_fix_rate,
            'wrapper_details': {
                name: wrapper.get_compatibility_statistics()
                for name, wrapper in self.active_wrappers.items()
            }
        }
    
    def generate_fix_report(self) -> str:
        """生成修复报告"""
        stats = self.get_global_statistics()
        
        report = []
        report.append("=== EMRS参数修复报告 ===")
        report.append(f"活跃包装器数量: {stats['active_wrappers']}")
        report.append(f"总方法调用次数: {stats['total_method_calls']}")
        report.append(f"成功调用次数: {stats['total_successful_calls']}")
        report.append(f"修复调用次数: {stats['total_fixed_calls']}")
        report.append(f"失败调用次数: {stats['total_failed_calls']}")
        report.append(f"整体成功率: {stats['overall_success_rate']:.2%}")
        report.append(f"整体修复率: {stats['overall_fix_rate']:.2%}")
        report.append("")
        
        # 详细的包装器统计
        for name, wrapper_stats in stats['wrapper_details'].items():
            report.append(f"包装器 {name}:")
            report.append(f"  调用次数: {wrapper_stats['total_calls']}")
            report.append(f"  成功率: {wrapper_stats['success_rate']:.2%}")
            report.append(f"  修复率: {wrapper_stats['fix_rate']:.2%}")
            
            if wrapper_stats['parameter_fixes']:
                report.append("  参数修复:")
                for param, count in wrapper_stats['parameter_fixes'].items():
                    report.append(f"    {param}: {count}次")
            
            if wrapper_stats['method_redirects']:
                report.append("  方法重定向:")
                for old_method, new_method in wrapper_stats['method_redirects'].items():
                    report.append(f"    {old_method} -> {new_method}")
            report.append("")
        
        return "\n".join(report)

# === 工厂函数和便捷接口 ===

def create_emrs_parameter_fixer(logger=None) -> EMRSParameterFixer:
    """创建EMRS参数修复器实例"""
    return EMRSParameterFixer(logger=logger)

def quick_fix_emrs_call(emrs_instance, method_name: str, **kwargs) -> Any:
    """快速修复EMRS方法调用"""
    fixer = EMRSParameterFixer()
    return fixer.fix_method_call(emrs_instance, method_name, **kwargs)

def wrap_emrs_for_compatibility(emrs_instance) -> EMRSCompatibilityWrapper:
    """为EMRS实例添加兼容性包装"""
    return EMRSCompatibilityWrapper(emrs_instance)

if __name__ == "__main__":
    # 简单测试
    print("EMRS参数修复模块测试")
    
    # 测试参数验证器
    validator = EMRSParameterValidator()
    print(f"参数验证测试: {validator.validate_parameter('development_stage', 'child')}")
    print(f"参数修复测试: {validator.auto_fix_parameter('development_stage', 'invalid')}")
    
    # 测试参数映射器
    mapper = EMRSParameterMapper()
    test_params = {'current_state': {'health': 100}, 'action_taken': 'move'}
    mapped = mapper.map_parameters(test_params)
    print(f"参数映射测试: {mapped}")
    
    print("EMRS参数修复模块测试完成！") 