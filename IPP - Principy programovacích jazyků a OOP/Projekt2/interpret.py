# -*- coding: utf-8 -*-
from __future__ import print_function
import xml.etree.ElementTree as ET
import sys, getopt

# INSTRUCTIONS

zero_operands_inst = ("CREATEFRAME","PUSHFRAME","POPFRAME","BREAK","RETURN")
one_operands_inst_var = ("DEFVAR","POPS")
one_operands_inst_label = ("CALL","LABEL","JUMP")
one_operands_inst_symb = ("PUSHS","WRITE","EXIT","DPRINT")

two_operands_inst_var_symb = ("MOVE","NOT","INT2CHAR","STRLEN","TYPE")
two_operands_inst_var_type = ("READ")

three_operands_inst_var_int_or_var = ("ADD","SUB","MUL","IDIV")
three_operands_inst_var_other = ("LT","GT","EQ","AND","OR","STRI2INT","CONCAT","GETCHAR","SETCHAR")
three_operands_inst_label_other = ("JUMPIFEQ","JUMPIFNEQ")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


fileso = None
filein = None
opts, args = getopt.getopt(sys.argv[1:], None,["source=","input=","help"])


mystdin = sys.stdin

for opt, arg in opts:
    if opt == "--source":
        try:
            fileso = open(arg,"r")
        except:
            eprint("Chyba pri otevirani souboru pro source")
            sys.exit(11)
    elif opt == "--input":
        try:
            filein = open(arg,"r")
        except:
             eprint("Chyba pri otevirani souboru pro input")
             sys.exit(11)
    elif opt == "--help":
        print("Skript interpret.py\n")
        if len(opts) == 1:
            sys.exit(0)
        else:
            sys.exit(10)
        
if opts:
    if opts[0][0] not in ("--source","--input"):
        eprint("neni zadany parametr --source ani --input")
        sys.exit(10)
else:
     eprint("neni zadany parametr --source ani --input")
     sys.exit(10)

    


if fileso == None:
    fileso = ""
    for line in sys.stdin:
        fileso += line
        
    try:
       root = ET.fromstring(fileso)
    except:
        eprint("Spatna struktura XML na vstupu")
        sys.exit(31)
    
else:
    if filein != None:
        sys.stdin = filein
        
    try:
        tree = ET.parse(fileso)
        root = tree.getroot()
    except:
        eprint("Spatna struktura XML na vstupu")
        sys.exit(31)
    
"""
if filein == None:
    filein = []
    for line in sys.stdin:
        filein.append(line)
        filein = list(reversed(filein))
"""


    




    




order_arr=[0]
program = {}

global_frame={}
temp_frame={}

local_frame=[]



local_frame_stack=[]
labels_dict={}


temp_frame_act = False


# prevod ecscape sekvence na znak
def isstring(order, string):
    i = 0
    transtr = ""
    if string == None:
        string = ""
    while i < len(string):
        c = string[i]
        if c == '\\':
            try:
                char1 = string[i+1]
                char2 = string[i+2]
                char3 = string[i+3]
                value = (100 * int(char1) + 10 * int(char2) + int(char3))
                if value <= 0 or value >= 999:
                    eprint("Radek:",order,"Chyba - Znak mimo povoleny rozsah")
                    sys.exit(32)
            except:
                eprint("Radek:",order,"Chyba - Spatna escape sekvence u stringu")
                sys.exit(32)
            i = i + 3
            transtr =  transtr + chr(value)
        else:
            transtr = transtr + c
        i = i + 1
    return transtr
    


# prevod na bool
def isbool(order, symb):
    if symb == "true":
        return True
    elif symb == "false":
        return False
    else:
        eprint("Radek:",order,"Chyba -",symb,"musi byt datoveho typu bool")
        sys.exit(53)

# prevod na int
def isint(order, symb):
    #print("zavolal")
    try:
        value = int(symb)
    except ValueError:
        eprint("Radek:",order,"Chyba -",symb,"musi byt datoveho typu int")
        sys.exit(53)
    else:
        return value

    
# Zapis nebo cteni z promenne v danem ramci
# vraci dvojici (hodnota, typ)
def work_with_var(var, value, typ, operation):
    global global_frame, local_frame_stack, temp_frame, temp_frame_act
    frame = var[:2]
    var_str = var[3:]
    if frame == "GF":
        if var_str in global_frame:
            if operation == "write":
                global_frame[var_str][0] = value
                global_frame[var_str][1] = typ
            else:
                value = global_frame[var_str][0]
                typ = global_frame[var_str][1]
        else:
            eprint("Chyba - Pokus o pristup k nedefinovane promenne",var,"v ramci GF")
            sys.exit(54)
    
    elif frame == "LF":
        if local_frame_stack:
            if var_str in local_frame_stack[len(local_frame_stack)-1]:
                if operation == "write":
                    local_frame_stack[len(local_frame_stack)-1][var_str][0] = value
                    local_frame_stack[len(local_frame_stack)-1][var_str][1] = typ
                else:
                    value = local_frame_stack[len(local_frame_stack)-1][var_str][0]
                    typ = local_frame_stack[len(local_frame_stack)-1][var_str][1]
            else:
                eprint("Chyba - Pokus o pristup k nedefinovane promenne",var,"v aktualnim ramci LF")
                sys.exit(54)
        else:
            eprint("Chyba - Pokus o pristup k promenne",var,"v nedefinovanem ramci LF")
            sys.exit(55)
            
    elif frame == "TF":
        if temp_frame_act:
            if var_str in temp_frame:
                if operation == "write":
                    temp_frame[var_str][0] = value
                    temp_frame[var_str][1] = typ
                else:
                    value = temp_frame[var_str][0]
                    typ = temp_frame[var_str][1]
            else:
                eprint("Chyba - Pokus o pristup k nedefinovane promenne",var,"v ramci TF")
                sys.exit(54)
        else:
            eprint("Chyba - Pokus o pristup k promenne",var,"v nedefinovanem ramci TF")
            sys.exit(55)
            
            
    return value, typ
    
    
