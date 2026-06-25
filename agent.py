from typing import Dict, Any, List, Literal
from langgraph.graph import StateGraph, END

from state import AgentState
from tools import HRTools
from llm_client import LLMClient
from config import Config

class HRAgent:
    """LangGraph-based HR CV Analysis Agent"""
    
    def __init__(self):
        print(f"ℹ️ Using LLM Provider: {Config.LLM_PROVIDER}")
        
        self.llm_client = LLMClient(Config.LLM_PROVIDER)
        self.tools = HRTools(self.llm_client)
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        workflow.add_node("load_data", self.load_data)
        workflow.add_node("process_cv", self.process_cv)
        workflow.add_node("analyze_with_llm", self.analyze_with_llm)
        workflow.add_node("update_results", self.update_results)
        workflow.add_node("mark_processed", self.mark_processed)
        
        workflow.set_entry_point("load_data")
        workflow.add_edge("load_data", "process_cv")
        workflow.add_edge("process_cv", "analyze_with_llm")
        workflow.add_edge("analyze_with_llm", "update_results")
        workflow.add_edge("update_results", "mark_processed")
        
        workflow.add_conditional_edges(
            "mark_processed",
            self.should_continue,
            {
                "continue": "process_cv",
                "end": END
            }
        )
        
        return workflow
    
    def load_data(self, state: AgentState) -> AgentState:
        """Load unprocessed rows from input CSV"""
        print("📂 Loading data...")
        
        unprocessed_rows = self.tools.read_input_csv(state['input_file'])
        
        if not unprocessed_rows:
            print("✅ No unprocessed rows found. All done!")
            state['unprocessed_rows'] = []
            state['is_processed'] = True
            return state
        
        print(f"📊 Found {len(unprocessed_rows)} unprocessed rows")
        state['unprocessed_rows'] = unprocessed_rows
        state['current_index'] = 0
        state['is_processed'] = False
        
        return state
    
    def process_cv(self, state: AgentState) -> AgentState:
        """Process the current CV row"""
        print("📄 Processing CV...")
        
        if state['current_index'] >= len(state['unprocessed_rows']):
            state['is_processed'] = True
            return state
        
        current_row = state['unprocessed_rows'][state['current_index']]
        
        state['current_row'] = current_row
        state['job_id'] = current_row.get('Job ID', 'Unknown')
        state['job_title'] = current_row.get('Position Title', 'Unknown')
        state['job_description'] = current_row.get('Position Description', 'N/A')
        state['candidate_name'] = current_row.get('Candidate Name', 'Unknown')
        state['cv_content'] = current_row.get('CV Content', 'No CV provided')
        
        print(f"👤 Processing: {state['candidate_name']} for {state['job_title']}")
        
        return state
    
    def analyze_with_llm(self, state: AgentState) -> AgentState:
        """Analyze the CV using LLM"""
        print("🧠 Analyzing CV with LLM...")
        
        result = self.tools.analyze_cv(
            state['job_id'],
            state['job_title'],
            state['job_description'],
            state['candidate_name'],
            state['cv_content']
        )
        
        if result:
            state['match_score'] = result.get('matchScore', 0)
            state['cv_summary'] = result.get('cvSummary', 'No summary provided')
            state['strengths'] = result.get('strengths', 'Not specified')
            state['weaknesses'] = result.get('weaknesses', 'Not specified')
            state['call_applicant'] = result.get('callApplicant', False)
            state['decision'] = result.get('decision', 'REJECT')
            state['reasoning'] = result.get('reasoning', 'No reasoning provided')
            
            print(f"✅ Analysis complete - Decision: {state['decision']}, Score: {state['match_score']}%")
        else:
            state['error'] = "Failed to analyze CV"
            print("❌ Failed to analyze CV")
            # Use fallback values
            state['match_score'] = 50
            state['cv_summary'] = "Analysis failed, manual review needed"
            state['strengths'] = "Could not determine"
            state['weaknesses'] = "Could not determine"
            state['call_applicant'] = True
            state['decision'] = 'CONSIDER'
            state['reasoning'] = "Technical error during analysis"
        
        return state
    
    def update_results(self, state: AgentState) -> AgentState:
        """Update results CSV"""
        print("💾 Updating results...")
        
        if state['error']:
            return state
        
        row_data = {
            'job_id': state['job_id'],
            'position_title': state['job_title'],
            'candidate_name': state['candidate_name'],
            'match_score': state['match_score'],
            'cv_summary': state['cv_summary'],
            'strengths': state['strengths'],
            'weaknesses': state['weaknesses'],
            'call_applicant': state['call_applicant'],
            'decision': state['decision'],
            'reasoning': state['reasoning']
        }
        
        success = self.tools.update_results_csv(state['results_file'], row_data)
        
        if success:
            print(f"✅ Results updated for {state['candidate_name']}")
        else:
            print(f"❌ Failed to update results for {state['candidate_name']}")
            state['error'] = "Failed to update results"
        
        return state
    
    def mark_processed(self, state: AgentState) -> AgentState:
        """Mark current row as processed in input CSV"""
        print("✅ Marking as processed...")
        
        if state['error']:
            return state
        
        success = self.tools.mark_row_processed(state['input_file'], state['job_id'])
        
        if success:
            print(f"✅ Marked {state['job_id']} as processed")
        else:
            print(f"❌ Failed to mark {state['job_id']} as processed")
            state['error'] = "Failed to mark as processed"
        
        state['current_index'] += 1
        
        return state
    
    def should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """Check if there are more rows to process"""
        if state['current_index'] < len(state['unprocessed_rows']):
            return "continue"
        else:
            print("✅ All rows processed!")
            return "end"
    
    def run(self, input_file: str, results_file: str):
        """Run the agent"""
        print("🚀 Starting HR CV Analysis Agent...")
        print("=" * 50)
        print(f"ℹ️ Using provider: {Config.LLM_PROVIDER}")
        print(f"ℹ️ Input file: {input_file}")
        print(f"ℹ️ Results file: {results_file}")
        print("=" * 50)
        
        initial_state = {
            'input_file': input_file,
            'results_file': results_file,
            'unprocessed_rows': [],
            'current_index': 0,
            'current_row': None,
            'job_id': None,
            'job_title': None,
            'job_description': None,
            'candidate_name': None,
            'cv_content': None,
            'match_score': None,
            'cv_summary': None,
            'strengths': None,
            'weaknesses': None,
            'call_applicant': None,
            'decision': None,
            'reasoning': None,
            'is_processed': False,
            'error': None,
            'messages': []
        }
        
        try:
            final_state = self.app.invoke(initial_state, {"recursion_limit": 500})
            print("=" * 50)
            print("🏁 Agent completed!")
            return final_state
        except Exception as e:
            print(f"❌ Agent failed: {e}")
            return None