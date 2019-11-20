import numpy as np
from scipy.optimize import linprog


def linprog_lb_wrapper(c, A_ub=None, b_ub=None, A_lb=None, b_lb=None, A_eq=None, b_eq=None, \
                       bounds=None, method='simplex', callback=None, options=None):
    """
    Scipy linprog function wrapper that allows to use lower bounds.
    """
    if A_lb is None:
        res = linprog(c, A_ub, b_ub, A_eq, b_eq, bounds, method, callback, options)
        return res
    elif (b_lb is None) or (len(b_lb) != len(A_lb)):
        # catch the error here
        print('Error')

    A_ub_new, b_ub_new = np.array(A_ub, dtype=float), np.array(b_ub, dtype=float)
    A_lb_new, b_lb_new = np.array(A_lb, dtype=float), np.array(b_lb, dtype=float)
    A_lb_new *= -1.0
    b_lb_new *= -1.0
    A_ub_new = np.vstack((A_ub_new, A_lb_new))
    b_ub_new = np.concatenate((b_ub_new, b_lb_new))

    res = linprog(c=c, A_ub=A_ub_new, b_ub=b_ub_new, A_eq=A_eq, b_eq=b_eq, bounds=bounds, \
                  method=method, callback=callback, options=options)

    return res
