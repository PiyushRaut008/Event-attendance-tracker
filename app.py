from flask import Flask, render_template, redirect, url_for, request, session, flash
from pymongo import MongoClient
app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.event_database
events_collection = db.events
students_collection = db.students

ADMIN_KEYS = {'12345', 'PIYUSH'}

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def loginhandle():
    if request.method == 'POST':
        admin_key = request.form.get('admin_key')
        if admin_key in ADMIN_KEYS:
            return render_template("sheet.html")
        else:
            return render_template('index.html') + "<script>alert('Access Denied !!!!');</script>"
    return render_template('index.html')

@app.route('/create_event', methods=['POST'])
def create_event():
    event_name = request.form['event_name']
    date = request.form['date']
    coordinator = request.form['coordinator']
    phone_no = request.form['phone_no']
    email_id = request.form['email_id']

    event = {
        'event_name': event_name,
        'date': date,
        'coordinator': coordinator,
        'phone_no': phone_no,
        'email_id': email_id
    }

    events_collection.insert_one(event)
    return redirect(url_for('event_list'))

@app.route('/event_list')
def event_list():
    events = events_collection.find({}, {'_id': 0, 'event_name': 1, 'date': 1})
    return render_template('event_list.html', events=events)

@app.route('/event_details')
def event_details():
    event_name = request.args.get('event_name')
    date = request.args.get('date')
    coordinator = request.args.get('coordinator')
    return render_template('create_event.html', event_name=event_name, date=date, coordinator=coordinator)

@app.route('/student_entry', methods=['GET', 'POST'])
def student_entry():
    if request.method == 'POST':
        event_name = request.form['event_name']
        student_name = request.form['student_name']
        roll_no = request.form['roll_no']
        branch = request.form['branch']
        college = request.form['college']
        semester = request.form['semester']
        phone_no = request.form['phone_no']
        email = request.form['email']
        date = request.form['date']

        student = {
            'event_name': event_name,
            'student_name': student_name,
            'roll_no': roll_no,
            'branch': branch,
            'college': college,
            'semester': semester,
            'phone_no': phone_no,
            'email': email,
            'date': date
        }

        students_collection.insert_one(student)
        return redirect(url_for('event_details', event_name=event_name, date=date, coordinator=request.form['coordinator']))
    
    event_name = request.args.get('event_name')
    date = request.args.get('date')
    coordinator = request.args.get('coordinator')
    return render_template('student_entry.html', event_name=event_name, date=date, coordinator=coordinator)

@app.route('/submit_student', methods=['POST'])
def submit_student():
    event_name = request.form['event_name']
    student_name = request.form['student_name']
    roll_no = request.form['roll_no']
    branch = request.form['branch']
    college = request.form['college']
    semester = request.form['semester']
    phone_no = request.form['phone_no']
    email = request.form['email']
    date = request.form['date']

    student = {
        'event_name': event_name,
        'student_name': student_name,
        'roll_no': roll_no,
        'branch': branch,
        'college': college,
        'semester': semester,
        'phone_no': phone_no,
        'email': email,
        'date': date
    }

    students_collection.insert_one(student)
    return "Data Entered Successfully"



@app.route('/delete_student', methods=['POST'])
def delete_student():
    
    roll_no = request.form['roll_no']
    students_collection.delete_one({'roll_no': roll_no})
    return "Data deleted"



@app.route('/update_student', methods=['POST'])
def update_student():
    roll_no = request.form['roll_no']
    student = students_collection.find_one({'roll_no': roll_no})
    return render_template('update_student.html', student=student)

@app.route('/submit_update', methods=['POST'])
def submit_update():
    roll_no = request.form['roll_no']
    
    students_collection.update_one(
        {'roll_no': roll_no},
        {
            '$set': {
                'student_name': request.form['student_name'],
                'college': request.form['college'],
                'branch': request.form['branch'],
                'semester': request.form['semester'],
                'phone_no': request.form['phone_no'],
                'email': request.form['email'],
                'date': request.form['date']
            }
        }
    )
    return redirect(url_for('view_data', event_name=request.form['event_name']))

@app.route('/class_data')
def class_data():
    return render_template('class_data.html')

@app.route('/display_students', methods=['GET'])
def display_students():
    branch = request.args.get('branch')
    college = request.args.get('college')
    semester = request.args.get('semester')
    date = request.args.get('date')

    query = {
        'branch': branch,
        'college': college,
        'semester': semester,
        'date': date
    }

    students = list(students_collection.find(query, {'_id': 0}))
    return render_template('display_students.html', students=students)


@app.route('/check_students')
def check_students():
    return render_template('check_students.html', result=None)



@app.route('/check_student', methods=['POST'])
def check_student():
    student_name = request.form['student_name']
    roll_no = request.form['roll_no']
    event_name = request.form['event_name']
    date = request.form['date']

    query = {
        'student_name': student_name,
        'roll_no': roll_no,
        'event_name': event_name,
        'date': date
    }

    student = students_collection.find_one(query)

    if student:
        result = "Yes this will present in that event"
    else:
        result = "There is no record of this student in that event"

    return render_template('check_students.html', result=result)


@app.route('/view_data')
def view_data():
    event_name = request.args.get('event_name')
    students = students_collection.find({'event_name': event_name}, {'_id': 0, 'student_name': 1, 'college': 1, 'roll_no': 1, 'branch': 1, 'semester': 1})
    return render_template('view_data.html', students=students)

if __name__ == '__main__':
    app.run(debug=True)
