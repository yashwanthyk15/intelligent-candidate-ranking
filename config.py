"""
Redrob Hackathon — Central Configuration
All weights, thresholds, keyword lists, and scoring parameters.
"""
from datetime import date

# Reference date for recency calculations
REFERENCE_DATE = date(2026, 6, 15)

# ============================================================================
# DIMENSION WEIGHTS (must sum to 1.0)
# ============================================================================
WEIGHTS = {
    'role_alignment': 0.28,
    'shipped_systems': 0.25,
    'tech_depth': 0.20,
    'experience': 0.12,
    'behavioral': 0.10,
    'location': 0.05,
}

# ============================================================================
# DIMENSION 1: ROLE ALIGNMENT — Title Tier Mapping
# ============================================================================
TITLE_TIER_S = [
    'ml engineer', 'ai engineer', 'ai research engineer', 'senior ml engineer',
    'senior machine learning engineer', 'nlp engineer', 'search engineer',
    'ranking engineer', 'recommendation systems engineer', 'machine learning engineer',
    'senior ai engineer', 'staff ml engineer', 'principal ml engineer',
    'applied ml engineer', 'applied ai engineer', 'junior ml engineer',
]

TITLE_TIER_A = [
    'data scientist', 'senior data scientist', 'senior data engineer',
    'analytics engineer', 'research scientist', 'research engineer',
    'applied scientist', 'ml ops engineer', 'mlops engineer',
]

TITLE_TIER_B = [
    'software engineer', 'senior software engineer', 'backend engineer',
    'data engineer', 'data analyst', 'full stack developer',
    'senior backend engineer', 'platform engineer',
]

TITLE_TIER_C = [
    'devops engineer', 'cloud engineer', 'qa engineer', 'java developer',
    '.net developer', 'mobile developer', 'frontend engineer',
    'ios developer', 'android developer', 'sre engineer',
]

TITLE_TIER_F = [
    'hr manager', 'accountant', 'marketing manager', 'sales executive',
    'content writer', 'civil engineer', 'mechanical engineer',
    'graphic designer', 'customer support', 'operations manager',
    'business analyst', 'project manager', 'product manager',
    'teacher', 'doctor', 'lawyer', 'nurse', 'pharmacist',
]

# ============================================================================
# DIMENSION 2: SHIPPED SYSTEMS — Career History Keywords
# ============================================================================
SHIPPED_TIER1_KEYWORDS = [
    'ranking system', 'retrieval system', 'recommendation system',
    'search system', 'candidate matching', 'talent matching',
    'hybrid retrieval', 're-ranking', 'reranking',
    'vector search', 'semantic search', 'embedding-based retrieval',
    'learning to rank', 'learning-to-rank',
    'candidate ranking', 'job matching', 'relevance scoring',
]

SHIPPED_TIER2_KEYWORDS = [
    'deployed', 'shipped', 'production', 'inference',
    'model serving', 'fine-tuned', 'fine tuned', 'trained model',
    'embedding drift', 'index refresh', 'feature pipeline',
    'real users', 'real-world', 'latency', 'throughput',
    'a/b test', 'a/b testing', 'ab testing', 'online experiment',
    'served', 'serving', 'scaled to', 'scale-up',
    'monitoring', 'model monitoring', 'mlops',
]

SHIPPED_TIER3_KEYWORDS = [
    'machine learning', 'deep learning', 'neural network',
    'nlp', 'natural language', 'transformer', 'bert',
    'gpt', 'llm', 'large language model', 'pytorch', 'tensorflow',
    'scikit-learn', 'xgboost', 'lightgbm', 'random forest',
    'embeddings', 'word2vec', 'sentence-transformers',
    'hugging face', 'huggingface',
]

SCALE_EVIDENCE_KEYWORDS = [
    'users', 'scale', 'million', 'thousands', 'hundreds of',
    'improved', 'reduced', 'increased', 'optimized',
    'latency from', 'throughput from', 'accuracy from',
    '%', 'percent', 'engagement', 'ctr', 'conversion',
]

SHIPPED_TIER1_POINTS = 15
SHIPPED_TIER1_CAP = 60
SHIPPED_TIER2_POINTS = 10
SHIPPED_TIER2_CAP = 40
SHIPPED_TIER3_POINTS = 5
SHIPPED_TIER3_CAP = 20
SCALE_BONUS = 10
SHIPPED_MAX_SCORE = 130

