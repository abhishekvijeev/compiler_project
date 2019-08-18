import re
import sys

"""
Global Variables

"""

symbolTable = dict()
externalVariables = dict()
localVariables = list()
keyword = ["include", "define", "while", "do", "for", "return", "extern"]
dataType = ["void", "int", "short", "long", "char", "float", "double"]
preDefRoutine = ["printf", "scanf"]
identifier = "^[^\d\W]\w*\Z"
punctuator = "^[()[\]{};.,]$"
aritmeticOperator = "^[-+*/]$"
assignmentOperator = "^=$"
relationalOperator = ["<", ">", "<=", ">=", "==", "!="]
logicalOperator = ["&&", "||", "!"]
number = "^\d+$"
spaces = "[' ''\n''\t']"

intermediate_code = str()
syntax_tree = str()

top = 0
i_ = 1
tmp = str()
li = [0] * 50
lb = 0
fp = 1
label = 1

syntax_tree_top = 0
syntax_tree_i_ = 1
syntax_tree_tmp = str()
syntax_tree_do = 0
syntax_tree_li = [0] * 50
syntax_tree_label = 1
syntax_tree_wh = ["dd"]	
op = str()



def loadSymbolTable():
	
	symbolTable["keyword"] = keyword
	symbolTable["dataType"] = dataType
	symbolTable["preDefRoutine"] = preDefRoutine

"""
Functions to generate 3-address intermediate code

"""

def push(val):
	global top,li
	top = top+1
	li[top]=val
	


def codegen():
	global tmp,i_,top,li, intermediate_code
	tmp = "t"
	tmp+=str(i_)
	#print(tmp +" = "+str(li[top-2]), str(li[top-1]), str(li[top]))
	intermediate_code += tmp + " = " + str(li[top-2]) + " " + str(li[top-1]) + " " + str(li[top]) + "\n"
	top-=2
	li[top]=tmp
	i_=i_+1


def codegen_umin():
	global tmp,i_,top,li, intermediate_code
	tmp = "t"
	tmp+=str(i_)
	#print(tmp+" = -"+str(li[top]))
	intermediate_code += tmp + " = -" + str(li[top]) + "\n"
	top=top-1
	li[top]=tmp
	i_=i_+1

def codegen_assign():
	global tmp,i_,top,li, intermediate_code
	#print(str(li[top-1])+" = "+str(li[top]))
	intermediate_code += str(li[top-1]) + " = " + str(li[top]) + "\n"
	top=top-2


def lab1():
	global label, intermediate_code
	#print("L"+str(label)+":")
	intermediate_code += "L" + str(label) + ":" + "\n"
	label = label+1
	
def lab2():
	global tmp,i_,top,li,label, intermediate_code
	tmp = "t"
	tmp+=str(i_)
	#print(tmp+" =  "+li[top-2],li[top-1],li[top])
	#print("if "+tmp+" goto L"+str(label-1))
	intermediate_code += tmp +" =  " + str(li[top-2]) + " " + str(li[top-1]) + " " + str(li[top]) + "\n"
	intermediate_code += "if " + tmp + " goto L" + str(label-1) + "\n"
	i_=i_+1
	label = label-1
	top = top-3



"""
Functions to generate a syntax tree

"""

def syntax_tree_push(val):
	global syntax_tree_top, syntax_tree_li
	syntax_tree_top = syntax_tree_top + 1
	syntax_tree_li[syntax_tree_top]=val
	


def syntax_tree_gen():
	global syntax_tree_tmp, syntax_tree_i_, syntax_tree_top, syntax_tree_li, syntax_tree
	tmp = "N"
	tmp+=str(syntax_tree_i_)
	#print("NODE "+tmp +" -> "+str(syntax_tree_li[syntax_tree_top-2])+" <-- "+ str(syntax_tree_li[syntax_tree_top-1])+" --> "+ str(syntax_tree_li[syntax_tree_top]))
	syntax_tree += "NODE " + tmp + " -> " + str(syntax_tree_li[syntax_tree_top-2]) + " <-- " + str(syntax_tree_li[syntax_tree_top-1]) + " --> " + str(syntax_tree_li[syntax_tree_top]) + "\n"
	#if(do==1):
		#print("do --> "+tmp)
	syntax_tree_top -= 2
	syntax_tree_li[syntax_tree_top] = tmp
	syntax_tree_i_ = syntax_tree_i_ + 1


def syntax_tree_gen_umin():
	global syntax_tree_tmp, syntax_tree_i_, syntax_tree_top, syntax_tree_li, syntax_tree
	tmp = "t"
	tmp+=str(syntax_tree_i_)
	#print(tmp+" = -"+str(syntax_tree_li[syntax_tree_top]))
	syntax_tree += tmp + " = -" + str(syntax_tree_li[syntax_tree_top]) + "\n"
	syntax_tree_top=syntax_tree_top-1
	syntax_tree_li[syntax_tree_top]=tmp
	syntax_tree_i_=syntax_tree_i_+1

