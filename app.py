from flask import Flask, render_template, request, flash, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'dharshan.bro.secret.key'

# Database setup functions
def get_db_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users_signup.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
        cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        
        flash('Signup Successful!', 'success')
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/home')
def home():
    if 'username' in session:
        username=session['username']
        return render_template('home.html',usernam=username)
    else:
        return redirect(url_for('login'))

@app.route('/set_city', methods=['POST', 'GET'])
def set_city():
    if request.method == 'POST':
        value = request.form['city']
        session['s_city'] = value
        flash(f'City set to {value.capitalize()}', 'success')
        return redirect(url_for('get_distance'))
    return render_template('city.html')

@app.route('/get_distance', methods=['POST', 'GET'])
def get_distance():
    dist = None
    costkm = None
    avail_vehi = None
    from_di = None
    to_di = None
    vandi = None
    s_city = session.get('s_city')
    
    if request.method == 'POST':
        from_di = request.form['from_di']
        to_di = request.form['to_di']
        vandi = request.form['vandi']
        
        with get_db_connection('distances.db') as conn:
            cur = conn.cursor()
            q1 = 'SELECT distance FROM distance WHERE (Location_A=? AND Locaton_B=?) OR (Location_A=? AND Locaton_B=?)'
            cur.execute(q1, (from_di, to_di, to_di, from_di))
            res = cur.fetchone()
        
        if res:
            with get_db_connection('vehicle.db') as conn:
                cur = conn.cursor()
                q2 = 'SELECT cost FROM vehicle_list WHERE vehicle=?'
                cur.execute(q2, (vandi,))
                cost = cur.fetchone()
                
                q3 = 'SELECT avail FROM vehicle_list WHERE vehicle=?'
                cur.execute(q3, (vandi,))
                avail = cur.fetchone()
                
                if avail and avail[0] == 0:
                    dist = res[0]
                    costkm = cost[0] * dist
                    avail_vehi = 1
                else:
                    avail_vehi=2
    
    return render_template('vehicle.html', distance=dist, cost=costkm, from_dist=from_di, to=to_di, wandi=vandi, availability=avail_vehi, city=s_city)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users_signup.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        conn.close()
        
        if user and user[1] == password:
            session['username'] = username
            flash('Login Successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid Credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
