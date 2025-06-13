"""
- Author:     Nelson Gomez
- Student ID: 20149073
- Started:    2025-03-28
- Finished:   ---


ICTPRG302 AT2 Project - Wordle Game CLI


The game implements a text-based Wordle game, where the player has
6 attempts to guess a target word. The game provides feedback after
each guess and stores player scores in a file. It reads two text files:
- target_words.txt: A list of possible target words.
- all_words.txt: A list of valid words that the player can guess.

Features:
- 5-letter Word Guessing Game
- Input Validation
- Invalid Inputs Ignored
- Strict Feedback System
- User-Friendly Visual Feedback
- Handles Repeated Letters Accurately
- Custom Word Lists (target_words.txt and all_words.txt)
- Help Command
- Personalized Greeting
- Built-in Testing with Doctest
- Score History Stored Internally
- Modular Design

"""






import random

# ==========================
# FUNCTIONS
# ==========================

def load_words(file_name):
    """Loads words from a .txt file, one per line."""
    with open(file_name, 'r', encoding='utf-8') as file:
        return [line.strip().lower() for line in file]

def score(guess, secret):
    """
    Returns a tuple with score values:
    2 = correct letter in correct position
    1 = correct letter in wrong position
    0 = incorrect letter

    Examples
    --------
    >>> score("hello", "world")
    (0, 0, 0, 2, 1)
    >>> score("hello", "hello")
    (2, 2, 2, 2, 2)
    >>> score("cheer", "chair")
    (2, 2, 0, 0, 2)
    >>> score("bells", "label")
    (1, 1, 1, 1, 0)
    >>> score("yummy", "mummy")
    (0, 2, 2, 2, 2)
    >>> score("spear", "pears")
    (1, 1, 1, 1, 1)
    """
    feedback = [0] * 5
    secret_used = [False] * 5

    # First pass: correct letter in correct position
    for i in range(5):
        if guess[i] == secret[i]:
            feedback[i] = 2
            secret_used[i] = True

    # Second pass: correct letter in wrong position
    for i in range(5):
        if feedback[i] == 0:
            for j in range(5):
                if guess[i] == secret[j] and not secret_used[j]:
                    feedback[i] = 1
                    secret_used[j] = True
                    break

    return tuple(feedback)

def display_feedback(guess, score_tuple):
    """Displays the feedback to the player."""

    """
    Displays the visual feedback for a given guess based on its score.

    Parameters
    ----------
    guess : str
        The 5-letter word guessed by the player.

    score_tuple : tuple
        A tuple of 5 integers representing the score for each letter:
        2 = correct letter in correct position (✓)
        1 = correct letter in wrong position   (!)
        0 = incorrect letter                   (X)

    Output
    ------
    Prints the guess in uppercase and the corresponding feedback symbols below.

    Example
    -------
    >>> display_feedback("hello", (0, 0, 0, 2, 1))
    H E L L O
    X X X ✓ !

    >>> display_feedback("yummy", (0, 2, 2, 2, 2))
    Y U M M Y
    X ✓ ✓ ✓ ✓

    >>> display_feedback("bells", (1, 1, 1, 1, 0))
    B E L L S
    ! ! ! ! X
    """
    letters = [ch.upper() for ch in guess]
    symbols = []

    for s in score_tuple:
        if s == 2:
            symbols.append("✓")
        elif s == 1:
            symbols.append("!")
        else:
            symbols.append("X")

    print(" ".join(letters))
    print(" ".join(symbols) + "\n")

def greet_player():
    """Prints ASCII art and welcomes the player."""
    wordle_art = """
W   W  OOO  RRRR   DDDD   L      EEEEE    GGGG     A    M   M  EEEEE
W   W O   O R   R  D   D  L      E       G        A A   MM MM  E    
W W W O   O RRRR   D   D  L      EEEE    G GGG   AAAAA  M M M  EEEE 
W W W O   O R  R   D   D  L      E       G   G   A   A  M   M  E    
 W W   OOO  R   R  DDDD   LLLLL  EEEEE    GGGG   A   A  M   M  EEEEE
"""
    print(wordle_art)
    name = input("Hi there! What's your name? ").strip().capitalize()
    print(f"\nWelcome, {name}!\n")
    show_instructions()
    return name

def show_instructions():
    """Displays the instructions for the game."""
    print("Your goal is to guess the secret 5-letter word in no more than 6 valid attempts.")
    print("After each guess, you'll get feedback:\n")
    print("✓  → Correct letter in the correct position")
    print("!  → Correct letter in the wrong position")
    print("X  → Letter not in the word\n")
    print("Type 'help' at any time to see these instructions again.\n")

def play():
    """Main game logic."""
    target_words = load_words('target_words.txt')
    valid_words = set(load_words('all_words.txt'))
    secret_word = random.choice(target_words)
    scores = []

    player_name = greet_player()
    attempts = 0

    while attempts < 6:
        guess = input(f"Attempt {attempts + 1}/6: ").lower()

        if guess == "help":
            show_instructions()
            continue

        if len(guess) != 5:
            print("The word must have exactly 5 letters.\n")
            continue

        if not guess.isalpha():
            print("Only letters are allowed (no numbers or symbols).\n")
            continue

        if guess not in valid_words:
            print("That word is not in the list of allowed guesses.\n")
            continue

        attempts += 1

        score_result = score(guess, secret_word)
        display_feedback(guess, score_result)
        scores.append((guess, score_result))

        if guess == secret_word:
            print(f"Congratulations, {player_name}! You guessed the word!")
            break
    else:
        print(f"Sorry, {player_name}. The word was: {secret_word.upper()}")

    return scores

# ==========================
# MAIN CALL
# ==========================

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    play()
