
# Test cases
test1 = [-2, -5, -6]
test2 = [[-6], [-8], [-12]]
test3 = [[-2, -4], [-2, -6], [-2, -8], [-4, -6], [-4, -8], [-6, -8]]

# convert [-2, -5, -6] to [[-2], [-5], [-6]]
def test1_to_test2(test1):
    return [[x] for x in test1]
# convert [[-6], [-8], [-12]] to [-6, -8, -12]
def test2_to_test1(test2):
    return [x[0] for x in test2]

def converter(test):
    if type(test[0]) == list:
        return test2_to_test1(test)
    else:
        return test1_to_test2(test)
