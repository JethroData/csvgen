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
from setuptools.package_index import unique_values



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

max_buff_size = 1024 * 1024
  
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
    
def gen_from_list(name, target_uv, actual_uv):
    global datalists
    data = datalists.get(name)
    if data == None:
        load_list(name)
        data = datalists.get(name)
    
    if target_uv == 0 or target_uv > len(data):
        return data[randint(0, len(data) -1)]
    else:
        if target_uv > actual_uv:
            return data[actual_uv]
        else:
            return data[randint(0, target_uv -1)]
        

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

def parseFunc(func):
    funcName = func[0:func.index('(')]
    if funcName not in ['substr', 'concat', 'copy', 'replace', 'upper', 'lower', 'add', 'sub', 'mult', 'div', 'mod', 'min', 'max', 'avg']:
        sys.stderr.write("Error: Unsupported function name " + funcName)
        sys.exit(2)
        
    params = func[func.index('(') + 1:func.index(')')].split(',')
    params = [x.strip() for x in params]
    params = [x.strip("'") for x in params]
    return [funcName] + params
    
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
                sys.stderr.write("Error: Type " + datatype + " must have a parameter\n")
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
            if len(params) < 4:
                sys.stderr.write("Error: Type " + datatype + " must have min and max parameters\n")
                sys.exit(2)
            minrange = int(params[1])
            maxrange = int(params[2])
            unique_values = 0
            if len(params) > 3:
                unique_values = int(params[3])
            if len(params) > 4:
                nullp = int(params[4])
                
            desc.append(nullp)
            desc.append(minrange)
            desc.append(maxrange)
            desc.append(unique_values)
            if unique_values > 0:
                userlists[num] = []
                
        elif datatype in format_types:
            if len(params) < 4:
                sys.stderr.write("Error: Type " + datatype + " must have 3 parameters\n")
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
            if len(params) > 2:
                desc.append(params[2])
            else:
                desc.append("")
        elif datatype == 'func':
            if len(params) < 1:
                sys.stderr.write("Error: Missing function\n")
                sys.exit(2)
                
            f = parseFunc(params[1])
            if len(params) > 2:
                nullp = int(params[2])    
            desc.append(nullp)
            desc.append(f)
        else:
            unique_values = 0
            if len(params) > 1:
                unique_values = int(params[1])
            if len(params) > 2:
                nullp = int(params[2])
            desc.append(nullp)
            desc.append(unique_values)
            desc.append(0)
        
        descriptions.append(desc)
        num += 1

def getMin(params, row_list):
    l = []
    for p in params:
        l.append(int(getParam(p, row_list)))
        
    return min(l)

def getMax(params, row_list):
    l = []
    for p in params:
        l.append(int(getParam(p, row_list)))
        
    return max(l)

def getAvg(params, row_list):
    l = []
    for p in params:
        l.append(int(getParam(p, row_list)))
        
    return float(sum(l))/len(l)


def getParam(p, row_list):
    if p[0] == '\\':
        return row_list[int(p[1:]) - 1]
    else:
        return p
    
def generate_func(desc, row_list):
    nullp = desc[0]
    if nullp > 0 and randint(0, 100) < nullp:
        return ""
    
    f = desc[1]
    if f[0] == 'substr':
        s = getParam(f[1], row_list)
        start = int(f[2])
        end = len(s) + 1
        if len(f) > 3:
            end = int(f[3])
        if end > 0 and end < start:
            end = start
        return s[start - 1: end - 1]
    elif f[0] == 'concat':
        return getParam(f[1], row_list) + getParam(f[2], row_list)
    elif f[0] == 'copy':
        return getParam(f[1], row_list)
    elif f[0] == 'replace':
        return getParam(f[1], row_list).replace(getParam(f[2], row_list), getParam(f[3], row_list))
    elif f[0] == 'upper':
        return getParam(f[1], row_list).upper()
    elif f[0] == 'lower':
        return getParam(f[1], row_list).lower()
    elif f[0] == 'add':
        return str(int(getParam(f[1], row_list)) + int(getParam(f[2], row_list)))
    elif f[0] == 'sub':
        return str(int(getParam(f[1], row_list)) - int(getParam(f[2], row_list)))
    elif f[0] == 'mult':
        return str(int(getParam(f[1], row_list)) * int(getParam(f[2], row_list)))
    elif f[0] == 'div':
        return str(int(getParam(f[1], row_list)) / int(getParam(f[2], row_list)))
    elif f[0] == 'mod':
        return str(int(getParam(f[1], row_list)) % int(getParam(f[2], row_list)))
    elif f[0] == 'min':
        return str(getMin(f[1:], row_list))
    elif f[0] == 'max':
        return str(getMax(f[1:], row_list))
    elif f[0] == 'avg':
        return str(getAvg(f[1:], row_list))
    else:
        return ""

