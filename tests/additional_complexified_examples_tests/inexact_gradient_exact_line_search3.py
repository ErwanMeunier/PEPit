import numpy as np

import PEPit as PEPit
from PEPit.functions import SmoothStronglyConvexFunction
from PEPit.point import Point


def wc_inexact_gradient_exact_line_search_complexified3(L, mu, epsilon, n, verbose=1):
    """
    See description in `PEPit/examples/unconstrained_convex_minimization/inexact_gradient_exact_line_search.py`.
    This example is for testing purposes; the worst-case result is supposed to be the same as that of the other routine,
    but the exact line-search steps are imposed via LMI constraints (instead of relying on the `exact_linesearch_step`
    primitive). Here, the initial condition is also imposed via an LMI.

    Args:
        L (float): the smoothness parameter.
        mu (float): the strong convexity parameter.
        epsilon (float): level of inaccuracy.
        n (int): number of iterations.
        verbose (int): Level of information details to print.

                        - -1: No verbose at all.
                        - 0: This example's output.
                        - 1: This example's output + PEPit information.
                        - 2: This example's output + PEPit information + CVXPY details.

    Returns:
        pepit_tau (float): worst-case value
        theoretical_tau (float): theoretical value

    Example:
        >>> pepit_tau, theoretical_tau = wc_inexact_gradient_exact_line_search_complexified(L=1, mu=0.1, epsilon=0.1, n=2, verbose=1)
        (PEPit) Setting up the problem: size of the main PSD matrix: 7x7
        (PEPit) Setting up the problem: performance measure is minimum of 1 element(s)
        (PEPit) Setting up the problem: Adding initial conditions and general constraints ...
        (PEPit) Setting up the problem: initial conditions and general constraints (1 constraint(s) added)
        (PEPit) Setting up the problem: 2 lmi constraint(s) added
                         Size of PSD matrix 1: 2x2
                         Size of PSD matrix 2: 2x2
        (PEPit) Setting up the problem: interpolation conditions for 1 function(s)
                         function 1 : Adding 14 scalar constraint(s) ...
                         function 1 : 14 scalar constraint(s) added
        (PEPit) Compiling SDP
        (PEPit) Calling SDP solver
        (PEPit) Solver status: optimal (solver: SCS); optimal value: 0.5188573779100247
        *** Example file: worst-case performance of inexact gradient descent with exact linesearch ***
                PEPit guarantee:         f(x_n)-f_* <= 0.518857 (f(x_0)-f_*)
                Theoretical guarantee:   f(x_n)-f_* <= 0.518917 (f(x_0)-f_*)

    """

    # Instantiate PEP
    problem = PEPit.PEP()

    # Declare a strongly convex smooth function
    func = problem.declare_function(SmoothStronglyConvexFunction, mu=mu, L=L)

    # Start by defining its unique optimal point xs = x_* and corresponding function value fs = f_*
    xs = func.stationary_point()
    fs = func(xs)

    # Then define the starting point x0 of the algorithm as well as corresponding gradient and function value g0 and f0
    x0 = problem.set_initial_point()
    gx0, _ = func.oracle(x0)

    # Set the initial constraint that is the distance between f0 and f_*
    #problem.set_initial_condition(func(x0) - fs <= 1)
    # equivalent to [ 1 func(x0)-fs; func(x0)-fs 1] >> 0    
    matrix_of_expressions_init = np.array([[1, func(x0) - fs], [func(x0) - fs, 1]])
    problem.add_psd_matrix(matrix_of_expressions=matrix_of_expressions_init)

    # Run n steps of the inexact gradient method with ELS
    x = x0
    gx = gx0
    for i in range(n):
        gx_prev = gx
        x_prev = x
        x = Point()
        gx, fx = func.oracle(x)

        matrix_of_expressions = np.array([[epsilon * gx_prev ** 2, gx_prev * gx], [gx_prev * gx, epsilon * gx ** 2]])
        problem.add_psd_matrix(matrix_of_expressions=matrix_of_expressions)
        func.add_constraint((x - x_prev) * gx == 0)

    # Set the performance metric to the function value accuracy
    problem.set_performance_metric(func(x) - fs)

    # Solve the PEP
    pepit_verbose = max(verbose, 0)
    pepit_tau = problem.solve(verbose=pepit_verbose)

    # Compute theoretical guarantee (for comparison)
    Leps = (1 + epsilon) * L
    meps = (1 - epsilon) * mu
    theoretical_tau = ((Leps - meps) / (Leps + meps)) ** (2 * n)

    # Print conclusion if required
    if verbose != -1:
        print('*** Example file: worst-case performance of inexact gradient descent with exact linesearch ***')
        print('\tPEPit guarantee:\t f(x_n)-f_* <= {:.6} (f(x_0)-f_*)'.format(pepit_tau))
        print('\tTheoretical guarantee:\t f(x_n)-f_* <= {:.6} (f(x_0)-f_*)'.format(theoretical_tau))
        
    # Return the worst-case guarantee of the evaluated method (and the reference theoretical value)
    return pepit_tau, theoretical_tau


if __name__ == "__main__":
    pepit_tau, theoretical_tau = wc_inexact_gradient_exact_line_search_complexified3(L=1, mu=0.1, epsilon=0.1, n=10, verbose=1)
