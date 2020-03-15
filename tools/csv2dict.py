import csv
import os

#Paths
thisFilePath = os.path.abspath(__file__)
thisFolderPath = os.path.dirname(thisFilePath)

def csv2dict(iFile):
# This function takes a csv file a return a list. Each element of the list is and ordered dictionary corresponding to each row of the csv file, keys are the first row of the csv file.
    outList = [] #Init output list
    with open(iFile, newline='') as csvfile:
        reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONE)
        for row in reader: 
            for key, value in row.items():
                # Try to convert strings to numerical values.
                try: 
                    value = float(value)
                except:
                    pass
                row[key] = value            
            outList.append(row)

        return outList
            



            