# ============================================================================
# DIMENSION 3: TECHNICAL DEPTH — Core Domain Keywords
# ============================================================================
CORE_DOMAINS = {
    'embeddings_retrieval': [
        'sentence-transformers', 'sentence transformers', 'openai embeddings',
        'bge', 'e5', 'embeddings', 'dense retrieval', 'semantic search',
        'faiss', 'embedding', 'vector embedding', 'text embedding',
        'contrastive learning', 'siamese', 'bi-encoder', 'cross-encoder',
    ],
    'vector_db_search': [
        'pinecone', 'weaviate', 'qdrant', 'milvus', 'opensearch',
        'elasticsearch', 'faiss', 'vector database', 'hybrid search',
        'vector store', 'vector index', 'ann', 'approximate nearest',
        'hnsw', 'ivf', 'bm25',
    ],
    'ranking_systems': [
        'learning-to-rank', 'learning to rank', 'ltr', 'xgboost',
        'neural ranking', 'ranking', 're-ranking', 'reranking',
        'relevance', 'candidate scoring', 'pointwise', 'pairwise',
        'listwise', 'lambdamart', 'lambdarank',
    ],
    'evaluation_frameworks': [
        'ndcg', 'mrr', 'map', 'mean average precision',
        'precision', 'recall', 'f1', 'a/b testing', 'a/b test',
        'offline evaluation', 'online metrics', 'benchmark',
        'evaluation framework', 'metric', 'ground truth',
    ],
    'python_production': [
        'python', 'fastapi', 'flask', 'django', 'production',
        'api', 'microservice', 'deployment', 'docker', 'kubernetes',
        'ci/cd', 'rest api', 'grpc',
    ],
}

# ============================================================================
# DIMENSION 4: EXPERIENCE — Ideal Ranges
# ============================================================================
EXPERIENCE_SCORE_MAP = [
    # (min_yoe, max_yoe, score)
    (5, 9, 1.0),
    (4, 5, 0.85),
    (9, 12, 0.75),
    (3, 4, 0.60),
    (12, 15, 0.50),
    (15, 50, 0.40),
    (0, 3, 0.30),
]

JOB_HOPPER_THRESHOLD_MONTHS = 18
JOB_HOPPER_PENALTY = 0.15

# ============================================================================
# DIMENSION 5: BEHAVIORAL — Signal Weights
# ============================================================================
BEHAVIORAL_WEIGHTS = {
    'recency': 0.35,
    'open_to_work': 0.20,
    'response_rate': 0.20,
    'notice_period': 0.10,
    'market_validation': 0.15,
}

RECENCY_SCORES = [
    (30, 1.0),
    (90, 0.75),
    (180, 0.40),
    (365, 0.10),
    (9999, 0.05),
]

NOTICE_SCORES = [
    (30, 1.0),
    (60, 0.75),
    (90, 0.50),
    (120, 0.30),
    (180, 0.15),
]

# ============================================================================
# DIMENSION 6: LOCATION
# ============================================================================
PREFERRED_LOCATIONS = [
    'pune', 'noida', 'delhi', 'new delhi', 'delhi ncr', 'gurgaon',
    'gurugram', 'faridabad', 'ghaziabad',
]
TIER1_INDIA_LOCATIONS = [
    'bangalore', 'bengaluru', 'mumbai', 'hyderabad', 'chennai', 'kolkata',
]

# ============================================================================
# CONSULTING COMPANIES (JD explicit disqualifier)
# ============================================================================
CONSULTING_COMPANIES = [
    'tcs', 'infosys', 'wipro', 'accenture', 'cognizant', 'capgemini',
    'tech mahindra', 'hcl', 'mindtree', 'mphasis', 'hexaware',
    'persistent', 'l&t infotech', 'lti', 'ltimindtree',
    'atos', 'dxc', 'unisys', 'ntt data',
]

PRODUCT_COMPANIES = [
    'swiggy', 'zomato', 'cred', 'razorpay', 'ola',
    'flipkart', 'paytm', 'phonepe', 'meesho', 'groww',
    'zerodha', 'dream11', 'byju', 'unacademy',
    'pied piper', 'hooli', 'stark industries',
]

# ============================================================================
# HONEYPOT DETECTION THRESHOLDS
# ============================================================================
HONEYPOT_EXPERT_ZERO_DURATION_MIN = 2
HONEYPOT_EXPERIENCE_SKILL_RATIO = 3

# ============================================================================
# KEYWORD STUFFING THRESHOLDS
# ============================================================================
STUFFING_HIGH_SKILL_COUNT = 22
STUFFING_EXPERT_RATIO = 0.60
STUFFING_TITLE_SKILL_MISMATCH = 8

AI_ML_SKILL_KEYWORDS = [
    'machine learning', 'deep learning', 'nlp', 'natural language processing',
    'computer vision', 'pytorch', 'tensorflow', 'scikit-learn',
    'neural network', 'reinforcement learning', 'gans', 'cnn', 'rnn',
    'lstm', 'transformer', 'bert', 'gpt', 'llm', 'rag',
    'embeddings', 'vector', 'faiss', 'pinecone', 'weaviate', 'qdrant',
    'milvus', 'recommendation', 'ranking', 'retrieval',
    'fine-tuning', 'fine tuning', 'lora', 'qlora', 'peft',
    'hugging face', 'openai', 'langchain', 'llamaindex',
    'sentiment analysis', 'text classification', 'named entity',
    'object detection', 'image classification', 'speech recognition',
    'tts', 'asr', 'mlops', 'kubeflow', 'mlflow',
    'feature engineering', 'model serving', 'bentoml',
    'weights & biases', 'wandb', 'experiment tracking',
    'xgboost', 'lightgbm', 'catboost', 'random forest',
    'statistical modeling', 'bayesian', 'a/b testing',
    'opencv', 'yolo', 'prompt engineering',
    'opensearch', 'elasticsearch', 'bm25',
    'data pipelines', 'spark', 'hadoop', 'airflow',
    'python', 'r programming',
]
