import pandas as pd
import numpy as np

file_name = "map_1"
df = pd.read_csv(f'tile_maps/{file_name}.csv',header=None, index_col=None )
nf = df.to_numpy()

des_pos = np.argwhere((nf == 4) | (nf == 5))
ruby_pos = np.argwhere((nf == 3) | (nf == 5))
player_pos = np.argwhere(nf == 2)

print(des_pos)
print(ruby_pos)
print(player_pos)
print(df)