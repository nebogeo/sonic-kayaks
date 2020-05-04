import csv
import sys

def read_as_array(file,col):
    the_list = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            the_list.append(row[col])
    return the_list

with open(sys.argv[3],"w") as f:
    for v in read_as_array(sys.argv[1],int(sys.argv[2])):
        f.write(str(v)+";\n")
    f.close()
