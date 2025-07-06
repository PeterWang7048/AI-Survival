#!/usr/bin/env python3
"""
增强版四层决策系统
实现：紧急情况 → V3决策库 → WBM规则 → CDL探索
"""

def enhanced_make_decision_with_wooden_bridge(self, game):
    """使用WBM进行决策（重构版 - 四层决策架构：紧急情况 → V3决策库 → WBM规则 → CDL探索）"""
    try:
        # === 第一层：紧急情况处理（最高优先级）===
        threats = self.detect_threats(game.game_map)
        is_emergency = (threats or self.hp < 30 or self.food < 20 or self.water < 20)
        
        if is_emergency:
            # 紧急情况下使用整合决策系统的基础生存逻辑
            if hasattr(self, 'integrated_decision_active') and self.integrated_decision_active and self.integrated_decision_system:
                try:
                    from main import DecisionContext
                    context = DecisionContext(
                        hp=self.hp,
                        food=self.food,
                        water=self.water,
                        position=(self.x, self.y),
                        day=getattr(game, 'current_day', 1),
                        environment=self._get_current_environment_type(game),
                        threats_nearby=len(threats) > 0,
                        resources_nearby=self._get_nearby_resources(game),
                        urgency_level=self._calculate_urgency_level()
                    )
                    
                    decision, confidence, source = self.integrated_decision_system.make_decision(context)
                    
                    if decision and confidence > 0.3:  # 紧急情况下降低置信度要求
                        if self.logger:
                            self.logger.log(f"{self.name} 🚨 紧急情况决策: {decision} (来源: {source}, 置信度: {confidence:.2f})")
                        return decision
                except Exception as e:
                    if self.logger:
                        self.logger.log(f"{self.name} 紧急情况决策失败: {str(e)}")
        
        # === 第二层：V3决策库匹配（高置信度阈值）===
        if hasattr(self, 'integrated_decision_active') and self.integrated_decision_active and self.integrated_decision_system:
            try:
                from main import DecisionContext
                context = DecisionContext(
                    hp=self.hp,
                    food=self.food,
                    water=self.water,
                    position=(self.x, self.y),
                    day=getattr(game, 'current_day', 1),
                    environment=self._get_current_environment_type(game),
                    threats_nearby=len(threats) > 0,
                    resources_nearby=self._get_nearby_resources(game),
                    urgency_level=self._calculate_urgency_level()
                )
                
                decision, confidence, source = self.integrated_decision_system.make_decision(context)
                
                # V3决策库需要高置信度（≥70%）
                if decision and confidence >= 0.70 and source == 'v3_library':
                    if self.logger:
                        self.logger.log(f"{self.name} 🏗️ V3决策库匹配: {decision} (来源: {source}, 置信度: {confidence:.2f})")
                    return decision
                    
            except Exception as e:
                if self.logger:
                    self.logger.log(f"{self.name} V3决策库匹配失败: {str(e)}")
        
        # === 第三层：WBM规则构建（中等置信度阈值）===
        if hasattr(self, 'integrated_decision_active') and self.integrated_decision_active and self.integrated_decision_system:
            try:
                from main import DecisionContext
                context = DecisionContext(
                    hp=self.hp,
                    food=self.food,
                    water=self.water,
                    position=(self.x, self.y),
                    day=getattr(game, 'current_day', 1),
                    environment=self._get_current_environment_type(game),
                    threats_nearby=len(threats) > 0,
                    resources_nearby=self._get_nearby_resources(game),
                    urgency_level=self._calculate_urgency_level()
                )
                
                decision, confidence, source = self.integrated_decision_system.make_decision(context)
                
                # WBM规则需要中等置信度（≥50%）
                if decision and confidence >= 0.50 and source == 'wbm_rule':
                    if self.logger:
                        self.logger.log(f"{self.name} 🌉 WBM规则构建: {decision} (来源: {source}, 置信度: {confidence:.2f})")
                    return decision
                    
            except Exception as e:
                if self.logger:
                    self.logger.log(f"{self.name} WBM规则构建失败: {str(e)}")
        
        # === 第四层：CDL好奇心驱动探索（资源充足时的默认选择）===
        # 在相对不紧急的情况下，让V3决策库和WBM退位给CDL学习机制
        if not is_emergency and self.hp >= 50 and self.food >= 40 and self.water >= 40:
            # 使用增强版CDL探索
            if hasattr(self, '_execute_enhanced_cdl_exploration'):
                try:
                    cdl_decision = self._execute_enhanced_cdl_exploration(game)
                    if cdl_decision:
                        if self.logger:
                            self.logger.log(f"{self.name} 🎯 CDL好奇心驱动探索: {cdl_decision} (资源充足，主动学习)")
                        return cdl_decision
                except Exception as e:
                    if self.logger:
                        self.logger.log(f"{self.name} CDL探索失败: {str(e)}")
            
            # 备用CDL探索
            try:
                cdl_result = self._execute_cdl_exploration_move(game)
                if cdl_result:
                    if self.logger:
                        self.logger.log(f"{self.name} 🎯 CDL备用探索: explore (资源充足，主动学习)")
                    return 'explore'
            except Exception as e:
                if self.logger:
                    self.logger.log(f"{self.name} CDL备用探索失败: {str(e)}")
        
        # === 最终备选：基础生存逻辑===
        if hasattr(self, 'integrated_decision_active') and self.integrated_decision_active and self.integrated_decision_system:
            try:
                from main import DecisionContext
                context = DecisionContext(
                    hp=self.hp,
                    food=self.food,
                    water=self.water,
                    position=(self.x, self.y),
                    day=getattr(game, 'current_day', 1),
                    environment=self._get_current_environment_type(game),
                    threats_nearby=len(threats) > 0,
                    resources_nearby=self._get_nearby_resources(game),
                    urgency_level=self._calculate_urgency_level()
                )
                
                decision, confidence, source = self.integrated_decision_system.make_decision(context)
                
                if decision:
                    if self.logger:
                        self.logger.log(f"{self.name} 🏗️ 整合决策系统建议行动: {decision} (来源: {source}, 置信度: {confidence:.2f})")
                    return decision
                    
            except Exception as e:
                if self.logger:
                    self.logger.log(f"{self.name} 整合决策系统失败: {str(e)}")
        
        # === 传统WBM备选机制 ===
        # 如果所有新机制都失败，回退到传统WBM
        current_goals = self._establish_current_goals(game)
        
        for goal in current_goals:
            # 从经验中提取规律
            extracted_rules = self._extract_rules_from_experience(goal)
            
            # 获取基础生存规律
            basic_rules = self._get_basic_survival_rules(goal)
            
            # 合并规律
            all_rules = extracted_rules + basic_rules
            
            # 选择最佳规律
            if all_rules:
                best_rule = max(all_rules, key=lambda r: r.get('confidence', 0))
                
                # 构建木桥计划
                bridge_plan = {
                    'goal': goal,
                    'rule': best_rule,
                    'action': best_rule.get('action', 'explore'),
                    'confidence': best_rule.get('confidence', 0.5)
                }
                
                # 执行计划
                execution_result = self._convert_bridge_to_game_action(bridge_plan, {})
                
                if execution_result:
                    if self.logger:
                        self.logger.log(f"{self.name} 🌉 WBM决策记录EOCATR经验: {execution_result}")
                    return execution_result
        
        # 最终默认行动
        return 'explore'
        
    except Exception as e:
        if self.logger:
            self.logger.log(f"{self.name} WBM决策系统完全失败: {str(e)}")
        return 'explore'

def apply_enhanced_decision_system():
    """应用增强版四层决策系统"""
    from main import ILAIPlayer
    
    # 将新方法绑定到ILAIPlayer类
    ILAIPlayer.make_decision_with_wooden_bridge = enhanced_make_decision_with_wooden_bridge
    
    print("✅ 增强版四层决策系统已应用到ILAIPlayer类")

if __name__ == "__main__":
    apply_enhanced_decision_system()
    print("🎯 增强版四层决策系统独立运行完成") 