def syntax_tree_gen_assign():
	global syntax_tree_tmp, syntax_tree_i_, syntax_tree_top, syntax_tree_li, syntax_tree
	#print(str(syntax_tree_li[syntax_tree_top-1])+" <-- = --> "+str(syntax_tree_li[syntax_tree_top]))
	syntax_tree += str(syntax_tree_li[syntax_tree_top-1]) + " <-- = --> " + str(syntax_tree_li[syntax_tree_top]) + "\n"
	if(syntax_tree_do!=0):
		syntax_tree += "do --> =" + "\n"
	else:
		syntax_tree += "main --> =" + "\n"
	syntax_tree_top=syntax_tree_top-2


def syntax_tree_lab1():
	global syntax_tree_label
	#print("L"+str(label)+":")
	syntax_tree_label = syntax_tree_label+1


def syntax_tree_lab2():
	global syntax_tree_tmp, syntax_tree_i_, syntax_tree_top, syntax_tree_li, syntax_tree_label, syntax_tree_wh, syntax_tree
	tmp = "N"
	tmp+=str(syntax_tree_i_)
	#print("NODE "+tmp +" -> "+str(syntax_tree_li[syntax_tree_top-2])+" <-- "+ str(syntax_tree_li[syntax_tree_top-1])+" --> "+ str(syntax_tree_li[syntax_tree_top]))
	#print("if "+tmp+" goto L"+str(label-1));
	syntax_tree += "NODE " + tmp + " -> " + str(syntax_tree_li[syntax_tree_top-2]) + " <-- " + str(syntax_tree_li[syntax_tree_top-1]) + " --> " + str(syntax_tree_li[syntax_tree_top]) + "\n"
	syntax_tree_i_=syntax_tree_i_+1
	syntax_tree_wh[0]=tmp
	syntax_tree_label = syntax_tree_label-1
	syntax_tree_top = syntax_tree_top-3


"""
Lexical Analyzer

"""

def validLexeme(string):
	
	res = False
	if(string in keyword):
		#print("key " + string + "\n")
		res = "keyword"
	elif(string in dataType):
		#print("dataType " + string + "\n")
		res = "dataType"
	elif(string in preDefRoutine):
		res = "preDefRoutine"
	elif(re.match(identifier, string)):
		#print("id " + string + "\n")
		res = "identifier"
	elif(re.match(punctuator, string)):
		#print("punc " + string)
		res = "punctuator"
	elif(re.match(number, string)):
		res = "number"
	elif(re.match(aritmeticOperator, string)):
		res = "arithmeticOperator"
	elif(re.match(assignmentOperator, string)):
		res = "assignmentOperator"
	elif(string in relationalOperator):
		res = "relationalOperator"
	elif(string in logicalOperator):
		res = "logicalOperator"
	elif(string == "#"):
		res = "hashOperator"
	elif(string == ".h"):
		res = "headerExtension"
	elif(string == "true" or string == "false"):
		res = "boolean"
	elif(string == "++"):
		res = "incrementOperator"
	elif(string == "--"):
		res = "decrementOperator"
	return res

def lexer():
	global lb
	global fp
	
	lexeme = prg[lb:fp]
	
	while(re.match(spaces, lexeme)):
		#print("x " + lexeme + "\n")
		lb = lb + 1
		fp = fp + 1
		lexeme = prg[lb:fp]
	
	#if(re.match(spaces, prg[
	#print("lexeme: " + lexeme + " type: " + str(type(lexeme)) + "\n");
	res = validLexeme(lexeme)
	while((not res) and (fp <= len(prg))):
		#print("lexeme1: " + lexeme + "\n")
		fp = fp + 1
		lexeme = prg[lb:fp]
		res = validLexeme(lexeme)
	
	#print(lexeme + "\n")
	tokenType = res
	res = validLexeme(lexeme)
	while((res) and (fp <= len(prg))):
		#print("lexeme2: " + lexeme + "\n")
		fp = fp + 1
		lexeme = prg[lb:fp]
		tokenType = res
		res = validLexeme(lexeme)
	
	lexeme = prg[lb:fp - 1]
	lb = fp - 1
	
	if((tokenType != False) and (tokenType not in symbolTable)):
		symbolTable[tokenType] = list()
		
	if((tokenType != False) and lexeme not in symbolTable[tokenType]):
		symbolTable[tokenType].append(lexeme.strip())
	
	#print("TOKEN: " + str(lexeme) + " TYPE: " + str(tokenType) + "\n");
	#print(str(lb) + " " + str(fp) + "\n")
	#print(str(len(prg)))
	return dict({tokenType:lexeme})

