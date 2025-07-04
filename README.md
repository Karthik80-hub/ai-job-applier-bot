# AI Job Application Assistant

An intelligent job application automation system that helps streamline your job search process using AI and automation. This tool helps you find, analyze, and apply to jobs that match your profile automatically.

## System Overview

The system operates through a sophisticated pipeline that combines AI-powered analysis, automated job discovery, and intelligent application submission:

1. **Resume Analysis & Role Inference**
   - Extracts and analyzes resume content using GPT-4
   - Infers suitable job roles based on experience and skills
   - Processes both PDF and DOCX formats with OCR support
   - Identifies key skills and qualifications

2. **Intelligent Job Discovery**
   - Multi-platform job scraping (Greenhouse, Workday, Lever, iCIMS, custom)
   - Company career page discovery using Google Custom Search
   - Dynamic job board parsing with fallback mechanisms
   - Configurable job sources via YAML configuration

3. **ATS-Optimized Matching**
   - Advanced ATS scoring system (keyword + semantic matching)
   - Skills extraction and matching
   - Role suitability scoring
   - Missing skills identification and suggestions

4. **Automated Application Process**
   - Intelligent form filling using Playwright
   - Custom resume tailoring for each application
   - Cover letter generation using GPT-4
   - Application status tracking and notifications

5. **User Interface & Control**
   - Gradio-based web interface
   - Real-time application dashboard
   - Job matching visualization
   - Application status monitoring

## Tech Stack

### Backend Technologies
- **Python 3.9+**: Core programming language
- **FastAPI**: High-performance API framework
- **PostgreSQL**: Database for application tracking
- **Redis**: Caching and job queue management
- **Playwright**: Web automation and form filling
- **PyMuPDF (fitz)**: PDF processing and text extraction
- **python-docx**: DOCX file handling
- **pytesseract**: OCR for image-based resumes
- **BeautifulSoup4**: Web scraping and parsing
- **Requests**: HTTP client for API interactions

### AI & Machine Learning
- **OpenAI GPT-4**: 
  - Role inference
  - Resume analysis
  - Cover letter generation
  - Job matching
- **LangChain**: LLM orchestration and prompt management
- **Custom ATS Scoring System**:
  - Keyword matching
  - Semantic similarity
  - Skills extraction

### Frontend & Interface
- **Gradio**: Web interface and dashboard
- **HTML/CSS/JavaScript**: Custom UI components
- **Chart.js**: Data visualization
- **TailwindCSS**: Styling (if custom frontend is added)

### APIs & External Services
- **OpenAI API**: GPT-4 access
- **Google Custom Search API**: Company discovery
- **SMTP**: Email notifications
- **Various Job Board APIs**:
  - Greenhouse
  - Workday
  - Lever
  - iCIMS

### Development & Testing
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking
- **Git**: Version control
- **Docker**: Containerization (optional)

### Data Storage & Management
- **PostgreSQL**: Application tracking database
- **JSON**: Configuration and job data
- **YAML**: Job sources and criteria
- **CSV**: Application history export

### Security & Authentication
- **Environment Variables**: Secure configuration
- **API Key Management**: Secure API access
- **Database Encryption**: Secure data storage
- **HTTPS**: Secure communication

### Monitoring & Logging
- **Python Logging**: Application logging
- **Custom Dashboard**: Application tracking
- **Email Notifications**: Status updates
- **CSV Exports**: Application history

## Technical Architecture

### Core Components

1. **LLM Modules** (`llm_modules/`)
   - `role_inference.py`: Job role extraction from resume
   - `resume_matcher.py`: ATS scoring and job matching
   - `resume_tailor.py`: Custom resume generation
   - `ats_matcher.py`: Advanced ATS scoring system

2. **Scraping Engine** (`scrapers/`)
   - `universal_scraper.py`: Unified job scraping interface
   - `company_discovery.py`: Career page discovery
   - Platform-specific scrapers:
     - `greenhouse_scraper.py`
     - `workday_scraper.py`
     - `lever_scraper.py`
     - `icims_scraper.py`
     - `custom_scraper.py` (fallback)

3. **Application Engine** (`application_engine/`)
   - `form_filler.py`: Automated form submission
   - `job_status_service.py`: Application tracking
   - `user_profile_service.py`: User data management

4. **Web Interface** (`frontend/`)
   - Gradio-based dashboard
   - Job matching visualization
   - Application status monitoring
   - Resume upload and analysis

5. **Core Services** (`core/`)
   - `job_controller.py`: Pipeline orchestration
   - `pipeline_controller.py`: Main application flow
   - Configuration management

### Data Flow

1. Resume Upload → Role Inference
2. Role Inference → Company Discovery
3. Company Discovery → Job Scraping
4. Job Scraping → ATS Matching
5. ATS Matching → Resume Tailoring
6. Resume Tailoring → Application Submission
7. Application Submission → Status Tracking

## Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Google Custom Search API key (for company discovery)
- Modern web browser
- Internet connection
- PDF/DOCX resume file
- PostgreSQL database (for application tracking)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Karthik80-hub/ai-job-applier-bot.git
   cd ai-job-applier-bot
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix/MacOS
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_api_key_here
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_custom_search_engine_id
   RESUME_PATH=path/to/your/resume.pdf
   DATABASE_URL=postgresql://user:password@localhost:5432/jobbot
   EMAIL_SENDER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_specific_password
   EMAIL_RECEIVER=your_email@gmail.com
   ```

5. **Initialize the database**:
   ```bash
   python -c "from application_engine.job_status_service import init_db; init_db()"
   ```

## Usage

1. **Start the Application**:
   ```bash
   python gradio_app.py
   ```

2. **Access the Web Interface**:
   - Open your browser and navigate to http://localhost:7860
   - Upload your resume
   - Configure job preferences
   - Start the application process

3. **Monitor Applications**:
   - View application status in the dashboard
   - Track successful and failed applications
   - Export application history
   - Receive email notifications

## Configuration

### Job Sources
Edit `configs/job_sources.yaml` to add or modify job sources:
```yaml
sources:
  - name: Company Name
    platform: platform_type
    url: career_page_url
```

### Application Criteria
Configure job matching criteria in `configs/criteria.yaml`:
```yaml
titles:
  - "Software Engineer"
  - "Full Stack Developer"
locations:
  - "Remote"
  - "New York"
exclude:
  titles: ["Intern", "Junior"]
  companies: ["Startup Inc"]
  keywords: ["contract", "temporary"]
```

## Features in Detail

### Resume Analysis
- Extracts text from PDF/DOCX with OCR support
- Identifies skills, experience, and qualifications
- Uses GPT-4 for role inference
- Generates ATS-optimized content

### Job Discovery
- Supports multiple job board platforms
- Intelligent career page discovery
- Custom scraping for unique job sites
- Configurable job source management

### Application Automation
- Smart form filling with Playwright
- Custom resume generation per application
- Cover letter generation using GPT-4
- Application status tracking
- Email notifications

### Monitoring & Analytics
- Real-time application dashboard
- Success/failure tracking
- Application history export
- Performance analytics

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is designed to assist with job applications and should be used responsibly. Always review generated content before submission and ensure compliance with job platform terms of service.

## Acknowledgments

- OpenAI for providing the GPT-4 API
- The open-source community for various libraries and tools used in this project
- Contributors and users who have provided feedback and improvements

---
*Last updated: Test MCP server functionality*
