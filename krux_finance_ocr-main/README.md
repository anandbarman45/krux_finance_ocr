# Krux Finance OCR - Business Proof Engine

This project is a Deep Learning based OCR and Document Classification system for Indian Business Proofs. It supports 12 document classes including GST, COI, Udyam, and more.

## Prerequisites

### 1. Python Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 2. System Dependencies (Windows)
This project requires **Tesseract OCR** and **Poppler** (for PDF handling).

#### Tesseract OCR
1. Download the installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install it (e.g., to `C:\Program Files\Tesseract-OCR`).
3. **Important**: Add the installation directory to your System PATH environment variable.
   - Or, uncomment the line in `train.py` and `inference.py`:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```

#### Poppler
1. Download the latest binary from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/).
2. Extract the zip file.
3. Add the `bin` folder (e.g., `C:\path\to\poppler\bin`) to your System PATH.

## Usage

### 1. Generate Synthetic Data
Generate the training dataset (images will be saved in `dataset/`):
```bash
python data_generator.py
```

### 2. Train the Model
Train the LayoutLMv3 model on the generated data:
```bash
python train.py
```
This will save the trained model to `./saved_12class_model`.

### 3. Run Inference (CLI)
Run the inference pipeline on a document image or PDF:
```bash
python inference.py path/to/your/document.jpg
```

## API Service & Deployment

### Run API Locally
Start the FastAPI server:
```bash
uvicorn app:app --reload
```
Access the API docs at `http://localhost:8000/docs`.

### Docker Deployment (AWS)
This project is ready for AWS (ECS, App Runner) using Docker.

1. **Build the Image**:
   ```bash
   docker build -t krux-ocr .
   ```

2. **Run Container Locally**:
   ```bash
   docker run -p 8000:8000 krux-ocr
   ```

3. **Deploy to AWS**:
   - Push the image to **Amazon ECR**.
   - Create a task definition in **AWS ECS** or a service in **AWS App Runner** using the ECR image.
   - Ensure the service has at least 2GB RAM for the ML model.

## Project Structure
- `app.py`: FastAPI web server.
- `Dockerfile`: Docker configuration for Linux deployment.
- `data_generator.py`: Generates synthetic images.
- `train.py`: Trains the model.
- `inference.py`: Core inference logic.
- `utils.py`: Helper functions.
