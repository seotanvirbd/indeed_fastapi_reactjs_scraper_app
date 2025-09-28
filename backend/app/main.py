# backend/app/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import io
import logging
import time
import json
from datetime import datetime
from typing import Dict, Any

from .models import ScrapeRequest, ScrapeResponse
from .scraper_final import IndeedScraper
from .utils import jobs_to_csv, jobs_to_excel, jobs_to_json

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Indeed Job Scraper API", 
    version="2.0.0",
    description="Professional Indeed job scraping service with enhanced logging and error handling"
)

# CORS middleware with enhanced configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for current scrape results
current_jobs_data = []

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"🔄 Request started: {request.method} {request.url}")
    logger.info(f"📡 Client IP: {request.client.host}")
    logger.info(f"🌐 User-Agent: {request.headers.get('user-agent', 'Unknown')}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response details
    logger.info(f"✅ Request completed: {request.method} {request.url}")
    logger.info(f"📊 Status: {response.status_code}")
    logger.info(f"⏱️  Processing time: {process_time:.3f}s")
    logger.info(f"📏 Response size: {response.headers.get('content-length', 'Unknown')} bytes")
    
    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ Validation error for {request.url}: {exc.errors()}")
    return HTTPException(
        status_code=400,
        detail={
            "message": "Request validation failed",
            "errors": exc.errors(),
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"❌ HTTP error for {request.url}: {exc.status_code} - {exc.detail}")
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.get("/")
async def root():
    logger.info("🏠 Root endpoint accessed")
    return {
        "message": "Indeed Job Scraper API is running!",
        "version": "2.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "scrape": "/scrape (POST)",
            "download_csv": "/download/csv (GET)",
            "download_excel": "/download/excel (GET)",
            "download_json": "/download/json (GET)"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    logger.info("🔍 Health check requested")
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "uptime": time.time(),
        "current_jobs_count": len(current_jobs_data),
        "memory_usage": "Available",  # Could add actual memory stats
        "services": {
            "scraper": "operational",
            "file_export": "operational"
        }
    }
    
    logger.info(f"💚 Health check completed: {health_status['status']}")
    return health_status

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_jobs(request: ScrapeRequest):
    """Scrape jobs from Indeed with enhanced logging"""
    global current_jobs_data
    
    logger.info("🎯 Scrape request received")
    logger.info(f"📋 Parameters: job_title='{request.job_title}', location='{request.location}', pages={request.pages}")
    
    # Validate request parameters
    if not request.job_title.strip():
        logger.error("❌ Empty job title provided")
        raise HTTPException(status_code=400, detail="Job title cannot be empty")
    
    if request.pages < 1 or request.pages > 10:
        logger.error(f"❌ Invalid pages parameter: {request.pages}")
        raise HTTPException(status_code=400, detail="Pages must be between 1 and 10")
    
    logger.info("✅ Request parameters validated")
    
    start_time = time.time()
    
    try:
        logger.info("🤖 Initializing Indeed scraper...")
        scraper = IndeedScraper()
        
        logger.info("🚀 Starting scraping process...")
        result = scraper.scrape_jobs(
            job_title=request.job_title,
            location=request.location,
            max_pages=request.pages
        )
        
        scraping_duration = time.time() - start_time
        logger.info(f"⏱️  Scraping completed in {scraping_duration:.2f} seconds")
        
        # Store results globally for download endpoints
        current_jobs_data = result["jobs"]
        
        logger.info(f"✅ Scraping successful: {len(current_jobs_data)} jobs found")
        logger.info(f"📊 Results: total_jobs={result.get('total_jobs', 0)}, pages_scraped={result.get('pages_scraped', 0)}")
        
        # Add performance metrics to response
        response_data = ScrapeResponse(**result)
        
        return response_data
    
    except Exception as e:
        scraping_duration = time.time() - start_time
        logger.error(f"❌ Scraping failed after {scraping_duration:.2f} seconds")
        logger.error(f"💥 Error details: {str(e)}")
        logger.error(f"🔍 Error type: {type(e).__name__}")
        
        # Clear any partial data
        current_jobs_data = []
        
        raise HTTPException(
            status_code=500, 
            detail={
                "message": f"Scraping failed: {str(e)}",
                "error_type": type(e).__name__,
                "duration": scraping_duration,
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/download/csv")
async def download_csv():
    """Download current jobs data as CSV with enhanced logging"""
    logger.info("📥 CSV download requested")
    
    if not current_jobs_data:
        logger.warning("⚠️  No data available for CSV download")
        raise HTTPException(
            status_code=404, 
            detail="No data available. Please scrape jobs first."
        )
    
    try:
        logger.info(f"🔄 Converting {len(current_jobs_data)} jobs to CSV...")
        csv_content = jobs_to_csv(current_jobs_data)
        
        logger.info(f"✅ CSV generated successfully ({len(csv_content)} characters)")
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=indeed-jobs.csv"}
        )
        
    except Exception as e:
        logger.error(f"❌ CSV generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV generation failed: {str(e)}")

@app.get("/download/excel")
async def download_excel():
    """Download current jobs data as Excel with enhanced logging"""
    logger.info("📥 Excel download requested")
    
    if not current_jobs_data:
        logger.warning("⚠️  No data available for Excel download")
        raise HTTPException(
            status_code=404, 
            detail="No data available. Please scrape jobs first."
        )
    
    try:
        logger.info(f"🔄 Converting {len(current_jobs_data)} jobs to Excel...")
        excel_content = jobs_to_excel(current_jobs_data)
        
        logger.info(f"✅ Excel generated successfully ({len(excel_content)} bytes)")
        
        return StreamingResponse(
            io.BytesIO(excel_content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=indeed-jobs.xlsx"}
        )
        
    except Exception as e:
        logger.error(f"❌ Excel generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Excel generation failed: {str(e)}")

@app.get("/download/json")
async def download_json():
    """Download current jobs data as JSON with enhanced logging"""
    logger.info("📥 JSON download requested")
    
    if not current_jobs_data:
        logger.warning("⚠️  No data available for JSON download")
        raise HTTPException(
            status_code=404, 
            detail="No data available. Please scrape jobs first."
        )
    
    try:
        logger.info(f"🔄 Converting {len(current_jobs_data)} jobs to JSON...")
        json_content = jobs_to_json(current_jobs_data)
        
        logger.info(f"✅ JSON generated successfully ({len(json_content)} characters)")
        
        return StreamingResponse(
            io.StringIO(json_content),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=indeed-jobs.json"}
        )
        
    except Exception as e:
        logger.error(f"❌ JSON generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"JSON generation failed: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get current session statistics"""
    logger.info("📊 Stats requested")
    
    stats = {
        "current_jobs_count": len(current_jobs_data),
        "timestamp": datetime.now().isoformat(),
        "session_info": {
            "has_data": len(current_jobs_data) > 0,
            "last_scrape": "Available" if current_jobs_data else "No data"
        }
    }
    
    if current_jobs_data:
        # Add data analytics
        companies = {}
        locations = {}
        
        for job in current_jobs_data:
            company = job.get('Company', 'Unknown')
            location = job.get('Location', 'Unknown')
            
            companies[company] = companies.get(company, 0) + 1
            locations[location] = locations.get(location, 0) + 1
        
        stats["analytics"] = {
            "unique_companies": len(companies),
            "unique_locations": len(locations),
            "top_companies": sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_locations": sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    logger.info(f"📈 Stats generated: {stats}")
    return stats

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Indeed Job Scraper API starting up...")
    logger.info("🌐 Server ready to accept connections")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Indeed Job Scraper API shutting down...")
    logger.info("👋 Goodbye!")