# prida promenou do daneho ramce (funkce DEFVAR)
def add_to_XX_frame(var):
    global global_frame, local_frame_stack, temp_frame, temp_frame_act
    frame = var[:2]
    var_str = var[3:]
    if frame == "GF":
        if not(var_str in global_frame):
            global_frame.update({var_str : ["",""]})
        else:
            eprint("Chyba - Pokus o redefinici promenne",var,"v ramci GF")
            sys.exit(52)
            
    elif frame == "LF":
        if local_frame_stack:
            if not(var_str in local_frame_stack[len(local_frame_stack)-1]):
                local_frame_stack[len(local_frame_stack)-1].update({var_str : ["",""]})
            else:
                eprint("Chyba - Pokus o redefinici promenne",var,"v ramci LF")
                sys.exit(52)
        else:
            eprint("Chyba - Pokus o vlozeni",var,"do nedefinovaneho LF")
            sys.exit(55)
            
    elif frame == "TF":
        if temp_frame_act:
            if not(var_str in temp_frame):
                temp_frame.update({var_str : ["",""]})
            else:
                eprint("Chyba - Pokus o redefinici promenne",var,"v ramci TF")
                sys.exit(52)
        else:
            eprint("Chyba - Pokus o vlozeni",var,"do nedefinovaneho TF")
            sys.exit(55)

    return 
        
#prepocet orderu na index v poli
def recalc_inst_pointer_pos(program_arr, order): 
    i = 0
    for row in program_arr:
        for key in row:
            if order == key:
                return i
            else: 
                i = i + 1

# kontrola jestli je promenna ve spravnem tvaru
def check_var_syntax(var):
        frame = var[:3]
        var_str = var[3:]
        if frame != "GF@" and  frame != "LF@" and frame != "TF@":
            eprint(var,"Spatny format promenne!")
            sys.exit(32)
        if var_str[0].isdigit():
            eprint(var,"Spatny format promenne!")
            sys.exit(32)
        for char in var_str[4:]:
            if(char.isspace() or not(char.isalnum() or char == '&' or char == '_' or char == '%' or char == '-' or char == '$' or char == '*')):
                eprint(var,"Spatny format promenne!")
                sys.exit(32)
        return 


         
# kontrola jestli je konstanta ve spravnem tvaru
def check_symb_syntax(symb_type, text):
    if symb_type == "string":
        if text == None:
            text = ""
        for char in text:
            if char == "#" or char.isspace():
                 eprint("Spatny format retezce")
                 sys.exit(32)
    elif symb_type == "int":
        try:
            int(text)
        except ValueError:
            eprint("Spatny format integeru")
            sys.exit(32)
        
    elif symb_type == "bool":
        if text != "true" and text != "false":
            eprint("Spatny format boolu")
            sys.exit(32)
    elif symb_type == "nil":
        if text != "nil":
            eprint("Spatny format nilu")
            sys.exit(32)
    else:
         eprint("Spatny format konstanty")
         sys.exit(32)
     
    return 
        

#kontrola jestli je navesti ve spravnem tvaru
def check_label_syntax(label):
    if label[0].isdigit():
        eprint("Spatny format navesti")
        sys.exit(32)
    for char in label[1:]:
        if(char.isspace() or not(char.isalnum() or char == '&' or char == '_' or char == '%' or char == '-' or char == '$' or char == '*')):
             eprint("Spatny format navesti")
             sys.exit(32)
             
    return


