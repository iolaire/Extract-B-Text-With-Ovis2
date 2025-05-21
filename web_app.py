import csv
from flask import Flask, render_template, send_from_directory, request, url_for

app = Flask(__name__)
app.secret_key = '23908#$*(#)'

def load_data():
    try:
        with open('output.csv', 'r') as file:
            return csv.DictReader(file)
    except FileNotFoundError:
        return None
    except Exception as e:
        return f"Error loading data: {e}"

@app.route('/', methods=['GET', 'POST'])
def home():
    data = load_data()
    
    if not data:
        return render_template('index.html'), 404
    
    # Get the current row index based on request arguments
    try:
        current_row_idx = int(request.args.get('r', 0)) % len(data)
    except (TypeError, ValueError):
        current_row_idx = 0

    if not data or current_row_idx < 0 or current_row_idx >= len(data):
        return render_template('index.html', data=data, row=None, errors=[])

    can_save = True
    errors = []

    try:
        if request.method == 'POST' and 'save_edit_newcsv' in request.form:
            edited_text = request.form['edit_text']
            new_item = None

            # Find the current row by its text or as the next available row if no text
            for idx, row in enumerate(data):
                if idx == current_row_idx:  # Ensure we're updating the correct row
                    new_item = data[idx].copy()
                    new_item.update({'text': edited_text})
                    data.pop(idx)
                    data.insert(current_row_idx, new_item)
                    break

            if not new_item:
                errors.append("No text field found in original data!")

        # Handle save functionality
        if can_save and 'save' in request.form:
            try:
                with open('output.csv', 'w') as file:
                    writer = csv.DictWriter(file, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                return render_template('index.html', data=data, row=current_row_idx, errors=errors)
            except Exception as e:
                errors.append(f"Failed to save changes: {str(e)}")

    except Exception as e:
        errors.append(f"An error occurred: {str(e)}")
    
    return render_template('index.html', data=data, row=current_row_idx, errors=errors)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

@app.route('/prev')
def prev_row():
    try:
        data = load_data()
        if not data:
            return "No data to display", 404

        current_row_idx = int(request.args.get('r', 0)) % len(data)
        new_idx = (current_row_idx - 1) % len(data)
        
        return render_template(
            'index.html',
            data=data,
            row=new_idx,
        )
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/next')
def next_row():
    try:
        data = load_data()
        if not data:
            return "No data to display", 404

        current_row_idx = int(request.args.get('r', 0)) % len(data)
        new_idx = (current_row_idx + 1) % len(data)
        
        return render_template(
            'index.html',
            data=data,
            row=new_idx,
        )
    except Exception as e:
        return f"Error: {str(e)}"