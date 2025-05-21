# Image Text Extraction and Processing Pipeline

This project provides an automated solution for extracting text from images using the Ovis2-1B machine learning model. It processes images, extracts text content, and organizes the results into a structured CSV format with corresponding text files for each processed image.

The system is designed to handle large collections of images, particularly focusing on files with "_b.jpg" suffix. It leverages state-of-the-art machine learning capabilities to extract both printed and handwritten text, numbers, symbols, and location information while maintaining the original formatting. The extracted information is systematically organized and stored for easy review and analysis through a companion display utility.

## Repository Structure
```
.
├── DateReviewOvis.py          # Main script for image processing and text extraction
└── display_output_csv.py      # Utility script to view processed results in HTML format
```

## Usage Instructions
### Prerequisites
- Python 3.6 or higher
- PyTorch
- Transformers library
- Pillow (PIL)
- pandas
- Sufficient disk space for image processing and storage
- CUDA-capable GPU (optional, for improved performance)

### Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install required packages:
```bash
pip install torch transformers Pillow pandas
```

3. Set up environment variables:
```bash
export FLASHATTN_FORCE_DISABLE="1"
export TOKENIZERS_PARALLELISM="false"
```

### Quick Start
1. Configure the input directory in `DateReviewOvis.py`:
```python
directory_path = '/path/to/your/images/'
```

2. Run the text extraction process:
```bash
python DateReviewOvis.py
```

3. View the results:
```bash
python display_output_csv.py
```

### More Detailed Examples
#### Processing a Specific Directory
```python
from DateReviewOvis import find_b_jpg_files, load_ovis2_model_and_prepare_query, process_image_and_generate_text

# Load the model
model, query = load_ovis2_model_and_prepare_query()

# Process a specific directory
directory_path = '/path/to/images/'
image_paths = find_b_jpg_files(directory_path)

for path in image_paths:
    text, exec_time = process_image_and_generate_text(path, model, query)
    print(f"Processed {path}: {text}")
    print(f"Processing time: {exec_time}")
```

### Troubleshooting
#### Common Issues
1. GPU Memory Issues
   - Error: "CUDA out of memory"
   - Solution: Adjust `max_memory` parameter in model loading:
   ```python
   model = AutoModelForCausalLM.from_pretrained(
       "AIDC-AI/Ovis2-1B",
       max_memory=0.4  # Reduce memory usage
   )
   ```

2. Image Loading Failures
   - Error: "Cannot identify image file"
   - Solution: Verify image format and file permissions
   - Check image file integrity

#### Debugging
- Enable logging for detailed output:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

- Check log files at:
  * Model processing logs: `./logs/model_processing.log`
  * Image processing logs: `./logs/image_processing.log`

## Data Flow
The system processes images through a pipeline that extracts text and organizes results into structured formats.

```ascii
[Input Images] -> [ML Model Processing] -> [Text Extraction]
       |                    |                     |
       v                    v                     v
  [Image Copy]        [Progress Logs]      [Text Storage]
       |                    |                     |
       v                    v                     v
[Images Folder]    [Processing Stats]     [CSV Output]
```

Key Component Interactions:
1. Image Discovery: Recursively finds all "_b.jpg" files in specified directory
2. Model Initialization: Loads Ovis2-1B model with optimized settings
3. Text Extraction: Processes images through ML model with custom query
4. Result Storage: Saves extracted text to "_t.txt" files
5. Data Organization: Maintains CSV record of all processed files
6. Image Management: Copies processed images to review folder
7. Result Display: Provides HTML visualization of processed data