from flask import Flask, jsonify, render_template, request, redirect, url_for,flash
from transformers import pipeline
from Querypart import Queries
from flask_cors import CORS
import os
import pandas as pd
app = Flask(__name__,template_folder=os.path.abspath('templates'))
CORS(app)
qa_pipeline = pipeline("text-generation", model="gpt2")
excel_file_path = "general_questions.xlsx"  # Path to your Excel file
questions_df = pd.read_excel(excel_file_path)

table = Queries(dbname="kids")
#main page
@app.route('/')
def main():
    return render_template('main.html')
@app.route('/service')
def service():
    return render_template('service.html')

# contact_page
@app.route('/admin_contact')
def admin_contact():
    return render_template('admin_contact.html')

# admin_login_page
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        result = table.check_login(email, password)
        if result and len(result) > 0:
            current_user = result[0][0]  # Extracting user_id
            third_grade_marks = result[0][1]
            fourth_grade_marks = result[0][2]
            
            response = redirect(url_for('enter_marks', user_id=current_user))
            response.set_cookie('user_id', str(current_user))  # Optionally set a cookie
            
            if third_grade_marks and fourth_grade_marks:
                return redirect(url_for('user_dashboard', user_id=current_user))
            
            return response
        else:
            # flash("Invalid email or password")
            error_message = "user not exit Please Sign up!"
            return render_template('user_login.html', error=error_message)
            # return redirect(url_for('user_login'))
    
    return render_template("user_login.html")

@app.route('/user_dashboard/<int:user_id>',methods=['GET'])
def user_dashboard(user_id):
        user_info = table.get_current_user_info(user_id)
        if user_info:
            user_name = user_info[0][0]
        
        # Fetch additional details about the user
        user_details = table.get_user_details(user_id)
        classification = user_details[0][1] if user_details else 'Unknown'
        classes = user_details[0][0]
        return render_template('user_dashboard.html',user_name=user_name,classification=classification,user_id=user_id,classes=classes)

@app.route('/enter_marks/<int:user_id>', methods=['GET', 'POST'])
def enter_marks(user_id):
    if request.method == 'POST':
        third_grade_marks = request.form.get('third_grade_marks')
        fourth_grade_marks = request.form.get('fourth_grade_marks')
        table.update_marks(user_id, third_grade_marks, fourth_grade_marks)
        return render_template('quize.html')

    return render_template('enter_marks.html', user_id=user_id)

# user_sign_up_page
@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    return render_template('user_signup.html')