"""
Parser functions for recursive descent parsing with backtracking

"""

def parse_start():
	
	status = program()
	
	if(status == 0):
		print("\nIntermediate code:\n")
		print(intermediate_code)

		print("\nSyntax Tree:\n")
		print(syntax_tree)
		print("SUCCESSFUL PARSING\n") 

	else:
		 print("FAILED PARSING\n")
	
	
def program():

	status = preProcessorDirective()
	
	if(status == 0):
		status = externDeclaration()
		
		if(status == 0):
			status = mainFunction()
	
	return status

def preProcessorDirective():

	status = 0
	token = lexer()
	
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	
	if(token_type == "hashOperator"):
		
		token = lexer()
		token_type = list(token.keys())[0]
		token_value = list(token.values())[0]
		
		if(token_type == "keyword" and token_value == "include"):
				
			token = lexer()
			token_type = list(token.keys())[0]
			token_value = list(token.values())[0]
			
			if(token_type == "relationalOperator" and token_value == "<"):
				
				token = lexer()
				token_type = list(token.keys())[0]
				token_value = list(token.values())[0]
				
				if(token_type == "identifier"):
					
					token = lexer()
					token_type = list(token.keys())[0]
					token_value = list(token.values())[0]
					
					
					if(token_type == "headerExtension"):
					
						token = lexer()
						token_type = list(token.keys())[0]
						token_value = list(token.values())[0]	
					
						if(token_type == "relationalOperator" and token_value == ">"):
					
								status = preProcessorDirective()
								#print(str(status) + " after return\n")
							
						else:
							print("Syntax error: expected '>' but received " + str(token_value) + "\n")
							status = 1
					else:
						print("Syntax error: expected 'Header Extension' but received " + str(token_value) + "\n")
						status = 1
						
				else:
					print("Syntax error: expected 'Identifer' but received " + str(token_value) + "\n")
					status = 1
			else:	
				print("Syntax error: expected '<' but received " + str(token_value) + "\n")
				status = 1
				
		elif(token_type == "keyword" and token_value == "define"):
			
			
			token = lexer()
			token_type = list(token.keys())[0]
			token_value = list(token.values())[0]
			
			if(token_type == "identifier"):
				
				variableName = token_value
				token = lexer()
				token_type = list(token.keys())[0]
				token_value = list(token.values())[0]
				
				if(token_type == "number"):
					
					variableValue = int(token_value.strip())
					symbolTable[variableName] = variableValue
					status = preProcessorDirective()
					
					
				else:
					print("Syntax error: expected 'Number' but received " + str(token_value) + "\n")
					status = 1
			else:
				print("Syntax error: expected 'Identifier' but received " + str(token_value) + "\n")
				status = 1
					
		else:
			print("Syntax error: expected 'Keyword include/define' but received " + str(token_value) + "\n")
			status = 1
	else:
		#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
		global lb, fp
		lb = lb - len(token_value)
		fp = fp - len(token_value)
		
	return status
	#print("Token key: " + str((token_type) + " values: " + str(token_value) + "\n"))	

def externDeclaration():
	
	
	status = 0
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]

	if(token_type == "keyword" and token_value == "extern"):

		status = declarationStatement()
		if(status == 0):
		
			token = lexer()
			token_type = list(token.keys())[0]
			token_value = list(token.values())[0].strip()

			if(not (token_type == "punctuator" and token_value == ";")):
				print("Syntax error: expected 'Punctuator Semicolon1' but received " + str(token_value) + "\n")
				status = 1
	else:
		#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
		global lb, fp
		lb = lb - len(token_value)
		fp = fp - len(token_value)	
	return status

def declarationStatement():
	
	status = 0
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	

	if(token_type == 'dataType'):
		
		dataType = token_value.strip()
		status = variable(dataType)
		
	else:
		print("Syntax error: expected 'Data Type' but received " + str(token_value) + "\n")
		status = 1
	
	return status
	
def optionalDeclarationStatement():
	
	status = 0
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	#print("before reset: " + str(token_value))
	#print("IN OPTDECL", token_type, token_value)

	if(token_type == 'dataType'):
	
		
		dataType = token_value.strip()
		status = variable(dataType)
		
	else:
	
		#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
		#print("resetting")
		global lb, fp
		lb = lb - len(token_value)
		fp = fp - len(token_value)
		status = 2
		#print("after reset: " + str(token_value))
	return status
	
	
