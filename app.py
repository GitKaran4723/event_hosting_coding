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
    database='abyudaya'
)

#times for the fest and rounds
#format of the date is (year, month, day, hour, minute)
fest_start_time = datetime(2024, 4, 19, 9, 0)

#round1
round1_start_time = datetime(2024, 4, 19, 12, 00)
round1_end_time = datetime(2024, 4, 19, 12, 15)

#round2
round2_start_time = datetime(2024, 4, 19, 12, 42)
round2_end_time = datetime(2024, 4, 19, 1, 10)

#round3 
round3_start_time = datetime(2024, 4, 18, 21, 57)
round3_end_time = datetime(2024, 4, 18, 22, 00)


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
            return redirect('/dashboard2')
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
        return render_template('round1/dashboard1.html', team_name=session['team_name'] , round1_start_time=round1_start_time)
    else:
        return redirect('/login1')
    
@app.route('/dashboard2')
def dashboard2():
    if 'team_name' in session:
        return render_template('round2/dashboard2.html', team_name=session['team_name'], round2_start_time=round2_start_time)
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
with open('questions12.json', 'r') as file:
    # Load JSON data from the file
    quizQuestions = json.load(file)


@app.route('/quiz')
def quiz():
    if 'team_name' in session:
        return render_template('round1/quiz.html', team_name=session['team_name'], questions=quizQuestions['questions'] , round1_end_time=round1_end_time)
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
        
        
        return render_template('round1/result1.html', score=score, total=len(quizQuestions['questions']) , team_name=session['team_name'])
    
    session.pop('team_name', None)

def save_responses_and_score(team_name, responses, score):
    # Open a cursor to execute SQL queries
    cursor = mysql_connection.cursor()
    
    # Define the SQL query to insert responses and score into the database
    sql_query = "INSERT INTO scores01 (team_name, responses, score) VALUES (%s, %s, %s)"
    
    # Execute the SQL query with the team name, responses, and score as parameters
    cursor.execute(sql_query, (team_name, responses, score))
    
    # Commit the transaction to save changes to the database
    mysql_connection.commit()
    
    # Close the cursor
    cursor.close()

# Open the JSON file for reading
with open('questions.json', 'r', encoding='utf-8') as file:
    # Load JSON data from the file
    debug_qns = json.load(file)


@app.route('/debugging')
def debugging():
    if 'team_name' in session:
        return render_template('round2/debugging.html', team_name=session['team_name'], questions = debug_qns['questions'] , round2_end_time=round2_end_time)
    else:
        return redirect('/login1')

# Open the JSON file for reading
with open('questions3.json', 'r') as file:
    # Load JSON data from the file
    data3 = json.load(file)

@app.route('/code3')
def code3():
    if 'team_name' in session:
        return render_template('round3/code3.html', team_name=session['team_name'], questions=data3['questions'])
    else:
        return redirect('/login3')

# other functionality

from flask import jsonify

@app.route('/run2', methods=['POST'])
def run2():
    if request.method == 'POST':
        language = request.json['language']
        code = request.json['code']
        question_number = int(request.json['questionNumber'])
        
        # Retrieve all test cases for the selected question
        test_cases = debugging['questions'][question_number]['test_cases']
        
        # Initialize a list to store results for each test case
        results = []
        
        # Iterate through all test cases
        for test_case in test_cases:
            inputs = test_case['input']
            expected_output = test_case['expected_output']
            
            # Execute and check the code with the current test case
            output, error = execute_and_check_code_with_input(code, language, inputs)
            
            # Check if there's any error
            if error:
                return error, 400  # Return error message with status code 400 (Bad Request)
            
            # Check if the output matches the expected output
            if output.strip() == expected_output.strip():
                result = 'pass'
            else:
                result = 'fail'
                
            # Append the result to the results list
            results.append({'input': inputs, 'expected_output': expected_output, 'actual_output': output, 'result': result})
        
        # Return the results as JSON
        return jsonify(results)


