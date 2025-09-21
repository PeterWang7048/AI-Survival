# 🧊 FrozenLake-v1 ILAI Experiment

> Evaluating ILAI's navigation capabilities in a stochastic, slippery 4×4 grid world environment.

## 🎯 Experiment Overview

This experiment evaluates the **Infant Learning AI (ILAI)** system against five baseline algorithms in the challenging FrozenLake-v1 environment with slippery surfaces enabled. The stochastic nature of the environment makes it an ideal testbed for evaluating adaptive learning and robust decision-making.

### 🎮 Environment Details

- **Environment**: OpenAI Gymnasium FrozenLake-v1
- **Grid Size**: 4×4 
- **Surface**: Slippery (`is_slippery=True`)
- **Challenge**: Agent may slip in unintended directions
- **Goal**: Navigate from start (S) to goal (G) while avoiding holes (H)

```
SFFF
FHFH  
FFFH
HFFG
```

## 🤖 Evaluated Algorithms

| Algorithm | Type | Key Features |
|-----------|------|--------------|
| **ILAI System** | Neuro-Symbolic | Regional risk assessment, E-A-R learning |
| **Q-Learning** | Model-Free RL | Tabular value function, ε-greedy exploration |
| **Deep Q-Network** | Deep RL | Neural network Q-approximation |
| **A* Search** | Planning | Optimal pathfinding with slipperiness adaptation |
| **Rule-Based** | Heuristic | Predefined navigation heuristics |
| **Random** | Baseline | Uniform random action selection |

## 📊 Performance Results

| Algorithm | Success Rate | Average Steps | Training Episodes |
|-----------|--------------|---------------|-------------------|
| **ILAI System** | **73.7% ± 3.4%** 🏆 | **6.2 ± 0.8** | 150 (online learning) |
| **Q-Learning** | 62.0% ± 4.2% | 6.8 ± 1.2 | 20,000 + 150 |
| **Deep Q-Network** | 45.0% ± 4.3% | 8.1 ± 1.5 | 20,000 + 150 |
| **Rule-Based** | 6.2% ± 2.3% | 12.4 ± 3.1 | N/A |
| **A* Search** | 4.6% ± 1.5% | 11.8 ± 2.9 | N/A |
| **Random Baseline** | 1.3% ± 0.9% | 15.7 ± 4.2 | N/A |

*Results based on 20 independent runs of 150 episodes each*

## 🚀 Quick Start

### Prerequisites
```bash
pip install gymnasium numpy pandas matplotlib
```

### Run Single Experiment
```bash
python frozenlake_main_experiment.py
```

### Custom Configuration
```python
from frozenlake_main_experiment import ExperimentManager

# Configure custom experiment
manager = ExperimentManager(
    episodes_per_experiment=150,
    num_experiments=20,
    environment_seed=42,
    log_detailed=True
)

# Run experiment
results = manager.run_full_experiment()
print(f"ILAI Success Rate: {results['ILAI_success_rate']:.1f}%")
```

## 🧠 ILAI Architecture Details

### Regional Decision-Making
ILAI divides the 4×4 grid into strategic regions with position-specific assessments:

```python
# Example regional strategy distribution
strategies = {
    "safety_first": 92.5%,      # Prioritize avoiding holes
    "high_reward": 6.4%,        # Direct goal-seeking
    "balanced_exploration": 1.1% # Exploration vs exploitation
}
```

### E-A-R Learning Mechanism
- **Environment (E)**: Current position and surrounding states
- **Action (A)**: Movement decision (Up/Down/Left/Right)  
- **Result (R)**: Outcome assessment (Safe/Dangerous/Goal/Progress)

### Dynamic Weight Adaptation
```python
decision_weights = {
    "safety": 0.4,          # Hole avoidance
    "progress": 0.3,        # Goal approach
    "exploration": 0.2,     # Unknown state investigation  
    "risk_aversion": 0.1    # Conservative movement
}
```

## 📁 File Structure

```
FrozenLake/
├── frozenlake_main_experiment.py      # 🎯 Main experiment runner
├── frozenlake_agents.py               # 🤖 ILAI & baseline implementations
├── frozenlake_experiment_manager.py   # ⚙️ Experiment framework
└── README.md                          # 📖 This file
```

### Key Components

- **`frozenlake_main_experiment.py`**: Entry point, configures and runs experiments
- **`frozenlake_agents.py`**: Contains `FairAcademicRegionILAI` and improved baseline agents
- **`frozenlake_experiment_manager.py`**: Handles experiment orchestration, logging, and statistics

## 🔬 Technical Highlights

### Curriculum Learning (Baselines)
Q-Learning and DQN agents undergo progressive training:
1. **Stage 1** (5K episodes): No slipperiness
2. **Stage 2** (5K episodes): 33% slipperiness  
3. **Stage 3** (5K episodes): 66% slipperiness
4. **Stage 4** (5K episodes): Full slipperiness

### ILAI Advantages
- **No Pre-training**: Learns online during evaluation
- **Interpretable Decisions**: Explicit reasoning for each action
- **Adaptive Strategy**: Dynamic weight adjustment based on experience
- **Regional Intelligence**: Position-aware risk assessment

## 📈 Learning Curves

ILAI demonstrates rapid convergence compared to baseline algorithms:

- **Episodes 1-15**: Rapid E-A-R knowledge acquisition  
- **Episodes 15+**: Consistent high-performance application
- **Final Performance**: Stabilizes around 73.7% success rate

## 🎛️ Configuration Options

### Environment Settings
```python
env_config = {
    "map_name": "4x4",
    "is_slippery": True,
    "render_mode": None  # Set to "human" for visualization
}
```

### Experiment Settings  
```python
experiment_config = {
    "episodes_per_run": 150,
    "num_runs": 20,
    "max_steps_per_episode": 100,
    "random_seeds": list(range(42, 62))  # Reproducible runs
}
```

## 📊 Output Files

The experiment generates comprehensive logs and statistics:

- **Individual Run Logs**: `frozenlake-runXX-YYYYMMDD-HHMMSS.log`
- **Summary Statistics**: `frozenlake_performance_summary.csv`  
- **Per-Run Data**: `frozenlake_performance_perrun.csv`
- **Leaderboard**: Embedded in summary logs

## 🔧 Troubleshooting

### Common Issues

**Low Performance**: Ensure `is_slippery=True` for realistic challenge
```python
# Correct configuration
env = gym.make('FrozenLake-v1', is_slippery=True)
```

**Memory Issues**: Reduce number of runs or episodes for testing
```python
# Quick test configuration  
manager = ExperimentManager(episodes_per_experiment=50, num_experiments=5)
```

## 🎯 Expected Use Cases

- **Research**: Baseline for neuro-symbolic AI comparisons
- **Education**: Demonstrate interpretable AI principles
- **Benchmarking**: Standard evaluation of adaptive learning algorithms
- **Development**: Test new ILAI variations and improvements

---

**📊 Experiment Stats**: 20 runs × 150 episodes × 6 algorithms = 18,000 total episodes evaluated  
**⏱️ Runtime**: ~45 minutes on standard hardware  
**💾 Output**: ~15MB of detailed logs and statistics