def variable(dataType):

	status = 0
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	#print("variable", token_type, token_value)

	if(token_type == 'identifier'):
		
		#print("received identifier, " + str(token_value))
		variableName = token_value.strip()
		
		if(dataType not in externalVariables):
			externalVariables[dataType] = list()
		
		if(variableName not in externalVariables[dataType]):
			externalVariables[dataType].append(variableName)
			#print(externalVariables)
		
		else:

			print("Syntax error: The variable "+str(token_value)+" of type "+token_type+" has already been initiliazed.\n")
			status = 1
		if(status==0):
			status = variableDash(dataType)
	else:
		print("Syntax error: expected 'Identifier' but received " + str(token_value) + "\n")
		status = 1
	
	return status

def variableDash(dataType):

	status = 0
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	
	if(token_type == 'punctuator' and token_value == ','):
		
		token = lexer()
		token_type = list(token.keys())[0]
		token_value = list(token.values())[0]
	
		if(token_type == 'identifier'):
			
			variableName = token_value.strip()
			if(dataType not in externalVariables):
				externalVariables[dataType] = list() 
		
			if(variableName not in externalVariables[dataType]):
				externalVariables[dataType].append(variableName)
			else:
				print("Syntax error: The variable "+str(token_value)+" of type "+token_type+" has already been initiliazed.\n")
				status = 1
			if(status==0):
				variableDash(dataType)
		
		else:
			print("Syntax error: expected 'Identifier' but received " + str(token_value) + "\n")
			status = 1
	else:
		#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
		global lb, fp
		#print(token_value)
		#print(str(lb) + " " + str(fp))
		lb = lb - len(token_value)
		fp = fp - len(token_value)
		#print(str(lb) + " " + str(fp))

	return status
	
def mainFunction():
	status = 0
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	
	if(token_type == "dataType" and token_value == "int"):
		
		status = mainDash()
		
	else:
		print("Syntax error: expected 'Return Type Integer' but received " + str(token_value) + "\n")
		status = 1
	
	return status
	
	
def mainDash():

	status = 0
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0].strip()
	
	#print(str(token_type) + " " + str(token_value))
	
	if(token_type == "identifier" and token_value == "main"):
	
		token = lexer()
		token_type = list(token.keys())[0]
		token_value = list(token.values())[0].strip()
		
		if(token_type == "punctuator" and token_value == "("):
		
			token = lexer()
			token_type = list(token.keys())[0]
			token_value = list(token.values())[0].strip()
			
			if(token_type == "punctuator" and token_value == ")"):
			
				token = lexer()
				token_type = list(token.keys())[0]
				token_value = list(token.values())[0].strip()
				
				if(token_type == "punctuator" and token_value == "{"):
				
					status = statements()
					
					if(status == 0):
						
						token = lexer()
						token_type = list(token.keys())[0]
						token_value = list(token.values())[0].strip()
						#print(token_value + str(len(token_value)))
						if(not(token_type == "punctuator" and token_value == "}")):
							print("Syntax error: expected 'Punctuator1 close curly bracket' but received " + str(token_value) + "\n")
							status = 1
				else:
					print("Syntax error: expected 'Punctuator open curly bracket' but received " + str(token_value) + "\n")
					status = 1
						
				
			
			elif(token_type == "dataType" and token_value == "int"):
			
				token = lexer()
				token_type = list(token.keys())[0]
				token_value = list(token.values())[0].strip()
				
				if(token_type == "identifier" and token_value == "argc"):
				
					token = lexer()
					token_type = list(token.keys())[0].strip()
					token_value = list(token.values())[0].strip()
					
					if(token_type == "punctuator" and token_value == ","):
				
						token = lexer()
						token_type = list(token.keys())[0]
						token_value = list(token.values())[0].strip()
						
						if(token_type == "dataType" and token_value == "char"):
				
							token = lexer()
							token_type = list(token.keys())[0]
							token_value = list(token.values())[0].strip()
							
							if(token_type == "arithmeticOperator" and token_value == "*"):
				
								token = lexer()
								token_type = list(token.keys())[0]
								token_value = list(token.values())[0]	.strip()
								
								if(token_type == "identifier" and token_value == "argv"):
				
									token = lexer()
									token_type = list(token.keys())[0]
									token_value = list(token.values())[0].strip()
									
									if(token_type == "punctuator" and token_value == "["):
				
										token = lexer()
										token_type = list(token.keys())[0]
										token_value = list(token.values())[0].strip()
										
										if(token_type == "punctuator" and token_value == "]"):
				
											token = lexer()
											token_type = list(token.keys())[0]
											token_value = list(token.values())[0].strip()
											
											if(token_type == "punctuator" and token_value == ")"):
				
												token = lexer()
												token_type = list(token.keys())[0]
												token_value = list(token.values())[0].strip()
											
												if(token_type == "punctuator" and token_value == "{"):
				
													status = statements()
					
													if(status == 0):
						
														token = lexer()
														token_type = list(token.keys())[0]
														token_value = list(token.values())[0].strip()
				
														if(not(token_type == "punctuator" and token_value == "}")):
															print("Syntax error: expected 'Punctuator2 close curly bracket' ", end = "")
															print("but received " + str(token_value) + "\n")
															status = 1
												else:
													print("Syntax error: expected 'Punctuator open curly bracket'  ", end = "")
													print("but received " + str(token_value) + "\n")
													status = 1
											
											else:
												print("Syntax error: expected 'Punctuator close round bracket' but received ", end = "")
												print(str(token_value) + "\n")
												status = 1
											
										else:
											print("Syntax error: expected 'Punctuator close square bracket' but received ", end = "")
											print(str(token_value) + "\n")
											status = 1
									else:
										print("Syntax error: expected 'Punctuator open square bracket' but received ", end = "")
										print(str(token_value) + "\n")
										status = 1
									
								else:
									print("Syntax error: expected 'Identifier argv' but received " + str(token_value) + "\n")
									status = 1
									
							else:
								print("Syntax error: expected 'Pointer operator *' but received " + str(token_value) + "\n")
								status = 1
							
						else:
							print("Syntax error: expected 'Data type character' but received " + str(token_value) + "\n")
							status = 1
						
					else:
						print("Syntax error: expected 'Punctuator comma' but received " + str(token_value) + "\n")
						status = 1	
				
				else:
					print("Syntax error: expected 'Identifier argc' but received " + str(token_value) + "\n")
					status = 1
				
			
			else:
				print("Syntax error: expected 'Punctuator close round bracket' but received " + str(token_value) + "\n")
				status = 1
				
		else:
			print("Syntax error: expected 'Punctuator open round bracket' but received " + str(token_value) + "\n")
			status = 1
	
	else:
		print("Syntax error: expected 'Identifier main' but received " + str(token_value) + "\n")
		status = 1
		
	return status