@app.route('/run', methods=['POST'])
def run():
    if request.method == 'POST':
        language = request.json['language']
        code = request.json['code']
        question_number = request.json['questionNumber']
        
        # Collect only test cases 1 and 2
        test_cases = data3['questions'][int(question_number)]['test_cases'][:2]
        
        # Initialize a list to store results for each test case
        results = []
        
        # Iterate through the selected test cases
        for test_case in test_cases:
            inputs = test_case['input']
            expected_output = test_case['expected_output']
            
            # Execute and check the code with the current test case
            output, error = execute_and_check_code_with_input(code, language, inputs)
            
            # Check if there's any error
            if error:
                return error, 400  # Return error message with status code 400 (Bad Request)
            
            # Check if the output matches the expected output
            if output.strip() == expected_output.strip():
                results.append({'input': inputs, 'expected_output': expected_output, 'actual_output': output, 'result': 'pass'})
            else:
                results.append({'input': inputs, 'expected_output': expected_output, 'actual_output': output, 'result': 'fail'})
        
        # Return the results as JSON
        return jsonify(results)



@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        language = request.json['language']
        code = request.json['code']
        question_number = request.json['questionNumber']
        
        # Collect all test cases
        test_cases = data3['questions'][int(question_number)]['test_cases']
        
        # Initialize a list to store results for each test case
        results = []
        total_score = 0
        
        # Iterate through all test cases
        for i, test_case in enumerate(test_cases):
            inputs = test_case['input']
            expected_output = test_case['expected_output']
            score = test_case['score']
            
            # Execute and check the code with the current test case
            try:
                output, error = execute_and_check_code_with_input(code, language, inputs)
            except Exception as e:
                return str(e)+" to deal with this : Click on run button", 400  # Return error message with status code 400 (Bad Request)
            # Check if there's any error
            if error:
                return error, 400  # Return error message with status code 400 (Bad Request)
            
            # Check if the output matches the expected output
            if output.strip() == expected_output.strip():
                result = 'pass'

            else:
                result = 'fail'
                score = 0
            
            total_score += score

            
            # Include inputs and outputs for the first two test cases
            if i < 2:
                results.append({'input': inputs, 'expected_output': expected_output, 'actual_output': output, 'result': result})
            else:
                results.append({'input': None, 'expected_output': None, 'actual_output': None, 'result': result})
        
        # Return the results as JSON
        return jsonify({'results': results, 'total_score': total_score})
 
@app.route('/run-with-input', methods=['POST'])
def run_with_input():
    if request.method == 'POST':
        # Extract data from the request
        language = request.json['language']
        code = request.json['code']
        input_values = request.json['inputValues']
        question_number = request.json['questionNumber']

        # Execute the code with input values
        output, error = execute_and_check_code_with_input(code, language, input_values)

        # Check if there was an error
        if error:
            # Return the error message with status code 400 (Bad Request)
            return error, 400
        else:
            # Return the output
            return output

def execute_and_check_code_with_input(code, language, inputs=None):
    team_name=session['team_name']

    if ("KARAN" in code):
        
        return None, "Dont try this here! you are noticed.."
    
    if language == 'c':
        return execute_and_check_c(team_name, code, inputs)
    elif language == 'cpp':
        return execute_and_check_cpp(team_name, code, inputs)
    elif language == 'java':
        return execute_and_check_java(team_name, code, inputs)
    else:
        # Unsupported language, return -1 marks
        return None, 'Unsupported language'

import subprocess
import os
import signal
import threading

