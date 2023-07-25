import pickle

file_path = r'HOME_REDACTED\TmrlData\reward\reward.pkl'
with open(file_path, 'rb') as file:
    unpickled_data = pickle.load(file)

# Work with the unpickled data
# For example, you can print it to see the content
print(unpickled_data)
print(len(unpickled_data))
