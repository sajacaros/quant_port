* axis 개념 설명
```
import pandas as pd

df = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(df)
# axis0은 가장 바깥쪽 array를 가리킴
# axis1은 그 안쪽 array를 가리킴
# axisn은 n만큼 안쪽 array를 가리킴
#axis0 index ->      0          1          2
#axis1 index ->   0  1  2    0  1  2    0  1  2
#df             [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(df.sum(axis=0))
print(df.sum(axis=1))

# sum(axis=0) 이 의미하는 것!!
# axis0에 해당하는 series의 합으로 생각하면 됨
s1 = pd.Series([1, 2, 3])
s2 = pd.Series([4, 5, 6])
s3 = pd.Series([7, 8, 9])
print(s1 + s2 + s3)
```