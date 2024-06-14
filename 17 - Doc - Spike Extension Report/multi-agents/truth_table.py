# from read_file import *
from kb2expression import *
import time
import numpy

class TruthTable():
    def __init__(self,kb,alpha):
        self.kb = kb2expr(kb)
        self.alpha = expr(alpha)
        self.symbols = list(prop_symbols(self.kb & self.alpha))
        self.result = None
        self.count = self.tt_check_all_count(self.kb, self.alpha, self.symbols, {})
        self.tt_entails()

    def get_result(self):
        # print(self.result)
        if self.result and self.count != 0:
            print(f"Yes: {self.count}")
            return True
        else:
            print("No")
            return False

    def tt_entails(self):
        """
        Does kb entail the sentence alpha? Use truth tables. For propositional
        kb's and sentences. Note that the 'kb' should be an Expr which is a
        conjunction of clauses.
        >>> tt_entails(expr('P & Q'), expr('Q'))
        True
        """
        time.sleep(0.01)
        assert not variables(self.alpha)
        self.result = self.tt_check_all(self.kb, self.alpha, self.symbols, {})
        # self.count = self.tt_check_all_count(self.kb, self.alpha, self.symbols, {})
    
    def tt_check_all(self,kb, alpha, symbols, model):
        """Auxiliary routine to implement tt_entails."""
        if not symbols:
            if pl_true(kb, model):
                result = pl_true(alpha, model)
                assert result in (True, False)
                return result
            else:
                return True
        else:
            P, rest = symbols[0], symbols[1:]
            return (self.tt_check_all(kb, alpha, rest, extend(model, P, True)) and
                    self.tt_check_all(kb, alpha, rest, extend(model, P, False)))

    
    def tt_check_all_count(self,kb, alpha, symbols, model):
        """
        Recursive function to count all models where both kb and alpha are true.
        
        Returns:
        int - Count of models where both kb and alpha are true.
        """
        if not symbols:
            if pl_true(kb, model):  # Check if the model satisfies the knowledge base
                if pl_true(alpha, model):  # Check if the model also satisfies the query
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            first, rest = symbols[0], symbols[1:]
            return (self.tt_check_all_count(kb, alpha, rest, extend(model, first, True)) +
                    self.tt_check_all_count(kb, alpha, rest, extend(model, first, False)))

    def time_estimated(self):
        """
        This function calculates the estimated of the function in 10 times
        """
        average = []
        for i in range(10):
            start = 0.01+ time.time()
            self.tt_entails()
            end = time.time()
            estimated_time = (end - start)*1000
            average.append(estimated_time)
        
        self.estimated_time = numpy.average(average)
        print(f"Elapsed time in average: {self.estimated_time:.2f} milliseconds")

def extend(s, var, val):
    """Copy dict s and extend it by setting var to val; return copy."""
    return {**s, var: val}
    
def prop_symbols(x):
    """Return the set of all propositional symbols in x."""
    if not isinstance(x, Expr):
        return set()
    elif is_prop_symbol(x.op):
        return {x}
    else:
        return {symbol for arg in x.args for symbol in prop_symbols(arg)}
    

def pl_true(exp, model={}):
    """Return True if the propositional logic expression is true in the model,
    and False if it is false. If the model does not specify the value for
    every proposition, this may return None to indicate 'not obvious';
    this may happen even when the expression is tautological.
    >>> pl_true(P, {}) is None
    True
    """
    if exp in (True, False):
        return exp
    op, args = exp.op, exp.args
    if is_prop_symbol(op):
        return model.get(exp)
    elif op == '~':
        p = pl_true(args[0], model)
        if p is None:
            return None
        else:
            return not p
    elif op == '|':
        result = False
        for arg in args:
            p = pl_true(arg, model)
            if p is True:
                return True
            if p is None:
                result = None
        return result
    elif op == '&':
        result = True
        for arg in args:
            p = pl_true(arg, model)
            if p is False:
                return False
            if p is None:
                result = None
        return result
    p, q = args
    if op == '==>':
        return pl_true(~p | q, model)
    elif op == '<==':
        return pl_true(p | ~q, model)
    pt = pl_true(p, model)
    if pt is None:
        return None
    qt = pl_true(q, model)
    if qt is None:
        return None
    if op == '<=>':
        return pt == qt
    elif op == '^':  # xor or 'not equivalent'
        return pt != qt
    else:
        raise ValueError('Illegal operator in logic expression' + str(exp))
    

def is_prop_symbol(s):
    """A proposition logic symbol is an initial-uppercase string.
    >>> is_prop_symbol('exe')
    False
    """
    return is_symbol(s) and s[0].isupper()


def variables(s):
    """Return a set of the variables in expression s.
    >>> variables(expr('F(x, x) & G(x, y) & H(y, z) & R(A, z, 2)')) == {x, y, z}
    True
    """
    variables = set()
    for x in subexpressions(s):
        if is_variable(x):
            variables.add(x)
    return variables

def is_variable(x):
    """A variable is an Expr with no args and a lowercase symbol as the op."""
    return isinstance(x, Expr) and not x.args and x.op[0].islower()

def is_symbol(s):
    """A string s is a symbol if it starts with an alphabetic char.
    >>> is_symbol('R2D2')
    True
    """
    return isinstance(s, str) and s[:1].isalpha()


def subexpressions(x):
    """Yield the subexpressions of an Expression (including x itself)."""
    yield x
    if isinstance(x, Expr):
        for arg in x.args:
            yield from subexpressions(arg)   

