from threading import Thread, Lock
import time
import sys
from datetime import datetime

threadLock = Lock()

class myThread (Thread):
    def __init__(self, threadID, name):
      Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.msg = []
      self.logs = "Thread"+str(threadID)+".txt"
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
    def putlogs(self, code):
        if code == 1:
            f = open(self.logs, "a")
            f.write(str(datetime.now()) + "   Putting message in node " + str(self.threadID) + "\n")
            f.close()
        elif code == 2:
            f = open(self.logs, "a")
            f.write(str(datetime.now()) + "   Reading message from tail node " + str(self.threadID) + "\n")
            f.close()
        elif code == 3:
            f = open(self.logs, "a")
            f.write(str(datetime.now()) + "   Removing node " + str(self.threadID) + "\n")
            f.close()
        elif code == 4:
            f = open(self.logs, "a")
            f.write(str(datetime.now()) + "   Adding node to tail " + str(self.threadID) + "\n")
            f.close()
    def getlogs(self):
        f = open(self.logs, "r")
        print("Logs of Node " + str(self.threadID))
        lines = f.readlines()
        for line in lines:
            print(line)
        f.close()

    
def getData(thread):
    #print data and thread id
    msg = thread.getmsg()
    print("reading from thread", thread.getthreadID())
    thread.putlogs(2)
    response = ""
    if len(msg) == 0:
        response = "No msgs yet!!"
    else:
        response = msg[-1]
    return response

def deleteNode(threads, id):
    #delete node, if the node is first or last, successor is made leader or reads from predecessor resp
    #print current leader and read-only server
    for i in range(len(threads)):
        print("ThreadID: ", threads[i].getthreadID())
        if threads[i].getthreadID() == id:
            #if thread is not the tail and chain is consistent
            print("n1", threads[i].getmsg()[-1])
            if i < len(threads) - 1 and threads[i].getmsg()[-1] == threads[i+1].getmsg()[-1]:
                print("n2", threads[i+1].getmsg()[-1])
                threads[i].join()
                threads[i].putlogs(3)
                threads.remove(threads[i])
                break
            
            #if thread is tail - no consistency check is required
            elif i == len(threads) - 1:
                threads[i].join()
                threads[i].putlogs(3)
                threads.remove(threads[i])
                break

            #if intermediate node and message wasn't propagated through the chain by the node
            elif threads[i].getmsg()[-1] != threads[i+1].getmsg()[-1]:
                print("n2", threads[i+1].getmsg()[-1])
                j = i+1
                while j < len(threads) - 1:
                    threads[j+1].putmsg(threads[i].getmsg()[-1])
                    threads[j+1].putlogs(1)
                    j += 1
                threads[i].join()
                threads[i].putlogs(3)
                threads.remove(threads[i])
                break
    return 1

def addNode(threads, id):
    #adds a node to the tail
    thread = myThread(id+1, "Thread"+str(id+1))
    thread.start()
    threads.append(thread)
    thread.putlogs(4)
    #Update new tail info from previous tail
    #print(threads[-2].getmsg())
    for m in threads[-2].getmsg():
        thread.putmsg(m)
        thread.putlogs(1)
    return

def propogateMsg(threads, msg):
    threads[0].putmsg(msg)
    threads[0].putlogs(1)
    i = 0
    while i < len(threads) - 1:
        threads[i+1].putmsg(threads[0].getmsg()[-1])
        threads[i+1].putlogs(1)
        i += 1
        print("put msg in node", i+1)
    return
    


numThreads = int(sys.argv[1])
threads = []
for i in range(numThreads):
    thread = myThread(i+1, "Thread"+str(i+1))
    thread.start()
    print("Starting " + thread.name)
    threads.append(thread)

print(threads)

while True:
    print("*****MENU*****")
    print("1. Enter data")
    print("2. Read data")
    print("3. Delete a node")
    print("4. Add a node")
    print("5. View logs")
    print("6. Exit")
    a = int(input())
    if a == 1:
        print("Enter message")
        msg = input()
        propogateMsg(threads, msg)
    elif a == 2:
        print(getData(threads[-1]))
    elif a == 3:
        print("Current Leader:", threads[0])
        print("Current reads node", threads[-1])
        print(threads)
        print("Please enter the index of the thread(1-based indexing)")
        id = int(input())
        deleteNode(threads, id)
        #If all threads have been deleted - terminate program
        if len(threads) == 0:
            print("Zero threads in the chain!")
            break
        print("Current Leader:", threads[0])
        print("Current reads node", threads[-1])
    elif a == 4:
        print("Current Leader:", threads[0])
        print("Current reads node", threads[-1])
        print("before adding", threads)
        id = threads[-1].getthreadID()
        addNode(threads, id)
        print("\n----------------------------\nafter adding", threads)
        print("Current Leader:", threads[0])
        print("Current reads node", threads[-1])  
    elif a == 5:
        for i in threads:
            i.getlogs() 
    elif a == 6:
        break

for t in threads:
    t.join()
print ("Exiting Main Thread")
