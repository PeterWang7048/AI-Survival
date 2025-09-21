# 🧠 ILAI: Infant Learning-Inspired Neuro-Symbolic Architecture

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


> **An interpretable AI architecture inspired by infant learning mechanisms, achieving superior performance and transparency across multiple reinforcement learning environments.**

## 🎯 Overview

This repository contains the complete experimental framework for evaluating the **Infant Learning AI (ILAI)** architecture across three benchmark environments. ILAI combines symbolic reasoning with adaptive learning mechanisms, inspired by how infants explore and understand their environment.

### 🏆 Key Achievements

- **📊 Superior Performance**: ILAI outperforms traditional baselines across all tested environments
- **🔍 High Interpretability**: 0.857±0.060 cross-environment interpretability score  
- **⚡ Efficient Learning**: Rapid convergence with minimal training episodes
- **🎯 Generalization**: Consistent performance across diverse task domains

## 🚀 Quick Start

### Prerequisites
```bash
pip install gymnasium numpy pandas matplotlib scipy seaborn
```

### Run Experiments

**FrozenLake-v1 Experiment:**
```bash
cd FrozenLake
python frozenlake_main_experiment.py
```

**Taxi-v3 Experiment:**
```bash
cd Taxi
python taxi_main_experiment.py
```

**Interpretability Analysis:**
```bash
python interpretability_calculator.py
```

## 📁 Repository Structure

```
ILAI-Experiments/
├── 📂 FrozenLake/           # 4×4 navigation with slippery surfaces
│   ├── frozenlake_main_experiment.py      # Main experiment runner
│   ├── frozenlake_agents.py               # ILAI & baseline implementations
│   └── frozenlake_experiment_manager.py   # Experiment framework
├── 📂 Taxi/                 # 5×5 pickup-delivery environment  
│   ├── taxi_main_experiment.py            # Main experiment runner
│   ├── taxi_baseline_framework.py         # Comprehensive baselines
│   ├── taxi_environment.py                # Environment implementation
│   └── taxi_ilai_system.py               # Taxi-specific ILAI
├── interpretability_calculator.py         # Cross-environment analysis
└── README.md               # This file
```

## 🧪 Experiments Overview

| Environment | Agents | Episodes/Run | Runs | Key Challenge |
|-------------|--------|---------------|------|---------------|
| **FrozenLake-v1** | 6 | 150 | 20 | Stochastic slippery navigation |
| **Taxi-v3** | 6 | 50 | 20 | Multi-step pickup-delivery planning |
| **Cross-Analysis** | All | N/A | N/A | Interpretability evaluation |

## 📈 Performance Results

### FrozenLake-v1 (Slippery Environment)
- **ILAI System**: 73.7% ± 3.4% ⭐
- **Q-Learning**: 62.0% ± 4.2%
- **Deep Q-Network**: 45.0% ± 4.3%
- **Rule-based Agent**: 6.2% ± 2.3%
- **A* Search**: 4.6% ± 1.5%
- **Random Baseline**: 1.3% ± 0.9%

### Cross-Environment Interpretability
- **ILAI**: 0.857 ± 0.060 🏆
- **Traditional ML**: 0.805 ± 0.116
- **Deep Learning**: 0.623 ± 0.103

## 🔬 Core Architecture

ILAI implements three key mechanisms:

### 🌸 Blooming & Pruning Mechanism (BPM)
Neuroplasticity-inspired rule generation and validation
- **Blooming**: Generate candidate rules from experience
- **Pruning**: Validate and refine rules based on outcomes

### 🌉 Wooden Bridge Mechanism (WBM)  
Goal-directed rule composition and planning
- **Bridge Construction**: Combine rules into multi-step plans
- **Utility Evaluation**: Multi-attribute decision making

### 🎯 Scene Symbolization Mechanism (SSM)
Convert observations into structured symbolic tuples
- **E-A-R Format**: Environment-Action-Result representation
- **Dynamic Learning**: Adaptive symbolic pattern recognition

## 📊 Interpretability Metrics

We evaluate interpretability using five equal-weighted dimensions:

1. **Rule Fidelity** (20%) - Accuracy of extracted rules
2. **Decision Transparency** (20%) - Clarity of reasoning process  
3. **Stability** (20%) - Consistency across similar states
4. **Knowledge Extractability** (20%) - Ease of rule extraction
5. **Rule Simplicity** (20%) - Understandability of learned patterns

## 🛠️ Advanced Usage

### Custom Experiment Configuration
```python
# Example: Custom FrozenLake experiment
from FrozenLake.frozenlake_main_experiment import ExperimentManager

manager = ExperimentManager(
    episodes_per_experiment=200,
    num_experiments=10,
    log_directory="custom_logs/"
)
manager.run_full_experiment()
```

### Interpretability Analysis
```python
# Example: Custom interpretability calculation
from interpretability_calculator import calculate_interpretability

results = calculate_interpretability(
    environments=['FrozenLake', 'Taxi'],
    metrics_weights={'rule_fidelity': 0.3, 'transparency': 0.3, ...}
)
```

## 📝 Citation

If you use this code in your research, please cite our paper:

```bibtex
@article{wang2024ilai,
  title={An Infant Learning-Inspired Neuro-Symbolic Architecture for Knowledge Extraction and Interpretable AI},
  author={Wang, Lujia},
  journal={Machine Learning and Knowledge Extraction},
  year={2024}
}
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI Gymnasium for providing standardized RL environments
- The broader AI research community for foundational work in interpretable AI
- Reviewers and collaborators who helped improve this work

---

**📞 Contact**: [peter7048@sina.com](mailto:peter7048@sina.com)  
**🏫 Affiliation**: Shanghai Starriver Bilingual School  
**📊 GitHub**: [Your GitHub Profile](https://github.com/PeterWang7048/AI-Survival)