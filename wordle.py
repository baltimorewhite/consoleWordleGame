import random


# Lista de palabras de 5 letras/ bank words 
word_list = ['apple', 'brave', 'crane', 'grape', 'plumb', 'shine', 'smart', 'plant']
secret_word = random.choice(word_list)

def give_feedback(guess, secret):
    feedback = ""
    for i in range(5):
        letter = guess[i].upper()
        if guess[i] == secret[i]:
            feedback += f"[✓] {letter}   "
        elif guess[i] in secret:
            feedback += f"[!] {letter}   "
        else:
            feedback += f"[X] {letter}   "
    return feedback.strip()

welcome = input("Welcome to Wordle Game console version! what is your name? ").upper()
print(f"Hi {welcome}, You will have to guess a five letter word. You will have 6 attempts.\n")


for attempt in range(1, 7):
    guess = input(f"Try {attempt}/6: ").lower()


    if len(guess) != 5 or not guess.isalpha():
        print(" ! Please enter a valid 5-letter word.\n")
        continue

    if guess not in word_list:
        print("! That word is not on the list.\n")
        continue

    feedback = give_feedback(guess, secret_word)
    print("Result:")
    print(feedback + "\n")

    if guess == secret_word:
        print(" You won! Congratulations!")
        break
else:
    print(f"X The attempts were over. The word was: {secret_word.upper()}")
