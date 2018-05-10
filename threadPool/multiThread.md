# Python 多线程

由于全局解释锁（GIL）的原因，Python 的线程被限制到同一时刻只允许一个线程执行这样一个执行模型。所以，Python 的线程更适用于处理I/O和其他需要并发执行的阻塞操作（比如等待I/O、等待从数据库获取数据等等），而不是需要多处理器并行的计算密集型任务。

Python的标准库提供了两个模块：_thread和threading，_thread是低级模块，threading是高级模块，对_thread进行了封装。绝大多数情况下，我们只需要使用threading这个高级模块。

## 使用Python线程
Python中使用线程有两种方式：函数或者用类来包装线程对象。

### 函数方式（_thread）
调用thread模块中的start_new_thread()函数来产生新线程。
```python
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import _thread as thread
import time


# 为线程定义一个函数
def print_time(threadName, delay):
    count = 0
    while count < 5:
        time.sleep(delay)
        count += 1
        print("{}: {}".format(threadName, time.ctime(time.time())))


# 创建两个线程
try:
    thread.start_new_thread(print_time, ("Thread-1", 1,))
    thread.start_new_thread(print_time, ("Thread-2", 2,))
except:
    print("Error: unable to start thread")

while True:
    pass
```
执行结果如下
```
Thread-1: Thu May 10 15:35:04 2018
Thread-2: Thu May 10 15:35:05 2018
Thread-1: Thu May 10 15:35:05 2018
Thread-1: Thu May 10 15:35:06 2018
Thread-2: Thu May 10 15:35:07 2018
Thread-1: Thu May 10 15:35:07 2018
Thread-1: Thu May 10 15:35:08 2018
Thread-2: Thu May 10 15:35:09 2018
Thread-2: Thu May 10 15:35:11 2018
Thread-2: Thu May 10 15:35:13 2018
```
线程的结束一般依靠线程函数的自然结束；也可以在线程函数中调用thread.exit()，他抛出SystemExit exception，达到退出线程的目的。

### 使用类包装线程对象
把一个函数传入并创建Thread实例，然后调用start()开始执行。
```
#!/usr/bin/python
# -*- coding: UTF-8 -*-

from threading import Thread
import time


# 为线程定义一个函数
def print_time(threadName, delay):
    count = 0
    while count < 5:
        time.sleep(delay)
        count += 1
        print("{}: {}".format(threadName, time.ctime(time.time())))


# 创建两个线程
t1 = Thread(target=print_time, args=("Thread-1", 1,))
t2 = Thread(target=print_time, args=("Thread-2", 2,))

t1.start()
t2.start()
t1.join()
t2.join()
```
执行结果如下
```
Thread-1: Thu May 10 15:57:27 2018
Thread-2: Thu May 10 15:57:28 2018
Thread-1: Thu May 10 15:57:28 2018
Thread-1: Thu May 10 15:57:29 2018
Thread-1: Thu May 10 15:57:30 2018
Thread-2: Thu May 10 15:57:30 2018
Thread-1: Thu May 10 15:57:31 2018
Thread-2: Thu May 10 15:57:32 2018
Thread-2: Thu May 10 15:57:34 2018
Thread-2: Thu May 10 15:57:36 2018
```
同时我们也可以自定义类，直接从threading.Thread继承，然后重写__init__方法和run方法：
```python
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
import time

exitFlag = 0


class myThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        print("Starting " + self.name)
        print_time(self.name, self.counter, 5)
        print("Exiting " + self.name)


def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            (threading.Thread).exit()
        time.sleep(delay)
        print("{}: {}".format(threadName, time.ctime(time.time())))
        counter -= 1


# 创建新线程
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# 开启线程
thread1.start()
thread2.start()

print("Exiting Main Thread")
```
执行结果如下：
```
Starting Thread-1
Starting Thread-2
Exiting Main Thread
Thread-1: Thu May 10 16:20:25 2018
Thread-2: Thu May 10 16:20:26 2018
Thread-1: Thu May 10 16:20:26 2018
Thread-1: Thu May 10 16:20:27 2018
Thread-1: Thu May 10 16:20:28 2018
Thread-2: Thu May 10 16:20:28 2018
Thread-1: Thu May 10 16:20:29 2018
Exiting Thread-1
Thread-2: Thu May 10 16:20:30 2018
Thread-2: Thu May 10 16:20:32 2018
Thread-2: Thu May 10 16:20:34 2018
Exiting Thread-2
```
### 线程间的同步（Lock）
多线程和多进程最大的不同在于，多进程中，同一个变量，各自有一份拷贝存在于每个进程中，互不影响，而多线程中，所有变量都由所有线程共享，所以，任何一个变量都可以被任何一个线程修改，因此，线程之间共享数据最大的危险在于多个线程同时改一个变量，把内容给改乱了。

使用Thread对象的Lock和Rlock可以实现简单的线程同步，这两个对象都有acquire方法和release方法，对于那些需要每次只允许一个线程操作的数据，可以将其操作放到acquire和release方法之间。如下：
```python
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
import time


class myThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)
        # 获得锁，成功获得锁定后返回True
        # 可选的timeout参数不填时将一直阻塞直到获得锁定
        # 否则超时后将返回False
        threadLock.acquire()
        print_time(self.name, self.counter, 3)
        # 释放锁
        threadLock.release()
        print("Exiting " + self.name)


def print_time(threadName, delay, counter):
    while counter:
        time.sleep(delay)
        print("{}: {}".format(threadName, time.ctime(time.time())))
        counter -= 1


threadLock = threading.Lock()
threads = []

# 创建新线程
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# 开启新线程
thread1.start()
thread2.start()

# 添加线程到线程列表
threads.append(thread1)
threads.append(thread2)

# 等待所有线程完成
for t in threads:
    t.join()
print("Exiting Main Thread")
```
执行结果如下
```
Starting Thread-1
Starting Thread-2
Thread-1: Thu May 10 16:25:37 2018
Thread-1: Thu May 10 16:25:38 2018
Thread-1: Thu May 10 16:25:39 2018
Exiting Thread-1
Thread-2: Thu May 10 16:25:41 2018
Thread-2: Thu May 10 16:25:43 2018
Thread-2: Thu May 10 16:25:45 2018
Exiting Thread-2
Exiting Main Thread
```

http://www.runoob.com/python/python-multithreading.html



