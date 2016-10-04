#csvgen

csvgen generates csv files containing mock data that can be used to load as data sets

Prerequisites:
Python 2.6 or higher installed.

Install:
Download the rstr python package from https://pypi.python.org/pypi/rstr/2.1.3
Unzip rstr 
Open a command line. Go to the rstr-2.1.3 directory and run the following:
Linux (as root user): python setup.py install
Windows: setup.py install
Unzip the csvgen.zip into some directory.


Run:
From the command line, run the command:
Linux: python csvgen.py <parameters>
Windows: csvgen.py <parameters>

It accepts the following command line parameters:

-i number-of-rows -d delimiter -n null-string -o output-file description-file

Where:
number-of-rows - Number of rows to generate. Default = 1

delimiter - The delimiter to use. Default = ‘,’

null-string - The string to use for NULL. Default = “” (empty string)

output-file - The full path of the output file. Default is standard output.

description-file - The full path of the description file.

The description file describes the data to generate. Every line represents a different column.
Every line starts with a type and then may have specific parameters.

The following is a description of all types:

Row_number:
	Description: Generates a unique row number for each row, starting at 1 or at the number provided as parameter
	Parameters:  Start from, the number to start from, optional
				 Prefix, the prefix to prepend to the number, optional
	Example:     row_number 1000
	
boolean:
	Description: Generates a Boolean value, true or false
	Parameters:  Null %, the % of NULL values, 0-100, optional
	Example:     boolean 20

uuid:
	Description: Generates a unique uuid
	Parameters:  Null %, the % of NULL values, 0-100, optional	
	Example:     uuid 10

ip_address:
	Description: Generates and IP address
	Parameters:  Null %, the % of NULL values, 0-100, optional
	Example:     ip_address 20
	
regex:
	Description: Generates a string based on a regular expression
	Parameters:  Expression, the regular expression, mandatory
		     Null %, the % of NULL values, 0-100, optional	
	Example:     regex “201[2-5](0[1-9]|1[0-2])” 20
	
word:
	Description: Generates a random (meaningless) word
	Parameters:  min, the minimum number of syllables, mandatory
		     max, the maximum number of syllables, mandatory
			 Unique, the number of unique words to generate, optional
		     Null %, the % of NULL values, 0-100, optional	
	Example:     word 2 4 100 15
	
Number:
	Description: Generates a whole or decimal number
	Parameters:  Min, minimum value, mandatory
		     Max maximum value, mandatory
		     Decimal, the number of decimal places (0 for whole), mandatory
		     Null %, the % of NULL values, 0-100, optional	
	Example:     number 1 100 0 10
				 number 100 999 2 20
				 
Date:
	Description: Generates a date with a specified format
	Parameters:  Start, start date, mandatory
		     End, end date, mandatory
		     Format, the date format in an strftime format, mandatory
		     Null %, the % of NULL values, 0-100, optional	
	Example:     date "01-01-2012 00:00:00" "12-31-2012 23:59:59" "%m-%d-%Y %H:%M:%S" 30
		     date "05-27-2014" "06-31-2014" "%m-%d-%Y" 25
				 
fixed:
	Description: Generates a string provided as parameter
	Parameters:  Fixed value, the string to generate, mandatory
		     Null %, the % of NULL values, 0-100, optional	
	Example:     fixed hello 10
	
list:
	Description: Picks a string from a list of values
	Parameters:  List, list of values separated by a space enclosed by “[ ]” mandatory
		     Null %, the % of NULL values, 0-100, optional	
	Example:     list “[dog cat mouse]” 20
				 *** Note that you must enclose the list with quotes.
				 
func:
	Description: Generates a value by executing a function on other generated values. The function should be sorounded by double quotes. 
				 The other values are passed as parameters in the form '\n' where n is the column number starting at 1.
				 The following functions are supported:
				 substr(\n, start [,end])
					Extracts a substring from the nth column from start position to (the optional) end position.
					Example: substr(\2, 3, 5)
				 
				 concat(str1, str2)
					Concatenates 2 strings. Each string can be either a value from a different column (\n) or a string.
					Example: concat(\2, 'another string'), concat('hello ', \3)
				 
				 copy(\n)
					Copies the value of another column.
					Example: copy(\2)
					
				 replace(str, old, new)
					Replaces all occurrences of old in str by new. All parameters can be either a value from a different column (\n) or a string.
					Example: replace(\1, John, Joe)
				
				upper(\n), loawer(\n)
					Converts all characters of a column value to upper/lower case.
					Example: upper(\1), lower(\3)
				
				add(n1, n1) sub(n1, n1), mult(n1, n1), div(n1, n1), mod(n1, n1)
					Execute the arithmetic operation on 2 numbers. The parameters can be either a value from a different column (\n) or a number.
					Example: add(\1, 2), sub(5, \2), mult(\2, \3), div(\2, 10), mod(13, 12)
				
				
				min(params), max(params), avg(params)
					Calculates the minimum, maximum and average of the numeric parameters. The parameters can be either a value from a different column (\n) or a number.
					Example: min(\1, \2, \3), max(\3, 10), avg(\2, \3, 7)
					
	Parameter:  The function to execute sorrounded by '"', mandatory.
				Null %, the % of NULL values, 0-100, optional
	Example:	func "substr(\2, 3, 5)"
				func "add(\1, 2)" 25

				
In addition to the above types, you can also generate a string from a custom list of string. For a given type, there ahould be a file <type>.csv in the data directory. The file should contain a list of values, each one on a separate line. One of these values will be picked randomly.
The data directory already contains several type files, like first_name, last_name, state, country, etc. You can add new custom types by adding such a file to the data directory.
To use a custom type, specify the following:
<type-name> unique null%
Where <type-name> is the name of the file with the .csv extension and unique is the optional number of unique values to generate

For example: 

first_name  20 10

The zip file also contains a sample description file called sample.in.


In order to generate a large amount of data, you can use the generate.sh script which can run multiple csvgen.py in parallel.
It will spawn as many processes as requested and will create temporary output file for each. When all processes are done, it will combine the output to one file.

To use it, run the following:
./generate.sh <name> <rows> <number of processes> <delimiter>

Where:
<name> is the name of the  is a description file name “<name>.in”. It also uses the same name for the output file which is generated as “<name>.csv”. This parameter is mandatory.
<rows> is the number of rows to generate for each process. Default =1M
<number of processes> is the number of processes to run in parallel. Default=1
<delimiter> is the column delimiter to use. Default=’|’

