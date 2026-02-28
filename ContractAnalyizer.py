import pymupdf
import ollama
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
import argparse
import os


console = Console()

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file using PyMuPDF. Returns the extracted text as a string. """
    
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def run_checklist(contract_text: str, checklist: list) -> dict:
    """Runs a checklist of questions against the contract text and returns the results as a dictionary. """
    prompt = (
        "Analyze this contract for risks in these areas: termination, liability cap, "
        "IP ownership, jurisdiction. Output ONLY valid JSON like:\n"
        '{"termination": "summary (risk: low/medium/high)", '
        '"liability_cap": "summary (risk: low/medium/high)", '
        '"ip_ownership": "summary (risk: low/medium/high)", '
        '"jurisdiction": "summary (risk: low/medium/high)"}.\n\n"'
        f"CONTRACT:\n{contract_text}"
    )
    response = ollama.chat(
        model="gemma3:4b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes contracts and identifies risks in specific areas."},
            {"role": "user", "content": prompt}
        ]
    )
    
    import json
    try:
        result = json.loads(response['message']['content'])
        return result
    except json.JSONDecodeError:
        console.print("Failed to parse JSON response from the model. Here's the raw response:")
        console.print(response['message']['content'])
        return {}

def ask_about_contract(contract_text: str, question: str) -> str:
    """Returns an answer to a question about the contract text using the Ollama API. """
    response = ollama.chat(
        model="gemma3:4b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes contracts and provides clear answers to questions about the contract."},
            {"role": "user", "content": f"Here is the contract text:\n\n{contract_text}\n\nNow, please answer the following question about the contract:\n\n{question}"}
        ]
    )
    return response['message']['content']

def print_risk_summary(risk_summary: dict):
    """Prints a summary of risks in a nice table format using Rich. """
    table = Table(title="Contract Risk Summary")
    table.add_column("Risk Area", style="cyan", no_wrap=True)
    table.add_column("Summary", style="magenta")
    table.add_column("Risk Level", style="red")
    
    for area, summary in risk_summary.items():
        table.add_row(area.capitalize(), summary)
    
    console.print(table)
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze contract PDF")
    parser.add_argument("path", nargs="?", help="Path to contract PDF")
    parser.add_argument("--checklist", action="store_true", help="Run standard checklist automatically")
    args = parser.parse_args()
    
    if not args.path:
        path = Prompt.ask("Enter the path to the contract PDF")
    else:
        path = args.path
    
    if not os.path.isfile(path):
        console.print(f"File not found: {path}")
        exit(1)
        
    console.print(f"Extracting text from {path}...")
    contract_text = extract_text_from_pdf(path)
    console.print("Text extracted successfully. Now you can ask questions about the contract.")
    
    if args.checklist:
        console.print("Running standard checklist...")
        checklist = ["termination", "liability cap", "IP ownership", "jurisdiction"]
        risk_summary = run_checklist(contract_text, checklist)
        print_risk_summary(risk_summary)
        
    while True:
        question = Prompt.ask("Enter your question about the contract (or type 'exit' to quit)")
        if question.lower() == 'exit':
            console.print("Exiting the contract analyzer. Goodbye!")
            break
        answer = ask_about_contract(contract_text, question)
        console.print(f"Answer: {answer}\n")