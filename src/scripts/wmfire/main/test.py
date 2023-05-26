import numpy as np
import pandas as pd

# def sequence_generator(start, end, seq_len: int=5, skip_len: int=7):
#     num = start
#     while num <= end:
#         for i in range(seq_len):
#             yield num
#             num += 1
#         # num += 7
#         num += skip_len

def sequence_generator(start, len: int=100, on_len: int=5, skip_len: int=7):
    num = start
    seq_len = 0
    while True:
        if seq_len == len:
            break
        else:
            for i in range(on_len):
                if seq_len < len:
                    yield num
                    seq_len += 1
                    num += 1                    
                else:
                    break
            num += skip_len

# st = 1
# len = 18
# on_len = 5
# skip_len = 7

# seq = list(sequence_generator(st, len, on_len, skip_len))
# # print(seq)
            

# # Example usage
# barea = 27871
# df = pd.DataFrame({'id': np.arange(1,barea*20+1)})
# nr = df.shape[0]

# mth_size = barea
# mth_per_yr= 5
# yr_size = mth_size*mth_per_yr

# num_yr = round(nr/yr_size)
# num_mth = round(nr/mth_size)

# info = {
#     'barea': barea,
#     'nr': nr,
#     'mth_size': mth_size,
#     'mth_per_yr': mth_per_yr,
#     'yr_size': yr_size,
#     'num_yr': num_yr,
#     'num_mth': num_mth
# }

# for item in info:
#     print(f'{item}: {info[item]}')

# #print(list(sequence_generator(1, nr)))
# seq = list(sequence_generator(1, num_mth))
# print(seq)

# #sequence = np.array(list(sequence_generator(start_num, end_num)))
# #print(sequence)
# #print(sequence.repeat(5))  # if each month is 5 rows.


# s1 = {'a', 'b', 'c'}
# s2 = {'a', 'd', 'e'}
# s3 = {'d', 'e', 'f'}

# print(s1 & s2)
# print(s1 & s3)
# print(bool(s1 & s3))

# df = pd.DataFrame(
#     {'a':  ['three', 'two', 'one', 'three', 'two', 'one', 'three', 'three', 'two', 'three', 'one'],
#      'b': np.random.uniform(1,10, size=11)
#     }
# )

# print(df)

# print(df.groupby('a', sort=False).mean())
# print(df.size())

global_variable = 10

def set_global_variable():
    global global_variable  # Declare the variable as global
    global_variable = 15    # Modify the global variable

set_global_variable()
print("Updated global variable value:", global_variable)