# kontrola jednoho instrukcniho radku
def check_instruction_syntax(order, opcode, operands):
    global labels_dict
    
    if opcode in zero_operands_inst:
        if operands:
            eprint("Radek:",order,"Chyba - operand u instrukce",opcode,"ktera je bez operandu")
            sys.exit(32)
    
    
    elif opcode in one_operands_inst_var:
        if len(operands) == 1:
            if operands[0].get("type") == "var":
                check_var_syntax(operands[0].text)
            else:
                 eprint("Radek:",order,"Chyba - Spatny datovy typ operandu u instrukce",opcode,"s 1 operandem <var>")
        else:
            eprint("Radek:",order,"Chyba - Spatny pocet operandu u",opcode)
            sys.exit(32)
            
            
    elif opcode in one_operands_inst_label:
        if len(operands) == 1:
            if operands[0].get("type") == "label":
                check_label_syntax(operands[0].text)
                if opcode == "LABEL":
                    if not(operands[0].text in labels_dict.keys()):
                        labels_dict.update({operands[0].text : order})
                    else:
                        eprint("Radek:",order,"Chyba - Pokus o redefinici navesti",operands[0].text)
                        sys.exit(52)
            else:
                eprint("Radek:",order,"Chyba - Spatny datovy typ operandu u instrukce",opcode,"s 1 operandem <label>")
                sys.exit(32)
        else:
            eprint("Radek:",order,"Chyba - Spatny pocet operandu u instrukce",opcode,"s 1 operandem <label>")
            sys.exit(32)
            
            
    elif opcode in one_operands_inst_symb:
         if len(operands) == 1:
            if operands[0].get("type") == "var":
                check_var_syntax(operands[0].text)
            elif operands[0].get("type") in ("string","int","bool","nil"):
                check_symb_syntax(operands[0].get("type"), operands[0].text)
            else:
                 eprint("Radek:",order,"Chyba - Spatny datovy typ operandu u",opcode,"s 1 operandem <symb>")
                 sys.exit(32)
         else:
            eprint("Radek:",order,"Chyba - Spatny pocet operandu u",opcode,"s 1 operandem <symb>")
            sys.exit(32)
            
            
    elif opcode in two_operands_inst_var_symb:
         if len(operands) == 2:
            if operands[0].get("type") == "var":
                check_var_syntax(operands[0].text)
            else:
                eprint("Radek:",order,"Chyba - Spatny typ 1 operandu u instrukce se 2 operandy <var> <symb>")
                sys.exit(32)
                
                
            if operands[1].get("type") == "var":
                check_var_syntax(operands[1].text)
            elif operands[1].get("type") in ("string","int","bool","nil"):
                check_symb_syntax(operands[1].get("type"), operands[1].text)
            else:
                 eprint("Radek:",order,"Chyba - Spatny typ 2 operandu u instrukce se 2 operandy <var> <symb>")
                 sys.exit(32)
         else:
            eprint("Radek:",order,"Chyba - Spatny pocet operandu u instrukce se 2 operandy <var> <symb>")
            sys.exit(32)
        
        
    elif opcode in two_operands_inst_var_type:
        if len(operands) == 2:
            if operands[0].get("type") == "var" and operands[1].get("type") == "type":
                check_var_syntax(operands[0].text)
                if not(operands[1].text in ("int","string","bool")):
                    eprint("Radek:",order,"Chyba - Spatny typ operandu <type> u instrukce READ")
                    sys.exit(32)
            else:
                 eprint("Radek:",order,"Chyba - Spatny datovy typ operandu u instrukce READ")
                 sys.exit(32)
        else:
            eprint("Radek:",order,"Chyba - Spatny pocet operandu u instrukce se 2 operandy <var> <type>")
            sys.exit(32)
            
            
    elif opcode in three_operands_inst_var_int_or_var:
        if len(operands) == 3:
            if operands[0].get("type") == "var" and operands[1].get("type") in ("var","int","string","bool","nil") and operands[2].get("type") in ("var","int","string","bool","nil"):
                check_var_syntax(operands[0].text)
                if operands[1].get("type") == "var":
                    check_var_syntax(operands[1].text)
                else:
                    check_symb_syntax(operands[1].get("type"), operands[1].text)
                if operands[2].get("type") == "var":
                    check_var_syntax(operands[2].text)
                else:
                    check_symb_syntax(operands[2].get("type"), operands[2].text)
            else:
                eprint("Radek:",order,"Chyba - Spatny typ operandu u instrukce s 3 operandy <var> <symb> <symb>")
                sys.exit(32)
        else:
             eprint("Radek:",order,"Chyba - Spatny pocet operandu u instrukce",opcode,"s 3 operandy <var> <symb> <symb>")
             sys.exit(32)
            
            
    elif opcode in three_operands_inst_var_other:
        if len(operands) == 3:
            if operands[0].get("type") == "var" and operands[1].get("type") in ("var","string","int","bool","nil") and operands[2].get("type") in ("var","string","int","bool","nil"):
                check_var_syntax(operands[0].text)
                if operands[1].get("type") == "var":
                    check_var_syntax(operands[1].text)
                else:
                    check_symb_syntax(operands[1].get("type"), operands[1].text)
                if operands[2].get("type") == "var":
                    check_var_syntax(operands[2].text)
                else:
                    check_symb_syntax(operands[2].get("type"), operands[2].text)
            else:
                eprint("Radek:",order,"Chyba - Spatny typ operandu u instrukce s 3 operandy <var> <symb> <symb>")
                sys.exit(32)
        else:
             eprint("Radek:",order,"Chyba - Spatny pocet operandu u instrukce s 3 operandy <var> <symb> <symb>")
             sys.exit(32)
             
             
    elif opcode in three_operands_inst_label_other:
        if len(operands) == 3:
            if operands[0].get("type") == "label" and operands[1].get("type") in ("var","string","int","bool","nil") and operands[2].get("type") in ("var","string","int","bool","nil"):
                check_label_syntax(operands[0].text)
                if operands[1].get("type") == "var":
                    check_var_syntax(operands[1].text)
                else:
                    check_symb_syntax(operands[1].get("type"), operands[1].text)
                if operands[2].get("type") == "var":
                    check_var_syntax(operands[2].text)
                else:
                    check_symb_syntax(operands[2].get("type"), operands[2].text)
            else:
                eprint("Radek:",order,"Chyba - Spatny typ operandu u instrukce s 3 operandy <label> <symb> <symb>")
                sys.exit(32)
        else:
             eprint("Radek:",order,"Chyba - Spatny pocet operandu u instrukce s 3 operandy <label> <symb> <symb>")
             sys.exit(32)
    else:
        eprint("Radek:",order,"Chyba - neznamy opcode","\"",opcode,"\"")
        sys.exit(32)
    return



    



