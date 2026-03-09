

class Game:
     # ==== COSTRUTTORE ====
    def __init__(self, target_word):
        self.target_word = target_word         # Target: obiettivo da indovinare
        self.attempts = 0                      # Attemps: numero tentativi
        self.is_over = False                   # Gioco finito?
        self.max_attempts = len(target_word) + 2  # Numero max di tentativi --- scegliere tentativi fissi o dipende da lunghezza?
        
    # ==== METODO INDOVINA =====
    def check_guess(self, guess):

        #CONTROLLO SE GIOCO E' FINITO
        if self.is_over:
            raise Exception("Il gioco è finito")   #interfaccia
        
        #CONTROLLO LUNGHEZZA
        if len(guess) != len(self.target_word):
            raise ValueError("Lunghezza non valida") #interfaccia
        
        self.attempts += 1                         #incremento tentativo
        result = [None] * len(self.target_word)    #result: array per corretto, presente o assente
        usato = [False] * len(self.target_word)    #usato: stringa booleana, evita riutilizzo delle lettere

        #CICLO PER PAROLE CORRETTE
        for i in range(len(self.target_word)):
            if guess[i] == self.target_word[i]: 
                result[i] = "Corretto" 
                usato[i] = True 

        #CICLO PER PRESENTE E ASSENTE 
        for i in range(len(self.target_word)): #scorre la parola "guess" e array "result"
            if result[i] is None:   # solo lettere non corrette 
                trovato = False

                for j in range(len(self.target_word)):  #scorre la parola "target" e array "usato"
                    #se lettera presente ma non "usata"
                    if guess[i] == self.target_word[j] and not usato[j]: 
                        trovato = True
                        usato[j] = True
                        break              

                if trovato:    
                    result[i] = "Presente"     #esempio palla - lampa (presente, corretto, assente, presente, corretto)
                else: 
                    result[i] = "Assente"      #lettere doppie ma già usate es. cassa - sassi 

        return result
    

#main.py
game = Game("cane")   #classe Game si aspetta una parola, quella da indovinare

guess = input("Inserisci una parola: ")  # guess: tentativo di indovinare

result = game.check_guess(guess)

print(result)