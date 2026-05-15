from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/employees')
def employees():
    return render_template('employees.html')

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

if __name__ == '__main__':
    app.run(debug=True)