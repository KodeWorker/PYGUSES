# check divisibility
def check_divisibility(divisor, dividend):
    if dividend % divisor != 0:
        raise ValueError('Value not divisable.')
    return int(dividend/divisor)