data = {}
def statements():
	
	
	#print("top of statements\n")
	status = 0
	status = initializationStatement()
	global syntax_tree

	if(status == 0):
		#print("init success")
		token = lexer()
		token_type = list(token.keys())[0]
		token_value = list(token.values())[0]
		#print(token_value +" new value")
		tv = token_value.strip()
		if(token_type == "punctuator" and tv == ";"):

			status = statements()
		else:
			print("Syntax error: expected 'Punctuator semicolon2' but received " + str(token_value) + "\n")
			status = 1
			
			
	else:

		status = optionalDeclarationStatement()
		#print(status)
		if(status == 0):	
			#print("decl success")
			
			token = lexer()
			token_type = list(token.keys())[0]
			token_value = list(token.values())[0]
			tv = token_value.strip()
			if(token_type == "punctuator" and tv == ";"):
				
				status = statements()
			else:
				print("Syntax error: expected 'Punctuator semicolon3' but received " + str(token_value) + "\n")
				status = 1
		else:
			
			status = assignmentStatement()
			if(status == 0):
				#print("assgn success")
				syntax_tree += "assgn success\n"
				
				token = lexer()
				token_type = list(token.keys())[0]
				token_value = list(token.values())[0]
				tv = token_value.strip()
				if(token_type == "punctuator" and tv == ";"):
					status = statements()
				else:
					print("Syntax error: expected 'Punctuator semicolon4' but received " + str(token_value) + "\n")
					status = 1
			else:
				
				status = 0
				token = lexer()
				token_type = list(token.keys())[0]
				token_value = list(token.values())[0]
				#print("IN statements: " + token_value)
				if(token_type == "keyword" and token_value == "do"):
					#print("Do")
					global syntax_tree_do
					syntax_tree_do = syntax_tree_do+1
					token = lexer()
					token_type = list(token.keys())[0]
					token_value = list(token.values())[0].strip()
					lab1()
					syntax_tree_lab1()
					if(token_type == "punctuator" and token_value == "{"):
						#print("{")
						status = statements()
					

						#print("status: " + str(status))
						if(status == 0):
					
							token = lexer()
							token_type = list(token.keys())[0]
							token_value = list(token.values())[0].strip()
							#print(token_value)
							if(token_type == "punctuator" and token_value == "}"):
								#print("}")
								token = lexer()
								token_type = list(token.keys())[0]
								token_value = list(token.values())[0].strip()
								syntax_tree_do = syntax_tree_do-1
								
								if(syntax_tree_do == 0):
									syntax_tree += "main --> do" + "\n"
								else:
									syntax_tree += "do --> do" + "\n"

								if(token_type == "keyword" and token_value == "while"):
									#print("while")
									token = lexer()
									token_type = list(token.keys())[0]
									token_value = list(token.values())[0].strip()
		
									if(token_type == "punctuator" and token_value == "("):
										#print("(")
										status = condition()
										lab2()
										syntax_tree_lab2()
										if(status == 0):
					
											token = lexer()
											token_type = list(token.keys())[0]
											token_value = list(token.values())[0].strip()
		
											if(token_type == "punctuator" and token_value == ")"):
												#print(")")
												global syntax_tree_wh
												syntax_tree += "while --> " + syntax_tree_wh[0] + "\n"
												token = lexer()
												token_type = list(token.keys())[0]
												token_value = list(token.values())[0].strip()
		
												if(token_type == "punctuator" and token_value == ";"):
													#print("in statements: " + token_value + "\n")
													status = statements()
													if(syntax_tree_do == 0):
														syntax_tree += "main --> while" + "\n"
													else:
														syntax_tree += "do --> while" + "\n"
					
												else:
													print("Syntax error: expected 'Punctuator semicolon5' ", end = "")
													print("but received " + str(token_value) + "\n")
													status = 1
					
											else:
												print("Syntax error: expected 'Punctuator close round bracket' ", end = "")
												print("but received " + str(token_value) + "\n")
												status = 1
					
									else:
										print("Syntax error: expected 'Punctuator open round bracket' ", end = "") 
										print("but received " + str(token_value) + "\n")
										status = 1
					
								else:
									print("Syntax error: expected 'Keyword while' but received " + str(token_value) + "\n")
									status = 1
					
							else:
								print("Syntax error: expected 'Punctuator10 close curly bracket' but received " + str(token_value) + "\n")
								status = 1
					
					else:
						print("Syntax error: expected 'Punctuator open curly bracket' but received " + str(token_value) + "\n")
						status = 1
		
				
				else:
					status = 0
					tv = token_value.strip()
					#print("IN statements: " + token_value)
					if(tv == "{"):
							status = statements()
							
							#print("status: " + str(status))
							if(status == 0):
						
								token = lexer()
								token_type = list(token.keys())[0]
								token_value = list(token.values())[0].strip()
								#print(token_value)
								if(token_type == "punctuator" and token_value == "}"):
									status = statements()
								else:
									print("Syntax error: expected 'Punctuator close curly bracket' but received " + str(token_value) + "\n")
					else:
			
						#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
						global lb, fp
						#print(token_value)
						#print(str(lb) + " " + str(fp))
						lb = lb - len(token_value)
						fp = fp - len(token_value)
						#status = 2
									
	
	return status




