import pickle


with open("dictionary.txt", "rb") as f:
    data = pickle.load(f)
    print(max(data.values()))
f.close()

with open("temp.txt", 'rb') as f:
    data = pickle.load(f)
    print(data)