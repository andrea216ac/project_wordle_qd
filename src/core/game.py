

class Game:
    def __init__(self, target_word):
        self.target_word = target_word
        self.attempts = 0

    def check_guess(self, guess):

        #CONTROLLO LUNGHEZZA
        if len(guess) != len(self.target_word):
            raise ValueError("Lunghezza non valida") #interfaccia
        
        self.attempts += 1
        result = []

        for i in range(len(self.target_word)):
            if guess[i] == self.target_word[i]:
                result.append("CORRECT")
            elif guess[i] in self.target_word:
                result.append("PRESENT")
            else:
                result.append("ABSENT")

        return result
    

#main.py
game = Game("cane")   #classe Game si aspetta una parola, quella da indovinare

guess = input("Inserisci una parola: ")  # guess: tentativo di indovinare

result = game.check_guess(guess)

print(result)