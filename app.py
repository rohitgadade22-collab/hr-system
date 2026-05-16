from flask import Flask, render_template,request, redirect, url_for,jsonify
from database import get_connection
import configparser

app = Flask(__name__)
config = configparser.ConfigParser()

config.read('config.ini')

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
                CreatedDate,
                Status
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), 1
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

    # PAGE NUMBER
    page = request.args.get('page', 1, type=int)

    # PAGE SIZE FROM CONFIG
    per_page = int(
        config['pagination']['page_size']
    )

    # OFFSET
    offset = (page - 1) * per_page

    # TOTAL RECORDS
    cursor.execute("""
        SELECT COUNT(*)
        FROM Employee
    """)

    total_records = cursor.fetchone()[0]

    # TOTAL PAGES
    total_pages = (
        total_records + per_page - 1
    ) // per_page

    # FETCH EMPLOYEES WITH PAGINATION
    cursor.execute("""

        SELECT

            E.Id,
            E.FirstName,
            E.LastName,
            E.Email,
            E.EmployeeId,
            E.Phone,
            E.Address,

            E.Department AS DepartmentId,
            E.Position AS PositionId,

            D.Department,
            P.Position,

            E.JoiningDate,
            E.Status

        FROM Employee E

        INNER JOIN Department D
            ON E.Department = D.Id

        INNER JOIN Poitions P
            ON E.Position = P.Id

        ORDER BY E.Id DESC

        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY

    """, (offset, per_page))

    employees = cursor.fetchall()

    
    # TOTAL EMPLOYEES
    cursor.execute("""
        SELECT COUNT(*) AS TotalEmployees
        FROM Employee
    """)

    total_employees = cursor.fetchone()[0]
    # ACTIVE EMPLOYEES
    cursor.execute("""
    SELECT COUNT(*) AS ActiveEmployees
    FROM Employee
    WHERE Status = 1
    """)
    active_employees = cursor.fetchone()[0]

    # INACTIVE EMPLOYEES
    cursor.execute("""
        SELECT COUNT(*) AS InactiveEmployees
        FROM Employee
        WHERE Status = 0
    """)

    inactive_employees = cursor.fetchone()[0]

    

    

    conn.close()

    return render_template(
        'employees.html',
        employees=employees,
        departments=departments,
        positions=positions,
        total_employees=total_employees,
        active_employees=active_employees,
        inactive_employees=inactive_employees,
        page=page,
        total_pages=total_pages,
        active_page='employees'
    )

@app.route('/update_employee', methods=['POST'])
def update_employee():

    id = request.form['id']

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']
    department = request.form['department']
    position = request.form['position']
    joining_date = request.form['joining_date']
    address = request.form['address']
    status = request.form['status']

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE Employee

        SET

            FirstName = ?,
            LastName = ?,
            Email = ?,
            Phone = ?,
            Department = ?,
            Position = ?,
            JoiningDate = ?,
            Address = ?,
            Status = ?,
            ModifiedDate = GETDATE()

        WHERE Id = ?

    """,
    first_name,
    last_name,
    email,
    phone,
    department,
    position,
    joining_date,
    address,
    status,
    id)

    conn.commit()

    conn.close()

    return redirect(url_for('employees'))

@app.route('/attendance')
def attendance():

    conn = get_connection()

    cursor = conn.cursor()

    # FETCH ATTENDANCE
    cursor.execute("""

    SELECT

        A.Id,

        E.FirstName + ' ' + E.LastName
            AS EmployeeName,

        D.Department,

        A.CheckInTime,
        A.CheckOutTime,

        A.Status

    FROM Attendance A

    INNER JOIN Employee E
        ON A.EmployeeId = E.Id

    INNER JOIN Department D
        ON E.Department = D.Id

    WHERE
        A.AttendanceDate =
            CAST(GETDATE() AS DATE)

    ORDER BY A.Id DESC

    """)

    attendance = cursor.fetchall()

    # PRESENT COUNT
    cursor.execute("""

        SELECT COUNT(*)

        FROM Attendance

        WHERE
            AttendanceDate =
                CAST(GETDATE() AS DATE)

            AND Status = 'Present'

    """)

    present_count = cursor.fetchone()[0]

    # ABSENT COUNT
    cursor.execute("""

        SELECT COUNT(*)

        FROM Attendance

        WHERE
            AttendanceDate =
                CAST(GETDATE() AS DATE)

            AND Status = 'Absent'

    """)

    absent_count = cursor.fetchone()[0]

    # PENDING COUNT
    cursor.execute("""

        SELECT COUNT(*)

        FROM Employee E

        WHERE NOT EXISTS
        (
            SELECT 1

            FROM Attendance A

            WHERE
                A.EmployeeId = E.Id

                AND A.AttendanceDate =
                    CAST(GETDATE() AS DATE)
        )

    """)

    pending_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'attendance.html',
        attendance=attendance,
        present_count=present_count,
        absent_count=absent_count,
        pending_count=pending_count,
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