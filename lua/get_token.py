import subprocess
import random
import time
import sys
import json

NUMBER_OF_INSTRUCTIONS = 1                  # without return instruction

PREFIX = bytes([ 0x1b, 0x4c, 0x75, 0x61, 0x51, 0x0, 0x1, 0x4, 0x8, 0x4, 0x8, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x2, 0xfa
])

SUFFIX = bytes([
    0x1b, 0x0, 0x0, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x61, 0x0,
    0x3, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xf0, 0x3f, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x62, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x63,
    0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x64, 0x0, 0x4, 0x2, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x65, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x66, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x67, 0x0,
    0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x68, 0x0, 0x4, 0x2, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x69, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x6a, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x6b, 0x0, 0x4,
    0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x6c, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x6d, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x6e, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x6f, 0x0, 0x4, 0x2,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x70, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x71, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x72,
    0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x73, 0x0, 0x4, 0x2, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x74, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x75, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x76, 0x0,
    0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x77, 0x0, 0x4, 0x2, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x78, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x79, 0x0, 0x4, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7a, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0
])

RETURN_INSTRUCTION = bytes([ 0x1e, 0x0, 0x80, 0x0 ])
SEEN = {}

def generate_random_instruction(): # 4-byte instruction
    return bytes([random.randint(0, 255) for i in range(4)])

def create_lua_binary(instr_count, prefix, body, suffix):
    binary_form = (prefix + (instr_count + 1).to_bytes(4, byteorder='little')
                   + body + suffix)
    with open('ex.luap', 'bw') as binary_file:
        binary_file.write(binary_form)

TIMED_OUT = False
def generate_first_level_binaries():
    global TIMED_OUT
    global SEEN
    while not TIMED_OUT:
        instruction_seq = generate_random_instruction()
        sinstr = str(instruction_seq)
        if sinstr in SEEN: continue
        SEEN[sinstr] = 'try'
        create_lua_binary(instr_count=NUMBER_OF_INSTRUCTIONS,
                prefix=PREFIX,
                body=instruction_seq,
                suffix=(RETURN_INSTRUCTION + SUFFIX))
        try:
            result = subprocess.run(['lua', 'ex.luap'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1)
            SEEN[sinstr] = 'success'
        except subprocess.TimeoutExpired:
            SEEN[sinstr] = 'timedout'
            continue
        if len(result.stderr) == 0:
            SEEN[sinstr] = 'success'
        else:
            SEEN[sinstr] = result.stderr

import signal, os

def end_iteration(signum, frame):
    global TIMED_OUT
    TIMED_OUT = True

signal.signal(signal.SIGALRM, end_iteration)
signal.alarm(3600*24)

if __name__ == "__main__":
    start = time.perf_counter()
    generate_first_level_binaries()
    end = time.perf_counter()
    elapsed_time = end - start
    print(f"Elapsed {elapsed_time:.03f} secs.")
    with open("successful_sequences.json", "w") as file:
        json.dumps(SEEN)
