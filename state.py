from typing import List, Dict, Any, Optional, TypedDict, Annotated
from operator import add

class AgentState(TypedDict):
    """State for the HR Agent"""
    # Input data
    input_file: str
    results_file: str
    
    # Current row being processed
    current_row: Optional[Dict[str, Any]]
    current_index: int
    
    # All rows to process
    unprocessed_rows: List[Dict[str, Any]]
    
    # Analysis results
    job_id: Optional[str]
    job_title: Optional[str]
    job_description: Optional[str]
    candidate_name: Optional[str]
    cv_content: Optional[str]
    
    # LLM analysis results
    match_score: Optional[int]
    cv_summary: Optional[str]
    strengths: Optional[str]
    weaknesses: Optional[str]
    call_applicant: Optional[bool]
    decision: Optional[str]
    reasoning: Optional[str]
    
    # Control flow
    is_processed: bool
    error: Optional[str]
    messages: Annotated[List[Dict[str, Any]], add]