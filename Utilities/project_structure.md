project/
├── docker-compose.yml
├── .env
├── .env.example
├── requirements.txt
└── src/
    ├── db/
    │   ├── __init__.py
    │   ├── connection.py      # Connection management
    │   ├── migrations/        # Schema files
    │   └── loaders/           # Data loading modules
    ├── models/                # Data models / dataclasses
    ├── utils/
    │   ├── logger.py
    │   └── validators.py
    └── main.py