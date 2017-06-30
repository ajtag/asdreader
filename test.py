import os
import asdreader
import matplotlib.pyplot as plt

filename = 'sample.asd'

s = asdreader.reader(os.path.join('data', filename))
print(s.md)
plt.plot(s.wavelengths, s.reflectance)
plt.show()
