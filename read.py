import pickle


with open("dictionary.txt", "rb") as f:
    data = pickle.load(f)
    print(max(data.values()))