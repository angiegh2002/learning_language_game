import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM 
import os

model_path = "C:/Users/User\Desktop/New folder/لعبة تعليم اللغة/language_app/model/"

if not os.path.exists(model_path):
    raise ValueError(f"المسار {model_path} غير موجود")

tokenizer = AutoTokenizer.from_pretrained(
    model_path,
    local_files_only=True 
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    model_path,
    local_files_only=True  
).to("cpu")

model.eval()

async def generate_description(word: str) -> str:
    input_text = f"صف الكلمة التالية : {word}"
    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    )

    input_ids = inputs["input_ids"].to("cpu")
    attention_mask = inputs["attention_mask"].to("cpu")

    output_ids = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=50,
        num_beams=4,
        no_repeat_ngram_size=3,
        early_stopping=True
    )

    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return output_text
