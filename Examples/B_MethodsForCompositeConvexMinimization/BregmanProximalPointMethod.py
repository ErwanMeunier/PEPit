from PEPit.pep import PEP
from PEPit.Function_classes.convex_function import ConvexFunction
from PEPit.Primitive_steps.bregmanproximal_step import BregmanProximal_Step


def wc_bpp(gamma, n, verbose=True):
    """
    Consider the composite convex minimization problem,
        min_x { F(x) = f_1(x) + f_2(x) }
    where f_1(x) and f_2(x) are closed convex proper functions.

    This code computes a worst-case guarantee for Bregman Proximal Point method.
    That is, it computes the smallest possible tau(n,L) such that the guarantee
        F(x_n) - F(x_*) <= tau(n,L) * Dh(x_*,x_0)
    is valid, where x_n is the output of the Bregman Proximal Point method,
    where x_* is a minimizer of F,when Dh is the Bregman distance generated by h.

    The detailed approach (based on convex relaxations) is available in
    [1] Radu-Alexandru Dragomir, Adrien B. Taylor, Alexandre d’Aspremont, and
         Jérôme Bolte. "Optimal Complexity and Certification of Bregman
         First-Order Methods". (2019)

    :param gamma: (float) step size.
    :param n: (int) number of iterations.
    :param verbose: (bool) if True, print conclusion

    :return: (tuple) worst_case value, theoretical value
    """

    # Instantiate PEP
    problem = PEP()

    # Declare three convex functions
    func1 = problem.declare_function(ConvexFunction,
                                    {})
    func2 = problem.declare_function(ConvexFunction,
                                     {})
    h = problem.declare_function(ConvexFunction,
                                     {})
    # Define the function to optimize as the sum of func1 and func2
    func = func1 + func2

    # Start by defining its unique optimal point xs = x_* and its function value fs = F(x_*)
    xs = func.optimal_point()
    fs = func.value(xs)
    ghs, hs = h.oracle(xs)

    # Then define the starting point x0 of the algorithm and its function value f0
    x0 = problem.set_initial_point()
    gh0, h0 = h.oracle(x0)

    # Set the initial constraint that is the Bregman distance between x0 and x^*
    problem.set_initial_condition(hs - h0 - gh0 * (xs - x0) <= 1)

    # Compute n steps of the Bregman Proximal Point method starting from x0
    gh = gh0
    for i in range(n):
        x, _, _, _, _ = BregmanProximal_Step(gh, h, func, gamma)
        _, ff = func.oracle(x)
        gh, _ = h.oracle(x)

    # Set the performance metric to the final distance in function values to optimum
    problem.set_performance_metric(ff - fs)

    # Solve the PEP
    pepit_tau = problem.solve()

    # Compute theoretical guarantee (for comparison)
    theoretical_tau = 1/gamma/n

    # Print conclusion if required
    if verbose:
        print('*** Example file: worst-case performance of the Bregman Proximal Point in function values ***')
        print('\tPEP-it guarantee:\t f(x_n)-f_* <= {:.6} Dh(x0,xs)'.format(pepit_tau))
        print('\tTheoretical guarantee :\t f(x_n)-f_* <= {:.6} Dh(x0,xs) '.format(theoretical_tau))
    # Return the worst-case guarantee of the evaluated method (and the upper theoretical value)
    return pepit_tau, theoretical_tau


if __name__ == "__main__":

    gamma = 3
    n = 5

    pepit_tau, theoretical_tau = wc_bpp(gamma=gamma,
                   n=n)