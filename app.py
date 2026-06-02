from flask import Flask, request, redirect, send_from_directory, render_template_string
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DATABASE = "applications.db"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==========================
# DATABASE SETUP
# ==========================

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        role TEXT NOT NULL,
        salary TEXT,
        location TEXT,
        status TEXT DEFAULT 'Applied',
        favorite INTEGER DEFAULT 0,
        resume TEXT,
        applied_date TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ==========================
# HOME PAGE
# ==========================

@app.route("/")
def home():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM applications
        ORDER BY favorite DESC, id DESC
    """)

    applications = cursor.fetchall()

    total = len(applications)

    interviews = len(
        [a for a in applications if a[5] == "Interview"]
    )

    offers = len(
        [a for a in applications if a[5] == "Offer"]
    )

    conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Dream Job Tracker</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>

<style>
*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    font-family:'Segoe UI',sans-serif;
}

body{
    min-height:100vh;
    padding:30px;
    background:linear-gradient(
        135deg,
        #6a11cb,
        #2575fc,
        #00d4ff
    );
    background-size:400% 400%;
    animation:bgMove 12s ease infinite;
    color:white;
}

@keyframes bgMove{

    0%{
        background-position:0% 50%;
    }

    50%{
        background-position:100% 50%;
    }

    100%{
        background-position:0% 50%;
    }

}

.container{
    max-width:1400px;
    margin:auto;
}

h1{
    text-align:center;
    margin-bottom:10px;
}

.subtitle{
    text-align:center;
    margin-bottom:25px;
}

#themeBtn{
    position:fixed;
    top:20px;
    right:20px;
    z-index:999;
}

.dashboard{
    display:flex;
    gap:20px;
    margin-bottom:20px;
}

.card{
    flex:1;
    background:rgba(255,255,255,0.9);
    color:black;
    padding:20px;
    border-radius:20px;
    text-align:center;
    box-shadow:0 8px 20px rgba(0,0,0,0.2);
    transition:.3s;
}

.card:hover{
    transform:translateY(-5px);
}

form{
    background:white;
    color:black;
    padding:20px;
    border-radius:20px;
    margin-bottom:20px;
    box-shadow:0 5px 15px rgba(0,0,0,.2);
}

input,
select{
    width:100%;
    padding:12px;
    margin:8px 0;
    border-radius:10px;
    border:1px solid #ddd;
}

.favorite-box{
    margin:10px 0;
}

.favorite-box input{
    width:auto;
}

button{
    padding:12px;
    border:none;
    border-radius:10px;
    cursor:pointer;
    transition:.3s;
}

button:hover{
    transform:scale(1.05);
}

form button{
    width:100%;
    background:#2575fc;
    color:white;
}

#search{
    margin-bottom:20px;
}

table{
    width:100%;
    border-collapse:collapse;
    background:white;
    color:black;
    overflow:hidden;
    border-radius:15px;
}

th{
    background:#2575fc;
    color:white;
}

th,td{
    padding:12px;
    border:1px solid #ddd;
    text-align:center;
}

tr:hover{
    background:#f4f7ff;
}

.badge{
    color:white;
    padding:5px 10px;
    border-radius:20px;
}

.applied{
    background:#3498db;
}

.interview{
    background:#f39c12;
}

.offer{
    background:#2ecc71;
}

.rejected{
    background:#e74c3c;
}

.action-btn{
    text-decoration:none;
    padding:6px 10px;
    border-radius:8px;
    color:white;
    margin:2px;
    display:inline-block;
}

.download{
    background:#2ecc71;
}

.favorite{
    background:#f39c12;
}

.delete{
    background:#e74c3c;
}

.chart-container{
    background:white;
    margin-top:30px;
    padding:20px;
    border-radius:20px;
}

.dark{
    background:#121212;
}

.dark form,
.dark table,
.dark .card,
.dark .chart-container{
    background:#1f1f1f;
    color:white;
}

.dark th{
    background:#333;
}

@media(max-width:768px){

    body{
        padding:15px;
    }

    .dashboard{
        flex-direction:column;
    }

    table{
        font-size:12px;
    }

}
</style>

</head>

<body>

<button id="themeBtn">
🌙 Dark Mode
</button>

<div class="container">

<h1>🚀 Dream Job Tracker</h1>

<p class="subtitle">
Track all your job applications in one place
</p>

<div class="dashboard">

<div class="card">
<h2>{{ total }}</h2>
<p>Total Applications</p>
</div>

<div class="card">
<h2>{{ interviews }}</h2>
<p>Interviews</p>
</div>

<div class="card">
<h2>{{ offers }}</h2>
<p>Offers</p>
</div>

</div>

<form action="/add" method="POST" enctype="multipart/form-data">

<input type="text"
name="company"
placeholder="🏢 Company Name"
required>

<input type="text"
name="role"
placeholder="👨‍💻 Job Role"
required>

<input type="text"
name="salary"
placeholder="💰 Salary">

<input type="text"
name="location"
placeholder="📍 Location">

<select name="status">

<option value="Applied">Applied</option>
<option value="Interview">Interview</option>
<option value="Offer">Offer</option>
<option value="Rejected">Rejected</option>

</select>

<div class="favorite-box">

<input type="checkbox"
id="favorite"
name="favorite">

<label for="favorite">
⭐ Favorite Company
</label>

</div>

<input type="file" name="resume">

<button type="submit">
Save Application
</button>

</form>

<input
type="text"
id="search"
placeholder="🔍 Search Applications">

<table id="jobTable">

<thead>

<tr>

<th>Company</th>
<th>Role</th>
<th>Salary</th>
<th>Location</th>
<th>Status</th>
<th>Favorite</th>
<th>Resume</th>
<th>Date</th>
<th>Actions</th>

</tr>

</thead>

<tbody>

{% for app in applications %}

<tr>

<td>{{ app[1] }}</td>
<td>{{ app[2] }}</td>
<td>{{ app[3] }}</td>
<td>{{ app[4] }}</td>

<td>

<span class="badge {{ app[5]|lower }}">

{{ app[5] }}

</span>

</td>

<td>

<a
class="action-btn favorite"
href="/favorite/{{ app[0] }}">

{% if app[6] == 1 %}
⭐
{% else %}
☆
{% endif %}

</a>

</td>

<td>

{% if app[7] %}

<a
class="action-btn download"
href="/resume/{{ app[7] }}">

📄 Download

</a>

{% else %}

No Resume

{% endif %}

</td>

<td>{{ app[8] }}</td>

<td>

<a
class="action-btn delete"
href="/delete/{{ app[0] }}"
onclick="return confirm('Delete this application?')">

🗑 Delete

</a>

</td>

</tr>

{% endfor %}

</tbody>

</table>

<div class="chart-container">

<canvas id="myChart"></canvas>

</div>

</div>

<script>

const total = {{ total }};
const interviews = {{ interviews }};
const offers = {{ offers }};

new Chart(
document.getElementById("myChart"),
{
type:"bar",
data:{
labels:[
"Applications",
"Interviews",
"Offers"
],
datasets:[{
label:"Statistics",
data:[
total,
interviews,
offers
]
}]
}
}
);

document.getElementById("themeBtn")
.addEventListener("click",function(){

document.body.classList.toggle("dark");

});

document.getElementById("search")
.addEventListener("keyup",function(){

let filter =
this.value.toLowerCase();

let rows =
document.querySelectorAll(
"#jobTable tbody tr"
);

rows.forEach(row=>{

let text =
row.innerText.toLowerCase();

row.style.display =
text.includes(filter)
? ""
: "none";

});

});

document.querySelector("form")
.addEventListener("submit",function(){

confetti({
particleCount:150,
spread:90
});

});

</script>

</body>
</html>
""",
applications=applications,
total=total,
interviews=interviews,
offers=offers
)


