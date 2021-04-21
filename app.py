from flask import Flask, render_template, url_for, request,redirect,Response
from flask.globals import current_app
from flask.helpers import flash
from flaskext.mysql import MySQL
import os
import pymysql.cursors

app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_DB'] = 'student-portal'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''

mysql = MySQL(app, cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/student/portal', methods=['GET', 'POST'])
def student_portal():
    if request.method == 'POST':
        form_data = request.form
        first_name = form_data['fname']
        middle_name = form_data['mname']
        last_name = form_data['lname']
        email = form_data['email']
        dob = form_data['dob']
        gender = form_data['gndr']
        phone = form_data['phone']
        address = form_data['address']
        state = form_data['state']
        lg = form_data['lg']
        kin = form_data['kin']
        score = form_data['score']
        # vallidation
        if first_name=='' or middle_name=='' or last_name=='' or email=='' or dob=='' or gender=='' or phone==''\
            or address=='' or state =='' or lg=='' or kin=='' or score=='':
            flash('Please fill valid details in all fields', 'danger')
            return redirect(url_for('student_portal'))
        # image handling
        image_name = ''
        image = request.files['image']
        if image:
            image_name = first_name+middle_name+last_name+'.png'
            filepath = os.path.join(current_app.root_path,'static/uploads/'+image_name)
            image.save(filepath)
        # saving the info to the database
        conn= mysql.get_db()
        if conn:
            cursor=conn.cursor()
            cursor.execute('insert into students (image,firstname, surname, middlename, email, date_of_birth, gender, phone, address,state_of_origin,local_govt,next_of_kin,jamb_score)\
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',\
                (image_name,first_name,last_name,middle_name,email,dob,gender,phone,address,state,lg,kin,score))
            conn.commit()
            return redirect(url_for('students_index'))
        else:
            flash('Unable to save the information. Please try again later')
            return redirect(url_for('student_portal'))
    return render_template('portal_form.html')


@app.route('/admin/portal', methods=['GET'])
def students_index():
    conn = mysql.get_db()
    cursor = conn.cursor()
    cursor.execute('select * from students')
    students = cursor.fetchall()
    return render_template('students_index.html', students=students)


@app.route('/admin/students/<id>', methods=['GET'])
def student_details(id):
    student_id=id
    conn = mysql.get_db()
    cursor = conn.cursor()
    cursor.execute('select * from students where id=%s', student_id)
    student = cursor.fetchall()[0]
    return render_template('student_details.html', student=student)

@app.route('/admin/change_status/<id>', methods=['POST'])
def status_change(id):
    student_id = id
    admisssion_status = request.form['value']
    conn = mysql.get_db()
    cursor = conn.cursor()
    cursor.execute('update students set admission=%s where id=%s', (admisssion_status,student_id))
    conn.commit()
    return Response(admisssion_status, status=200)

if __name__ == '__main__':
    app.run(debug=True)