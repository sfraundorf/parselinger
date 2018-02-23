import textwrap
import string

class LingerItem:
	"""An item to be presented in Linger or WebSPR."""
	def __init__(self):
		self.experiment = ""
		self.itemname = ""
		self.condition = ""
		self.itemtext = ""
		self.compquestions = []
		self.maxwidth = 55
		self.messagetime = 1000

	def print_condition_data (self, outfile=None):
		# Print the condition data
		print >> outfile, "# %s %s %s" % (self.experiment, self.itemname, self.condition)
		
	def print_item_text (self, outfile=None):
		# Print the text of the item
		print >> outfile, textwrap.fill(self.itemtext, self.maxwidth)
		
	def print_comprehension_questions (self, outfile=None):
		# Print each comprehension question
		for question in self.compquestions:
			question.print_question(outfile=outfile)
			
	def print_item(self, outfile=None):
		# Print the entire item
		self.print_condition_data(outfile=outfile)
		self.print_item_text(outfile=outfile)
		self.print_comprehension_questions(outfile=outfile)
		print >> outfile, ""
				
	def ibex_condition_data (self, outfile=None):
		# Print the condition data in Ibex format
		print >> outfile, '"%s"' % (self.condition)
		
	def ibex_item_text (self, outfile=None):
		# Print the text of the item in Ibex format
		if string.count(self.itemtext, '\n') > 1:
			# item already has manual line breaks
			wrappedtext = self.itemtext
		else:
			# wrap the text ourself
			wrappedtext = textwrap.fill(self.itemtext, self.maxwidth)
		# Print the sentence with any trailing newline deleted
		print >> outfile, '			"DashedSentence", {s: %r},' % (wrappedtext.rstrip('\n'))

	def ibex_comprehension_questions(self, outfile=None):
		# Print each comprehension question in Ibex format
		for i in range(0,len(self.compquestions)):
			if i == len(self.compquestions)-1:
				self.compquestions[i].ibex_question(outfile=outfile, lastquestion=True)
			else:
				self.compquestions[i].ibex_question(outfile=outfile, lastquestion=False)
	
	def print_ibex_item(self, outfile=None, lastitem=False, practice=False):
		# End with a comma only if another item follows
		if lastitem:
			endcharacter = ''
		else:
			endcharacter = ','
		# Add S for critical items or P for practice
		if practice:
			headcharacter = "P"
		else:
			headcharacter = "S"
		# Print the entire item in Ibex format
		print >> outfile, '["%s_%s_%s",' % (headcharacter, self.condition, self.itemname)
		self.ibex_item_text(outfile=outfile)
		self.ibex_comprehension_questions(outfile=outfile)
		print >> outfile, ']%s' % endcharacter
		
	def print_ibex_practice(self, outfile=None, lastitem=False):
		self.print_ibex_item(outfile=outfile, lastitem=lastitem, practice=True)
		
class LingerQuestion:
	"""A question of some form for a Linger item."""
	def __init__(self):
		self.text = ""
		
	def print_question (self, outfile=None):
		# Generic printing of a comprehension question
		print >> outfile, "? %s" % (self.text)

	def ibex_question (self, outfile=None, lastquestion=True):
		# End with a comma only if another question follows
		if lastquestion:
			endcharacter = ''
		else:
			endcharacter = ','
		# Print the comprehension question in Ibex format
		print >> outfile, '			"Question", {q: "%s"},' % (self.text)
		print >> outfile, '			"Separator", {transfer: 1000, normalMessage: "  ", errorMessage: "WRONG!"}%s' % (endcharacter)		
				
	def get_end_character(self, lastquestion=True):
		# For Ibex items, end with a comma iff another question follows
		if lastquestion:
			return ''
		else:
			return ','						
		
class LingerStimulusFile(file):
	"""A file that contains Linger stimulus items."""
	
	def get_linger_items(self):

		currentitem = LingerItem()
		allitems = []

		for line in self:
			if line[0] == "#":
				# condition data
				conditiondata = line.split()
				currentitem.experiment = conditiondata[1]
				currentitem.itemname = conditiondata[2]
				currentitem.condition = conditiondata[3]
			elif line[0] == "?" or line[0] == "|":
				# comprehension question
				if "|" in line:
					questiondata = line.split('|')
					questiontext = questiondata[1][1:]
				else:
					questiondata = line.split('?')
					questiontext = questiondata[1][1:] + '?'
				if "Y" in questiondata[2][1]:
					newquestion = YesNoQuestion()
					newquestion.answer = True
				elif "N" in questiondata[2][1]:
					newquestion = YesNoQuestion()				
					newquestion.answer = False
				else:
					newquestion = MultipleChoiceQuestion()
					newquestion.answers = str.split(questiondata[2], ',')
					newquestion.answers = [item.translate(None, ' "\'') for item in newquestion.answers]
				newquestion.text = questiontext
				currentitem.compquestions.append(newquestion)
			elif line[0] == "\n" or len(line) < 2:
				# add the completed item to the list
				allitems.append(currentitem)
				# start a new item
				currentitem = LingerItem()
			else:
				if currentitem.itemtext == "":
					# start item text
					currentitem.itemtext = line
				else:
					currentitem.itemtext = currentitem.itemtext + line
	
		return allitems
		
class MultipleChoiceQuestion(LingerQuestion):
	"""A multiple choice comprehension question for a
	self-paced reading item."""
	def __init__(self):
		self.answers = []
		
	def ibex_question (self, outfile=None, lastquestion=True):
		# End with a comma only if another question follows
		endcharacter = self.get_end_character(lastquestion)
		# Print the comprehension question in Ibex format
		print >> outfile, '			"Question", {q: "%s", as: %d}%s' % (self.text, self.mc_answers(), endcharacter)
		
	def mc_answers(self):
		return ', '.join(['"' + item + '"' for item in self.answers])
		
class YesNoQuestion(LingerQuestion):
	"""A yes/no comprehension question for a self-paced
	reading item."""
	def __init__(self):
		self.answer = True
		
	def print_question (self, outfile=None):
		# Print the comprehension question
		print >> outfile, "? %s %s" % (self.text, self.letter_answer())
		
	def ibex_question (self, outfile=None, lastquestion=True):
		# End with a comma only if another question follows
		endcharacter = self.get_end_character(lastquestion)
		# Print the comprehension question in Ibex format
		print >> outfile, '			"Question", {q: "%s", hasCorrect: %d},' % (self.text, self.binary_answer())
		print >> outfile, '			"Separator", {transfer: 1000, normalMessage: "  ", errorMessage: "WRONG!"}%s' % (endcharacter)
		
	def letter_answer (self):
		# Get the question answer as a Y or an N
		if self.answer == True:
			return 'Y'
		else:
		 	return 'N'
		 	
	def binary_answer (self):
		# Get the question answer as a 0 (Yes/True) or a 1 (No/False)
		# (ordered to match the display order)
		if self.answer == True:
			return 0
		else:
			return 1		