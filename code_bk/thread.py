from threading import *
import time

def test(v, d, c):
    for _ in range(c):
        print(v, end='')
        time.sleep(d)

t1 = Thread(target=test, args=(1,0.1,60))
t2 = Thread(target=test, args=(3,0.3,20))
t3 = Thread(target=test, args=(5,0.5,12))
t4 = Thread(target=test, args=(10,1,6))

t1.start()
t2.start()
t3.start()
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()
print("Main Thread")
