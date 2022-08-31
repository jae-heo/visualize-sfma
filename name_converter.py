import os
import pandas as pd

for fname in os.listdir('data5'):
    data = pd.read_csv("data5/{}".format(fname), sep=",", engine='c')

run_flag = True
while run_flag:
    run_flag = False
    for row_index, row in data.iterrows():
        for element in row:
            column_index = str(element).find("X_P")
            if column_index != -1:
                new_row1 = row.copy()
                new_row2 = row.copy()
                new_row3 = row.copy()
                data.drop(data.index[row_index])
                new_row1.loc[column_index] = "FP"
                new_row2.loc[column_index] = "DN"
                new_row3.loc[column_index] = "DP"
                data.append(new_row1)
                data.append(new_row2)
                data.append(new_row3)

                run_flag = True
                break
