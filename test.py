"""from random import randint
import numpy

I = numpy.array([[bool(randint(0, 1))] for _ in range(7)])
W1 = numpy.array([[bool(randint(0, 1)) for _ in range(7)] for _ in range(7)])
W2 = numpy.array([[bool(randint(0, 1)) for _ in range(7)] for _ in range(7)])



print(I * W1)
print()
"""


class User_data:
    pass


a = User_data()
print(a.__class__)
print(User_data.__class__)