def initializationStatement():

	status = 0
	
	global lb, fp
		
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	#print("initializationStatement", token_type, token_value)

	if(token_type == "dataType"):
		if(token_value not in data):
			data[token_value] = {}
		
		status = initStat(token_value)
		
		
	else:
		
		#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
		#print(token_value)
		#print(str(lb) + " " + str(fp))
		lb = lb - len(token_value)
		fp = fp - len(token_value)
		status = 2
	#print('returning' + str(status))	
	return status
	
	
def initStat(dt):


	status = multipleInitialization(dt)
	#print(status)	
	
	return status
		
def multipleInitialization(dt):
	global data
	status = 0
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]

	#print("multipleInitialization", token_type, token_value)
	tk = token_value
	if(token_type == "identifier"):

		for data_type in data:
			if(token_value in data[data_type]):
				print("Syntax error:", token_value, "already declared as type", data_type)
				sys.exit("FAILED PARSING")

		push(tk)
		syntax_tree_push(tk)
		#print(tk)
		if(token_value not in data[dt]):
			
			if(dt=="int"):
				data[dt][token_value]=int(0)
			elif(dt=="char"):
				data[dt][token_value]=str(0)
			elif(dt=="float"):
				data[dt][token_value]=float(0)
			elif(dt=="double"):
				data[dt][token_value]=float(0)
			else:
				data[dt][token_value]=0
			#print(" "+token_value +":)")
			
		else:
			print("Syntax error: The variable has already been initialized\n")
			return 1
		
		token = lexer()
		token_type = list(token.keys())[0]
		token_value = list(token.values())[0]
		tv = token_value.strip()
		
		if(tv == ";"):
			#print("; la")
			global lb, fp
			#print(token_value)
			#print(str(lb) + " " + str(fp))
			lb = lb - len(token_value)
			fp = fp - len(token_value)
			return 0
		elif(token_type == "assignmentOperator" and tv == "="):
				
			status = E(dt,tk)
			codegen_assign()
			syntax_tree_gen_assign()
			#print(status)
			
			if(status == 0):
				
				status = multinit(dt)
				#if(status == 2):
					#status = 0
				#print(status)
		elif(token_type == "punctuator" and tv == ","):
			#print(",")
			status = multipleInitialization(dt)
			
		else:
				
			print("Syntax error: expected 'Assignment2 Operator' but received " + str(tv) + "\n")
			status = 1
	else:
			
		print("Syntax error: expected 'Identifier' but received " + str(tv) + "\n")
		status = 1
	
	return status
	