def interpret(program):
    global global_frame, local_frame_stack, temp_frame, temp_frame_act, labels_dict
    
    index = 0
    call_stack=[]
    data_stack=[]
    program_arr=[]
    
    for item in sorted(program.items()) : program_arr.append(dict([item]))
    
    
    
    while True:
        #print ("INDEX:",index)
        if index < len(program_arr):
            program = program_arr[index]
            
            for key in program : order = key
            opcode = program[order][0]
        else:
            break
    
        if opcode == "CREATEFRAME":
            temp_frame_act = True
            temp_frame = {}
           
            
        elif opcode == "MOVE":
            if program[order][2].get("type") == "var":
                value, typ = work_with_var(program[order][2].text, None, None, "get")
                if value == "" and typ == "":
                     eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                     sys.exit(56)
            else:
                value = program[order][2].text
                typ = program[order][2].get("type")
                
                if typ == "string":
                    value = isstring(order, value)
            
            work_with_var(program[order][1].text, value, typ, "write")
           
        
        elif opcode == "PUSHFRAME":
            if temp_frame_act == True:
                local_frame_stack.append(temp_frame)
               
                temp_frame_act = False
            else:
                eprint("Radek:",order,"Chyba - Pokus o PUSHFRAME nedefinovaneho ramce")
                sys.exit(55)
           
                
        elif opcode == "POPFRAME":
            if not local_frame_stack:
                eprint("Radek:",order,"Chyba - K provedeni POPFRAME neni zadny ramec LF k dispozici")
                sys.exit(55)
            else:
                temp_frame_act = True
                temp_frame = local_frame_stack.pop()
                
         
        
        elif opcode == "DEFVAR":
            add_to_XX_frame(program[order][1].text)
        
        
        elif opcode == "LABEL":
            pass
        
        
        elif opcode == "JUMP":
            if program[order][1].text in labels_dict.keys():
                order = labels_dict[program[order][1].text]
                
                index = recalc_inst_pointer_pos(program_arr, order)
            else:
                eprint("Radek:",order,"Chyba - Pokus o JUMP na nedefinovane navesti")
                sys.exit(52)
        
        
        elif opcode == "CALL":
            if program[order][1].text in labels_dict.keys():
                call_stack.append(order)
                order = labels_dict[program[order][1].text]
                index = recalc_inst_pointer_pos(program_arr, order)
            else:
                eprint("Radek:",order,"Chyba - Pokus o CALL na nedefinovane navesti")
                sys.exit(52)
                
                
        elif opcode == "RETURN":
            if call_stack:
                order = call_stack.pop()
                index = recalc_inst_pointer_pos(program_arr, order)
            else:
                eprint("Radek:",order,"Chyba - Pokus o RETURN bez predchoziho CALL")
                sys.exit(56)
            
        elif opcode == "PUSHS":
            if program[order][1].get("type") == "var":
                value1, typ1 = work_with_var(program[order][1].text, None, None,"get")
                data_stack.append((value1, typ1))
            else:
                if program[order][1].get("type") == "string":
                    value1 = isstring(order, program[order][1].text)
                else:
                    value1 = program[order][1].text
                    
                data_stack.append((value1, program[order][1].get("type")))
            
            
        elif opcode == "POPS":
            if data_stack:
                value, typ = data_stack.pop()
                work_with_var(program[order][1].text, value, typ , "write")
            else:
                 eprint("Radek:",order,"Chyba - Pokus o vyjmuti hodnoty z prazdneho zasobniku")
                 sys.exit(56)
                
                
        elif opcode in ("ADD","SUB","MUL","IDIV"):
            if program[order][2].get("type") == "var":
                value1, typ1 =  work_with_var(program[order][2].text, None, None, "get")
                if value1 == "" and typ1 == "":
                     eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                     sys.exit(56)
                else:
                    if typ1 == "int":
                        value1 = isint(order,value1)
                    else:
                        eprint("Radek:",order,"Chyba - Spatny datovy typ druheho operandu u instrukce",opcode)
                        sys.exit(53)
            else:
                if program[order][2].get("type") == "int":
                    value1 = isint(order, program[order][2].text)
                else:
                    eprint("Radek:",order,"Chyba - Spatny datovy typ druheho operandu u instrukce",opcode)
                    sys.exit(53)
            
            if program[order][3].get("type") == "var":
                value2, typ2 =  work_with_var(program[order][3].text, None, None, "get")
                if (value2 and typ2) == "":
                     eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                     sys.exit(56)
                else:
                    if typ2 == "int":
                        value2 = isint(order,value2)
                    else:   
                        eprint("Radek:",order,"Chyba - Spatny datovy typ tretiho operandu u instrukce",opcode)
                        sys.exit(53)
            else:
                if program[order][3].get("type") == "int":
                    value2 = isint(order, program[order][3].text)
                else:
                    eprint("Radek:",order,"Chyba - Spatny datovy typ tretiho operandu u instrukce",opcode)
                    sys.exit(53)
          
            if opcode == "ADD":
                work_with_var(program[order][1].text, value1 + value2, "int", "write")
            elif opcode == "SUB":
                work_with_var(program[order][1].text, value1 - value2, "int", "write")
            elif opcode == "MUL":
                work_with_var(program[order][1].text, value1 * value2, "int", "write")
            else:
                try:
                    value1 // value2
                except ZeroDivisionError:
                     eprint("Radek:",order,"Chyba - Deleni nulou u instrukce IDIV")
                     sys.exit(57)
                else:
                    work_with_var(program[order][1].text, value1 // value2, "int", "write")
           
            
        elif opcode in ("LT","GT","EQ"):
            if program[order][2].get("type") == "var":
                value1, typ1 = work_with_var(program[order][2].text, None, None, "get")
                if value1 == "" and typ1 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
            elif program[order][2].get("type") in ("int","bool","string","nil"):
                if program[order][2].get("type") == "string":
                    value1 = isstring(order, program[order][2].text)
                    typ1 = "string"
                else:
                    value1 = program[order][2].text
                    typ1 = program[order][2].get("type")
            else:
                eprint("Radek:",order,"Chyba - Spatny datovy typ druheho operandu u instrukce",opcode)
                sys.exit(53)
                
            if program[order][3].get("type") == "var":
                value2, typ2 = work_with_var(program[order][3].text, None, None, "get")
                if value2 == "" and typ2 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
            elif program[order][3].get("type") in ("int","bool","string","nil"):
                if program[order][3].get("type") == "string":
                    value2 = isstring(order, program[order][3].text)
                    typ2 = "string"
                else:
                    value2 = program[order][3].text
                    typ2 = program[order][3].get("type")
            else:
                eprint("Radek:",order,"Chyba - Spatny datovy typ tretiho operandu u instrukce",opcode)
                sys.exit(53)
            
            if typ1 != typ2 and not((typ1 == "nil" or typ2 == "nil") and opcode == "EQ"):
                eprint("Radek:",order,"Chyba - Rozdilne typy operandu u instrukce",opcode)
                sys.exit(53)
            else:
                if typ1 == "int":
                    value1 = isint(order, value1)
                if typ2 == "int":
                    value2 = isint(order, value2)
                    
                if typ1 == "bool":
                    value1 = isbool(order, value1)
                if typ2 == "bool":
                    value2 = isbool(order, value2)
                    
                if opcode == "LT":
                    if value1 < value2:
                        work_with_var(program[order][1].text, "true", "bool", "write")
                    else:
                        work_with_var(program[order][1].text, "false", "bool", "write")
                elif opcode == "GT":
                    if value1 > value2:
                        work_with_var(program[order][1].text, "true", "bool", "write")
                    else:
                        work_with_var(program[order][1].text, "false", "bool", "write")
                else:
                    if value1 == value2:
                        work_with_var(program[order][1].text, "true", "bool", "write")
                    else:
                        work_with_var(program[order][1].text, "false", "bool", "write")
               
                
        elif opcode in ("AND","OR"):
            if program[order][2].get("type") == "var":
                value1, typ1 = work_with_var(program[order][2].text, None, None, "get")
                if value1 == "" and typ1 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
            elif program[order][2].get("type") == "bool":
                value1 = program[order][2].text
                typ1 = "bool"
            else:
                eprint("Radek:",order,"Chyba - Spatny datovy typ druheho operandu u instrukce",opcode)
                sys.exit(53)
                
            if program[order][3].get("type") == "var":
                value2, typ2 = work_with_var(program[order][3].text, None, None, "get")
                if value2 == "" and typ2 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
            elif program[order][3].get("type") == "bool":
                value2 = program[order][3].text
                typ2 = "bool"
            else:
                eprint("Radek:",order,"Chyba - Spatny datovy typ tretiho operandu u instrukce",opcode)
                sys.exit(53)
            
            if not(typ1 == typ2 and typ1 == "bool"):
                eprint("Radek:",order,"Chyba - Typy operandu u instrukce",opcode,"nejsou bool")
                sys.exit(53)
            else:
                value1 = isbool(order, value1)
                value2 = isbool(order, value2)
                if opcode == "AND":
                    if value1 == True and value2 == True:
                         work_with_var(program[order][1].text, "true", "bool", "write")
                    else:
                         work_with_var(program[order][1].text, "false", "bool", "write")
                else:
                    if value1 == False and value2 == False:
                         work_with_var(program[order][1].text, "false", "bool", "write")
                    else:
                         work_with_var(program[order][1].text, "true", "bool", "write")
                         
                         
        elif opcode == "NOT":
            if program[order][2].get("type") == "var":
                value1, typ1 = work_with_var(program[order][2].text, None, None, "get")
                if value1 == "" and typ1 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
            elif program[order][2].get("type") == "bool":
                value1 = program[order][2].text
                typ1 = "bool"
            else:
                eprint("Radek:",order,"Chyba - Spatny datovy typ druheho operandu u instrukce NOT")
                sys.exit(53)
                
            if typ1 != "bool":
                eprint("Radek:",order,"Chyba - Typ operandu u instrukce NOT neni bool")
                sys.exit(53)
            else:
                value1 = isbool(order, value1)
                if value1 == True:
                    work_with_var(program[order][1].text, "false", "bool", "write")
                else:
                    work_with_var(program[order][1].text, "true", "bool", "write")
        
        
        elif opcode == "INT2CHAR":
            if program[order][2].get("type") == "var":
                value1, typ1 = work_with_var(program[order][2].text, None, None, "get")
                if value1 == "" and typ1 == "":
                     eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                     sys.exit(56)
                if typ1 != "int":
                     eprint("Radek:",order,"Chyba - operand musi by int")
                     sys.exit(53)
                try:
                    value1 = chr(int(value1))
                except ValueError:
                     eprint("Radek:",order,"Chyba - Nevalidni ordinalni hodnota druheho operandu u instrukce INT2CHAR")
                     sys.exit(58)
            else:
                if program[order][2].get("type") != "int":
                    eprint("Radek:",order,"Chyba - operand musi by int")
                    sys.exit(53)
                try:
                    value1 = chr(int(program[order][2].text))
                except ValueError:
                     eprint("Radek:",order,"Chyba - Nevalidni ordinalni hodnota druheho operandu u instrukce INT2CHAR")
                     sys.exit(58)
            
            work_with_var(program[order][1].text, value1, "string", "write")
            
            
        elif opcode == "STRI2INT":
            if program[order][2].get("type") == "var":
                value1, typ1 = work_with_var(program[order][2].text, None, None, "get")
                if value1 == "" and typ1 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
                    
                if typ1 != "string":
                    eprint("Radek:",order,"Chyba - Typ druheho operandu u instrukce STR2INT neni string")
                    sys.exit(53)
            else:
                value1 = program[order][2].text
                typ1 = program[order][2].get("type")
                if typ1 != "string":
                    eprint("Radek:",order,"Chyba - Typ druheho operandu u instrukce STR2INT neni string")
                    sys.exit(53)
                else:
                    value1 = isstring(order, value1)
            
            if program[order][3].get("type") == "var":
                value2, typ2 = work_with_var(program[order][3].text, None, None, "get")
                if value2 == "" and typ2 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
            else:
                value2 = program[order][3].text
                typ2 = program[order][3].get("type")
            
            if typ2 != "int":
                eprint("Radek:",order,"Chyba - Typ tretiho operandu u instrukce STR2INT neni int")
                sys.exit(53)
            else:
                value2 = isint(order, value2)
                if value2 > (len(value1)-1) or value2 < 0:
                    eprint("Radek:",order,"Chyba - Indexace mimo daný řetězec u instrukce STR2INT")
                    sys.exit(58)
                else:
                    work_with_var(program[order][1].text, ord(value1[value2]), "int", "write")
                        
                        
        elif opcode == "READ":
            try:
                value1 = input()#filein.pop()
            except:
                 work_with_var(program[order][1].text, "nil", "nil", "write")
            else:
                if program[order][2].text == "int":
                    try:
                        value1 = int(value1)
                    except:
                        work_with_var(program[order][1].text, "nil", "nil", "write")
                    else:
                        work_with_var(program[order][1].text, value1, "int", "write")
                         
                elif program[order][2].text == "bool":
                    if value1.lower() == "true":
                        work_with_var(program[order][1].text, "true", "bool", "write")
                    else:
                        work_with_var(program[order][1].text, "false", "bool", "write")
                else:
                    try:
                        value1 = str(value1)
                    except:
                        work_with_var(program[order][1].text, "nil", "nil", "write")
                    else:
                        if value1 == "":
                            work_with_var(program[order][1].text, "", "string", "write")
                        else:
                            work_with_var(program[order][1].text, value1, "string", "write")
                    
                    
        elif opcode == "WRITE":
            if program[order][1].get("type") == "var":
                value1, typ1 = work_with_var(program[order][1].text, None, None, "get")
                if typ1 == "nil":
                    print("", end="")
                else:
                    print(value1, end="")
            else:
                if program[order][1].get("type") == "nil":
                    print("", end="")
                elif program[order][1].get("type") == "string":
                    print(isstring(order, program[order][1].text), end="")
                else:
                    print(program[order][1].text, end="")
                    
                    
        elif opcode == "CONCAT":
            if program[order][2].get("type") == "var":
                value1, typ1 = work_with_var(program[order][2].text, None, None, "get")
                if value1 == "" and typ1 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
                if typ1 != "string":
                    eprint("Radek:",order,"Chyba - Datovy typ u druheho operandu instrukce CONCAT neni string")
                    sys.exit(53)
            else:
                if program[order][2].get("type") == "string":
                    value1 = isstring(order, program[order][2].text)
                else:
                    eprint("Radek:",order,"Chyba - Datovy typ u druheho operandu instrukce CONCAT neni string")
                    sys.exit(53)
            
            if program[order][3].get("type") == "var":
                value2, typ2 = work_with_var(program[order][3].text, None, None, "get")
                if value2 == "" and typ2 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
                if typ2 != "string":
                    eprint("Radek:",order,"Chyba - Datovy typ u tretiho operandu instrukce CONCAT neni string")
                    sys.exit(53)
            else:
                if program[order][3].get("type") == "string":
                    value2 = isstring(order, program[order][3].text)
                else:
                    eprint("Radek:",order,"Chyba - Datovy typ u tretiho operandu instrukce CONCAT neni string")
                    sys.exit(53)
                    
            work_with_var(program[order][1].text, value1 + value2, "string", "write")
            
            
        elif opcode == "STRLEN":
            if program[order][2].get("type") == "var":
                value1, typ1 = work_with_var(program[order][2].text, None, None, "get")
                if value1 == "" and typ1 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
                if typ1 != "string":
                    eprint("Radek:",order,"Chyba - Datovy typ u druheho operandu instrukce STRLEN neni string")
                    sys.exit(53)
            else:
                if program[order][2].get("type") == "string":
                    value1 = isstring(order, program[order][2].text)
                else:
                    eprint("Radek:",order,"Chyba - Datovy typ u druheho operandu instrukce STRLEN neni string")
                    sys.exit(53)
            
            work_with_var(program[order][1].text, len(value1), "int", "write")
             
             
        elif opcode == "GETCHAR":
            if program[order][2].get("type") == "var":
                value1, typ1 = work_with_var(program[order][2].text, None, None, "get")
                if value1 == "" and typ1 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
                if typ1 != "string":
                    eprint("Radek:",order,"Chyba - Datovy typ u druheho operandu instrukce GETCHAR neni string")
                    sys.exit(53)
            else:
                if program[order][2].get("type") == "string":
                    value1 = isstring(order, program[order][2].text)
                else:
                    eprint("Radek:",order,"Chyba - Datovy typ u druheho operandu instrukce GETCHAR neni string")
                    sys.exit(53)
            
            if program[order][3].get("type") == "var":
                value2, typ2 = work_with_var(program[order][3].text, None, None, "get")
                if value2 == "" and typ2 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
                if typ2 == "int":
                    value2 = isint(order, value2)
                else:
                    eprint("Radek:",order,"Chyba - Datovy typ u tretiho operandu instrukce GETCHAR neni int")
                    sys.exit(53)
            else:
                if program[order][3].get("type") == "int":
                    value2 = isint(order, program[order][3].text)
                else:
                    eprint("Radek:",order,"Chyba - Datovy typ u tretiho operandu instrukce GETCHAR neni int")
                    sys.exit(53)
                    
            try:
                value1 = value1[value2]
            except:
                eprint("Radek:",order,"Chyba - Indexace mimo daný řetězec u instrukce GETCHAR")
                sys.exit(58)
            else:
                work_with_var(program[order][1].text, value1, "string", "write")
                
                
        elif opcode == "SETCHAR":
            value1, typ1 = work_with_var(program[order][1].text, None, None, "get")
            if value1 == "" and typ1 == "":
                eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                sys.exit(56)
            if typ1 != "string":
                eprint("Radek:",order,"Chyba - Datovy typ u prvniho operandu instrukce SETCHAR neni string")
                sys.exit(53)
            
            if program[order][2].get("type") == "var":
                value2, typ2 = work_with_var(program[order][2].text, None, None, "get")
                if value2 == "" and typ2 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
                if typ2 == "int":
                    value2 = isint(order, value2)
                else:
                    eprint("Radek:",order,"Chyba - Datovy typ u druheho operandu instrukce SETCHAR neni int")
                    sys.exit(53)
               
            else:
                if program[order][2].get("type") == "int":
                    value2 = isint(order, program[order][2].text)
                else:
                    eprint("Radek:",order,"Chyba - Datovy typ u druheho operandu instrukce SETCHAR neni int")
                    sys.exit(53)
            
            if program[order][3].get("type") == "var":
                value3, typ3 = work_with_var(program[order][3].text, None, None, "get")
                if value3 == "" and typ3 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
                if typ3 != "string":
                    eprint("Radek:",order,"Chyba - Datovy typ u tretiho operandu instrukce SETCHAR neni string")
                    sys.exit(53)
                if value3 == "":
                    sys.exit(58)
                
            else:
                if program[order][3].get("type") == "string":
                    value3 = isstring(order, program[order][3].text)
                    if value3 == "":
                        sys.exit(58)
                else:
                    eprint("Radek:",order,"Chyba - Datovy typ u tretiho operandu instrukce SETCHAR neni string")
                    sys.exit(53)


            try:
                value1[value2]
            except:
                eprint("Radek:",order,"Chyba - Indexace mimo daný řetězec u instrukce SETCHAR")
                sys.exit(58)
            else:
                valuearr = list(value1)
                
                if value3:
                    valuearr[value2] = value3[0]
                else:
                    valuearr[value2] = ""
                    
                value1 = ""
                for i in valuearr: value1 += i
               
                    
                work_with_var(program[order][1].text, value1, "string", "write")
                
                    
        elif opcode == "TYPE":
            if program[order][2].get("type") == "var":
                value1, typ1 = work_with_var(program[order][2].text, None, None, "get")
                work_with_var(program[order][1].text, typ1, "string", "write")
            else:
                if program[order][2].get("type") == "int":
                    work_with_var(program[order][1].text, "int", "string", "write")
                elif program[order][2].get("type") == "string":
                    work_with_var(program[order][1].text, "string", "string", "write")
                elif program[order][2].get("type") == "bool":
                    work_with_var(program[order][1].text, "bool", "string", "write")
                else:
                    work_with_var(program[order][1].text, "nil", "string", "write")
                    
                    
        elif opcode in ("JUMPIFEQ","JUMPIFNEQ"):
            if program[order][2].get("type") == "var":
                value1, typ1 = work_with_var(program[order][2].text, None, None, "get")
                if value1 == "" and typ1  == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
            else:
                typ1 = program[order][2].get("type")
                value1 = program[order][2].text
                if typ1 == "int":
                    value1 = isint(order, value1)
                elif typ1 == "string":
                    value1 = isstring(order, value1)
                elif typ1 == "bool":
                    value1 = isbool(order, value1)
                    
            if program[order][3].get("type") == "var":
                value2, typ2 = work_with_var(program[order][3].text, None, None, "get")
                if value2 == "" and typ2 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
            else:
                typ2 = program[order][3].get("type")
                value2 = program[order][3].text
                if typ2 == "int":
                    value2 = isint(order, value2)
                elif typ2 == "string":
                    value2 = isstring(order, value2)
                elif typ2 == "bool":
                    value2 = isbool(order, value2)
                    
            if typ1 == typ2 or typ1 == "nil" or typ2 == "nil":
                if (opcode == "JUMPIFEQ" and value1 == value2) or (opcode == "JUMPIFNEQ" and value1 != value2):
                    if program[order][1].text in labels_dict.keys():
                        order = labels_dict[program[order][1].text]
                        index = recalc_inst_pointer_pos(program_arr, order)
                    else:
                        eprint("Radek:",order,"Chyba - Pokus o",opcode,"na nedefinovane navesti")
                        sys.exit(52)
            else:
                eprint("Radek:",order,"Chyba - Datovy typy se u instrukce",opcode,"musi rovnat")
                sys.exit(53)
                
      
        elif opcode == "EXIT":
            if program[order][1].get("type") == "var":
                value1, typ1 = work_with_var(program[order][1].text, None, None, "get")
                if value1 == "" and typ1 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
                if typ1 == "int":
                    if int(value1) >= 0 and int(value1) <= 49:
                        sys.exit(int(value1))
                    else:
                        eprint("Radek:",order,"Chyba - Nevalidni celociselna hodnota u EXIT")
                        sys.exit(57)
                else:
                    eprint("Radek:",order,"Chyba - Datovy typy se u instrukce EXIT musi byt int")
                    sys.exit(53)
                    
            elif program[order][1].get("type") == "int":
                value1 = isint(order, program[order][1].text)
                if value1 >= 0 and value1 <= 49:
                    sys.exit(value1)
                else:
                    eprint("Radek:",order,"Chyba - Nevalidni celociselna hodnota u EXIT")
                    sys.exit(57)
            else:
                eprint("Radek:",order,"Chyba - Datovy typy se u instrukce EXIT musi byt int")
                sys.exit(53)
                
        elif opcode == "DPRINT":
            if program[order][1].get("type") == "var":
                value1, typ1 = work_with_var(program[order][1].text, None, None, "get")
                if value1 == "" and typ1 == "":
                    eprint("Radek:",order,"Chyba - Pokus o cteni z prazdne promenne")
                    sys.exit(56)
            else:
                value1 = program[order][1].text
                     
            eprint(value1)
        
        elif opcode == "BREAK":
            eprint("Pozice v kodu:",order)
            eprint("Globalni ramec:",global_frame)
            eprint("Pocet vykonanych instrukci:",index+1)
                
           

        index = index + 1
         
    
    
    
# zpracovani xml po instrukcich
for instruction in root:
    args=[]
    instruction_row = []
    #print(instruction.get("order"), instruction.get("opcode") )
    
    order = instruction.get("order")
    opcode = instruction.get("opcode")
    
    if opcode == None or order == None or instruction.tag != "instruction":
        eprint("Neocekavana struktura XML")
        sys.exit(32)
    
    try:
        order = int(order)
    except:
        eprint("Poradove cislo instrukce neni int")
        sys.exit(32)
        
        
    if order < 0 or order in order_arr:
        eprint("Spatne poradove cislo instrukce")
        sys.exit(32)
    
    order_arr.append(order)
    instruction_row.append(opcode)
    
    
    for arg in instruction:
        if arg.tag == "arg1":
            args.insert(0,arg)
        elif arg.tag == "arg2":
            args.insert(1,arg)
        elif arg.tag == "arg3":
            args.insert(2,arg)
        else:
            eprint("Radek:",order,"Chyba, Pocet argumentu je mensi nez 1 nebo vetsi nez 3")
            sys.exit(32)

    for i in args : instruction_row.append(i)
    
    
    
    check_instruction_syntax(order, opcode, args)
    program.update({order : instruction_row})
    

interpret(program)










