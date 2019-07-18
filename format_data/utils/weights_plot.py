import numpy as np
import json
import matplotlib.pyplot as plt

with open("latest_sg_weights_3.json", 'r') as f:
    data = json.load(f)
data = np.array(data)
plt.figure()
plt.bar(data[:, 0], data[:, 1])
plt.xlabel('spacegroup number')
plt.ylabel('occurrence')
plt.title('Occurrence for each spacegroup')
plt.show()
