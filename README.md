# clinical-ai
Clinical AI - это чат-бот на основе искусственного интеллекта способный анализировать загруженные клинические рекомендации на русском языке, извлекать из них методы лечения и вести диалог с врачом, задавая уточняющие вопросы для подбора оптимальной тактики терапии.

## Лицензия

Данный проект распространяется на условиях **закрытой авторской лицензии**.

Любое использование, копирование, модификация, передача третьим лицам, а также использование
в научных, образовательных, медицинских и коммерческих целях **запрещены без письменного согласия автора**.

См. файл [LICENSE](./LICENSE).

## Промпты 
| Режим                      | Модель        | Назначение                        |
| -------------------------- | ------------- | --------------------------------- |
| `extract_guideline`        | `qwen_3_4b`   | Парсинг клин. рекомендаций        |
| `extract_patient_facts`    | `qwen_3_4b`   | Извлечение фактов из реплик врача |
| `ask_clarifying_questions` | `gemma_3_27b` | Уточняющие вопросы                |
| `final_decision`           | `gemma_3_27b` | Тактика лечения                   |

## Файловая структура 
```
├── README.md
├── backend
│   ├── Dockerfile
│   └── app
│       ├── api
│       │   ├── chat.py
│       │   ├── health.py
│       │   └── upload.py
│       ├── config.py
│       ├── main.py
│       ├── models
│       │   ├── db.py
│       │   └── schemas.py
│       ├── prompts
│       │   ├── ask_clarifying_questions.txt
│       │   ├── extract_guideline.txt
│       │   ├── extract_patient_facts.txt
│       │   └── final_decision.txt
│       ├── services
│       │   ├── dialogue.py
│       │   ├── extractor.py
│       │   ├── llm_client.py
│       │   ├── parser.py
│       │   └── retriever.py
│       └── storage
│           └── faiss
├── docker-compose.yml
├── frontend
│   ├── Dockerfile
│   ├── package.json
│   └── src
│       ├── App.jsx
│       ├── api.js
│       └── pages
│           └── Chat.jsx
└── nginx
    └── nginx.conf
```