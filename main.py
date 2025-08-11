from argon2 import PasswordHasher

ph = PasswordHasher()

hash = ph.hash("blas is the best!")

print(hash)
try:
    if ph.verify(hash, "blas is the best"):
        print("Password verified!")
except:
    print("Password verification failed!")
