import pandas as pd
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from llm_client import LLMClient

class HRTools:
    """Tools for the HR Agent"""
    
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
    
    def read_input_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Read the input CSV file and return unprocessed rows."""
        try:
            df = pd.read_csv(file_path)
            
            if 'is_processed' not in df.columns:
                df['is_processed'] = False
            
            rows = df.to_dict('records')
            unprocessed = [row for row in rows if str(row.get('is_processed', '')).upper() != 'TRUE']
            
            return unprocessed
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return []
        except Exception as e:
            print(f"❌ Error reading input CSV: {e}")
            return []
    
    def read_results_csv(self, file_path: str) -> pd.DataFrame:
        """Read the results CSV file"""
        try:
            if os.path.exists(file_path):
                return pd.read_csv(file_path)
            else:
                return pd.DataFrame(columns=[
                    'Job ID', 'Position Title', 'Candidate Name', 
                    'Match Score', 'CV Summary', 'Strengths', 
                    'Weaknesses', 'Call Applicant', 'Decision', 
                    'Reasoning', 'Processed Date'
                ])
        except Exception as e:
            print(f"❌ Error reading results CSV: {e}")
            return pd.DataFrame()
    
    def update_results_csv(self, results_file: str, row_data: Dict[str, Any]) -> bool:
        """Update the results CSV with the analysis results."""
        try:
            results_df = self.read_results_csv(results_file)
            
            new_row = {
                'Job ID': row_data.get('job_id', 'Unknown'),
                'Position Title': row_data.get('position_title', 'Unknown'),
                'Candidate Name': row_data.get('candidate_name', 'Unknown'),
                'Match Score': row_data.get('match_score', 0),
                'CV Summary': row_data.get('cv_summary', ''),
                'Strengths': row_data.get('strengths', ''),
                'Weaknesses': row_data.get('weaknesses', ''),
                'Call Applicant': row_data.get('call_applicant', False),
                'Decision': row_data.get('decision', 'REJECT'),
                'Reasoning': row_data.get('reasoning', ''),
                'Processed Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            results_df = pd.concat([results_df, pd.DataFrame([new_row])], ignore_index=True)
            results_df.to_csv(results_file, index=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating results CSV: {e}")
            return False
    
    def mark_row_processed(self, input_file: str, job_id: str) -> bool:
        """Mark a row as processed in the input CSV."""
        try:
            df = pd.read_csv(input_file)
            
            mask = df['Job ID'] == job_id
            if mask.any():
                df.loc[mask, 'is_processed'] = True
                df.to_csv(input_file, index=False)
                return True
            else:
                print(f"⚠️ Job ID '{job_id}' not found in input file")
                return False
                
        except Exception as e:
            print(f"❌ Error marking row as processed: {e}")
            return False
    
    def analyze_cv(self, job_id: str, position_title: str,
                   position_description: str, candidate_name: str,
                   cv_content: str) -> Optional[Dict[str, Any]]:
        """Analyze the CV using the LLM client"""
        return self.llm_client.analyze_cv(
            job_id, position_title, position_description,
            candidate_name, cv_content
        )