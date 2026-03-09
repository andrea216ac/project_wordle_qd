

class Game:
     # ==== COSTRUTTORE ====
    def __init__(self, target_word):
        self.target_word = target_word         # Target: obiettivo da indovinare
        self.attempts = 0                      # Attemps: numero tentativi
        self.is_over = False                   # Gioco finito?
        self.max_attempts = len(target_word) + 2  # Numero max di tentativi --- scegliere tentativi fissi o dipende da lunghezza?
        
    # ==== METODO INDOVINA =====
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