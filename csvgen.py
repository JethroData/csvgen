#!/usr/bin/python

from random import randint
from datetime import datetime, timedelta
import random
import string
import uuid
import socket
import struct
import sys, getopt
import shlex
import rstr



datalists = {}
userlists = {}

rows = 1

delimiter = ','

nullstr = ''

vowels = list('aeiou')

descriptions = []
      
simple_types = ['boolean', 'gender', 'gender_abbrev', 'uuid', 'ip_address',]
param_types = ['regex', 'fixed', 'list']
range_types = ['word']
format_types = ['number', 'date']
  
def gen_rownumber(start, row_number):
    return start + row_number

def gen_number(minnum, maxnum, decimals):
    num = randint(minnum, maxnum)
    if decimals > 0:
        dec = num + random.random()
        f = "%." + str(decimals) + "f"
        return f % dec
    else:
        return num
    
     
def word_part(letter_type):
    if letter_type is 'c':
        return random.sample([ch for ch in list(string.lowercase) if ch not in vowels], 1)[0]
    if letter_type is 'v':
        return random.sample(vowels, 1)[0]
  
def gen_syllable():
    ran = random.random()
    if ran < 0.333:
        return word_part('v') + word_part('c')
    if ran < 0.666:
        return word_part('c') + word_part('v')
    return word_part('c') + word_part('v') + word_part('c')

  
def gen_word(min_syllables, max_syllables):
    word = ''
    syllables = min_syllables + int(random.random() * (max_syllables - min_syllables))
    for i in range(0, syllables):
        word += gen_syllable()
    
    return word.capitalize()

def load_list(name):
    global datalists
    lines = [line.rstrip('\n') for line in open('data/' + name + '.csv')]
    datalists[name] = lines
    
def gen_from_list(name):
    global datalists
    data = datalists.get(name)
    if data == None:
        load_list(name)
        data = datalists.get(name)
    return data[randint(0, len(data) -1)]

def gen_from_user_list(num):
    global userlists
    data = userlists.get(num)
    return data[randint(0, len(data) -1)]

def td_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def random_date(start, end):
    return start + timedelta(seconds=randint(0, int(td_seconds(end - start))))

def gen_date(start, end, date_format):
    startts = datetime.strptime(start, date_format)
    endts = datetime.strptime(end, date_format)
    return random_date(startts, endts).strftime(date_format)
    
def gen_bool():
    n = randint(0, 1)
    if n == 0:
        return "false"
    return "true"

def gen_uuid():
    return uuid.uuid4()

def gen_ipaddress():
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

def gen_regex(regex):
    return rstr.xeger(regex)

def read_description(filename):
    global descriptions, userlists, row_number_num
    num = 0
    lines = [line.rstrip('\n') for line in open(filename)]
    for line in lines:
        if line == '':
            continue
        params = shlex.split(line)
        desc = []
        datatype = params[0]
        desc.append(datatype)
        nullp = 0
        if datatype in param_types:
            if len(params) < 2:
                sys.stderr.write("Error: Type " + datatype + " must have a parameter")
                sys.exit(2)
            param = params[1]
            if len(params) > 2:
                nullp = int(params[2])
            desc.append(nullp)
            if datatype == 'list':
                items = shlex.split(param[1:-1])
                userlists[num] = map(str.strip, items)
            desc.append(param)
        elif datatype in range_types:
            if len(params) < 3:
                sys.stderr.write("Error: Type " + datatype + " must have min and max parameters")
                sys.exit(2)
            minrange = int(params[1])
            maxrange = int(params[2])
            if len(params) > 3:
                nullp = int(params[3])
                
            desc.append(nullp)
            desc.append(minrange)
            desc.append(maxrange)
        elif datatype in format_types:
            if len(params) < 4:
                sys.stderr.write("Error: Type " + datatype + " must have 3 parameters")
                sys.exit(2)
            if len(params) > 1:
                minrange = params[1]
            if len(params) > 2:
                maxrange = params[2]
            if len(params) > 3:
                format = params[3]
            if len(params) > 4:
                nullp = int(params[4])    
            desc.append(nullp)
            if datatype == 'number':
                desc.append(int(minrange))
                desc.append(int(maxrange))
                desc.append(int(format))
            else:
                desc.append(minrange)
                desc.append(maxrange)
                desc.append(format)   
        elif datatype == 'row_number':
            desc.append(nullp)
            if len(params) > 1:
                desc.append(int(params[1]))
            else:
                desc.append(1)
            
        else:
            if len(params) > 1:
                nullp = int(params[1])
            desc.append(nullp)
        
        descriptions.append(desc)
        num += 1
      

def generate_csv():
    buff = ""
    for i in range(0, rows):
        last = len(descriptions)
        j = 1
        for desc in descriptions:
            datatype = desc[0]
            nullp = desc[1]
            if nullp > 0 and randint(0, 100) < nullp:
                buff += nullstr
            elif datatype == 'row_number':
                buff += str(gen_rownumber(desc[2], i))
            elif datatype == 'boolean':
                buff += gen_bool()
            elif datatype == 'uuid':
                buff += str(gen_uuid())
            elif datatype == 'ip_address':
                buff += str(gen_ipaddress())
            elif datatype == 'regex':
                buff += gen_regex(desc[2])
            elif datatype == 'fixed':
                buff += desc[2]
            elif datatype == 'word':
                buff += gen_word(desc[2], desc[3])
            elif datatype == 'number':
                buff += str(gen_number(desc[2], desc[3], desc[4]))
            elif datatype == 'date':
                buff += gen_date(desc[2], desc[3], desc[4])
            elif datatype == 'list':
                buff += gen_from_user_list(j - 1)
            else:
                buff += gen_from_list(datatype) 
            if j < last:
                buff += delimiter
            j += 1
        
        sys.stdout.write(buff + '\n')
        buff = ""
        
def main(argv):
    global rows, delimiter, nullstr
    try:
        opts, args = getopt.getopt(argv,"i:d:n:o:")
    except getopt.GetoptError:
        sys.stderr.write('csvgen.py -i <number of rows> -d <delimiter> -n <null string> -o <output file> <description file>')
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-i':
            rows = int(arg)
        elif opt == '-d':
            delimiter = arg
            if delimiter.startswith('"') or delimiter.startswith("'"):
                delimiter = delimiter[1:-1]
        elif opt == '-n':
            nullstr = arg
            if delimiter.startswith('"') or delimiter.startswith("'"):
                nullstr = nullstr[1:-1]
        elif opt == '-o':
            sys.stdout = open(arg,'w')
            
    if len(args) == 0:
        sys.stderr.write('csvgen.py -i <number of rows> -d <delimiter> -n <null string> -o <output file> <description file>')
        sys.exit(2)
    
    read_description(args[0])
    t1 = datetime.now()
    generate_csv()
    t2 = datetime.now()
    sys.stderr.write("Running time is: " + str(t2-t1) + "\n")

if __name__ == "__main__":
    main(sys.argv[1:])
