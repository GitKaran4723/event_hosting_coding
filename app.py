from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, session
import mysql.connector
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL connection
mysql_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='codingpg'
)

#times for the fest and rounds
#format of the date is (year, month, day, hour, minute)
fest_start_time = datetime(2024, 4, 19, 9, 0)
round1_start_time = datetime(2024, 4, 19, 9, 30)
round2_start_time = datetime(2024, 4, 19, 2, 30)
round3_start_time = datetime(2024, 4, 20, 10, 30)


@app.route('/')
def index():
    return render_template('index.html', fest_start_time=fest_start_time)

@app.route('/rounds')
def rounds():
    return render_template('rounds_time.html')

@app.route('/round1login')
def round1login():
    return render_template('round1/round1login.html')

@app.route('/round2login')
def round2login():
    return render_template('round2/round2login.html')

@app.route('/round3login')
def round3login():
    return render_template('round3/round3login.html')

@app.route('/login1', methods=['GET', 'POST'])
def login1():
    if request.method == 'POST':
        team_name = request.form['team_name']
        password = request.form['password']

        cursor = mysql_connection.cursor()
        cursor.execute("SELECT id, name FROM teams WHERE name = %s AND password = %s", (team_name, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['team_name'] = user[1]
            return redirect('/dashboard1')
        else:
            return render_template('round1/round1login.html', message='Invalid credentials. Please try again.')

    return render_template('round1/round1login.html')

@app.route('/login2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        team_name = request.form['team_name']
        password = request.form['password']

        cursor = mysql_connection.cursor()
        cursor.execute("SELECT id, name FROM teams WHERE name = %s AND password = %s", (team_name, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['team_name'] = user[1]
            return redirect('/dashboard3')
        else:
            return render_template('round2/round2login.html', message='Invalid credentials. Please try again.')

    return render_template('round2/round3login.html')

@app.route('/login3', methods=['GET', 'POST'])
def login3():
    if request.method == 'POST':
        team_name = request.form['team_name']
        password = request.form['password']

        cursor = mysql_connection.cursor()
        cursor.execute("SELECT id, name FROM teams WHERE name = %s AND password = %s", (team_name, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['team_name'] = user[1]
            return redirect('/dashboard3')
        else:
            return render_template('round3/round3login.html', message='Invalid credentials. Please try again.')

    return render_template('round3/round3login.html')

@app.route('/dashboard1')
def dashboard1():
    if 'team_name' in session:
        return render_template('round1/dashboard1.html', team_name=session['team_name'])
    else:
        return redirect('/login1')
    
@app.route('/dashboard2')
def dashboard2():
    if 'team_name' in session:
        return render_template('round2/dashboard2.html', team_name=session['team_name'])
    else:
        return redirect('/login2')

@app.route('/dashboard3')
def dashboard3():
    if 'team_name' in session:
        return render_template('round3/dashboard3.html', team_name=session['team_name'])
    else:
        return redirect('/login3')
    
@app.route('/logout1', methods=['POST'])
def logout1():
    session.pop('team_name', None)
    return redirect('/round1login')

@app.route('/logout2', methods=['POST'])
def logout2():
    session.pop('team_name', None)
    return redirect('/round2login')

@app.route('/logout3', methods=['POST'])
def logout3():
    session.pop('team_name', None)
    return redirect('/round3login')

import json

# Open the JSON file for reading
with open('questions1.json', 'r') as file:
    # Load JSON data from the file
    quizQuestions = json.load(file)


@app.route('/quiz')
def quiz():
    if 'team_name' in session:
        return render_template('round1/quiz.html', team_name=session['team_name'], questions=quizQuestions['questions'])
    else:
        return redirect('/login1')

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if request.method == 'POST':
        submitted_answers = {}
        for key, value in request.form.items():
            if key.startswith('question'):
                question_number = int(key.replace('question', ''))
                submitted_answers[question_number] = value
        
        print(submitted_answers)
        # Compare submitted answers with correct answers from JSON file
        correct_answers = {idx: question['solution'] for idx, question in enumerate(quizQuestions['questions'])}
        score = sum(1 for idx, answer in correct_answers.items() if submitted_answers.get(idx) == answer)
        
        # Save the responses and score to the database
        save_responses_and_score(session['team_name'], json.dumps(submitted_answers), score)
        
        return render_template('round1/result1.html', score=score, total=len(quizQuestions['questions']))

def save_responses_and_score(team_name, responses, score):
    # Open a cursor to execute SQL queries
    cursor = mysql_connection.cursor()
    
    # Define the SQL query to insert responses and score into the database
    sql_query = "INSERT INTO scores (team_name, responses, score) VALUES (%s, %s, %s)"
    
    # Execute the SQL query with the team name, responses, and score as parameters
    cursor.execute(sql_query, (team_name, responses, score))
    
    # Commit the transaction to save changes to the database
    mysql_connection.commit()
    
    # Close the cursor
    cursor.close()

# Open the JSON file for reading
with open('questions3.json', 'r') as file:
    # Load JSON data from the file
    data = json.load(file)

@app.route('/code3')
def code3():
    if 'team_name' in session:
        return render_template('round3/code3.html', team_name=session['team_name'], questions=data['questions'])
    else:
        return redirect('/login3')

# other functionality


@app.route('/run', methods=['POST'])
def run():
    if request.method == 'POST':
        language = request.json['language']
        code = request.json['code']
        # Execute and check the code
        output, error = execute_and_check_code(code, language)
        if error:
            return error, 400  # Return error message with status code 400 (Bad Request)
        return output

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Process the submission and calculate the score
        # Redirect to the score page
        return redirect('/score')

def execute_and_check_code(code, language):
    team_name=session['team_name']

    inputs = "10 60"

    if language == 'c':
        return execute_and_check_c(team_name, code, inputs)
    elif language == 'cpp':
        return execute_and_check_cpp(team_name, code)
    elif language == 'java':
        return execute_and_check_java(team_name, code)
    else:
        # Unsupported language, return -1 marks
        return None, 'Unsupported language'

import subprocess
import os

def execute_and_check_c(team_name, code, inputs=None):
    # Generate unique file names based on team name
    c_file_name = f'{team_name}_temp.c'
    binary_file_name = f'{team_name}_temp.exe'

    try:
        # Write the code to the C file
        with open(c_file_name, 'w') as file:
            file.write(code)
        
        # Compile the C code
        compilation = subprocess.run(['gcc', c_file_name, '-o', binary_file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if compilation was successful
        if compilation.returncode != 0:
            # Compilation failed, return compilation error
            return None, f"Compilation failed: {compilation.stderr.decode('utf-8').strip()}"
        
        # Execute the compiled C code
        if inputs:
            execution = subprocess.run([f'./{binary_file_name}'], input=inputs.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            execution = subprocess.run([f'./{binary_file_name}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        output = execution.stdout.decode('utf-8')
        error = execution.stderr.decode('utf-8').strip()
        
        return output, error
    
    except Exception as e:
        # An exception occurred, return error message
        return None, f"Error: {str(e)}"
    
    finally:
        # Clean up - delete the temporary files
        if os.path.exists(c_file_name):
            os.remove(c_file_name)
        if os.path.exists(binary_file_name):
            os.remove(binary_file_name)
    

def execute_and_check_cpp(team_name, code):
    # Generate unique file names based on team name
    cpp_file_name = f'{team_name}_temp.cpp'
    binary_file_name = f'{team_name}_temp_cpp.exe'

    # Write the code to the C++ file
    with open(cpp_file_name, 'w') as file:
        file.write(code)
    
    # Compile the C++ code
    compilation = subprocess.run(['g++', cpp_file_name, '-o', binary_file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    compilation_output = compilation.stderr.decode('utf-8').strip()
    
    if compilation.returncode == 0:
        # Execute the compiled C++ code
        execution = subprocess.run([f'./{binary_file_name}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = execution.stdout.decode('utf-8')
        error = execution.stderr.decode('utf-8').strip()
        
        # Clean up - delete the temporary files
        os.remove(cpp_file_name)
        os.remove(binary_file_name)
        
        return output, error
    else:
        # Clean up - delete the temporary C++ file
        os.remove(cpp_file_name)
        
        return None, compilation_output 


def execute_and_check_java(team_name, code):
    # Generate unique file name based on team name
    java_file_name = f'{team_name}_Main.java'
    class_file_name = f'{team_name}_Main.class'

    # Write the code to the Java file
    with open(java_file_name, 'w') as file:
        file.write(code)
    
    try:
        # Compile the Java code
        compilation = subprocess.run(['javac', java_file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        compilation_output = compilation.stderr.decode('utf-8').strip()

        if compilation.returncode == 0:
            # Execute the compiled Java code
            execution = subprocess.run(['java', f'{team_name}_Main'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = execution.stdout.decode('utf-8')
            error = execution.stderr.decode('utf-8').strip()
            
            # Clean up - delete the temporary files
            if os.path.exists(java_file_name):
                os.remove(java_file_name)
            if os.path.exists(class_file_name):
                os.remove(class_file_name)
            
            return output, error
        else:
            # Clean up - delete the temporary Java file
            if os.path.exists(java_file_name):
                os.remove(java_file_name)
            
            return None, compilation_output
    except FileNotFoundError:
        # Clean up - delete the temporary Java file if it exists
        if os.path.exists(java_file_name):
            os.remove(java_file_name)
        
        return None, "File not found error occurred."
if __name__ == "__main__":
    # Run the Flask app on localhost (local system)
    app.run(host='127.0.0.1', port=5000, debug=True)
    
    # Run the Flask app on all network interfaces (local network)
    app.run(host='0.0.0.0', port=5000, debug=True)

