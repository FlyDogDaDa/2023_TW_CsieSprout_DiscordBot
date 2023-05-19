@property
def A():
    return "AAAAAAAAAAAAA"


print("{A}".format(**{"A": A}))
