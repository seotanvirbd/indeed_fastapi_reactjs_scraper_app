# backend/app/utils.py
import pandas as pd
import json
import io
from typing import List, Dict

def jobs_to_csv(jobs_data: List[Dict]) -> str:
    """Convert jobs data to CSV string"""
    df = pd.DataFrame(jobs_data)
    return df.to_csv(index=False)

def jobs_to_excel(jobs_data: List[Dict]) -> bytes:
    """Convert jobs data to Excel bytes"""
    df = pd.DataFrame(jobs_data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer.getvalue()

def jobs_to_json(jobs_data: List[Dict]) -> str:
    """Convert jobs data to JSON string"""
    return json.dumps(jobs_data, indent=2, ensure_ascii=False)