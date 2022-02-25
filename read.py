import pickle


# with open("dictionary.txt", "rb") as f:
#     data = pickle.load(f)
#     print(data)
# #     print(max(data.values()))
# f.close()

# with open("postings.txt", 'rb') as f:
#     for i in range(5):
#         print(pickle.load(f))


with open("postings.txt", 'rb') as f:
    # for i in range(2):
    f.seek(12724215)
    result = pickle.load(f)
f.close()
print(result)