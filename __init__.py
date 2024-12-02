from flask import Flask, render_template, request, send_file
import os
from parser import parse_and_generate_excel

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_link = request.form['url']
        user_page = request.form['page']
        
        if user_link:
            csv_file = parse_and_generate_excel(user_link,int(user_page))
            return send_file(csv_file, as_attachment=True)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
