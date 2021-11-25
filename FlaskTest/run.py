from flask import Flask, request, render_template, jsonify, render_template_string
from waitress import serve
from numpy import isnan
import json

from Apis import ReadJson, col_map, cols

app = Flask(__name__)
app.config["DEBUG"] = True

def replaceNaN(x):
    if isinstance(x, float):
        if isnan(x):
            return "否"
    return x

@app.route('/', methods=['GET'])
def my_form():
    return render_template('my-form.html')

# @app.route('/', methods=['POST'])
# def my_form_post():
#     return render_template('my-form.html')
    # text = request.form['text']
    # error_msg = '此代號無資料'    
    # if not len(text):
    #     return render_template('my-form.html', error_msg=error_msg)
    # text = text.upper()
    # data = [x for x in ReadJson() if text == x['STC_Ticker'] or text == x['FUT_Ticker']]
    # header = [col_map[col] for col in cols]
    # values = []
    # if data:
    #     for d in data:
    #         values.append([replaceNaN(d[col]) for col in cols])
    #     return render_template('my-form.html', header=header, values=values)
    # else:
    #     return render_template('my-form.html', header=header, value=values, error_msg=error_msg)
    # return text.upper()

@app.route('/api', methods=['POST'])
def UpdateStatus():
    params = request.args
    if not params:
        params = json.loads(request.data)
    text = params['stockId']
    error_msg = '此代號無資料'
    render_text = """
        
        <text> {{error_msg}}</text>
        <table>
            <tr>
                {% for head in header %}
                <th align="center">{{head}}</th>
                {% endfor %}
            </tr>
            {% for row in values %}
            <tr>
                {% for cell in row %}
                <td align="center">{{cell}}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </table>
    """
    if not len(text):
        return render_template_string(render_text, error_msg=error_msg)
    text = text.upper()
    data = [x for x in ReadJson() if text == x['STC_Ticker'] or text == x['FUT_Ticker']]
    header = [col_map[col] for col in cols]
    values = []
    
    if data:
        for d in data:
            values.append([replaceNaN(d[col]) for col in cols])
        return render_template_string(render_text, header=header, values=values)
    else:
        return render_template_string(render_text, header=header, value=values, error_msg=error_msg)
    return "test response" #jsonify("test response")

if __name__ == '__main__':
    serve(app, host='localhost', port=5000, threads=4)
    
    