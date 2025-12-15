import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# --- CONFIGURATION ---
# The folder where you extracted your model
MODEL_PATH = "my_professionalizer_model"

print(f"⏳ Loading Professionalizer from '{MODEL_PATH}'...")

# 1. Force CPU execution
# (This avoids the "WinError 1114" DLL crash you faced earlier)
device = "cpu"
print(f"   Using device: {device.upper()}")

try:
    # Load the Tokenizer and Model
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH).to(device)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"\n❌ Error: Could not load the model.")
    print(f"   Make sure the folder '{MODEL_PATH}' exists and contains 'config.json'.")
    print(f"   Details: {e}")
    exit()

def professionalize_text(text):
    """
    Takes rude/informal text and makes it professional.
    """
    # 1. Tokenize Input
    # No prefix needed because we trained it directly on instructions or raw text
    inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True).to(device)
    
    # 2. Generate Output
    # We use a bit of 'temperature' to make it sound natural, not robotic
    output_ids = model.generate(
        inputs["input_ids"],
        max_length=128,
        num_beams=4,          # Tries 4 different phrasings to find the best one
        early_stopping=True,
        temperature=0.7,      # Creativity level (0.0 = Robot, 1.0 = Wild)
    )
    
    # 3. Decode back to text
    corrected_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return corrected_text

# --- MAIN LOOP ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print(" 👔 THE PROFESSIONALIZER (OFFLINE) ")
    print("="*50)
    print("Type your rude/casual message below.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("\n📝 Your Input: ")
        
        if user_input.lower().strip() in ['exit', 'quit']:
            print("Goodbye! 👋")
            break
        
        if not user_input.strip():
            continue

        print("Thinking...", end="", flush=True)
        
        try:
            result = professionalize_text(user_input)
            
            print("\r" + " " * 20 + "\r", end="") # Clear 'Thinking...'
            print("-" * 40)
            print(f"✨ Professional: {result}")
            print("-" * 40)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")