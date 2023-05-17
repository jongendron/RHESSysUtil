import numpy as np
import pandas as pd

# a = pd.DataFrame(
#     {'_id': [1, 2, 3],
#      'col1': [1, 2, 3],
#      'col2': [10, 20, 30]
#      }
# )

# b = pd.DataFrame(
#     {'_id': [1, 2, 3],
#      'col3': [100, 200, 300]
#      }
# )

# c = pd.merge(a, b, on=['_id'], how='outer').copy()

# print('a:')
# print(a)
# print()
# print('b:')
# print(b)
# print()
# print('c:')
# print(c)
# print()

# a['col1'][0] = 4

# print('a:')
# print(a)
# print()
# print('c:')
# print(c)
# print()

# a = pd.DataFrame({'a':[]})
# print('a: ', a, sep='\n')

# b = None

# b.copy().groupby(['a'])

# a = pd.DataFrame({'a': [3, 1, 3], 'b': [1, 1, 1], 'c': ['apple', 'tree', 'grass']})

# print(a.drop_duplicates(subset=['a', 'b'])[['a', 'b']])

a = 'mean'
b = ['a', 'b', 'c']
b = None

print(bool(a))
print(bool(b))
print(bool(a) and bool(b))