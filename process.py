from pprint import PrettyPrinter
import fitz
import sys
import functools

person = { #basic definition of resume
	"name":"",
	"email":"",
	"phone":"",
	"college":"",
	"degree":"",
	"branch":"",
	"sections":[]
}
BULLETS = ["•", "-", "–"]
HEADERS= {
	"education": [
		"education",
		"academic qualifications",
		"academics",
		"qualifications"
	],
	"achievements": [
		"achievements",
		"academic achievements",
		"honors",
		"awards",
		"scholastic achievements",
		"certification"
	],
	"projects": [
		"project",
		"key projects"
	],
	"experience": [
		"work experience",
		"experience",
		"prior experience",
		"research experience"
	],
	"positions of responsiblity": [
		"positions of responsibility",
		"position of responsibility",
		"involvement"
	],
	"skills": [
		"skills",
		"technical skills"
	],
	"courses": [
		"academic workload",
		"courses",
		"key courses",
		"relevant courses",
		"coursework"
	],
	"contact": [
		"contact"
	],
	"miscellaneous": [
		"miscellaneous",
		"extracurricular",
		"activities",
		"extra-curricular"
	]
	
}
HEADERS_ALL = functools.reduce(lambda x, y: x + y[1],HEADERS.items(), [])
# print(HEADERS_ALL)

print_p = PrettyPrinter(indent=4).pprint

i = 4
if (sys.argv[1] != None):
	i = int(sys.argv[1])
doc = fitz.open(f"resumes/resume{i}.pdf")

resume = []
font_matrix = {}
#array of blocks, which are arrays of lines, which are arrays of spans

header_candidates = []

def resume_text_print():
	for block in resume:
		for line in block:
			for span in line['spans']:
				print(span['text'], end="|")
			print("")
		print("\n")
	print("\n\n")

def html_render():
	j = 0
	for page in doc:
		j += 1
		with open(f"resume{i}-{j}.html", "w") as f:
			f.write(page.get_text("html"))

def structure_text_print():
	for page in doc:
		blocks = page.get_text("dict")["blocks"]
		print(blocks)


# structure_text_print()

#preprocess step 0: extract all internet links and check those for profiles


# preprocess step 1: build a resume object of blocks/lines/spans
for page in doc:
	for b_idx, b in enumerate(page.get_text("dict")["blocks"]):
		lines = []
		for l_idx, l in enumerate(b["lines"]):
			#if on same line as latest element in lines arr, merge with that lines arr
			for s_idx, s in enumerate(l["spans"]):
				#collect font and font size data
				#store a matrix of font and font-size combinations
				#test: {(font, font-size): occurrences,}
				if ((s['font'], s['size']) not in font_matrix):
					font_matrix[(s['font'], s['size'])] = 1
				else:
					font_matrix[(s['font'], s['size'])] += 1
				
			if (len(lines) == 0):
				lines.append(l)
				continue
			#if current line is on the same y-level as a previous line, merge them
			if (abs(l['bbox'][3] - lines[-1]['bbox'][3]) < 2 and abs(l['bbox'][1] - lines[-1]['bbox'][1]) < 2):
				lines[-1]['spans'] += l['spans']
			else:
				lines.append(l)
		resume.append(lines)

#preprocess step 2: merge span with previous if it starts with a lowercase character or a space
new_resume = []
for block in resume:
	new_lines = []
	for idx, line in enumerate(block):
		new_spans = []
		for span in line['spans']:
			if (len(new_spans) == 0):
				new_spans.append(span)
				continue
			
			if (span['text'][0] == ' '):
				new_spans[-1]['text'] += span['text']
			elif (span['text'][0].islower()):
				# if (span['text'] == "cation"):
# 					print(span)
# 					print(new_spans[-1])
# 					print(abs(new_spans[-1]['bbox'][2] - span['bbox'][0]))
				if (abs(new_spans[-1]['bbox'][2] - span['bbox'][0]) < 1.5):
					new_spans[-1]['text'] += span['text']
				else:
					new_spans[-1]['text'] += " " + span['text']
			else:
				new_spans.append(span)
				
		line['spans'] = new_spans
		if (idx == 0):
			new_lines.append(line)
			continue
		
		#merge line with previous if it starts with a lowercase character
		if (line['spans'][0]['text'][0].islower()):
			new_lines[-1]['spans'] += line['spans']
		else:
			new_lines.append(line)
	new_resume.append(new_lines)
resume = new_resume

# print_p(resume)

#modal font size
size_dict = list(set([str(key[1]) for key in font_matrix]))
size_dict = {x: 0 for x in size_dict}
for ((font, fontsize), occurrence) in font_matrix.items():
	size_dict[str(fontsize)] += occurrence
# print(size_dict)
modal_size = list(size_dict.keys())[0]
for size in size_dict:
	if (size_dict[size] > size_dict[modal_size]):
		modal_size = size
modal_size = float(modal_size)
# print(modal_size)
# print(font_matrix)


#extract candidate headers
for block in resume:
	for line in block:
		for span in line['spans']:
			counter = []
			if (span["flags"] & 16): #is bold
				counter.append("bold")
			if (len(line["spans"]) == 1): #is the only item in the line
				counter.append("only item")
			if (span['size'] > modal_size): #size larger than modal size
				counter.append("larger")
			if (span['text'].isupper() or "Cap" in span['font']): #full uppercase?
				counter.append("uppercase")
			if (len(span['text'].split()) < 4):
				counter.append("few words")
			if (span['text'][0] in BULLETS): #first char of header is never a bullet
				counter = []
			if (len(counter) >= 3):
				header_candidates.append((span['text'], span['font'], counter, len(counter)))
				# print("Header candidate")
# 					print(s['text'])

#process candidate headers and split resume into sections
#idea: formatting is consistent across headers, and ideally
#headers are the majority/plurality element in the above set
#idea 2: NLP it to see if everything is a noun - if *any*
#proper nouns, discard immediately


# section_headers = []
# #deal with first header separately, is name
# name = header_candidates[0][0].split()
# name = " ".join([x.capitalize() for x in name])
# person['name'] = name
# #deal with rest generically
# for (header, _, __, ___) in header_candidates:
# 	for section in HEADERS:
# 		for example in HEADERS[section]:
# 			if header.lower() in example or example in header.lower():
# 				section_headers.append((section, header))
# 				break #stop checking for this *section*
# print(section_headers)
	


# print_p(resume)
# print_p(header_candidates)
# resume_text_print()