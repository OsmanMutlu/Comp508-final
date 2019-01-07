import glob
import cv2
import string
import pandas as pd
import re

label_dict = {}

for i,char in enumerate(list(string.digits) + list(string.ascii_uppercase) + list(string.ascii_lowercase)):
    label_dict[i+1] = char

print(label_dict)

df = pd.DataFrame()

for filename in glob.glob("English/Fnt/**/*.png", recursive=True):
    
    im = cv2.imread(filename)

    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    resized = cv2.resize(gray, (20,20))

    label = label_dict[int(re.sub(".*img(\d+).*\.png$", "\g<1>", filename))]
    df = df.append({'img':resized, 'label':label}, ignore_index=True)

df.to_csv("char_data.csv", index=False)
