import csv


def convert_to_num_art(row):
    if row[-5] != '':
        row[-5] = len(row[-5].strip('[]').split(','))
    else:
        row[-5] = 0


def convert_to_num_fountain(row):
    if row[-4] != '':
        row[-4] = len(row[-4].strip('[]').split(','))
    else:
        row[-4] = 0


def convert_to_num_restroom(row):
    if row[-3] != '':
        row[-3] = len(row[-3].strip('[]').split(','))
    else:
        row[-3] = 0


def convert_to_num_hospital(row):
    if row[-2] != '':
        row[-2] = len(row[-2].strip('[]').split(','))
    else:
        row[-2] = 0


def convert_to_num_dog(row):
    if row[-1] != '':
        row[-1] = len(row[-1].strip('[]').split(','))
    else:
        row[-1] = 0


def write_to_new_csv(lst):
    new_file = './output/updated_sw_collection.csv'
    my_csv = csv.writer(open(new_file, 'w'))
    for row in lst:
        my_csv.writerow(row)


def main():
    file = './output/new_sw_collection.csv'
    lst = []
    with open(file, 'r') as f:
        rows = csv.reader(f)
        for row in rows:
            # print(row)
            lst.append(row[4:])
        # print(lst)
    f.close()

    row_id = 0
    for row in lst:
        if row_id != 0:
            convert_to_num_art(row)
            convert_to_num_fountain(row)
            convert_to_num_restroom(row)
            convert_to_num_hospital(row)
            convert_to_num_dog(row)
        else:
            row_id = 1

    write_to_new_csv(lst)


if __name__ == '__main__':
    main()