@app.route("/add", methods=["POST"])
def add():

    company = request.form.get("company")
    role = request.form.get("role")
    salary = request.form.get("salary")
    location = request.form.get("location")
    status = request.form.get("status")

    favorite = 1 if request.form.get("favorite") else 0

    filename = ""

    if "resume" in request.files:

        file = request.files["resume"]

        if file.filename != "":

            filename = (
                datetime.now().strftime("%Y%m%d%H%M%S")
                + "_"
                + file.filename
            )

            file.save(
                os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )
            )

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
    """
    INSERT INTO applications
    (
    company,
    role,
    salary,
    location,
    status,
    favorite,
    resume,
    applied_date
    )
    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
    company,
    role,
    salary,
    location,
    status,
    favorite,
    filename,
    datetime.now().strftime(
    "%d-%m-%Y %H:%M"
    )
    )
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/favorite/<int:id>")
def favorite(id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
    """
    UPDATE applications
    SET favorite =
    CASE
    WHEN favorite = 1
    THEN 0
    ELSE 1
    END
    WHERE id=?
    """,
    (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
    "DELETE FROM applications WHERE id=?",
    (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/resume/<filename>")
def resume(filename):

    return send_from_directory(
    UPLOAD_FOLDER,
    filename,
    as_attachment=True
    )


if __name__ == "__main__":

    app.run(
    debug=True,
    host="0.0.0.0",
    port=5000
    )