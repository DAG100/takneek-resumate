from pprint import PrettyPrinter
import fitz
import sys
import functools
import re
import unicodedata
import spacy

nlp = spacy.load('en_core_web_sm')

person = { #basic definition of resume
	"name":"",
	"email":[],
	"github_url":"",
	"linkedin_url":"",
	"phone":"",
	"college":"",
	"degree":"",
	"branch":"",
	"sections":{},
	"links": []
}
BULLETS = ["•", "-", "–"]
HEADERS= {
	"education": [
		"education",
		"academics",
		"qualification",
		"qualifications"
	],
	"achievements": [
		"achievement",
		"honors",
		"awards",
		"certification",
		"accomplishment"
	],
	"projects": [
		"project",
	],
	"experience": [
		"experience",
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

i = 1
if (len(sys.argv) > 1 and sys.argv[1] != None):
	i = int(sys.argv[1])

doc = fitz.open(f"misc/resumes/resume{i}.pdf")

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
		print_p(blocks)

def text_print():
	for page in doc:
		print(page.get_text())

structure_text_print()

#preprocess step 0: extract all internet links and check those for profiles
for page in doc:
	link = page.first_link
	while (link):
		if (link.is_external):
			exp = re.search('github.com/([a-zA-Z0-9\-\.]+)', link.uri) #github profile username
			if (exp and person['github_url'] == ""):
				person['github_url'] = exp.expand(r"github.com/\1")
				
			exp = re.search('linkedin.com/([\S]+)', link.uri) #linkedin profile link
			if (exp and person['linkedin_url'] == "" and not "company" in exp.expand(r"\1")):
				person['linkedin_url'] = exp.expand(r"linkedin.com/\1")
				
			exp = re.search('([^:\s/]+@[\S]+)', link.uri) #email
			if (exp):
				person['email'].append(exp.expand(r"\1"))
				
			person['links'].append(link.uri)
		link = link.next

# preprocess step 1: build a resume object of blocks/lines/spans
for page in doc:
	for b_idx, b in enumerate(page.get_text("dict", flags= fitz.TEXTFLAGS_DICT & ~ fitz.TEXT_PRESERVE_IMAGES)["blocks"]):
		lines = []
		for l_idx, l in enumerate(b["lines"]):
			#if on same line as latest element in lines arr, merge with that lines arr
			for s_idx, s in enumerate(l["spans"]):
				#normalise strings i.e. remove ligatures
				s['text'] = unicodedata.normalize("NFKD", s['text'])
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
				#fix bbox
				lines[-1]['bbox'] = (
					min(lines[-1]['bbox'][1], l['bbox'][1]),
					min(lines[-1]['bbox'][0], l['bbox'][0]),
					max(lines[-1]['bbox'][2], l['bbox'][2]),
					max(lines[-1]['bbox'][3], l['bbox'][3])
				)
			else:
				lines.append(l)
		resume.append(lines)

#preprocess step 2: merge span with previous if it starts with a lowercase character or a space and is close by (if it is very close-by stick 'em together anyway), remove empty spans
new_resume = []
for block in resume:
	new_lines = []
	for idx, line in enumerate(block):
		new_spans = []
		for span in line['spans']:
			if (span['text'].strip() == ""):
				continue

			if (len(new_spans) == 0):
				new_spans.append(span)
				continue
			
			#merge if font sizes are ~ the same, otherwise they are clearly different things
			
			
			if (abs(new_spans[-1]['bbox'][2] - span['bbox'][0]) < span['size']/10 and abs(new_spans[-1]['size'] - span['size']) < 1):
				merged = False
				if (span['text'][0] == ' '):
					new_spans[-1]['text'] += span['text']
					merged = True
				elif (abs(new_spans[-1]['bbox'][2] - span['bbox'][0]) < span['size']/15):
					new_spans[-1]['text'] += span['text']
					merged = True
				elif (span['text'][0].islower()):
					new_spans[-1]['text'] += " " + span['text']
					merged = True
				if (merged):
					#fix bbox
					new_spans[-1]['bbox'] = (
						min(new_spans[-1]['bbox'][0], span['bbox'][0]),
						min(new_spans[-1]['bbox'][1], span['bbox'][1]),
						max(new_spans[-1]['bbox'][2], span['bbox'][2]),
						max(new_spans[-1]['bbox'][3], span['bbox'][3])
					)
			else:
				new_spans.append(span)
				
		line['spans'] = new_spans
		if (len(new_spans) == 0):
			continue
		if (len(new_lines) == 0):
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
				header_candidates.append((span['text'], span['font'], counter, len(counter), span))
				# print("Header candidate")
# 					print(s['text'])

#process candidate headers and split resume into sections
#idea: formatting is consistent across headers, and ideally
#headers are the majority/plurality element in the above set
#idea 2: NLP it to see if everything is a noun - if *any*
#proper nouns, discard immediately

print_p(header_candidates)

section_headers = []
#deal with first header separately, is name
#first check if it is in the headers list
#if it is, then the ordering of the pdf
#elements is screwed up -> skip name for now,
#will try to extract using nlp on text form
name = header_candidates[0][0]
# print(name)
if (not functools.reduce(lambda x, y: x or y,[x in HEADERS_ALL for x in name.lower().split()])):
	name = name.split()
	name = " ".join([x.capitalize() for x in name])
	person['name'] = name
#deal with rest generically
for header_obj in header_candidates:
	header = header_obj[0]
	for section in HEADERS:
		for example in HEADERS[section]:
			if header.lower() in example or example in header.lower():
				section_headers.append((section, header_obj))
				break #stop checking for this *section*
# print(section_headers)

#*header_obj: (
# span['text'],
# span['font'], 
# counter, 
# len(counter), 
# span
# )

#turn section headers into full sections
line_flattened_resume = []
for block in resume:
	for line in block:
		line_flattened_resume.append(line)

curr_index = 0
prev_index = 0
for section_index, (section, header_obj) in enumerate(section_headers):
	if (section not in person['sections']):
		person['sections'][section] = []
	print(section)
	while (curr_index < len(line_flattened_resume)):
		line = line_flattened_resume[curr_index]
		if (header_obj[4] in line['spans']): #found the right line
			break
		curr_index += 1
	print(f"found at line {curr_index}, prev_index: {prev_index}")
	if (section_index == 0):
		#first index -> add first section to "personal"
		if (person['name'] != ""):
			person['sections']['personal'] = line_flattened_resume[0:curr_index]
	else:
		person['sections'][section_headers[section_index - 1][0]] += line_flattened_resume[prev_index:curr_index]

	prev_index = curr_index
#handle last section_heading
person['sections'][section_headers[len(section_headers) - 1][0]] += line_flattened_resume[curr_index:]
	
# 	
# print_p(section_headers)
# 
# resume_text_print()
# 
# print_p(person)
for section, lines in person['sections'].items():
	print(section)
	print("---")
	for line in lines:
		for span in line['spans']:
			print(span['text'], end="|")
		print("")
	print("\n\n---\n\n")

#handle personal section
#personal section: 
if ("personal" in person['sections']):
	#regex phone number, email
	personal_text = ""
	for line in person['sections']['personal']:
		for span in line['spans']:
			personal_text += span['text'] + " "
	phone = re.search("[0-9\s+()]{8,15}" ,personal_text)
	if (phone):
		person['phone'] = phone.expand(r"\1")
	email = re.search("([^:\s/]+@[\S]+)", personal_text)
	if (email):
		email_text = email.expand(r"\1")
		if (not email_text in person['email']):
			person['email'].append(email_text)
	personal_text = [x.lower() for x in personal_text.split()]
	personal_nlp = nlp(" ".join(personal_text))
	for (sent in personal_nlp)
	





# print(resume)
# print_p(header_candidates)
# resume_text_print()