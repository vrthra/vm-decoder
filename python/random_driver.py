import os
import driver as D

def validate_python(input_str_len, log_level):
    try:
        input_str = D.create_python_binary_random(input_str_len)
        output = D.execute_binary('')
        print(repr(output))
        if output == "complete":
            return "complete",-1,""
        elif output == "incomplete":
            return "incomplete", -1, ""
        else:
            return "wrong", len(input_str), "input_str[-1]"
    except Exception as e:
        msg = str(e)
        print("Can't parse: " + msg)
        n = len(msg)
        return "wrong", n, ""

import random
def generate(log_level):
    while True:
        curr_str_len = random.randint(1,1000)
        rv, n, c = validate_python(curr_str_len, log_level)
        if log_level:
            print("%s n=%d, c=%s. Input string is %s" % (rv,n,c,curr_str))
        if rv == "complete":
            return n
        elif rv == "wrong":
            continue
        else:
            print("ERROR What is this I dont know !!!")
            break
    return None


import time
def create_valid_strings(n, log_level):
    os.remove("valid_inputs.txt") if os.path.exists('valid_inputs.txt') else None
    tic = time.time()
    i = 0
    while True: # while
        i += 1
        created_string = generate(log_level)
        toc = time.time()
        if created_string is not None:
            with open("valid_inputs.txt", "a") as myfile:
                var = f"Time used until input was generated: {toc - tic:f}\n" + repr(created_string) + "\n\n"
                myfile.write(var)

create_valid_strings(10, 0)
