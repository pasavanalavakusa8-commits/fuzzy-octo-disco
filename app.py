from flask import Flask, request, jsonify, render_template_string, send_file
import pyrebase
import zipfile
import io
import json

app = Flask(__name__)

# Aapka Firebase Config (API Key apni real daal lena)
firebase_config = {
  "apiKey": "AIzaSyC... (APNI KEY YAHAN DAALEIN)",
  "authDomain": "upi-2-3aa4a.firebaseapp.com",
  "databaseURL": "https://upi-2-3aa4a-default-rtdb.firebaseio.com",
  "projectId": "upi-2-3aa4a",
  "storageBucket": "upi-2-3aa4a.firebasestorage.app",
  "messagingSenderId": "43372315924",
  "appId": "1:43372315924:web:170f0f7a9faa9f614eee01"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

# Basic HTML UI Route
@app.route('/')
def index():
    return '''
    <h2>My Secure Vault</h2>
    <form action="/login" method="POST">
        <input type="email" name="email" placeholder="Email" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <button type="submit">Login / Register</button>
    </form>
    '''

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    try:
        # Try to login, if fails, create account (Basic logic)
        user = auth.sign_in_with_email_and_password(email, password)
    except:
        user = auth.create_user_with_email_and_password(email, password)
    
    # Login hone ke baad dashboard dikhayenge jahan save aur download button honge
    return f'''
    <h3>Welcome!</h3>
    <p>Token: {user['idToken'][:10]}...</p>
    <a href="/download_zip?token={user['idToken']}&uid={user['localId']}"><button>Download All in ZIP</button></a>
    <hr>
    <h4>Save Data</h4>
    <form action="/save_data" method="POST">
        <input type="hidden" name="uid" value="{user['localId']}">
        <input type="text" name="type" placeholder="Type (password, call_history)" required><br>
        <textarea name="data" placeholder="Paste data here..." required></textarea><br>
        <button type="submit">Save to Firebase</button>
    </form>
    '''

@app.route('/save_data', methods=['POST'])
def save_data():
    uid = request.form['uid']
    data_type = request.form['type']
    data_content = request.form['data']
    
    # Data ko Firebase me user ki UID ke andar save karna
    db.child("users").child(uid).child(data_type).push(data_content)
    return "Data Saved! <a href='/'>Go Back</a>"

@app.route('/download_zip')
def download_zip():
    uid = request.args.get('uid')
    
    # Firebase se user ka saara data nikalna
    user_data = db.child("users").child(uid).get().val()
    
    if not user_data:
        return "No data found to download!"

    # Memory me ZIP file create karna (Storage me save kiye bina)
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        
        # Alg alg category ka data alg folder/file me save karna
        for category, items in user_data.items():
            # Example: category = 'passwords', 'images', 'call_history'
            folder_path = f"{category}/"
            
            # Combine all items into a single text or save separately
            content = json.dumps(items, indent=4)
            
            # ZIP ke andar file add karna
            zf.writestr(f"{folder_path}data.json", content)
            
            # Agar image base64 hai, toh usko decode karke .jpg me bhi save kar sakte hain yahan

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='My_Vault_Backup.zip'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
