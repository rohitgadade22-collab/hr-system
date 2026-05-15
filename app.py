from flask import Flask, render_template,request, redirect, url_for,jsonify
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

@app.route('/get_positions/<int:department_id>')
def get_positions(department_id):

    print("Department ID:", department_id)  # Debugging statement
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            Id,
            Position
        FROM Poitions
        WHERE DId = ?
    """, (department_id,))

    positions = cursor.fetchall()

    conn.close()

    position_list = []

    for item in positions:

        position_list.append({
            'Id': item.Id,
            'Position': item.Position
        })

    return jsonify(position_list)

@app.route('/employees', methods=['GET', 'POST'])
def employees():

    conn = get_connection()

    cursor = conn.cursor()

    # INSERT EMPLOYEE
    if request.method == 'POST':

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        empid = request.form['empid']
        phone = request.form['phone']
        department = request.form['department']
        position = request.form['position']
        joining_date = request.form['joining_date']
        address = request.form['address']

        cursor.execute("""
            INSERT INTO Employee
            (
                FirstName,
                LastName,
                Email,
                EmployeeId,
                Phone,
                Department,
                Position,
                JoiningDate,
                Address,
                CreatedDate
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE()
            )
        """,
        first_name,
        last_name,
        email,
        empid,
        phone,
        department,
        position,
        joining_date,
        address)

        conn.commit()

        return redirect(url_for('employees'))

    # FETCH DEPARTMENTS
    cursor.execute("""
        SELECT
            Id,
            Department
        FROM Department
        ORDER BY Department
    """)

    departments = cursor.fetchall()

    # FETCH POSITIONS
    cursor.execute("""
        SELECT
            Id,
            Position
        FROM Poitions
        ORDER BY Position
    """)

    positions = cursor.fetchall()

    # FETCH EMPLOYEES
    cursor.execute("""

        SELECT

            E.Id,
            E.FirstName,
            E.LastName,
            E.Email,
            E.Phone,
            D.Department,
            P.Position,
            E.JoiningDate

        FROM Employee E

        INNER JOIN Department D
            ON E.Department = D.Id

        INNER JOIN Poitions P
            ON E.Position = P.Id

        ORDER BY E.Id DESC

    """)

    employees = cursor.fetchall()

    conn.close()

    return render_template(
        'employees.html',
        employees=employees,
        departments=departments,
        positions=positions,
        active_page='employees'
    )

@app.route('/attendance')
def attendance():
    return render_template(
        'attendance.html',
        active_page='attendance'
    )

#@app.route('/department')
#def department():
#    return render_template(
#        'department.html',
#        active_page='department'
#    )

# ==============================
# Position Page
# ==============================

@app.route('/position', methods=['GET', 'POST'])
def position():

    conn = get_connection()

    cursor = conn.cursor()

    # INSERT POSITION
    if request.method == 'POST':

        department_id = request.form['department']

        position_name = request.form['position_name']

        cursor.execute("""
            INSERT INTO Poitions
            (
                DId,
                Position
            )
            VALUES (?, ?)
        """,
        department_id,
        position_name)

        conn.commit()

        return redirect(url_for('position'))

    # FETCH DEPARTMENTS
    cursor.execute("""
        SELECT
            Id,
            Department
        FROM Department
        ORDER BY Department
    """)

    departments = cursor.fetchall()

    # FETCH POSITIONS
    cursor.execute("""
        SELECT
            P.Id,
            D.Department,
            P.Position
        FROM Poitions P
        INNER JOIN Department D
            ON P.DId = D.Id
        ORDER BY P.Id DESC
    """)

    positions = cursor.fetchall()

    conn.close()

    return render_template(
        'position.html',
        departments=departments,
        positions=positions,
        active_page='position'
    )


# ==============================
# Department Page
# ==============================


@app.route('/department', methods=['GET', 'POST'])
def department():

    conn = get_connection()

    cursor = conn.cursor()

    # INSERT
    if request.method == 'POST':

        department_name = request.form['department_name']

        cursor.execute("""
            INSERT INTO Department
            (
                Department
            )
            VALUES (?)
        """, department_name)

        conn.commit()

        return redirect(url_for('department'))

    # FETCH
    cursor.execute("""
        SELECT
            Id,
            Department
        FROM Department
        ORDER BY Id DESC
    """)

    departments = cursor.fetchall()

    conn.close()

    return render_template(
        'department.html',
        departments=departments,
        active_page='department'
    )


if __name__ == '__main__':
    app.run(debug=True)