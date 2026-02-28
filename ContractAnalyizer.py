import pymupdf
import ollama
from rich.console import Console
from rich.prompt import Prompt


console = Console()

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def ask_about_contract(contract_text: str, question: str) -> str:
    response = ollama.chat(
        model="gemma3:4b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes contracts and provides clear answers to questions about the contract."},
            {"role": "user", "content": f"Here is the contract text:\n\n{contract_text}\n\nNow, please answer the following question about the contract:\n\n{question}"}
        ]
    )
    return response['choices'][0]['message']['content']


if __name__ == "__main__":
    path = Prompt.ask("Enter the path to the contract PDF")
    console.print(f"Extracting text from {path}...")
    contract_text = extract_text_from_pdf(path)
    console.print("Text extracted successfully. Now you can ask questions about the contract.")
    
    while True:
        question = Prompt.ask("Enter your question about the contract (or type 'exit' to quit)")
        if question.lower() == 'exit':
            console.print("Exiting the contract analyzer. Goodbye!")
            break
        answer = ask_about_contract(contract_text, question)
        console.print(f"Answer: {answer}\n")