import os
import random
from PIL import Image, ImageDraw
from utils import get_font, create_mock_qr, ensure_dir

# Define all 12 Classes
CLASSES = [
    "GST", "COI", "GUMASTA", "UDYAM", "FSSAI",
    "EKARMIKA", "DRUG_LICENSE", "IEC", "PTEC", "TAN",
    "TRADE_LICENSE_WB", "PARTNERSHIP_DEED"
]

def generate_gst(filename):
    img = Image.new('RGB', (1000, 1400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((400, 50), "Government of India", fill="black", font=get_font(30, True))
    draw.text((380, 90), "Form GST REG-06", fill="black", font=get_font(24, True))
    gstin = f"27{random.randint(10000,99999)}A1Z5"
    draw.text((50, 220), f"Registration Number : {gstin}", fill="black", font=get_font(22, True))
    draw.text((600, 930), "DS GOODS AND SERVICES", fill="black", font=get_font(18))
    img.save(filename)

def generate_coi(filename):
    img = Image.new('RGB', (1000, 1400), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    draw.text((280, 100), "MINISTRY OF CORPORATE AFFAIRS", fill="black", font=get_font(24, True))
    cin = f"U72900MH{random.randint(2015,2025)}PTC{random.randint(100000,999999)}"
    draw.text((50, 500), f"Corporate Identity Number: {cin}", fill="black", font=get_font(20, True))
    draw.rectangle([600, 900, 850, 1000], fill="yellow", outline="black")
    draw.text((620, 920), "DS MINISTRY OF CORPORATE", fill="black", font=get_font(18))
    img.save(filename)

def generate_gumasta(filename):
    img = Image.new('RGB', (1400, 1000), (255, 250, 240))
    draw = ImageDraw.Draw(img)
    draw.text((600, 50), "FORM 'F'", fill="black", font=get_font(36, True))
    draw.text((450, 100), "Maharashtra Shops and Establishments Act", fill="black", font=get_font(28, True))
    lic_no = f"MH/MUM/{random.randint(1000,9999)}"
    draw.text((100, 250), f"Registration No: {lic_no}", fill="red", font=get_font(28, True))
    draw.ellipse([1000, 600, 1200, 800], outline="blue", width=5)
    img.save(filename)

def generate_udyam(filename):
    img = Image.new('RGB', (1000, 1400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((400, 180), "UDYAM", fill="darkblue", font=get_font(48, True))
    draw.text((300, 240), "REGISTRATION CERTIFICATE", fill="black", font=get_font(28, True))
    qr = create_mock_qr(150)
    img.paste(qr, (750, 50))
    udyam_no = f"UDYAM-MH-03-{random.randint(1000000,9999999)}"
    draw.text((250, 350), f"UDYAM REGISTRATION NUMBER: {udyam_no}", fill="black", font=get_font(24, True))
    img.save(filename)

def generate_fssai(filename):
    img = Image.new('RGB', (1000, 1400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((300, 100), "Food Safety and Standards Authority of India", fill="darkblue", font=get_font(24, True))
    fssai_no = f"1{random.randint(10,20)}{random.randint(10000000000,99999999999)}"
    draw.text((350, 200), f"Lic No: {fssai_no}", fill="black", font=get_font(36, True))
    img.save(filename)

def generate_ekarmika(filename):
    img = Image.new('RGB', (1000, 1400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((350, 50), "GOVERNMENT OF KARNATAKA", fill="black", font=get_font(28, True))
    draw.text((400, 90), "DEPARTMENT OF LABOUR", fill="black", font=get_font(24, True))
    reg_no = f"KA/BNG/{random.randint(10000,99999)}"
    draw.text((100, 250), f"Registration No: {reg_no}", fill="red", font=get_font(26, True))
    img.save(filename)

def generate_drug_license(filename):
    img = Image.new('RGB', (1000, 1400), (240, 255, 240))
    draw = ImageDraw.Draw(img)
    draw.text((400, 50), "FORM 20", fill="black", font=get_font(32, True))
    draw.text((200, 150), "LICENCE TO SELL, STOCK OR EXHIBIT DRUGS", fill="black", font=get_font(24, True))
    draw.text((750, 1080), "DRUG CONTROL", fill="purple", font=get_font(18, True))
    img.save(filename)

def generate_iec(filename):
    img = Image.new('RGB', (1000, 1400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((300, 250), "IMPORTER-EXPORTER CODE CERTIFICATE", fill="darkblue", font=get_font(26, True))
    iec_code = f"{random.randint(1000000000, 9999999999)}"
    draw.text((100, 350), f"IEC Number: {iec_code}", fill="black", font=get_font(30, True))
    img.save(filename)

def generate_ptec(filename):
    img = Image.new('RGB', (1000, 1400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((350, 50), "FORM II", fill="black", font=get_font(32, True))
    ptec_no = f"99{random.randint(10000000,99999999)}P"
    draw.text((100, 250), f"Enrollment Certificate No: {ptec_no}", fill="black", font=get_font(24, True))
    img.save(filename)

def generate_tan(filename):
    img = Image.new('RGB', (1000, 1400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((400, 100), "TAN ALLOTMENT LETTER", fill="black", font=get_font(24, True))
    tan_no = f"MUM{random.choice(['A','B'])}{random.randint(10000,99999)}C"
    draw.rectangle([300, 200, 700, 300], outline="black", width=2)
    draw.text((350, 240), f"TAN: {tan_no}", fill="black", font=get_font(36, True))
    img.save(filename)

def generate_trade_license_wb(filename):
    img = Image.new('RGB', (1000, 1400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((300, 50), "THE KOLKATA MUNICIPAL CORPORATION", fill="darkblue", font=get_font(26, True))
    draw.text((350, 150), "CERTIFICATE OF ENLISTMENT", fill="red", font=get_font(28, True))
    ce_no = f"{random.randint(1000000000, 9999999999)}"
    draw.text((600, 270), ce_no, fill="black", font=get_font(24, True))
    img.save(filename)

def generate_partnership_deed(filename):
    img = Image.new('RGB', (1000, 1400), (240, 255, 240))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 950, 300], outline="green", width=5)
    draw.text((400, 80), "INDIA NON JUDICIAL", fill="black", font=get_font(30, True))
    draw.text((350, 350), "DEED OF PARTNERSHIP", fill="black", font=get_font(32, True))
    img.save(filename)

def main():
    print("🚀 Generating Dataset for 12 Classes...")
    for c in CLASSES:
        ensure_dir(f"dataset/{c}")

    # Generate 25 samples per class
    for i in range(25):
        generate_gst(f"dataset/GST/gst_{i}.jpg")
        generate_coi(f"dataset/COI/coi_{i}.jpg")
        generate_gumasta(f"dataset/GUMASTA/gumasta_{i}.jpg")
        generate_udyam(f"dataset/UDYAM/udyam_{i}.jpg")
        generate_fssai(f"dataset/FSSAI/fssai_{i}.jpg")
        generate_ekarmika(f"dataset/EKARMIKA/eka_{i}.jpg")
        generate_drug_license(f"dataset/DRUG_LICENSE/dl_{i}.jpg")
        generate_iec(f"dataset/IEC/iec_{i}.jpg")
        generate_ptec(f"dataset/PTEC/ptec_{i}.jpg")
        generate_tan(f"dataset/TAN/tan_{i}.jpg")
        generate_trade_license_wb(f"dataset/TRADE_LICENSE_WB/tl_{i}.jpg")
        generate_partnership_deed(f"dataset/PARTNERSHIP_DEED/deed_{i}.jpg")
    
    print("✅ Dataset Generation Complete.")

if __name__ == "__main__":
    main()
