# Program extracting first column 
import xlrd 

def write_to_file(line):
    with open("rupture_prediction_rules.txt", "w") as text_file:
        print(line, file=text_file)

def read_xl():
    loc = ("Rule_Matrix_final.xlsx")
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(6) 
    with open("rupture_prediction_rules.txt", "w") as rules_file:
        for i in range(sheet.nrows):
            row_val = ''
            for j in range(sheet.ncols):
                if(type(sheet.cell_value(i, j)) == float):
                    row_val += str(sheet.cell_value(i, j)) + ' '
                else:
                    row_val += sheet.cell_value(0, j) + ' ' + sheet.cell_value(i, j) + ' '

                if(j == sheet.ncols - 2):
                    row_val = row_val.strip() + '\t'

            line_to_write = row_val.replace('rule_1', '').replace('rule_2', '').replace('_',' ').replace('  ', ' ')
            print(line_to_write, file=rules_file)

read_xl()

# Try to make user's query as close to rules as possible before converting to vector
# Removing stop words, keeping only nouns, convert age to strings like generation x/ baby boomers
# 