def generate_csv():
    buff = ""
    for i in range(0, rows):
        last = len(descriptions)
        row_list = []
        j = 1
        has_func = False
        for desc in descriptions:
            datatype = desc[0]
            nullp = desc[1]
            if datatype == 'func':
                has_func = True
                row_list.append("")
            elif nullp > 0 and randint(0, 100) < nullp:
                row_list.append(nullstr)
            elif datatype == 'row_number':
                row_list.append(desc[3] + str(gen_rownumber(desc[2], i)))
            elif datatype == 'boolean':
                row_list.append(gen_bool())
            elif datatype == 'uuid':
                row_list.append(str(gen_uuid()))
            elif datatype == 'ip_address':
                row_list.append(str(gen_ipaddress()))
            elif datatype == 'regex':
                row_list.append(gen_regex(desc[2]))
            elif datatype == 'fixed':
                row_list.append(desc[2])
            elif datatype == 'word':
                uv = desc[4]
                if uv > 0:
                    wlist = userlists[j - 1]
                    if len(wlist) < uv:
                        newword = gen_word(desc[2], desc[3])
                        while newword in wlist:
                            newword = gen_word(desc[2], desc[3])
                        wlist.append(newword)
                        row_list.append(newword)
                    else:
                        row_list.append(gen_from_user_list(j - 1))
                else: 
                    row_list.append(gen_word(desc[2], desc[3]))
            elif datatype == 'number':
                row_list.append(str(gen_number(desc[2], desc[3], desc[4])))
            elif datatype == 'date':
                row_list.append(gen_date(desc[2], desc[3], desc[4]))
            elif datatype == 'list':
                row_list.append(gen_from_user_list(j - 1))
            else:
                uv = desc[3]
                row_list.append(gen_from_list(datatype, desc[2], uv))
                desc[3] = uv + 1
            j += 1
        
        if has_func == False:
            for i in range(0, last):
                buff += row_list[i]
                if i < last - 1:
                    buff += delimiter
        else:
            for i in range(0, last):
                if descriptions[i][0] == 'func':
                    buff += generate_func(descriptions[i][1:], row_list)
                else:
                    buff += row_list[i]
                if i < last - 1:
                    buff += delimiter
        buff += '\n'
        
        if len(buff) > max_buff_size:
            sys.stdout.write(buff)
            buff = ""
            
    if len(buff) > 0:
        sys.stdout.write(buff)
        
def main(argv):
    global rows, delimiter, nullstr
    try:
        opts, args = getopt.getopt(argv,"i:d:n:o:")
    except getopt.GetoptError:
        sys.stderr.write('csvgen.py -i <number of rows> -d <delimiter> -n <null string> -o <output file> <description file>\n')
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-i':
            rows = int(arg)
        elif opt == '-d':
            delimiter = arg
            if delimiter.startswith('"') or delimiter.startswith("'"):
                delimiter = delimiter[1:-1]
            if len(delimiter) > 1 and not delimiter.startswith('\\'):
                sys.stderr.write("Invalid delimiter. Must be one character.\n")
                sys.exit(2)
        elif opt == '-n':
            nullstr = arg
            if nullstr.startswith('"') or nullstr.startswith("'"):
                nullstr = nullstr[1:-1]
        elif opt == '-o':
            sys.stdout = open(arg,'w')
            
    if len(args) == 0:
        sys.stderr.write('csvgen.py -i <number of rows> -d <delimiter> -n <null string> -o <output file> <description file>\n')
        sys.exit(2)
    
    read_description(args[0])
    t1 = datetime.now()
    generate_csv()
    t2 = datetime.now()
    sys.stderr.write("Running time is: " + str(t2-t1) + "\n")

if __name__ == "__main__":
    main(sys.argv[1:])
