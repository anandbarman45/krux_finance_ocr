import os
import re
import torch
import pytesseract
import argparse
from PIL import Image
from pdf2image import convert_from_path
from transformers import LayoutLMv3Processor, LayoutLMv3ForSequenceClassification
from data_generator import CLASSES

# Ensure Tesseract is in PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_ocr(image):
    w, h = image.size
    df = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME, lang='eng', config='--oem 3 --psm 6').dropna()
    df = df[df.text.str.strip().astype(bool)]
    words = df.text.astype(str).tolist()
    boxes = [[max(0,min(1000,int(r['left']/w*1000))), max(0,min(1000,int(r['top']/h*1000))),
              max(0,min(1000,int((r['left']+r['width'])/w*1000))), max(0,min(1000,int((r['top']+r['height'])/h*1000)))]
             for _, r in df.iterrows()]
    if not words: words, boxes = ["empty"], [[0,0,1000,1000]]
    return words, boxes

class DocumentAI:
    def __init__(self, model_path="Krux01/document_ai_model_12class"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        
        # Handle subfolder for the specific Krux model
        subfolder = "document_ai_model_12class" if model_path == "Krux01/document_ai_model_12class" else None
        
        try:
            if subfolder:
                print(f"⬇️ Loading model from Hugging Face: {model_path} (subfolder: {subfolder})...")
                self.model = LayoutLMv3ForSequenceClassification.from_pretrained(model_path, subfolder=subfolder).to(self.device).eval()
                self.processor = LayoutLMv3Processor.from_pretrained(model_path, subfolder=subfolder, apply_ocr=False)
            else:
                print(f"⬇️ Loading model from: {model_path}...")
                self.model = LayoutLMv3ForSequenceClassification.from_pretrained(model_path).to(self.device).eval()
                self.processor = LayoutLMv3Processor.from_pretrained(model_path, apply_ocr=False)
        except OSError as e:
            print(f"⚠️ Failed to load model from {model_path}: {e}")
            print("⚠️ Using base model (untrained) for testing structure.")
            self.model = LayoutLMv3ForSequenceClassification.from_pretrained("microsoft/layoutlmv3-base", num_labels=len(CLASSES)).to(self.device).eval()
            self.processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
            
        self.id2label = {i: c for i, c in enumerate(CLASSES)}

    def _heuristic_check(self, text):
        t = text.upper()
        if "CORPORATE IDENTITY NUMBER" in t or "CIN" in t: return "COI" if "GST" not in t else None
        if "GST" in t and "REG-06" in t: return "GST"
        if "UDYAM" in t and "REGISTRATION" in t: return "UDYAM"
        if "FSSAI" in t: return "FSSAI"
        if "GUMASTA" in t or ("FORM F" in t and "ESTABLISHMENTS" in t): return "GUMASTA"
        if "KARNATAKA" in t and "FORM C" in t: return "EKARMIKA"
        if "FORM 20" in t or "DRUG" in t: return "DRUG_LICENSE"
        if "IMPORTER-EXPORTER" in t or "IEC" in t: return "IEC"
        if "PROFESSION TAX" in t or "FORM II" in t: return "PTEC"
        if "TAN" in t and "DEDUCTION" in t: return "TAN"
        if "KOLKATA MUNICIPAL" in t and "ENLISTMENT" in t: return "TRADE_LICENSE_WB"
        if "DEED OF PARTNERSHIP" in t: return "PARTNERSHIP_DEED"
        return None

    def _extract(self, doc_type, text):
        data = {"type": doc_type, "id_number": "Not Found"}

        if doc_type == "GST":
            # Strict GSTIN: 2 digits + 5 chars + 4 digits + 1 char + 1 char + Z + 1 char
            match = re.search(r"(?:Number|GSTIN)[\s:\-\.]*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})", text, re.IGNORECASE)
            if not match: match = re.search(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b", text)
            if match: data["id_number"] = match.group(1)

        elif doc_type == "COI":
            # Allow optional spaces between CIN parts to be robust to OCR tokenization
            pattern_ws = r"[LU]\s*[0-9]{5}\s*[A-Z]{2}\s*[0-9]{4}\s*[A-Z]{3}\s*[0-9]{6}"
            match = re.search(rf"(?:CIN|Identity\s*Number).*?({pattern_ws})", text, re.IGNORECASE | re.DOTALL)
            if not match:
                # Fallback: detect bare CIN even if the label wasn't OCR'ed
                alt = re.search(rf"\b{pattern_ws}\b", text)
                if alt:
                    data["id_number"] = re.sub(r"\s+", "", alt.group(0))
            else:
                data["id_number"] = re.sub(r"\s+", "", match.group(1))

        elif doc_type == "UDYAM":
            match = re.search(r"UDYAM-[A-Z]{2}-\d{2}-\d{7}", text, re.IGNORECASE)
            if match: data["id_number"] = match.group(0)

        elif doc_type == "FSSAI":
            match = re.search(r"(?:License|Lic).*?([0-9]{14})", text, re.IGNORECASE)
            if match: data["id_number"] = match.group(1)

        elif doc_type == "GUMASTA":
            match = re.search(r"(?:Registration\s*No)[\s:\-\.]*([A-Z0-9/]{5,25})", text, re.IGNORECASE)
            if match: data["id_number"] = match.group(1)

        elif doc_type == "IEC":
            match = re.search(r"(?:IEC\s*Number|Code).*?([0-9]{10})", text, re.IGNORECASE)
            if match: data["id_number"] = match.group(1)

        elif doc_type == "TAN":
            match = re.search(r"[A-Z]{4}[0-9]{5}[A-Z]{1}", text)
            if match: data["id_number"] = match.group(0)

        elif doc_type == "TRADE_LICENSE_WB":
            match = re.search(r"(?:CE\s*No|Enlistment).*?([0-9]{10,15})", text, re.IGNORECASE)
            if match: data["id_number"] = match.group(1)

        return data

    def analyze(self, image_path):
        if not os.path.exists(image_path):
            return {"Error": "File not found"}
            
        try:
            if image_path.lower().endswith('.pdf'):
                # Convert first page of PDF to image at moderate DPI for speed/accuracy
                images = convert_from_path(image_path, dpi=200, first_page=1, last_page=1)
                if not images:
                    return {"Error": "Empty PDF"}
                img = images[0].convert("RGB")
            else:
                img = Image.open(image_path).convert("RGB")
        except Exception as e:
            return {"Error": f"Failed to load image: {str(e)}"}

        words, boxes = get_ocr(img)
        full_text = " ".join(words)

        # 1. Heuristics
        doc_type = self._heuristic_check(full_text)
        conf = "100% (Rule-Based)"

        # 2. AI Model (Fallback)
        if not doc_type:
            enc = self.processor(img, words, boxes=boxes, truncation=True, padding="max_length", max_length=512, return_tensors="pt")
            with torch.no_grad():
                logits = self.model(input_ids=enc.input_ids.to(self.device), bbox=enc.bbox.to(self.device), pixel_values=enc.pixel_values.to(self.device), attention_mask=enc.attention_mask.to(self.device)).logits
            doc_type = self.id2label[logits.argmax(-1).item()]
            conf = f"{torch.softmax(logits, dim=1).max().item():.2%} (AI)"

        # 3. Extraction
        data = self._extract(doc_type, full_text)
        status = "VALID" if data["id_number"] != "Not Found" else "REVIEW_REQUIRED"

        return {"Type": doc_type, "Confidence": conf, "Status": status, "Data": data}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KruxOCR Inference")
    parser.add_argument("image_path", help="Path to the image file")
    args = parser.parse_args()
    
    pipeline = DocumentAI()
    res = pipeline.analyze(args.image_path)
    
    print("\n" + "="*40)
    print(f"📄 Type:   {res.get('Type')}")
    print(f"⚠️ Status: {res.get('Status')}")
    print(f"📂 Data:   {res.get('Data')}")
    print("="*40)
