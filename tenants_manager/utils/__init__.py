import random

def generate_random_numbers(length=6):
    """
    Generate a list of unique random numbers.

    :param count: Number of random numbers to generate.
    :param lower_bound: Minimum value for the random numbers.
    :param upper_bound: Maximum value for the random numbers.
    :return: List of unique random numbers.
    """
    return "".join(str(random.randint(0, 9)) for _ in range(length))

