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

Python的Queue模块中提供了同步的、线程安全的队列类，能够在多线程中直接使用。可以使用队列来实现线程间的同步。
下面这个例子会创建三个线程和五个任务。异步的处理完线程后退出。

```
#!/usr/bin/python
# -*- coding: UTF-8 -*-

from queue import Queue
import threading
import time

class myThread(threading.Thread):
    def __init__(self, target, args=(), kwargs=None):
        super(myThread, self).__init__(target=target, args=args, kwargs=kwargs)

    def run(self):
        try:
            if self._target:
                print('Starting {}'.format(self._args[0]))
                self._target(*self._args, **self._kwargs)
                print('Exiting {}'.format(self._args[0]))
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs

# 数据处理函数
def process_data(threadName, wq):
    while not exitFLag:
        queueLock.acquire()
        if not workQueue.empty():
            time.sleep(1)
            data = wq.get()
            queueLock.release()
            print("{} processing {}".format(threadName, data))
        else:
            queueLock.release()
            time.sleep(1)

if __name__ == "__main__":
    queueLock = threading.Lock()
    workQueue = Queue(10)
    threadList = ["Thread-1", "Thread-2", "Thread-3"]
    workNameList = ["One", "Two", "Three", "Four", "Five"]
    threads = []

    # 定义退出标志
    exitFLag = 0

    # 填充任务队列
    for work in workNameList:
        workQueue.put(work)

    # 创建线程
    for threadName in threadList:
        thread = myThread(target=process_data, args=(threadName, workQueue))
        thread.start()
        threads.append(thread)

    # 等待任务被处理完
    while not workQueue.empty():
        pass

    # 通知线程结束循环
    exitFLag = 1

    # 等待所有的进程完成
    for t in threads:
        t.join()
    print("Exiting Main Thread.")

```

执行结果如下
```
Starting Thread-1
Starting Thread-2
Starting Thread-3
Thread-1 processing One
Thread-2 processing Two
Thread-3 processing Three
Thread-1 processing Four
Thread-2 processing Five
Exiting Thread-2
Exiting Thread-3
Exiting Thread-1
Exiting Main Thread.
```

## 线程池
通过上面的介绍，基本就介绍完了Python中多线程的基本使用了。但是因为GIL的存在，使得Python中的多线程比较的鸡肋，甚至连官方的线程池都没有。下面简单介绍下第三方的线程池，并主要讲下如何自己实现一个线程池。

### concurrent.futures
python3中自带的，python2的话需要安装futures模块。

```
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import concurrent.futures
import urllib.request

URLS = ['http://www.foxnews.com/',
        'http://www.cnn.com/',
        'http://europe.wsj.com/',
        'http://www.bbc.co.uk/',
        'http://some-made-up-domain.com/']

# Retrieve a single page and report the URL and contents
def load_url(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read()

# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            print('%r page is %d bytes' % (url, len(data)))
```
执行结果如下
```
'http://some-made-up-domain.com/' generated an exception: <urlopen error [Errno -2] Name or service not known>
'http://www.cnn.com/' page is 169879 bytes
'http://www.foxnews.com/' page is 238516 bytes
'http://www.bbc.co.uk/' page is 303508 bytes
'http://europe.wsj.com/' page is 960476 bytes
```

http://www.dongwm.com/archives/%E4%BD%BF%E7%94%A8Python%E8%BF%9B%E8%A1%8C%E5%B9%B6%E5%8F%91%E7%BC%96%E7%A8%8B-PoolExecutor%E7%AF%87/


JOB：创建一个可以控制最小和最大线程数的线程池，通过守护进程检测任务数和存活线程数，任务数较多时，增加线程数至最大线程。任务数子较少时，将线程数维持在最小数量。


