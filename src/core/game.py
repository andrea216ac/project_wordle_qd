target = "cane"
guess = input("Inserisci parola: ")

for i in range(len(target)):
    if guess[i] == target[i]:
        print("CORRECT")
    elif guess[i] in target:
        print("PRESENT")
    else:
        print("ABSENT") 