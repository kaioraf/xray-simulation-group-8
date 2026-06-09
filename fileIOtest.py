import os, glob
path = '/home/kaio/Documents/Uni/Practicum 1/Data'
avg_list = {}
std_dev_list = {}
for filename in glob.glob(os.path.join(path, '*.csv')):
      print(filename)
      with open(os.path.join(os.getcwd(), filename), 'r') as file: # open in readonly mode
            csvFile = csv.reader(file)
            next(csvFile)
            summ = 0
            len=0
            for lines in csvFile:
                  summ += float(lines[1])
                  len += 1
            avg_list.update({filename: (summ/len)})
      with open(os.path.join(os.getcwd(), filename), 'r') as file: 
            csvFile = csv.reader(file)
            next(csvFile)
            var = 0
            for lines in csvFile:
                  var += ((float(lines[1]) - (summ/len))**2)
            