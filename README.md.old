# AutoPublisherAI

**AutoPublisherAI** is a next-generation content orchestration platform designed to automate the entire content lifecycle. From intelligent, SEO-optimized article generation to multi-platform publishing, this project aims to provide a seamless, powerful, and scalable solution for content creators and businesses.

## 🚀 Core Features

- **AI-Powered Content Generation:** Leverages advanced language models (like GPT-4) to create high-quality, relevant, and SEO-friendly articles.
- **Intelligent SEO Analysis:** Analyzes top search results to build a content structure that is engineered to rank.
- **Multi-Platform Publishing:** A plugin-based architecture for publishing content across various platforms, starting with WordPress and Instagram.
- **Modular & Scalable:** Built on a microservices architecture to ensure scalability, maintainability, and easy extension to new platforms (Facebook, X, LinkedIn, etc.).

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, FastAPI
- **Architecture:** Microservices
- **Containerization:** Docker, Docker Compose
- **Task Queue:** Celery, Redis
- **Database:** PostgreSQL
- **AI:** OpenAI API (GPT-4, DALL-E 3)

## 📁 Project Structure

```
AutoPublisherAI/
├── services/
│   ├── content-service/      # AI content generation service
│   ├── publishing-service/   # Multi-platform publishing service
│   └── orchestrator-service/ # Workflow coordination service
├── docker-compose.yml         # Service orchestration
└── README.md
```

## 🏗️ Architecture

The project follows a **microservices architecture** where each service is:
- **Independent:** Can be developed, tested, and deployed separately
- **Containerized:** Runs in its own Docker container
- **Scalable:** Can be scaled horizontally based on demand
- **Communicates via REST APIs:** Clean, well-defined interfaces

### Services Overview

1. **Content Service** (`content-service`)
   - Topic analysis and keyword research
   - SEO-optimized article generation
   - AI-powered image creation
   - Structured content formatting

2. **Publishing Service** (`publishing-service`)
   - Plugin-based architecture for multiple platforms
   - WordPress integration
   - Instagram integration
   - Extensible for Facebook, X, LinkedIn, etc.

3. **Orchestrator Service** (`orchestrator-service`)
   - Workflow management
   - Task scheduling and queuing
   - Service coordination
   - Status tracking and logging

## 🚦 Getting Started

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key
- (Optional) WordPress site with REST API access
- (Optional) Instagram Business Account

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Qsweet/AutoPublisherAI.git
   cd AutoPublisherAI
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start the services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the services:**
   - Content Service: http://localhost:8001
   - Publishing Service: http://localhost:8002
   - Orchestrator Service: http://localhost:8003

## 🔐 Environment Variables

See `.env.example` for all required environment variables.

## 📚 Documentation

Detailed documentation for each service can be found in their respective directories:
- [Content Service Documentation](./services/content-service/README.md)
- [Publishing Service Documentation](./services/publishing-service/README.md)
- [Orchestrator Service Documentation](./services/orchestrator-service/README.md)

## 🧪 Testing

```bash
# Run tests for all services
docker-compose run content-service pytest
docker-compose run publishing-service pytest
docker-compose run orchestrator-service pytest
```

## 🛣️ Roadmap

- [x] Project architecture design
- [x] Content service foundation
- [ ] WordPress publishing integration
- [ ] Instagram publishing integration
- [ ] Web dashboard UI
- [ ] Facebook integration
- [ ] X (Twitter) integration
- [ ] LinkedIn integration
- [ ] Advanced analytics
- [ ] Multi-language support

## 📄 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

This is a commercial project. For collaboration inquiries, please contact the project owner.

---

**Built with ❤️ for content creators who demand excellence.**

