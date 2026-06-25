#!/usr/bin/env python3
"""
HR CV Analysis Agent with LangGraph
Multi-provider LLM support (OpenAI, Claude, Groq, Mock)

Usage:
    python main.py

This agent reads unprocessed CVs from input.csv,
analyzes them using the configured LLM provider,
and writes results to results.csv.
"""

from agent import HRAgent
from config import Config
import os

def main():
    # Get file paths from config
    input_file = Config.INPUT_FILE
    results_file = Config.RESULTS_FILE
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file '{input_file}' not found!")
        print("Please create the file with the required columns:")
        print("- Job ID, Position Title, Position Description, Candidate Name, CV Content, is_processed")
        print("\nExample:")
        print('JOB001,Software Engineer,"Job description...",John Doe,"CV content...",FALSE')
        return
    
    # Check if provider is configured
    if not Config.is_configured():
        print(f"⚠️ Warning: {Config.LLM_PROVIDER} API key not found.")
        print("Falling back to mock provider for testing.")
        Config.LLM_PROVIDER = 'mock'
    
    # Initialize and run agent
    agent = HRAgent()
    agent.run(input_file, results_file)

if __name__ == "__main__":
    main()