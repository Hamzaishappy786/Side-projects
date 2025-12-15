import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# --- CONFIGURATION ---
# Just add 'r' before the string
MODEL_PATH = r"C:\Users\gamer\PycharmProjects\Side-projects\Generative AI\12. Docstring Function working\Training\Output\my_docstringer_model"

print(f"⏳ Loading DocStringer from '{MODEL_PATH}'...")

# 1. Load Model & Tokenizer
# Force CPU usage to avoid DLL errors on Windows
device = "cpu"
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH).to(device)
    print("✅ Model loaded! Ready to document code.")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("Did you extract the zip file correctly?")
    exit()


def document_code(raw_code):
    """
    Takes raw code and uses the AI to rewrite it with docstrings.
    """
    # 1. Add the prefix we used during training
    input_text = "Generate Python Docstring: " + raw_code

    # 2. Tokenize
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True).to(device)

    # 3. Generate
    # We use 'beam search' to make the AI think harder (better quality)
    outputs = model.generate(
        inputs["input_ids"],
        max_length=512,
        num_beams=4,
        early_stopping=True
    )

    # 4. Decode
    documented_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return documented_code


# --- INTERACTIVE LOOP ---
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print(" 🐍 DocStringer: Automatic Code Documentation ")
    print("=" * 50)
    print("Paste a Python function below (Press Enter twice to submit).")
    print("Type 'exit' to quit.\n")

    while True:
        print("\n👇 Paste Function Here:")
        lines = []
        while True:
            line = input()
            if line == "": break
            lines.append(line)

        raw_code = "\n".join(lines)

        if raw_code.strip().lower() == "exit":
            break

        if not raw_code.strip():
            continue

        print("\nThinking...", end="", flush=True)
        try:
            result = document_code(raw_code)

            print("\r" + " " * 20 + "\r", end="")  # Clear 'Thinking...'
            print("✨ DOCUMENTED CODE:\n")
            print("-" * 40)
            print(result)
            print("-" * 40)

        except Exception as e:
            print(f"\n❌ Error: {e}")