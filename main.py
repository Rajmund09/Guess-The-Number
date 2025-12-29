import random

n = random.randint(0,100)

a = -1

guesses = 0

while(a!=n):
    guesses+=1
    a = int(input("Guess the number between 0 to 100: "))
    if a == n and guesses == 1:
        print("wow you guss the number in first attempt")
    elif a > n:
        print("guss lower number  please")
    else:
        print("guss higher number please")
print(f"you have guessed the number {n} correctly in {guesses} attempts")
