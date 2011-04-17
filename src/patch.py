from byteplay import *

PATCH_NOMORE = 1

_PYSPY_ID = '_pyspy_id'
_PYSPY_SKIP = '_pyspy_skip'

def reg_name(globs, obj):
    _id = getattr(obj, _PYSPY_ID, None)
    if not _id:
        _id = '_pyspy_%i' % id(obj)
        obj._pyspy_id = _id
        
    if _id not in globs:
        globs[_id] = obj

    return _id
    
NOPATCH_CACHE = set()
NOMORE_CACHE = {} 

def can_patch(obj):
    k = (obj.__module__, obj.__name__)
    if k in NOPATCH_CACHE:
        return False

    if hasattr(obj, '_pyspy_can_patch'):
        return True
    try:
        obj._pyspy_can_patch = True
        return True
    except:
        NOPATCH_CACHE.add(k)
        return False

def _decorate(fun, callback):
    if hasattr(fun, _PYSPY_SKIP):
        return fun

    _id = callback._pyspy_id

    if hasattr(fun, _id):
        return fun

    nomore = NOMORE_CACHE.get(_id)
    if not nomore:
        nomore = NOMORE_CACHE.setdefault(_id, set())

    k = (fun.__module__, fun.__name__)
    if k in nomore:
        return fun

    callback._pyspy_skip = True
    res = callback(fun)
    flags, new_fun = res
    if flags:
        if flags & PATCH_NOMORE:
            if can_patch(fun):
                setattr(fun, callback._pyspy_id, True)
            else:
                nomore.add(k)

    return new_fun or fun

_decorate._pyspy_skip = True

def patch_pre(fun, callback):
    if not can_patch(fun):
        return False

    callback_name = reg_name(fun.func_globals, callback)
    
    patch = [(LOAD_CONST, -1),
             (LOAD_CONST, None),
             (IMPORT_NAME, 'inspect'),
             (STORE_FAST, 'inspect'),
             (LOAD_FAST, 'inspect'),
             (LOAD_ATTR, 'currentframe'),
             (CALL_FUNCTION, 0),
             (LOAD_GLOBAL, callback_name),
             (ROT_TWO, None),
             (CALL_FUNCTION, 1),
             (POP_TOP, None)]
    
    code = Code.from_code(fun.func_code)
    code.code[0:0] = patch

    try:
        fun.func_code = code.to_code()
    except:
        pass
    return True

def patch_return(fun, callback):
    if not can_patch(fun):
        return False

def patch_calls(fun, callback, **kw):
    if not can_patch(fun):
        return False

    module = fun.func_globals

    callback_name = reg_name(module, callback)
    wrapper_name  = reg_name(module, _decorate)

    def gen_patch(call_arg):
        argnum = call_arg & 0xff
        kwlen = (call_arg - argnum) >> 7
        argl = argnum + kwlen

        replace_call = [(BUILD_LIST, argl),
                        (STORE_FAST, '_pyspy_args'),
                        (LOAD_FAST, '_pyspy_args'),
                        (LOAD_ATTR, 'reverse'),
                        (CALL_FUNCTION, 0),
                        (POP_TOP, None),
                        (STORE_FAST, '_pyspy_fun'),

                        # Now function is on top of the stack
                        # start decorating
                        
                        (LOAD_FAST, '_pyspy_fun'),
                        (LOAD_GLOBAL, callback_name),   # callback
                        (LOAD_GLOBAL, wrapper_name),
                        (ROT_THREE, 0),
                        (CALL_FUNCTION, 2),
                        
                        (LOAD_FAST, '_pyspy_args'),
                        (UNPACK_SEQUENCE, argl),
                        ]


        return replace_call

#(LOAD_CONST, None)]

    cur_code = Code.from_code(fun.func_code)

    i = 0

    inserts = []
    for (cmd, arg) in cur_code.code:
        if cmd == CALL_FUNCTION:
            insert = gen_patch(arg)

            inserts.append((i, insert))

#        if fun == sort.generate_file and len(replaces) == 4:
#            break

        i += 1

    inserts.reverse()
    for i, ins in inserts:
        cur_code.code[i:i] = ins


    '''
    import dis
    print fun
    print dis.disassemble(fun.func_code)
    print cur_code.code
    '''
    try:
        fun.func_code = cur_code.to_code()
    except: pass

#    raise Exception()
    
def f():
    print 2
    

def test():
    def g():
        f()

    def printer(*args):
        print args
        
    patch_calls(g, printer)
    g()
'''
                        (DUP_TOP, None),
                        (LOAD_CONST, 'func_code'),
                        (LOAD_GLOBAL, 'hasattr'),
                        (ROT_THREE, None),
                        (CALL_FUNCTION, 2),
                        (JUMP_IF_FALSE, label_wrap),
                        
                        (POP_TOP, None),
                        
                        (DUP_TOP, None),
                        (LOAD_CONST, '_pyspy_skip'),
                        (LOAD_GLOBAL, 'hasattr'),
                        (ROT_THREE, None),
                        (CALL_FUNCTION, 2),
                        (JUMP_IF_TRUE, label_pop),

                        (POP_TOP, None),
                        
                        (DUP_TOP, None),
                        (LOAD_CONST, callback_name),
                        (LOAD_GLOBAL, 'hasattr'),
                        (ROT_THREE, None),
                        (CALL_FUNCTION, 2),
                        (JUMP_IF_TRUE, label_pop),
                        
                        (label_wrap, None),                        
                        (POP_TOP, None),            # pop hasattr result
'''