def execute_and_check_c(team_name, code, inputs=None, timeout=5):
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
        
        # Execute the compiled C code with timeout
        if inputs:
            execution = subprocess.run([f'./{binary_file_name}'], input=inputs.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        else:
            execution = subprocess.run([f'./{binary_file_name}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            
        output = execution.stdout.decode('utf-8')
        error = execution.stderr.decode('utf-8').strip()
        
        return output, error
    
    except subprocess.TimeoutExpired:
        return None, "Execution timed out"
    
    except Exception as e:
        # An exception occurred, return error message
        return None, f"Error: {str(e)}"
    
    finally:
        # Clean up - delete the temporary files
        if os.path.exists(c_file_name):
            os.remove(c_file_name)
        if os.path.exists(binary_file_name):
            os.remove(binary_file_name)

def execute_and_check_cpp(team_name, code, inputs=None, timeout=5):
    # Generate unique file names based on team name
    cpp_file_name = f'{team_name}_temp.cpp'
    binary_file_name = f'{team_name}_temp_cpp.exe'

    try:
        # Write the code to the C++ file
        with open(cpp_file_name, 'w') as file:
            file.write(code)
        
        # Compile the C++ code
        compilation = subprocess.run(['g++', cpp_file_name, '-o', binary_file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if compilation was successful
        if compilation.returncode != 0:
            # Compilation failed, return compilation error
            return None, f"Compilation failed: {compilation.stderr.decode('utf-8').strip()}"
        
        # Execute the compiled C++ code with timeout
        if inputs:
            print("inputs",inputs)
            execution = subprocess.run([f'./{binary_file_name}'], input=inputs.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        else:
            execution = subprocess.run([f'./{binary_file_name}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            
        output = execution.stdout.decode('utf-8')
        error = execution.stderr.decode('utf-8').strip()
        
        return output, error
    
    except subprocess.TimeoutExpired:
        return None, "Execution timed out"
    
    except Exception as e:
        # An exception occurred, return error message
        return None, f"Error: {str(e)}"
    
    finally:
        # Clean up - delete the temporary files
        if os.path.exists(cpp_file_name):
            os.remove(cpp_file_name)
        if os.path.exists(binary_file_name):
            os.remove(binary_file_name)

def execute_and_check_java(team_name, code, inputs=None, timeout=10):
    # Generate unique file name based on team name
    java_file_name = f'{team_name}_Main.java'
    class_file_name = f'{team_name}_Main'
    
    # Initialize output and error variables
    output = ""
    error = ""


    try:
        # Write the code to the Java file
        with open(java_file_name, 'w') as file:
            file.write(code)
        
        # Compile the Java code
        compilation = subprocess.run(['javac', java_file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if compilation was successful
        if compilation.returncode != 0:
            # Compilation failed, return compilation error
            return None, f"Compilation failed: {compilation.stderr.decode('utf-8').strip()}"
        
        # Define a function to execute the Java code
        def execute_java():
            nonlocal output, error
            try:
                # Execute the compiled Java code
                if inputs:
                    execution = subprocess.run(['java', class_file_name], input=inputs.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    execution = subprocess.run(['java', class_file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                output = execution.stdout.decode('utf-8')
                error = execution.stderr.decode('utf-8').strip()
            except Exception as e:
                error = f"Error: {str(e)}"
        
        # Create a thread to execute the Java code
        java_thread = threading.Thread(target=execute_java)
        java_thread.start()
        
        # Wait for the specified timeout duration
        java_thread.join(timeout)
        
        # If the Java thread is still alive, it means it has exceeded the timeout
        if java_thread.is_alive():
            # Terminate the entire process group
            java_process = subprocess.Popen(['java', class_file_name])
            os.kill(java_process.pid, signal.SIGTERM)
            return None, "Execution timed out"
        
        # Java execution completed within the timeout
        return output, error
    
    except Exception as e:
        # An exception occurred, return error message
        return None, f"Error: {str(e)}"
    
    finally:
        # Clean up - delete the temporary files
        if os.path.exists(java_file_name):
            os.remove(java_file_name)
        if os.path.exists(f"{class_file_name}.class"):
            os.remove(f"{class_file_name}.class")

@app.route('/give1')
def score():
    try:
        # Configure MySQL connection
        mysql_connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='abyudaya'
        )

        cursor = mysql_connection.cursor()
        
        cursor.execute("SELECT * FROM scores01 ORDER BY score DESC, transaction_time ASC;")

        # Fetch all rows
        scores = cursor.fetchall()

        # Close cursor and MySQL connection
        cursor.close()
        mysql_connection.close()

        return render_template('round1/scores01.html', scores=scores)
    
    except Exception as e:
        return render_template('submitted.html')

@app.route('/submit2', methods=['POST'])
def submit2():
    if request.method == 'POST':
        language = request.json['language']
        code = request.json['code']
        question_number = request.json['questionNumber']
        question_number_int = int(question_number)
        team_name = session['team_name']
        submission_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Store the results and other information in a text file
        file_name = f"{team_name}_question_{question_number_int+1}_{submission_time}.txt"
        folder_path = "round2_solutions"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        with open(os.path.join(folder_path, file_name), 'w') as file:
            file.write(f"Team Name: {team_name}\n")
            file.write(f"Submission Time: {submission_time}\n")
            file.write(f"Question Number: {question_number_int + 1}\n")
            file.write(f"Language: {language}\n")
            file.write("\nCode:\n")
            file.write(code)
            
        # Return the results as JSON
        return jsonify({'message': f'Question {question_number_int + 1} submitted'}), 200


if __name__ == "__main__":
    # Run the Flask app on localhost (local system)
    app.run(host='127.0.0.1', port=5000, debug=True)
    
    # Run the Flask app on all network interfaces (local network)
    app.run(host='0.0.0.0', port=5000, debug=True)

