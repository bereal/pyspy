
def sort_file(f):
    lines = [l for l in f]
    for l in sort_lines(lines):
        print_( l)

def print_(s):
    pass
#    print s
    

def sort_lines(lines):
    lines.sort()
    return lines

def s(a, b):
#    hasattr('', '')
    print a, b

def generate_file(fname):
    from random import randint

  #  print s(1,2)
    f = file(fname, 'w')
    for x in xrange(1000000):
        val = randint(1, 1000)
        f.write(str(val).zfill(4) + '\n')

def go(name):
    s(1,2)
    #ks(1,2)
    generate_file(name)
#    sort_file([1,2])
    #with file(name) as f:
    #   sort_file(f)

def trace(*args):
    return trace

if __name__=='__main__':
    import sys
    sys.settrace(trace)
    
    go('test.txt')
