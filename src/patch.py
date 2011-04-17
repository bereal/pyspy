import sys
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
    

def _decorate(fun, callback):
    if hasattr(fun, _PYSPY_SKIP):
        return fun

    if hasattr(fun, callback._pyspy_id):
        return fun

    callback._pyspy_skip = True
    res = callback(fun)
    flags, new_fun = res
    if flags:
        if hasattr(fun, 'func_code') and flags & PATCH_NOMORE:
            setattr(fun, callback._pyspy_id, True)

    return new_fun or fun


_decorate._pyspy_skip = True

def patch_pre(fun, callback):
    if not hasattr(fun, 'func_code'):
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

    fun.func_code = code.to_code()

#def patch_return(fun, callback):
#    callback_
    

s = set()

def patch_calls(fun, callback, **kw):
    if fun in s:
        raise Exception('!!!')
    s.add(fun)
    if not hasattr(fun, 'func_code'):
        return # cannot patch builtins

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

                        # Now function is on top of the stack
                        # start decorating
                        
                        (LOAD_GLOBAL, callback_name),   # callback
                        (LOAD_GLOBAL, wrapper_name),
                        (ROT_THREE, 0),
#                        (BUILD_LIST, 3),
#                        (PRINT_ITEM, None),
                        (CALL_FUNCTION, 2),
                        
                        (LOAD_FAST, '_pyspy_args'),
                        (UNPACK_SEQUENCE, argl),
                        ]


        return replace_call

#(LOAD_CONST, None)]

    cur_code = Code.from_code(fun.func_code)

    i = 0

    replaces = {}
    for (cmd, arg) in cur_code.code:
        if cmd == CALL_FUNCTION:
            insert = gen_patch(arg)

            replaces[i] = insert

        i += 1

    for i, ins in replaces.iteritems():
        cur_code.code[i:i] = ins


    fun.func_code = cur_code.to_code()

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
