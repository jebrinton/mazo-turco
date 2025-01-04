import pandas as pd

df = pd.DataFrame(columns=['one', 'two', 'three'])

df[0] = "maki"

print(df)

df[0] = "this"

print(df)