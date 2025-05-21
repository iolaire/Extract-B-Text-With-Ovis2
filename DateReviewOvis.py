import os
import time
from datetime import datetime
from shutil import copy as shutilcopy

import csv
from io import BytesIO
from PIL import Image
# Import only the necessary components from torch
from torch import backends, torch
from transformers import AutoProcessor, AutoModelForCausalLM

# Function to find b.jpg files in a directory and its subdirectories
def find_b_jpg_files(directory):
    found_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith("_b.jpg"):
                found_paths.append(os.path.join(root, file))
    return found_paths


#Function to load the ML model for later use, returns model and query
def load_ovis2_model_and_prepare_query():
    os.environ["FLASHATTN_FORCE_DISABLE"] = "1"  # Prevent FlashAttention from loading
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    device = "mps" if backends.mps.is_available() else "cpu"
    # load model
    
    try:
        model = AutoModelForCausalLM.from_pretrained("AIDC-AI/Ovis2-1B",  #"AIDC-AI/Ovis2-2B",
                                                     torch_dtype=torch.bfloat16,
                                                     multimodal_max_length=32768,
                                                     # device=device,
                                                     max_memory=.6,
                                                     llm_attn_implementation="eager",
                                                     trust_remote_code=True,
                                                     use_fast=True
                                                    )
        device = torch.device("mps")  # Metal Performance Shader (Apple GPU)
        model.to(device)
    except Exception as e:
        print(f"Error loading model or assigning device: {str(e)}")
        raise RuntimeError("Failed to load model or assign device") # Raise a specific exception instead of returning None

    text = """
    Extract all text from this image exactly as written, do not skip text, including:
    - Handwritten notes
    - Numbers and symbols
    - Location and cities
    Return the text in its original formatting. """
    # text = 'Caption the image in four sentences.'
    query = f'<image>\n{text}'
    return model, query


def process_image_and_generate_text(image_path, model, query):
    start_time = time.time()
    try:
        text_tokenizer, visual_tokenizer = get_tokenizers(model)
        images = load_images(image_path)
        input_ids, attention_mask, pixel_values = preprocess_inputs(model, query, images, text_tokenizer, visual_tokenizer)
        output = generate_output(model, input_ids, attention_mask, pixel_values, text_tokenizer)
        end_time = time.time()
        exec_time = calculate_execution_time(start_time, end_time)
        return output, exec_time
    except Exception as e:
        logging.error(f"Error generating caption: {str(e)}")
        return None

def get_tokenizers(model):
    return model.get_text_tokenizer(), model.get_visual_tokenizer()

def load_images(image_path):
    return [Image.open(image_path)]

def preprocess_inputs(model, query, images, text_tokenizer, visual_tokenizer):
    max_partition = 9
    prompt, input_ids, pixel_values = model.preprocess_inputs(query, images, max_partition=max_partition)
    attention_mask = torch.ne(input_ids, text_tokenizer.pad_token_id)
    input_ids = input_ids.unsqueeze(0).to(device=model.device)
    attention_mask = attention_mask.unsqueeze(0).to(device=model.device)
    if pixel_values is not None:
        pixel_values = pixel_values.to(dtype=visual_tokenizer.dtype, device=visual_tokenizer.device)
    pixel_values = [pixel_values]
    return input_ids, attention_mask, pixel_values

def generate_output(model, input_ids, attention_mask, pixel_values, text_tokenizer):
    with torch.inference_mode():
        gen_kwargs = dict(
            max_new_tokens=1024,
            do_sample=False,
            top_p=None,
            top_k=None,
            temperature=None,
            repetition_penalty=None,
            eos_token_id=model.generation_config.eos_token_id,
            pad_token_id=text_tokenizer.pad_token_id,
            use_cache=True
        )
        output_ids = model.generate(input_ids, pixel_values=pixel_values, attention_mask=attention_mask, **gen_kwargs)[0]
        return text_tokenizer.decode(output_ids, skip_special_tokens=True)

def calculate_execution_time(start_time, end_time):
    return f"Execution time: {end_time - start_time:.1f} seconds, {(end_time - start_time)/60:.1f} minutes"

start_time_overall = time.time()
# Define the directory containing the images
directory_path = '/Volumes/Gold/PhotosScannedAtLibraryImmich/'
model, query = load_ovis2_model_and_prepare_query()
all_paths = find_b_jpg_files(directory_path)

sample_paths =  all_paths[0:3] + all_paths[11:13] 

# Specify the path to save the CSV file
output_csv_path = os.path.join("output.csv")
images_subfolder = '/Volumes/Gold/python/create_folders_from_CSV/DateReviewOvis/images/'  # Define the full path to the images subfolder

with open(output_csv_path, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    # Write the header
    writer.writerow(["id", "path", "t_file_path", "text", "image_name"])
csv_file.close()

print(len(sample_paths))
for idx, path in enumerate(sample_paths):
    id = idx + 1  # Assigning an ID as index starts from 0
    # print(f"File: {path}")
    text,exec_time = process_image_and_generate_text(path, model, query)
    if text.strip():  # Print only non-empty text
        print(f"File: {path}, Text: {text}")
        
        # Create the corresponding t.txt file name
        base_name = os.path.splitext(os.path.basename(path))[0]
        t_file_path = f"{os.path.dirname(path)}/{base_name}_t.txt"
        
        #copy the image to the images subfolder for review
        shutilcopy(path, images_subfolder)
        
        #append the data to 
        with open(t_file_path, 'w') as text_file:
            text_file.write(text)
            with open(output_csv_path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
                # Write the header
                writer.writerow([id, path, t_file_path, text, f"{base_name}.jpg"])
            csv_file.close()

            print(f"Text saved to {t_file_path}")
        print(f"File: {path}, Text: {text}")
        print(f"{exec_time}")
end_time_overall = time.time()
exec_time_overall = calculate_execution_time(start_time_overall, end_time_overall)
print(f"{exec_time_overall}")