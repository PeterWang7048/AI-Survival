from blooming_and_pruning_model import BloomingAndPruningModel, CandidateRule, RuleType


class DummyLogger:
    def log(self, msg):
        # 避免Windows控制台编码报错，剥离emoji
        try:
            print(str(msg).encode('gbk', errors='ignore').decode('gbk'))
        except Exception:
            print(str(msg))


def make_rule(idx: int, activation: int, confidence: float, supp: int = 0, contra: int = 0):
    r = CandidateRule(
        rule_id=f"r{idx}",
        rule_type=RuleType.CONDITIONAL,
        pattern="E+O+A->R",
        conditions={"action": "collect_plant"},
        predictions={"expected_success": True},
    )
    r.activation_count = activation
    r.confidence = confidence
    # 证据
    for i in range(supp):
        r.evidence.supporting_experiences.append(f"s{i}")
    for i in range(contra):
        r.evidence.contradicting_experiences.append(f"c{i}")
    return r


def run_test():
    logger = DummyLogger()
    bpm = BloomingAndPruningModel(logger=logger)
    bpm.config.update({
        'auto_promotion_enabled': True,
        'auto_promote_repeat_threshold': 3,
        'auto_promote_confidence_threshold': 0.4,
        'auto_promote_max_contradiction_ratio': 0.5,
    })

    # 添加三个候选规则
    r1 = make_rule(1, activation=0, confidence=0.9)  # activation不足，不应晋升
    r2 = make_rule(2, activation=3, confidence=0.39)  # confidence不足，不应晋升
    r3 = make_rule(3, activation=3, confidence=0.5, supp=2, contra=1)  # 满足，应该晋升

    bpm.candidate_rules[r1.rule_id] = r1
    bpm.candidate_rules[r2.rule_id] = r2
    bpm.candidate_rules[r3.rule_id] = r3

    promoted = bpm._auto_promotion_check()
    assert 'r3' in promoted, "r3 应该被自动晋升"
    assert 'r1' not in promoted and 'r2' not in promoted, "r1/r2 不应晋升"
    assert 'r3' in bpm.validated_rules and 'r3' not in bpm.candidate_rules, "r3 应在已验证集合中"
    print("✅ 自测通过: 自动晋升按预期工作")


if __name__ == "__main__":
    run_test()


