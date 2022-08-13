import os


print(os.environ)

print("This list: ")

for k, v in os.environ.items():
    print(f"{k}={v}")
