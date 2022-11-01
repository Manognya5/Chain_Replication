from flask import Flask, request, redirect, url_for, render_template, session, send_from_directory, send_file, flash, abort, make_response
from threading import Thread, Lock
import time

app = Flask(__name__)

threadLock = Lock()

class myThread (Thread):
    def __init__(self, threadID, name):
      Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.msg = []
      self.logs = []
    def printmsg(self):
      print (self.msg)
    def getthreadID(self):
        return self.threadID
    def getname(self):
        return self.name
    def getmsg(self):
        return self.msg
    def putmsg(self, msg):
      threadLock.acquire()
      self.msg.append(msg)
      threadLock.release()

numThreads = 4
threads = []
for i in range(numThreads):
    thread = myThread(i+1, "Thread"+str(i+1))
    thread.start()
    print("Starting " + thread.name)
    threads.append(thread)

def propogateMsg(threads, msg):
    threads[0].putmsg(msg)
    #threads[0].putlogs(1)
    i = 0
    while i < len(threads) - 1:
        threads[i+1].putmsg(threads[0].getmsg()[-1])
        #threads[i+1].putlogs(1)
        i += 1
        print("put msg in node", i+1)
    return

def getData(thread):
    #print data and thread id
    msg = thread.getmsg()
    print("reading from thread", thread.getthreadID())
    #thread.putlogs(2)
    response = ""
    if len(msg) == 0:
        response = "No msgs yet!!"
    else:
        response = msg
    return response

length = 0
@app.route('/home')
def home():
	return render_template('index.html')

@app.route('/viewnotes', methods = ['GET', 'POST'])
def notes():

    if request.method == 'POST':
            note = request.form['note']	
            print(note)
            propogateMsg(threads, note)
            #session['note_ar'] += [note]  
            #length = len(session['note_ar']) 
    if len(session['note_ar']) > 0  :
        length = len(session['note_ar']) 
    notes = getData(threads[-1])
    return render_template('notes.html', notes=notes, length=len(notes))


if __name__ == '__main__':
	#app.run(host="0.0.0.0", port=80)
	app.secret_key = 'secret'
	app.debug = True
	app.run()
