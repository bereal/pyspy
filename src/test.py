import patch

def trace_call(frame):
    print "Entering:", frame.f_code.co_name

def trace_exit(frame):
    print "Leaving:", frame.f_code.co_name
    
def before_call(fun):
    if not hasattr(fun, 'func_code'):
        print "Calling builtin", fun
        return 0, 0
        
    return patch_trace(fun)

before_call._pyspy_skip = 1

def patch_trace(fun):
    patch.patch_calls(fun, before_call)

    if hasattr(fun, 'func_code'):
        patch.patch_pre(fun, trace_call)
        patch.patch_exit(fun, trace_exit)
    
#    if patch.patch_calls(fun, before_call):
    return patch.PATCH_NOMORE, None

def test():
    import sort
#    patch.patch_pre(sort.go, trace)
    patch_trace(sort.go)
    sort.go('test.txt')

if __name__=='__main__':
    test()