def multinit(dt):

	status = 0
	
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	tv = token_value.strip()
	
	if(token_type == "punctuator" and tv == ","):
	
		#print("got comma")
		status = multipleInitialization(dt)
	
	else:
		
		#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
		global lb, fp
		#print(token_value)
		#print(str(lb) + " " + str(fp))
		lb = lb - len(token_value)
		fp = fp - len(token_value)
		status = 0
		
	return status

def assignmentStatement():
	global data
	dty =''
	status = 0
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	tk = token_value
	#print("asgn")
	if(token_type == "identifier"):
		push(tk)
		syntax_tree_push(tk)
		#print(tk)
		for i in data:
			for j in data[i]:
				if(j==token_value):
					dty = i
		if(dty==''):
			print("Syntax error: The variable "+token_value+" has not been initialized.")
			sys.exit("FAILED PARSING\n")

		token = lexer()
		token_type = list(token.keys())[0]
		token_value = list(token.values())[0]
	
		if(token_type == "assignmentOperator" and token_value == "="):
				
			status = E(dty,tk)
			codegen_assign()
			syntax_tree_gen_assign()
			
		else:
			
			print("Syntax error: expected 'Assignment3 Operator' but received " + str(token_value) + "\n")
			status = 1
	else:
			
		#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
		global lb, fp
		#print(token_value)
		#print(str(lb) + " " + str(fp))
		lb = lb - len(token_value)
		fp = fp - len(token_value)
		status = 2
	
	return status

def condition():

	status = 0
	
	status = C()
			
	return status

def C():
	status = 0
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	tv = token_value.strip()
	if(token_type == "identifier" or token_type=="number"):
		push(tv)
		syntax_tree_push(tv)
		token = lexer()
		token_type = list(token.keys())[0]
		token_value = list(token.values())[0]
		tk = token_value.strip()
		if(token_type == "relationalOperator" or token_type == "logicalOperator"):
			push(tk)
			syntax_tree_push(tv)
			status = C() 
		elif(token_value == ")"):
			global lb, fp
			#print(token_value)
			#print(str(lb) + " " + str(fp))
			lb = lb - len(token_value)
			fp = fp - len(token_value)
			return 0
		else:
			return 1
	elif(not (token_type == "boolean")):
		
			print("Syntax error: expected 'Boolean' but received " + str(token_value) + "\n")
			status = 1
	return status

def E(dt,vn):

	status = F(dt,vn)

	if(status == 0):
	
		status = E1(dt,vn)
	
	return status
	
def E1(dt,vn):

	status = 0

	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	tv = token_value.strip()
	global op
	if(token_type == "arithmeticOperator" and tv == "+"):
		op = "+"
		push(tv)
		syntax_tree_push(tv)
		#print(tv)
		status = F(dt,vn)
		codegen()
		syntax_tree_gen()
		if(status == 0):
		
			status = E1(dt,vn)
			
	else:
	
		#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
		global lb, fp
		#print(token_value)
		#print(str(lb) + " " + str(fp))
		lb = lb - len(token_value)
		fp = fp - len(token_value)

	return status


def F(dt,vn):

	status = 0
	
	status = G(dt,vn)
	
	if(status == 0):
	
		status = F1(dt,vn)

	return status
	
def F1(dt,vn):

	status = 0

	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	tv = token_value.strip()
	global op
	if(token_type == "arithmeticOperator" and tv == "-"):
		op = "-"
		push(tv)
		syntax_tree_push(tv)
		#print(tv)
		status = G(dt,vn)
		codegen()
		syntax_tree_gen()
		if(status == 0):
		
			status = F1(dt,vn)
			
	else:
	
		#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
		global lb, fp
		#print(token_value)
		#print(str(lb) + " " + str(fp))
		lb = lb - len(token_value)
		fp = fp - len(token_value)

	return status
	
def G(dt,vn):

	status = 0
	
	status = H(dt,vn)

	if(status == 0):
	
		status = G1(dt,vn)

	return status

def G1(dt,vn):

	status = 0
	
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	tv = token_value.strip()
	global op
	if(token_type == "arithmeticOperator" and tv == "*"):
		push(tv)
		syntax_tree_push(tv)
		#print(tv)
		op = "*"
		status = H(dt,vn)
		codegen()
		syntax_tree_gen()
		if(status == 0):
		
			status = G1(dt,vn)
			
	else:
	
		#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
		global lb, fp
		#print(token_value)
		#print(str(lb) + " " + str(fp))
		lb = lb - len(token_value)
		fp = fp - len(token_value)


	return status
	
def H(dt,vn):

	status = 0
	
	status = I(dt,vn)
	
	if(status == 0):
	
		status = H1(dt,vn)

	return status
	
