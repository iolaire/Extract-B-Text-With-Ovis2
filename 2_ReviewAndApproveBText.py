import csv
# Import necessary modules from Flask
from flask import Flask, render_template, send_from_directory, request, url_for
import pandas as pd # Although imported, pandas is not used in the current code. Consider removing if not needed later.

# Initialize the Flask application
app = Flask(__name__)
# Set a secret key for the Flask app. This is used for secure sessions.
# Replace with a strong, unique key in a production environment.
app.secret_key = '23908#$*(#)'

# Cache to store the data read from the CSV file
data_cache = {}
# Index to keep track of the current row being displayed from the data_cache
row_index = 0  # Initialize row_index here

# Define the route for the home page, supporting both GET and POST methods
@app.route('/', methods=['GET', 'POST'])
def home():
    # Declare global variables to be modified within the function
    global row_index, data_cache
    
    # Load data from the CSV file into data_cache if it's not already loaded
    if not data_cache:
        with open('output.csv', 'r') as file:
            reader = csv.DictReader(file)
            data_cache = [row for row in reader]  # Convert CSV data to a list of dictionaries
    total_rows = len(data_cache) # Get the total number of rows in the data



    # Debug print statement to show current total rows and row index
    print(f"Total rows: {total_rows}, Row index: {row_index}")  # Add debug statement here

    # Handle POST requests, specifically when the 'save_edit_newcsv' button is clicked
    if request.method == 'POST' and 'save_edit_newcsv' in request.form:
        # Get the edited text from the form
        edited_text = request.form['edit_text']
        # Update the 'text' and 'text_edited' fields in the data_cache for the current row
        data_cache[row_index]['text'] = edited_text
        data_cache[row_index]['text_edited'] = '1' # Mark the row as edited
        
        # Write the edited text to the original text file path specified in the CSV
        with open(data_cache[row_index]['t_file_path'], 'w') as f:
            f.write(edited_text)  # Write edited_text to the identified file

        # Write the edited text to a new '_t_approved.txt' file.
        # This prevents overwriting the approved text in subsequent edits if needed.
        with open(data_cache[row_index]['t_file_path'].replace('_t.txt', '_t_approved.txt'), 'w') as f:
            f.write(edited_text)  # Write edited_text into the _t_approved files so we don't overwrite that text again

        # Save the updated data_cache back to the original output.csv file
        with open('output.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data_cache[0].keys())
            writer.writeheader() # Write the header row
            writer.writerows(data_cache) # Write all rows from the data_cache
    
    # Render the index.html template, passing the current row data and navigation indices
    return render_template('index.html', current_row=data_cache[row_index],
                           # Calculate the index for the previous row (loops around if at the beginning)
                           prev_row_index=(row_index - 1) % total_rows if row_index > 0 else None,
                           # Calculate the index for the next row (loops around)
                           next_row_index=(row_index + 1) % total_rows, 
                           # Pass the current row index
                           row_index=row_index,
                           # Pass the total number of rows
                           total_rows=total_rows)


# Route to serve image files from the 'images' directory
@app.route('/images/<path:filename>')
def serve_image(filename):
    # Use send_from_directory to securely serve the specified file from the 'images' folder
    return send_from_directory('images', filename)

# Route to navigate to the previous row
@app.route('/prev')
def prev_row():
    # Declare global variables
    global row_index, data_cache
    # Check if data_cache is loaded
    if data_cache:
        total_rows = len(data_cache) # Get the total number of rows
        # Decrement the row index, looping around to the last row if currently at the first row
        row_index = (row_index - 1) % total_rows
        # Render the index.html template with the updated row data and navigation indices
        return render_template(
            'index.html',
            current_row=data_cache[row_index],
            # Calculate the index for the previous row
            prev_row_index=(row_index - 1) % total_rows if row_index > 0 else None,
            # Calculate the index for the next row
            next_row_index=(row_index + 1) % total_rows,
            # Pass the current row index
            row_index=row_index,
            # Pass the total number of rows
            total_rows=total_rows
        )
    # If data_cache is empty, redirect to the home page (or render an empty state)
    return render_template('index.html')

# Route to navigate to the next row
@app.route('/next')
def next_row():
    # Declare global variables
    global row_index, data_cache
    # Check if data_cache is loaded
    if data_cache:
        total_rows = len(data_cache) # Get the total number of rows
        # Increment the row index, looping around to the first row if currently at the last row
        row_index = (row_index + 1) % total_rows
        # Render the index.html template with the updated row data and navigation indices
        return render_template(
            'index.html',
            current_row=data_cache[row_index],
            # Calculate the index for the previous row
            prev_row_index=(row_index - 1) % total_rows if row_index > 0 else None,
            # Calculate the index for the next row
            next_row_index=(row_index + 1) % total_rows,
            # Pass the current row index
            row_index=row_index,
            # Pass the total number of rows
            total_rows=total_rows
        )
    # If data_cache is empty, redirect to the home page (or render an empty state)
    return render_template('index.html')

# Main block to run the Flask application
if __name__ == '__main__':
    # Run the app in debug mode. This should be set to False in a production environment.
    app.run(debug=True)