@app.route('/add_user', methods=['POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['conform_password']
        student_class = request.form['class']
        email_exists = list(table.check_email(email))
        
        if email_exists:
            error_message = "User already exists"
            return render_template('user_signup.html', error=error_message)
        
        # Check if passwords match
        if password != confirm_password:
            error_message = "Passwords do not match"
            return render_template('user_signup.html', error=error_message)
        
        new_user = table.insert('user', f"'{name}','{email}','{password}','{confirm_password}','{student_class}'", "name,email,password,conform_password,class")
        
        if new_user:
            return redirect(url_for('user_login'))
        
        return render_template('user_signup.html', error="User creation failed")

    return redirect(url_for('user_signup'))

@app.route('/submit_results', methods=['POST'])
def submit_results():
    data = request.json
    user_id = data.get('user_id')
    score = data.get('score')
    percentage = data.get('percentage')
    # third_percentage=data.get('')
    
    print(f"Received data: user_id={user_id}, score={score}, percentage={percentage}")
    
    if user_id and score is not None and percentage is not None:
        # Update the user's score and percentage in the database
        result = table.text.execute(f"""
            UPDATE user 
            SET score = {score}, percentage = {percentage} 
            WHERE user_id = {user_id};
        """)
        table.database.commit()
        
        print(f"Updated user {user_id} with score {score} and percentage {percentage}")
        
        classify_student(user_id, score, percentage)  # Call classification function
        
        if result:
            return jsonify({'message': 'Your results have been submitted successfully!'})
        else:
            return jsonify({'message': 'Submit your results.'}), 500
    
    return jsonify({'message': 'Invalid data.'}), 400



@app.route('/count_details')
def count_details():
    user_count=int(table.user_count()[0][0])
    return render_template('count_details.html',user_count=user_count)

@app.route('/status_view/<int:user_id>', methods=['GET'])
def status_view(user_id):
    user_info = table.get_current_user_info(user_id)
    if user_info:
        user_name = user_info[0][0]
        
        # Fetch additional details about the user
        user_details = table.get_user_details(user_id)
        classification = user_details[0][6] if user_details else 'Unknown'
        
        return render_template('status_view.html',user_id=user_id, user_name=user_name, classification=classification)
    else:
        return redirect(url_for('user_login'))



@app.route('/classification_results')
def classification_results():
    results = table.get_classification_results()
    print(results)
    return render_template('classification_results.html', results=results)

def classify_student(user_id, score, percentage):
    # Define thresholds for classification based on both percentage and marks
    classification = 'Unknown'
    
    # Example thresholds
    poor_threshold_percentage = 50
    average_threshold_percentage = 75
    poor_threshold_marks = 40  # Example threshold for poor marks
    average_threshold_marks = 60  # Example threshold for average marks
    
    if percentage < poor_threshold_percentage :
        classification = 'poor'
    elif percentage < average_threshold_percentage:
        classification = 'average'
    else:
        classification = 'advanced'
    
    # Map classification to human-readable format
    classification_mapping = {
        'poor': 'Poor',
        'average': 'Average',
        'advanced': 'Advanced'
    }
    
    predicted_class = classification_mapping.get(classification, 'Unknown')
    print(f"Prediction for user_id {user_id}: {predicted_class}")
    
    # Update the classification in the database
    table.update_classification(user_id, predicted_class)
    print(f"Updated classification for user_id {user_id} to {predicted_class}")


@app.route('/material_page/<classification>')
def material_page(classification):
    if classification == 'Advanced':
        return render_template('advanced_materials.html')
    elif classification == 'Average':
        return render_template('avarage_materials.html')
    elif classification == 'Poor':
        return render_template('poor_materials.html')
    else:
        return redirect(url_for('main'))
@app.route('/scramble')
def scramble():
    return render_template('scramble.html')

@app.route('/admin_dashboard/<class_name>')
def admin_dashboard(class_name):
    # Fetch students by class
    students_performance = table.get_students_by_class(class_name)
    if not students_performance:
        print("No students found in this class!")  # Add this line to check
    else:
        print(f"Students fetched for {class_name}: {students_performance}")

    # Insights on poorly performing students
    weak_students = [student for student in students_performance if student[3] == 'Poor']

    return render_template('admin_dashboard.html', class_name=class_name, students=students_performance, weak_students=weak_students)

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get("question", "").strip()

    if not user_input:
        return jsonify({"error": "No question provided!"}), 400
    for _, row in questions_df.iterrows():
        if user_input == row["Question"].strip().lower():
            return jsonify({"answer": row["Answer"]})

    # Check if the input is a math expression (simple check using '×', '+', '-', etc.)
    if any(op in user_input for op in ['+', '-', '×', '÷', '*', '/']):
        try:
            # Attempt to evaluate the math expression
            user_input = user_input.replace("×", "*").replace("÷", "/")  # Normalize multiplication and division symbols
            result = str(sp.sympify(user_input))  # Use sympy for safe evaluation of mathematical expressions
            return jsonify({"answer": f"The result is: {result}"})
        except Exception as e:
            return jsonify({"error": f"Error in math expression: {str(e)}"}), 400

    # If it's not a math expression, generate a response from the model (automatic and dynamic)
    response = qa_pipeline(user_input, max_length=50, num_return_sequences=1)
    
    answer = response[0]['generated_text']
    return jsonify({"answer": answer.strip()})
@app.route('/chart_bot')
def chart_bot():
    # Render the chart_bot.html page
    return render_template('chart_bot.html')
@app.route('/games')
def game():
    return render_template('games.html')

if __name__ == '__main__':
    app.run(debug=True)
# gpt-3.5-turbo

