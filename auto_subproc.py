from multiprocessing import Process, Pipe
from threading import Thread

def auto_subproc(f):
    """
    Use to decorate a function which might crash Python.
    
    Its code will be run in a subprocess so your main process
    will be fine even in the event of a crash.        
    """
    
    def g(*args,**kwargs):
        
        def subf(conn,*args,**kwargs):
            try:
                res = f(*args,**kwargs)
                conn.send((True,res))
            except Exception as e:
                conn.send((False,e))

        conn, conn_child = Pipe()
        proc = Process(target=subf,args=(conn_child,)+args,kwargs=kwargs)
        proc.start()
                
        
        r = [None]
        def recv(): r[0] = conn.recv()
        th = Thread(target=recv)
        th.daemon=True
        th.start()

        while th.is_alive():
            th.join(1e-3)
            if not proc.is_alive(): 
                raise Exception('Process died')
        
        if r[0][0]: return r[0][1]
        else: raise r[0][1]
    
    return g
