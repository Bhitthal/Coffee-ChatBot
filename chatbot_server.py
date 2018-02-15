from flask import Flask,  render_template, redirect, url_for, request
app = Flask(__name__)
from chatbot_v2 import respond

app = Flask(__name__)

@app.route('/chat123/<sentence>')
def chat_server(sentence):
	return respond(sentence)

@app.route('/chat',methods = ['GET', 'POST'])
def chitchat():
   if request.method == 'POST':
      query = request.form['sent']
      print(query)
      return redirect(url_for('chat_server',sentence = query))
   else:
      query = request.args.get('sent')
      print(query)
      return redirect(url_for('chat_server',sentence = query))

@app.route("/")
def index():
   return render_template("first.html")


if __name__ == '__main__':
	app.debug = True
	#app.run()
	app.run(debug = True)