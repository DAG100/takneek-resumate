import sys
import os
import process

for i in range(1, 95):
	try:
		json_str = ""
		with open(f"misc/resumes/resume{i}.pdf", "rb") as f:
			json_str = process.process_resume(f.read())
		with open(f"test/resume{i}.txt", "w") as f:
			f.write(json_str)
		print(f"done with {i}")
	except:
		print(f"error with {i}")

