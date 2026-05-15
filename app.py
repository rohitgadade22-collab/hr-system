from flask import Flask, render_template
from database import get_connection

app = Flask(__name__)

# Check Database Connection
try:

    conn = get_connection()

    print("Database Connected Successfully")

    conn.close()

except Exception as e:

    print("Database Connection Failed")

    print(str(e))

@app.route('/')
def dashboard():
    return render_template(
        'dashboard.html',
        active_page='dashboard'
    )

@app.route('/employees')
def employees():
    return render_template(
        'employees.html',
        active_page='employees'
    )

@app.route('/attendance')
def attendance():
    return render_template(
        'attendance.html',
        active_page='attendance'
    )

@app.route('/department')
def department():
    return render_template(
        'department.html',
        active_page='department'
    )

@app.route('/position')
def position():
    return render_template(
        'position.html',
        active_page='position'
    )

if __name__ == '__main__':
    app.run(debug=True)