def H1(dt,vn):

	status = 0
	
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	tv = token_value.strip()
	
	if(token_type == "arithmeticOperator" and tv == "/"):
		global op
		op = "d"
		push(tv)
		syntax_tree_push(tv)
		#print(tv)
		status = I(dt,vn)
		codegen()
		syntax_tree_gen()
		if(status == 0):
		
			status = H1(dt,vn)
			
	else:
	
		#RESET POINTERS SINCE A WRONG TOKEN WAS OBTAINED
		global lb, fp
		#print(token_value + ":::" + str(len(token_value)))
		#print(str(lb) + " " + str(fp))
		
		lb = lb - len(token_value)
		fp = fp - len(token_value)

	return status
	
def I(dt,vn):
	global data, op
	status = 0
	chk = 0
	token = lexer()
	token_type = list(token.keys())[0]
	token_value = list(token.values())[0]
	tv = token_value.strip()
	#print("I", token_type, token_value)

	if(token_type == "arithmeticOperator" and tv == "-"):
		chk = 1
		push(tv)
		syntax_tree_push(tv)
		#print(tv)
		status = I(dt, vn)
		codegen_umin()
		syntax_tree_gen_umin()
	elif(not(token_type == "identifier" or token_type == "number")):
		print("Syntax error: expected 'Identifier/Number' but received " + str(token_value))
		status = 1
		return status
	if(token_type == "identifier" or token_type == "number"):
		#print("identifier")
		push(tv)
		syntax_tree_push(tv)
		#print(tv)

	if(token_type == "identifier"):
		if(token_value not in data[dt]):
			print("Syntax error: The variable " + token_value + " is has not been declared as an '" + dt + "'")
			sys.exit("FAILED PARSING\n")

	elif(token_value == "number"):
		if(not isinstance(token_value,dt)):
			print("Syntax error: The variable " + token_value + " belongs to a different type")
			sys.exit("FAILED PARSING\n")

	if(op==""):
		if(token_type == "identifier"):

			if(chk==1):
				data[dt][vn]=-1*data[dt][token_value]
				chk = 0
			else:
				#print(token_value)
				data[dt][vn]=data[dt][token_value]
			
		if(token_type == "number"):
			if(chk==1):
				data[dt][vn]=-1*float(token_value)
				chk = 0
			else:
				data[dt][vn]=float(token_value)
	elif(op=="d"):
		if(token_type == "identifier"):
			if(chk==1):
				data[dt][vn]/=-1*data[dt][token_value]
				chk = 0
				op=""
			else:
				data[dt][vn]/=data[dt][token_value]
				op=""
			
		if(token_type == "number"):
			if(chk==1):
				data[dt][vn]/=-1*float(token_value)
				chk = 0
				op = ""
			else:
				data[dt][vn]/=float(token_value)
				op = ""
	elif(op=="*"):
		if(token_type == "identifier"):
			if(chk==1):
				data[dt][vn]*=-1*data[dt][token_value]
				chk = 0
				op=""
			else:
				data[dt][vn]*=data[dt][token_value]
				op=""
			
		if(token_type == "number"):
			if(chk==1):
				data[dt][vn]*=-1*float(token_value)
				chk = 0
				op = ""
			else:
				data[dt][vn]*=float(token_value)
				op = ""
	elif(op=="-"):
		if(token_type == "identifier"):
			if(chk==1):
				data[dt][vn]-=-1*data[dt][token_value]
				chk = 0
				op=""
			else:
				data[dt][vn]-=data[dt][token_value]
				op=""
			
		if(token_type == "number"):
			if(chk==1):
				data[dt][vn]-=-1*float(token_value)
				chk = 0
				op = ""
			else:
				data[dt][vn]-=float(token_value)
				op = ""
	elif(op=="+"):
		if(token_type == "identifier"):
			if(chk==1):
				data[dt][vn]+=-1*data[dt][token_value]
				chk = 0
				op=""
			else:
				data[dt][vn]+=data[dt][token_value]
				op=""
			
		if(token_type == "number"):
			if(chk==1):
				data[dt][vn]+=-1*float(token_value)
				chk = 0
				op = ""
			else:
				#print(data)
				data[dt][vn]+=float(token_value)
				op = ""
	return status

"""
Removes comments from the source code

"""

def remove_comments(text):
    p = r'/\*[^*]*\*+([^/*][^*]*\*+)*/|//[^\n]*|("(\\.|[^"\\])*"|\'(\\.|[^\'\\])*\'|.[^/"\'\\]*)'
    return ''.join(m.group(2) for m in re.finditer(p, text, re.M|re.S) if m.group(2))

input_code = open("input.c").read()
prg = remove_comments(input_code)


loadSymbolTable()
parse_start()




		
	
