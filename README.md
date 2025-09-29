# 🎯 Indeed Job Scraper | Full-Stack Web Scraping Application with React, FastAPI & SeleniumBase

> Professional job listing aggregator built with Python FastAPI, React.js, and advanced web scraping techniques. Features real-time data extraction, anti-bot bypass using SeleniumBase CDP mode, RESTful API architecture, and multi-format data export (CSV, Excel, JSON).

![Professional Edition](https://img.shields.io/badge/Edition-Professional-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![React](https://img.shields.io/badge/React-18+-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

Indeed Job Scraper is a full-stack application that automates the process of collecting job listings from Indeed.com. Built with modern technologies and designed with a focus on usability, it bypasses anti-bot systems using SeleniumBase CDP mode and provides comprehensive analytics on scraped data.

### Why This Project?

- **Efficient Job Search**: Aggregate job listings quickly without manually browsing through pages
- **Data Export**: Export results in CSV, Excel, or JSON formats for further analysis
- **Real-time Analytics**: Get instant insights on companies, locations, and job distribution
- **Anti-Bot Bypass**: Utilizes SeleniumBase CDP mode to reliably scrape data

---

## ✨ Features

### Core Functionality
- 🔍 **Smart Job Scraping** - Search by job title and location with customizable page depth
- 🤖 **Anti-Bot Protection Bypass** - Uses SeleniumBase CDP mode for reliable scraping
- 📊 **Real-time Analytics** - Instant statistics on scraped results
- 🌐 **Remote Jobs Support** - Filter and search for remote positions
- ✅ **Link Validation** - Ensures 100% valid job listing URLs

### Data & Export
- 📥 **Multiple Export Formats**
  - CSV (Excel Compatible)
  - Native Excel Format (.xlsx)
  - JSON (Developer Friendly)
- 🔢 **Comprehensive Data Points**
  - Job Title
  - Company Name
  - Location
  - Job URL
  - Posting Date (if available)

### User Experience
- 🎨 **Modern, Responsive UI** - Clean interface built with React
- 🔎 **Advanced Filtering** - Filter jobs by title, company, or location
- 📈 **Top Companies Display** - See which companies are hiring most
- 🌍 **Location Insights** - View unique locations with job counts

---

## 📸 Screenshots

### Main Search Interface
![Job Scraper Interface](https://github.com/seotanvirbd/indeed_fastapi_reactjs_scraper_app/blob/main/indded_fastapi-react_app.png)
*Clean, intuitive search form with job title, location, and page depth controls*

### Results Dashboard
![Scraped Results](https://github.com/seotanvirbd/indeed_fastapi_reactjs_scraper_app/blob/main/table.png)
*Comprehensive results table with real-time analytics and filtering capabilities*

### Export Options
![Download Results](https://github.com/seotanvirbd/indeed_fastapi_reactjs_scraper_app/blob/main/download_button.png)
*Multiple export formats for seamless data integration*

---

## 🛠 Tech Stack

### Backend
- **Python 3.8+** - Core programming language
- **FastAPI** - Modern, fast web framework for building APIs
- **SeleniumBase** - Web automation and scraping with CDP mode
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - Lightning-fast ASGI server

### Frontend
- **React.js 18+** - UI library for building interactive interfaces
- **Axios** - Promise-based HTTP client
- **Modern CSS3** - Responsive styling with flexbox and grid
- **Component Architecture** - Modular, reusable components

### Browser Automation
- **Chrome DevTools Protocol (CDP)** - Direct browser control
- **Undetected Mode** - Bypasses anti-bot detection systems

---

## 🏗 Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  React Frontend │◄───────►│  FastAPI Backend │◄───────►│  Indeed.com     │
│                 │  HTTP   │                  │  CDP    │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
        │                            │
        │                            │
        ▼                            ▼
   User Interface            SeleniumBase Scraper
   - Search Form             - Browser Automation
   - Results Table           - Data Extraction
   - Export Tools            - Anti-Bot Bypass
```

### Data Flow

1. **User Input** → User enters search criteria in React frontend
2. **API Request** → Frontend sends POST request to FastAPI backend
3. **Scraping Process** → Backend initiates SeleniumBase scraper with CDP mode
4. **Data Extraction** → Scraper navigates Indeed, extracts job listings
5. **Processing** → Backend validates and structures data
6. **Response** → JSON data sent back to frontend
7. **Display** → React components render results with analytics
8. **Export** → User can download in preferred format

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14+ and npm
- Chrome/Chromium browser
- Git

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/indeed-scraper.git
cd indeed-scraper

# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install
```

---

## 🚀 Usage

### Starting the Application

#### 1. Start Backend Server

```bash
cd backend
python run.py
```

The API server will start at `http://localhost:8000`

#### 2. Start Frontend Development Server

```bash
cd frontend
npm start
```

The React app will open at `http://localhost:3000`

### Using the Scraper

1. **Enter Job Title** - Specify the position you're looking for (e.g., "Software Engineer", "Data Analyst")
2. **Set Location** - Enter a city, state, or "Remote" for remote positions
3. **Choose Pages** - Select how many Indeed result pages to scrape (1-10 recommended)
4. **Start Scraping** - Click "START SCRAPING" button
5. **View Results** - See results with analytics in real-time
6. **Filter & Search** - Use the search bar to filter results
7. **Export Data** - Download in your preferred format (CSV, Excel, JSON)

### Example Searches

```
Job Title: "Frontend Developer"
Location: "Remote"
Pages: 3

Job Title: "Marketing Manager"
Location: "New York, NY"
Pages: 5

Job Title: "Data Scientist"
Location: "San Francisco, CA"
Pages: 2
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### POST `/scrape`
Scrape job listings from Indeed.com

**Request Body:**
```json
{
  "job_title": "Software Engineer",
  "location": "Remote",
  "pages": 3
}
```

**Response:**
```json
{
  "jobs": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "Remote in San Francisco, CA",
      "url": "https://www.indeed.com/viewjob?jk=..."
    }
  ],
  "total": 15,
  "unique_companies": 12,
  "unique_locations": 8
}
```

#### GET `/health`
Check API health status

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-29T10:30:00Z"
}
```

### Interactive API Documentation

FastAPI provides automatic interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 📁 Project Structure

```
indeed-scraper/
├── backend/                      # Python FastAPI server
│   ├── app/
│   │   ├── __init__.py          # Package initializer
│   │   ├── main.py              # FastAPI app & endpoints
│   │   ├── models.py            # Pydantic data models
│   │   ├── scraper.py           # Indeed scraping logic
│   │   └── utils.py             # Helper functions
│   ├── requirements.txt         # Python dependencies
│   ├── run.py                   # Server startup script
│   └── venv/                    # Virtual environment
│
├── frontend/                     # React.js application
│   ├── public/
│   │   └── index.html           # HTML template
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── JobScraper.js   # Search form
│   │   │   ├── JobTable.js     # Results display
│   │   │   └── DownloadButtons.js # Export functionality
│   │   ├── services/
│   │   │   └── api.js          # API client
│   │   ├── App.js              # Main component
│   │   ├── App.css             # Styles
│   │   ├── index.js            # Entry point
│   │   └── index.css           # Base styles
│   ├── package.json            # Dependencies
│   └── node_modules/           # Installed packages
│
└── README.md                    # Documentation
```

---

## 🔧 Configuration

### Backend Configuration

Edit `backend/app/scraper.py` to customize scraping behavior:

```python
# Scraping settings
MAX_PAGES = 10
TIMEOUT = 30
RETRY_ATTEMPTS = 3

# CDP mode settings
HEADLESS = True
```

### Frontend Configuration

Edit `frontend/src/services/api.js` to change API endpoint:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint rules for JavaScript
- Write descriptive commit messages
- Add comments for complex logic
- Test before submitting PR

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Chrome binary not found"
```bash
# Solution: Install Chrome/Chromium
# Ubuntu/Debian:
sudo apt-get install chromium-browser

# macOS:
brew install --cask google-chrome
```

**Issue**: "Module not found" errors
```bash
# Backend solution:
pip install -r requirements.txt

# Frontend solution:
npm install
```

**Issue**: CORS errors in browser
```bash
# Ensure backend is running and CORS is configured in main.py
# Check FastAPI logs for details
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@seotanvirbd](https://github.com/seotanvirbd)
- LinkedIn: [Mohammad Tanvir](https://www.linkedin.com/in/seotanvirbd/)
- Portfolio: [https://seotanvirbd.com/portfolio/](https://seotanvirbd.com/portfolio/)

---

## 🙏 Acknowledgments

- **SeleniumBase** - For providing robust web automation tools
- **FastAPI** - For the excellent API framework
- **React** - For the powerful UI library
- **Indeed.com** - For providing job listing data

---

## ⚠️ Disclaimer

This tool is for educational and personal use only. Please review Indeed.com's Terms of Service and robots.txt before scraping. Use responsibly and respect rate limits. The authors are not responsible for any misuse of this software.

---

## 🔮 Future Enhancements

- [ ] User authentication and saved searches
- [ ] Email notifications for new job matches
- [ ] Advanced filtering (salary, job type, etc.)
- [ ] Support for multiple job boards
- [ ] Database integration for historical data
- [ ] Machine learning for job recommendations
- [ ] Docker containerization
- [ ] Cloud deployment guides

---

<div align="center">

**Made with ❤️ by Mohammad Tanvir, for developers**

⭐ Star this repo if you find it helpful!

</div>
