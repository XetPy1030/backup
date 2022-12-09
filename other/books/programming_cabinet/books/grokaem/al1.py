from time import sleep
from random import randint

min_num = 0
max_num = 100


def binary_search(array=list(range(min_num, max_num))):
    low = 0
    high = len(array) - 1
    rand_num = randint(min_num, max_num)
    
    while low <= high:
        mid = (low + high) // 2
        guess = array[mid]
        if guess == rand_num:
            return mid
        if guess > rand_num:
            high = mid - 1
        else:
            low = mid + 1
        print(mid, guess, low, high, rand_num)
    
    return None
        

print(binary_search())