import sys
import os

for i in range(1, 95):
	os.system(f"python3 process.py {i} > test/test{i}.txt")
	print(f"done with {i}")

