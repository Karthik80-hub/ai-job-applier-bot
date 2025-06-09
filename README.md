# AI Job Application Assistant

An intelligent job application automation system that helps streamline your job search process.

## Features

- Job scraping from multiple platforms
- Resume analysis and optimization
- Cover letter generation
- Application tracking
- AI-powered job matching

## Tech Stack

### Frontend
- Next.js 14
- TypeScript
- TailwindCSS
- Shadcn/ui
- React Query
- Zustand

### Backend
- NestJS
- PostgreSQL
- Redis
- OpenAI
- LangChain

## Prerequisites

- Node.js >= 20.10.0
- npm >= 10.2.3
- PostgreSQL >= 16
- Redis >= 7

## Getting Started

1. Clone the repository:
   ```bash
   git clone [your-repo-url]
   cd ai-job-applier-bot
   ```

2. Install dependencies:
   ```bash
   # Install root dependencies
   npm install

   # Install frontend dependencies
   cd frontend
   npm install

   # Install backend dependencies
   cd ../backend
   npm install
   ```

3. Set up environment variables:
   ```bash
   # Frontend (.env.local)
   NEXT_PUBLIC_API_URL=http://localhost:4000
   NEXT_PUBLIC_ANALYTICS_ENABLED=false

   # Backend (.env)
   PORT=4000
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/jobbot
   REDIS_URL=redis://localhost:6379
   OPENAI_API_KEY=your-api-key
   JWT_SECRET=your-secret-key
   ```

4. Start the development servers:
   ```bash
   # Start both frontend and backend
   npm run dev

   # Or start them separately:
   npm run dev:frontend
   npm run dev:backend
   ```

5. Open your browser and navigate to:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:4000

## Development

### Project Structure

```
├── frontend/                  # Next.js Frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── lib/             # Utility functions
│   │   ├── styles/          # Global styles
│   │   └── types/           # TypeScript types
│   └── public/              # Static files
│
├── backend/                  # NestJS Backend
│   ├── src/
│   │   ├── modules/         # Feature modules
│   │   ├── common/          # Shared code
│   │   └── config/          # Configuration
│   └── test/                # Test files
│
└── shared/                  # Shared code
    ├── types/               # Shared types
    └── constants/           # Shared constants
```

### Available Scripts

```bash
# Development
npm run dev          # Start both frontend and backend
npm run dev:frontend # Start frontend only
npm run dev:backend  # Start backend only

# Building
npm run build        # Build both frontend and backend
npm run build:frontend
npm run build:backend

# Testing
npm run test         # Run all tests
npm run test:frontend
npm run test:backend
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Features

- Scrape jobs from multiple sources
- GPT-powered resume matching
- Auto-apply via headless browser
- Daily scheduling and tracking

##  Tech Stack

- Python, Playwright
- OpenAI GPT / LangChain
- FastAPI (optional)
- MongoDB or SQLite
- Docker (optional)

## Setup

Clone the repo and install dependencies:

```bash
git clone https://github.com/Karthik80-hub/ai-job-applier-bot.git
cd ai-job-applier-bot
pip install -r requirements.txt