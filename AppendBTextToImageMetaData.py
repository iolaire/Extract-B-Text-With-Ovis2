import os
import time
from exiftool import ExifToolHelper
import re

def append_t_text(t_file_path):
    file_path_image = t_file_path.replace('_b_t_approved.txt','_a.jpg')
    file_path_caption = t_file_path.replace('_b_t_approved.txt','_b_t.txt') 
    caption_text = ''
    # print(file_path_image)
    # print(file_path_caption)
    with ExifToolHelper() as et:
        
        metadata = et.get_metadata(file_path_image)
        
        for data in metadata:
            # Check and print the EXIF:ImageDescription tag if it exists
            if "EXIF:ImageDescription" in data:
                hasCaption = 1
                caption = metadata[0]["EXIF:ImageDescription"]
                # print(caption)
                # with exiftool.ExifTool() as et:
            if "EXIF:DateTimeOriginal" in data:
                exif_date = metadata[0]["EXIF:DateTimeOriginal"]
                # print(exif_date)
    # with open(file_path_caption, 'r') as text_file:
    #     text_data = text_file.read()
    #     caption_text =  re.sub('\s+',' ',myString) 
        with open(file_path_caption, 'r') as text_file:
            # Read each line of the text file
            for line in text_file.readlines():
                stripped_line = line.strip()
                
                if stripped_line:  # Only add non-empty lines
                    caption_text += f" {stripped_line}"
        # print(caption_text)
    

    if caption == '':
        caption_final =  f'-back> {caption_text} <back-'.strip()
        # print('here')
    else:
        if caption.find('-back>') == -1:
            caption_final =  f'-back> {caption_text} <back- {caption}'.strip()
        else:
            # allready moved over, don't add text
            caption_final  = caption 
            print('no change')
        # print('there')
    print(caption_final.strip())
    with ExifToolHelper() as etc:
        etc.set_tags(file_path_image, {
            "EXIF:DateTimeOriginal": exif_date
            ,"EXIF:ImageDescription": caption_final
            ,"XMP:Description": caption_final # Optional for XMP metadata
            })
      
        # Remove any backup files created
        backup_file_path = file_path_image + "_original"
        if os.path.exists(backup_file_path):
            os.remove(backup_file_path)


def process_folder(root_folder):
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(('_b_t_approved.txt')):
                print(file)
                start_time = time.time()
                append_t_text(os.path.join(root, file))
                end_time = time.time()
                
                print(f"Execution time: {end_time - start_time:.1f} seconds, {(end_time - start_time)/60:.1f} minutes")

process_folder('/Volumes/Gold/PhotosScannedAtLibraryImmich/0408225_Scanned/77_Misc Family Favorites (check dates on back)__Petersburg AK/')