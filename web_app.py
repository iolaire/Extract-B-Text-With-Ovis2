import csv
from flask import Flask, render_template, send_from_directory, request, url_for

app = Flask(__name__)
app.secret_key = '23908#$*(#)'

data_cache = {}
row_index = 0  # Initialize row_index here

@app.route('/', methods=['GET', 'POST'])
def home():
    global row_index, data_cache
    
    if not data_cache:
        with open('output.csv', 'r') as file:
            reader = csv.DictReader(file)
            data_cache = [row for row in reader]  # Convert to list of dictionaries

    total_rows = len(data_cache)

    print(f"Total rows: {total_rows}, Row index: {row_index}")  # Add debug statement here

    if request.method == 'POST' and 'save_edit_newcsv' in request.form:
        edited_text = request.form['edit_text']
        data_cache[row_index]['text'] = edited_text
        data_cache[row_index]['text_edited'] = 1
        
        with open(data_cache[row_index]['t_file_path'], 'w') as f:
            f.write(edited_text)  # Write edited_text to the identified file
        
        # Save changes back to CSV
        with open('output.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data_cache[0].keys())
            writer.writeheader()
            writer.writerows(data_cache)
    
    return render_template('index.html', current_row=data_cache[row_index],
                           prev_row_index=(row_index - 1) % total_rows if row_index > 0 else None,
                           next_row_index=(row_index + 1) % total_rows, 
                           row_index=row_index)



@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

@app.route('/prev')
def prev_row():
    global row_index, data_cache
    if data_cache:
        row_index = (row_index - 1) % len(data_cache)
        total_rows = len(data_cache)
        return render_template(
            'index.html',
            current_row=data_cache[row_index],
            prev_row_index=(row_index - 1) % total_rows if row_index > 0 else None,
            next_row_index=(row_index + 1) % total_rows,
            row_index=row_index,
            total_rows=total_rows
        )

@app.route('/next')
def next_row():
    global row_index, data_cache
    if data_cache:
        row_index = (row_index + 1) % len(data_cache)
        total_rows = len(data_cache)
        return render_template(
            'index.html',
            current_row=data_cache[row_index],
            prev_row_index=(row_index - 1) % total_rows if row_index > 0 else None,
            next_row_index=(row_index + 1) % total_rows,
            row_index=row_index,
            total_rows=total_rows
        )

if __name__ == '__main__':
    app.run(debug=True)