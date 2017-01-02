#csvgen

csvgen generates csv files containing mock data that can be used to load as data sets

Prerequisites:
Python 2.6 or higher installed.

###Install

Download the rstr python package from https://pypi.python.org/pypi/rstr. This package enables data based on regular expressions.
Unzip the downloaded rstr package. 
Open a command line. Go to the rstr root directory directory and run the following:
Linux (as root user): 
	`python setup.py install`
Windows: 
	`setup.py install`
	
Unzip the csvgen.zip into some directory.


###Run

From the command line, run the command:
Linux: 
	`python csvgen.py <parameters>`
Windows: 
	`csvgen.py <parameters>`

It accepts the following command line parameters:

`-i number-of-rows -d delimiter -n null-string -o output-file description-file`

Where:
* number-of-rows - Number of rows to generate. Default = 1

* delimiter - The delimiter to use. Default = ‘,’

* null-string - The string to use for NULL. Default = “” (empty string)

* output-file - The full path of the output file. Default is standard output.

* description-file - The full path of the description file.

The description file describes the data to generate. Every line represents a different column.
Every line starts with a type and then may have specific parameters.

The following is a description of all types:

Type | Description | Parameters | Examples
---- | ----------- | ---------- | --------
row_number | Generates a unique row number for each row, starting at 1 or at the number provided as parameter | <ul><li>Start from - the number to start from, optional</li><li>Prefix - the prefix to prepend to the number, optional</li></ul> | row_number 1000
boolean | Generates a Boolean value, true or false |<ul><li>Null % - the % of NULL values, 0-100, optional</li></ul> | boolean 20
uuid | Generates a unique uuid | <ul><li>Null % - the % of NULL values, 0-100, optional</li></ul> | uuid 10
ip_address | Generates and IP address | <ul><li>Null % - the % of NULL values, 0-100, optional</li></ul> | ip_address 20
regex | Generates a string based on a regular expression | <ul><li>Expression - the regular expression, mandatory</li><li>Null % - the % of NULL values, 0-100, optional</li></ul> | regex “201[2-5](0[1-9]|1[0-2])” 20
word | Generates a random (meaningless) word | <ul><li>Min - the minimum number of syllables, mandatory</li><li>Max - the maximum number of syllables, mandatory</li><li>Unique - the number of unique words to generate, optional</li><li>Null % - the % of NULL values, 0-100, optional</li></ul> | word 2 4 100 15
number | Generates a whole or decimal number | <ul><li> Min - minimum value, mandatory<ul><li>Max maximum value, mandatory<ul><li>Decimal, the number of decimal places (0 for whole), mandatory<ul><li>Null %, the % of NULL values, 0-100, optional</li></ul>	| number 1 100 0 10, number 100 999 2 20
date | Generates a date with a specified format | <ul><li>Start - start date, mandatory</li><li>End - end date, mandatory</li><li>Format - the date format in an strftime format, mandatory</li><li>Null % - the % of NULL values, 0-100, optional</li></ul> | date "01-01-2012 00:00:00" "12-31-2012 23:59:59" "%m-%d-%Y %H:%M:%S" 30, date "05-27-2014" "06-31-2014" "%m-%d-%Y" 25
fixed | Generates a string provided as parameter | <ul><li>Fixed value - the string to generate, mandatory</li><li>Null % - the % of NULL values, 0-100, optional</li></ul> | fixed hello 10
list | Picks a string from a list of values | <ul><li>List - list of values separated by a space enclosed by “[ ]” mandatory</li><li>Null % - the % of NULL values, 0-100, optional</li></ul> | list “[dog cat mouse]” 20 (Note that you must enclose the list with quotes)
func | Generates a value by executing a function on other generated values. The function should be sorounded by double quotes. The other values are passed as parameters in the form '\n' where n is the column number starting at 1. See the list of supported functions below. | <ul><li>Function - the function to execute sorrounded by '"', mandatory</li><li>Null % - the % of NULL values, 0-100, optional</li></ul> | func "substr(\2, 3, 5)", func "add(\1, 2)" 25
				 
The following functions are supported:
* substr(\n, start [,end])
	Extracts a substring from the nth column from start position to (the optional) end position.
	Example: substr(\2, 3, 5)
				 
* concat(str1, str2)
	Concatenates 2 strings. Each string can be either a value from a different column (\n) or a string.
	Example: concat(\2, 'another string'), concat('hello ', \3)
				 
copy(\n)
	Copies the value of another column.
	Example: copy(\2)
					
replace(str, old, new)
	Replaces all occurrences of old in str by new. All parameters can be either a value from a different column (\n) or a string.
	Example: replace(\1, John, Joe)
				
upper(\n), lower(\n)
	Converts all characters of a column value to upper/lower case.
	Example: upper(\1), lower(\3)
				
add(n1, n1) sub(n1, n1), mult(n1, n1), div(n1, n1), mod(n1, n1)
	Execute the arithmetic operation on 2 numbers. The parameters can be either a value from a different column (\n) or a number.
	Example: add(\1, 2), sub(5, \2), mult(\2, \3), div(\2, 10), mod(13, 12)
				
				
min(params), max(params), avg(params)
	Calculates the minimum, maximum and average of the numeric parameters. The parameters can be either a value from a different column (\n) or a number.
	Example: min(\1, \2, \3), max(\3, 10), avg(\2, \3, 7)
					
				
In addition to the above types, you can also generate a string from a custom list of string. For a given type, there ahould be a file <type>.csv in the data directory. The file should contain a list of values, each one on a separate line. One of these values will be picked randomly.
The data directory already contains several type files, like first_name, last_name, state, country, etc. You can add new custom types by adding such a file to the data directory.
To use a custom type, specify the following:
`<type-name> unique null%`
Where <type-name> is the name of the file with the .csv extension and unique is the optional number of unique values to generate

For example: 

first_name  20 10

The zip file also contains a sample description file called sample.in.


In order to generate a large amount of data, you can use the generate.sh script which can run multiple csvgen.py in parallel.
It will spawn as many processes as requested and will create temporary output file for each. When all processes are done, it will combine the output to one file.

To use it, run the following:
`./generate.sh <name> <rows> <number of processes> <delimiter>`

Where:
* <name> is the name of the  is a description file name “<name>.in”. It also uses the same name for the output file which is generated as “<name>.csv”. This parameter is mandatory.
* <rows> is the number of rows to generate for each process. Default =1M
* <number of processes> is the number of processes to run in parallel. Default=1
* <delimiter> is the column delimiter to use. Default=’|’

