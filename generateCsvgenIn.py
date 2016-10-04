import sys, getopt, re, csv
from datetime import datetime, timedelta

conststrings = ['aaa', 'bbb', 'ccc', 'ddd', 'eee', 'fff', 'ggg', 'hhh', 'iii', 'jjj']

def getRows(table, stats):
    m = re.search('SHOW TABLES EXTENDED(.*?)Total query time', stats, re.S + re.M)
    if m != None:
        show_table = m.group(1)
        show_table = show_table[show_table.find('-\n')+1:show_table.rfind('\n-')].strip().rstrip()
        
        reader = csv.reader(show_table.split('\n'), delimiter='|')
        for row in reader:
            tmpTable = row[2].strip().rstrip()
            if tmpTable == table:
                return int(row[4])
        
        return 0
    
def getColumns(table, stats):
    columns = []
    m = re.search('SHOW ALL TABLES COLUMNS FULL(.*?)Total query time', stats, re.S + re.M)
    if m != None:
        columns_full = m.group(1)
        columns_full = columns_full[columns_full.find('-\n')+1:columns_full.rfind('\n-')].strip().rstrip()
        
        reader = csv.reader(columns_full.split('\n'), delimiter='|')
        for row in reader:
            tmpTable = row[1].strip().rstrip()
            if tmpTable == table:
                column = row[3].strip().rstrip()
                ctype = row[4].strip().rstrip()
                nullNum = int(row[6])
                distinctNum = int(row[7])
                if not column.startswith('_$'):
                    columns.append([column, ctype, nullNum, distinctNum])
                
    return columns      

def writePkey(outfile, ctype):
    line = "row_number 1"
    if ctype == 'STRING':
        line = line + ' pkey'
        
    outfile.write(line + "\n")
    
def  writeStringInput(outfile, nullp, distinct):
    if distinct == 1:
        line = 'fixed aaa'
    elif distinct <= 10:
        line = 'list "['
        for i in range(1, distinct):
            line = line + conststrings[i - 1] + ' '
        line = line + conststrings[distinct - 1] + ']"'
    elif distinct < 2000000:
        line = "words " + str(distinct)
    else:
        line = "word 2 5 0"
    
    if nullp > 0:
        line += ' ' + str(nullp)
    outfile.write(line + "\n")
    
def  writeNumericInput(outfile, nullp, distinct):
    line = 'number 1 ' + str(distinct) + ' 0 '
    if nullp > 0:
        line += ' ' + str(nullp)
    outfile.write(line + "\n")

def  writeTimestampInput(outfile, nullp, distinct):
    dateend = datetime.now().strftime("%Y-%m-%d")
    datestart = (datetime.now() - timedelta(days=distinct)).strftime("%Y-%m-%d")
    line = 'date "' + datestart + '" "' + dateend + '" "%Y-%m-%d"' 
    if nullp > 0:
        line += ' ' + str(nullp)
    outfile.write(line + "\n")
     
def generateInputFile(table, stats, outfilename):
    number_of_rows = getRows(table, stats)
    if number_of_rows == 0:
        sys.stderr.write('Table ' + table + ' does not exist.')
        sys.exit(2)
    
    columns = getColumns(table, stats)
    
    try:    
        outfile = open(outfilename, 'w')
    except IOError:
        print("Failed to open output file ")
        exit(-1)
        
    for c in columns:
        nullp = int(c[2] / number_of_rows * 100)
        if c[3] == number_of_rows:
            writePkey(outfile, c[1])
        elif c[1] == 'STRING':
            writeStringInput(outfile, nullp, c[3])
        elif c[1] == 'INTEGER' or c[1] == 'BIGINT' or c[1] == 'FLOAT' or c[1] == 'DOUBLE':
            writeNumericInput(outfile, nullp, c[3])
        elif c[1] == 'TIMESTAMP':
            writeTimestampInput(outfile, nullp, c[3])
    
    outfile.close()
    print("Saved output file to " + outfilename)
           
def main(argv):
    try:
        opts, args = getopt.getopt(argv,"d:")
    except getopt.GetoptError:
        sys.stderr.write('generateCsvgenIn.py [-d output directory] <table name> <statistics file>')
        sys.exit(2)  
    
    if len(args) < 2:
        sys.stderr.write('generateCsvgenIn.py [-d output directory] <table name> <statistics file>')
        sys.exit(2)
        
    outfilename = args[0] + ".in"
    for opt, arg in opts:
        if opt == '-d':
            outfilename = arg + '/' + outfilename
    
    
    
    try:    
        statsfile = open(args[1], "r")
    except IOError:
        print("Failed to open statistics file " + args[1] + "\n")
        exit(-1)
        
    stats = statsfile.read()
    statsfile.close()
    
    generateInputFile(args[0], stats, outfilename)
    
if __name__ == '__main__':
    main(sys.argv[1:])