"""
Multi-provider LLM Client for HR Agent.
Supports OpenAI, Claude, Groq, and Mock providers.
"""

import json
import re
from typing import Dict, Any, Optional
import os

class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    Automatically falls back to mock if no API key is available.
    """
    
    def __init__(self, provider: str = 'groq'):
        self.provider = provider
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize the appropriate client based on provider"""
        if self.provider == 'openai':
            try:
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                else:
                    print("⚠️ OpenAI API key not found. Falling back to mock.")
                    self.provider = 'mock'
                    self.client = None
            except ImportError:
                print("⚠️ OpenAI package not installed. Falling back to mock.")
                self.provider = 'mock'
                self.client = None
                
        elif self.provider == 'claude':
            try:
                import anthropic
                api_key = os.getenv('CLAUDE_API_KEY')
                if api_key:
                    self.client = anthropic.Anthropic(api_key=api_key)
                else:
                    print("⚠️ Claude API key not found. Falling back to mock.")
                    self.provider = 'mock'
                    self.client = None
            except ImportError:
                print("⚠️ Anthropic package not installed. Falling back to mock.")
                self.provider = 'mock'
                self.client = None
                
        elif self.provider == 'groq':
            try:
                from groq import Groq
                api_key = os.getenv('GROQ_API_KEY')
                if api_key:
                    self.client = Groq(api_key=api_key)
                else:
                    print("⚠️ Groq API key not found. Falling back to mock.")
                    self.provider = 'mock'
                    self.client = None
            except ImportError:
                print("⚠️ Groq package not installed. Falling back to mock.")
                self.provider = 'mock'
                self.client = None
                
        else:
            self.provider = 'mock'
            self.client = None
            print("ℹ️ Using Mock LLM provider (no API calls)")
    
    def analyze_cv(self, job_id: str, position_title: str,
                   position_description: str, candidate_name: str,
                   cv_content: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a CV using the configured LLM provider.
        Returns a structured dictionary with the analysis results.
        """
        system_prompt = """You are an expert HR recruiter and talent evaluator.
        Evaluate this candidate for the position and provide a detailed assessment.
        
        Return your response in EXACT JSON format with these fields:
        {
            "matchScore": number between 0-100,
            "cvSummary": "2-3 sentence summary of candidate's background",
            "strengths": "List of top 3 strengths (comma separated)",
            "weaknesses": "List of top 3 areas for improvement (comma separated)",
            "callApplicant": true or false,
            "decision": "HIRE" or "CONSIDER" or "REJECT",
            "reasoning": "Brief explanation of your decision"
        }
        
        Be fair, objective, and thorough in your evaluation. Only return valid JSON, no other text."""
        
        user_prompt = f"""Job ID: {job_id}
Position Title: {position_title}
Position Description: {position_description}

Candidate Name: {candidate_name}
CV Content: {cv_content}

Please evaluate this candidate for the position."""
        
        try:
            if self.provider == 'openai':
                response = self._call_openai(system_prompt, user_prompt)
            elif self.provider == 'claude':
                response = self._call_claude(system_prompt, user_prompt)
            elif self.provider == 'groq':
                response = self._call_groq(system_prompt, user_prompt)
            else:
                response = self._call_mock(job_id, position_title, candidate_name, cv_content)
            
            return self._parse_response(response)
            
        except Exception as e:
            print(f"❌ Error calling LLM: {e}")
            return self._fallback_response()
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content
    
    def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Call Claude API"""
        response = self.client.messages.create(
            model=os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022'),
            max_tokens=800,
            temperature=0.3,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text
    
    def _call_groq(self, system_prompt: str, user_prompt: str) -> str:
        """Call Groq API"""
        response = self.client.chat.completions.create(
            model=os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content
    
    def _call_mock(self, job_id: str, position_title: str,
                   candidate_name: str, cv_content: str) -> str:
        """Mock response for testing without API calls"""
        # Simple heuristic-based mock analysis
        score = 75
        if 'python' in cv_content.lower():
            score += 10
        if 'docker' in cv_content.lower():
            score += 5
        if 'product' in position_title.lower() and 'product' in cv_content.lower():
            score += 10
        if 'data' in position_title.lower() and 'sql' in cv_content.lower():
            score += 10
        
        # Cap at 95
        score = min(score, 95)
        
        decision = 'HIRE' if score >= 80 else 'CONSIDER' if score >= 60 else 'REJECT'
        
        return json.dumps({
            "matchScore": score,
            "cvSummary": f"{candidate_name} has relevant experience for the {position_title} position.",
            "strengths": "Relevant experience, Technical skills, Strong background",
            "weaknesses": "Limited leadership experience, No specific metrics, Lack of domain expertise",
            "callApplicant": decision == 'HIRE',
            "decision": decision,
            "reasoning": f"The candidate matches {score}% of the requirements for this position."
        })
    
    def _parse_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse the LLM response and extract JSON"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                print(f"⚠️ No JSON found in response")
                return None
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            return None
    
    def _fallback_response(self) -> Dict[str, Any]:
        """Fallback response when everything fails"""
        return {
            "matchScore": 50,
            "cvSummary": "Unable to analyze CV due to technical issues.",
            "strengths": "Could not determine",
            "weaknesses": "Could not determine",
            "callApplicant": True,
            "decision": "CONSIDER",
            "reasoning": "Manual review recommended due to analysis error."
        }