*** C2I ***
Classify companies into their industries by scrapping the web and comparing meta-descriptions to a weighted keyword dictionnary.
Outputs a file with company name, industry and confidence rating.
By Alan ROW

1 - Set-Up
In List.csv, list the company you want to transform
In Dict.csv, enter keywords, enterring them more than once will increase their weight
Will outout a file unto save location.

2 - Structure

	Imports names

	Scraps until sufficient meta-data is collected from the following:
		- Wikipedia
		- Duck Duck Go
		- Mojeek

	Imports dictionnary

	Initiate a scoring card for each industry

	Go word through every word in the meta data and compare to the dictionnary to populate the scoring card

	Highest scoreing industry is linked to the company name
	
	Calculate accuracy reading as % of words in meta-data that are included in the industry

	Save output as .csv
