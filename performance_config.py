# AI Survival Competition Performance Configuration
# Adjust these parameters to optimize game performance

# BMP rule generation optimization
BMP_TRIGGER_THRESHOLD = 5          # BMP trigger threshold (experience count)
BMP_GENERATION_INTERVAL = 15       # BMP generation interval (seconds)
BMP_MIN_EXPERIENCE_COUNT = 5       # Minimum experience count

# Knowledge sharing optimization
KNOWLEDGE_SHARE_INTERVAL = 5       # Knowledge sharing interval (rounds)
MAX_SHARES_PER_ROUND = 2          # Maximum shares per round
KNOWLEDGE_NOVELTY_THRESHOLD = 0.7  # Knowledge novelty threshold

# Experience storage optimization
EXPERIENCE_BATCH_SIZE = 20         # Experience batch processing size
EXPERIENCE_SYNC_INTERVAL = 60     # Experience sync interval (seconds)
EXPERIENCE_CACHE_SIZE = 500       # Experience cache size

# Logging optimization
ENABLE_DEBUG_LOGS = False         # Enable debug logs
LOG_LEVEL = "INFO"                # Log level
REDUCE_VERBOSE_LOGS = True        # Reduce verbose logs

# Game loop optimization
ENABLE_PERFORMANCE_MONITORING = True  # Enable performance monitoring
PERFORMANCE_REPORT_INTERVAL = 10      # Performance report interval (rounds)

print("📊 Performance configuration loaded")
print(f"  - BMP trigger threshold: {BMP_TRIGGER_THRESHOLD}")
print(f"  - Knowledge share interval: {KNOWLEDGE_SHARE_INTERVAL} rounds")
print(f"  - Experience batch size: {EXPERIENCE_BATCH_SIZE}")
print(f"  - Log level: {LOG_LEVEL}")
