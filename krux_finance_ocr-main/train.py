import os
import torch
import pytesseract
import pandas as pd
from PIL import Image
from transformers import LayoutLMv3Processor, LayoutLMv3ForSequenceClassification, TrainingArguments, Trainer, default_data_collator
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from data_generator import CLASSES

# Ensure Tesseract is in PATH or set it here if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_ocr(image):
    w, h = image.size
    # Use pytesseract to get words and bounding boxes
    df = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME).dropna()
    df = df[df.text.str.strip().astype(bool)]
    words = df.text.astype(str).tolist()
    boxes = [[max(0,min(1000,int(r['left']/w*1000))), max(0,min(1000,int(r['top']/h*1000))),
              max(0,min(1000,int((r['left']+r['width'])/w*1000))), max(0,min(1000,int((r['top']+r['height'])/h*1000)))]
             for _, r in df.iterrows()]
    if not words: words, boxes = ["empty"], [[0,0,1000,1000]]
    return words, boxes

class DocDataset(Dataset):
    def __init__(self, paths, labels, processor): 
        self.paths = paths
        self.labels = labels
        self.processor = processor

    def __len__(self): return len(self.paths)

    def __getitem__(self, i):
        img = Image.open(self.paths[i]).convert("RGB")
        words, boxes = get_ocr(img)
        enc = self.processor(img, words, boxes=boxes, truncation=True, padding="max_length", max_length=512, return_tensors="pt")
        enc = {k: v.squeeze() for k, v in enc.items()}
        enc['labels'] = torch.tensor(self.labels[i], dtype=torch.long)
        return enc

def train():
    print("🚀 Preparing Data...")
    label2id = {label: i for i, label in enumerate(CLASSES)}
    id2label = {i: label for i, label in enumerate(CLASSES)}
    
    processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)

    all_files, all_labels = [], []
    for c in CLASSES:
        path = f"dataset/{c}"
        if not os.path.exists(path):
            print(f"Warning: Dataset directory {path} not found. Run data_generator.py first.")
            continue
            
        fs = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.jpg', '.png'))]
        all_files.extend(fs)
        all_labels.extend([label2id[c]] * len(fs))

    if not all_files:
        print("❌ No data found. Please run data_generator.py first.")
        return

    train_f, test_f, train_l, test_l = train_test_split(all_files, all_labels, test_size=0.2, random_state=42)
    train_ds = DocDataset(train_f, train_l, processor)
    test_ds = DocDataset(test_f, test_l, processor)

    print(f"✅ Data Prepared. Training on {len(train_f)} samples, Validating on {len(test_f)} samples.")

    # Train Model
    os.environ["WANDB_DISABLED"] = "true"
    model = LayoutLMv3ForSequenceClassification.from_pretrained("microsoft/layoutlmv3-base", num_labels=len(CLASSES))
    model.config.id2label = id2label
    model.config.label2id = label2id
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    training_args = TrainingArguments(
        output_dir="./results_12class", 
        max_steps=150, # Short training for demo
        per_device_train_batch_size=4,
        learning_rate=5e-5, 
        remove_unused_columns=False, 
        report_to="none",
        save_strategy="no" # Save manually at end to save space
    )

    trainer = Trainer(
        model=model, args=training_args, train_dataset=train_ds,
        processing_class=processor, data_collator=default_data_collator
    )

    print("🚀 Starting Training...")
    trainer.train()
    
    print("💾 Saving Model...")
    model.save_pretrained("./saved_12class_model")
    processor.save_pretrained("./saved_12class_model")
    print("✅ Training Complete & Model Saved.")

if __name__ == "__main__":
    train()
