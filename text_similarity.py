from fuzzywuzzy import fuzz
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--text", required=True, help="input text file")
args = parser.parse_args()

with open("out_text", "r") as f:
    text = f.read()

with open(args.text, "r") as g:
    y_text = g.read()

print(fuzz.ratio(text, y_text) / 100)
