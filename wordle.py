"""
- Author:     Nelson Gomez
- Student ID: 20149073
- Started:    2025-03-28
- Finished:   2025-06-20


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
- User-Friendly Interface: Includes clear instructions and visual feedback (✓, ?, -).
- Handles Repeated Letters Accurately
- Custom Word Lists (target_words.txt and all_words.txt)
- Help Command
- Personalized Greeting
- Built-in Testing with Doctest
- Centralized Configuration: Uses constants and dictionaries for settings like feedback symbols, messages, and file paths.
- Error Handling: Includes validations for user input, file handling, and exceptions.
- Scoring System: Calculates scores based on the time taken to guess the word.
- High Score Table: Saves and displays the top 10 scores.

Code Structure:
- Imports: Standard modules like random, csv, datetime, etc.
- Configurations: Configurable constants and messages.
- Utility Functions: For loading words and initializing lists.
- Game Logic: Evaluates guesses and provides feedback.
- Scoring System: Loads, saves, and displays scores.
- Game Flow: Manages player interaction and game logic.

------------------------------------------------------------------------------

"""
# ==========================
# IMPORTS
# ==========================

import random
import csv
from datetime import datetime
import os
import time
import sys
from pathlib import Path

# ==========================
# CONSTANTS AND CONFIGURATION
# ==========================

# Testing configuration
RUN_TESTS = False

# Core game constants
MAX_ATTEMPTS = 6
SECRET_WORD_LENGTH = 5
TIME_PENALTY_PER_SECOND = 1
MAX_ALLOWED_TIME = 3600  # seconds (1 hour)

# File configuration - centralized file paths for easy maintenance
FILES_CONFIG = {
    'high_scores': 'high_scores.csv',  # High scores storage file
    'target_words': 'target_words.txt',  # Words that can be chosen as secret words
    'valid_words': 'all_words.txt'  # All valid words for guessing
}

# Game configuration - centralized game settings
GAME_CONFIG = {
    'max_attempts': MAX_ATTEMPTS,  # Maximum number of guesses allowed
    'word_length': SECRET_WORD_LENGTH,  # Length of secret word
    'time_penalty': TIME_PENALTY_PER_SECOND,  # Score penalty per second
    'max_time': MAX_ALLOWED_TIME,  # Maximum time allowed for valid score
    'base_score': 3600  # Base score before time penalty
}

# Feedback symbols configuration - easy to customize visual feedback
FEEDBACK_SYMBOLS = {
    'correct': "\u2713",  # ✓ - Correct letter in correct position
    'wrong_position': "?",  # ? - Correct letter in wrong position
    'not_in_word': "-"  # - - Letter not in the word
}

# System messages configuration - centralized for easy localization
MESSAGES = {
    'welcome': "Enter your name: ",
    'play_again': "Would you like to play again? (yes/no): ",
    'guess_prompt': "Enter your guess: ",
    'help_command': 'help',
    'goodbye': "Thanks for playing! See you next time.",
    'interrupted': "\nGoodbye! Thanks for playing!",
    'too_long': "You took too long! Legends must be fast and focused.",
    'try_again': "Try again and earn your place in the Hall of Fame.",
    'invalid_name': "Please enter a valid name.",
    'name_too_long': "Name is too long. Maximum 50 characters.",
    'enter_word': "Please enter a word.",
    'word_length_error': f"The word must be exactly {SECRET_WORD_LENGTH} letters.",
    'letters_only': "Only letters are allowed (no numbers or symbols).",
    'word_not_valid': "That word is not in the allowed list.",
    'yes_no_prompt': "Please answer 'yes' or 'no'.",
    'unexpected_error': "Unexpected error occurred. Please try again."
}


# ==========================
# UTILITY FUNCTIONS
# ==========================

def load_words(file_path):
    """
    Load words from a text file with comprehensive error handling.

    Args:
        file_path (str): Path to the file containing words

    Returns:
        list: List of valid words, empty list if file cannot be loaded

    Features:
        - Validates file existence and permissions
        - Filters words by length and alphabetic characters
        - Provides detailed error messages for debugging
        - Handles encoding issues gracefully
    """
    try:
        file_path = Path(file_path)

        # Check if file exists
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            print("Make sure the file exists in the current directory.")
            return []

        words = []

        # Open file with proper encoding
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, raw_line in enumerate(file, 1):
                try:
                    cleaned_word = raw_line.strip().lower()

                    # Skip empty lines
                    if cleaned_word:
                        # Validate word length
                        if len(cleaned_word) == GAME_CONFIG['word_length']:
                            # Validate alphabetic characters only
                            if cleaned_word.isalpha():
                                words.append(cleaned_word)
                            else:
                                print(
                                    f"Warning: Invalid word at line {line_num}: '{cleaned_word}' (contains non-alphabetic characters)")
                        else:
                            print(f"Warning: Word ignored at line {line_num}: '{cleaned_word}' (incorrect length)")

                except Exception as e:
                    print(f"Error processing line {line_num}: {e}")
                    continue

        # Final validation
        if not words:
            print(f"Error: No valid words found in {file_path}")
            return []

        print(f"Loaded {len(words)} words from {file_path}")
        return words

    except PermissionError:
        print(f"Error: Permission denied reading file {file_path}")
        return []
    except Exception as e:
        print(f"Unexpected error loading {file_path}: {e}")
        return []


def initialize_feedback_list():
    """
    Initialize feedback list with zeros.

    Returns:
        list: List of zeros with length equal to word length
    """
    return [0] * GAME_CONFIG['word_length']


def initialize_secret_usage_list():
    """
    Initialize usage tracking list for secret word letters.

    Returns:
        list: List of False values with length equal to word length
    """
    return [False] * GAME_CONFIG['word_length']


# ==========================
# CORE GAME LOGIC
# ==========================

def evaluate_guess(guessed_word, secret_word):
    """
    Evaluate a guess against the secret word using Wordle rules.

    Args:
        guessed_word (str): The word guessed by the player
        secret_word (str): The secret word to guess

    Returns:
        list: Feedback scores where:
              2 = correct letter in correct position
              1 = correct letter in wrong position
              0 = letter not in word

    Algorithm:
        1. First pass: Mark exact matches (green)
        2. Second pass: Mark letters in wrong positions (yellow)
        3. Uses letter tracking to handle duplicate letters correctly
    """
    feedback_scores = initialize_feedback_list()
    letter_usage_flags = initialize_secret_usage_list()

    # First pass: Find exact matches (correct position)
    for position in range(GAME_CONFIG['word_length']):
        if guessed_word[position] == secret_word[position]:
            feedback_scores[position] = 2  # Correct position
            letter_usage_flags[position] = True  # Mark as used

    # Second pass: Find letters in wrong positions
    for guess_position in range(GAME_CONFIG['word_length']):
        if feedback_scores[guess_position] == 0:  # Not already marked as correct
            for secret_position in range(GAME_CONFIG['word_length']):
                if (guessed_word[guess_position] == secret_word[secret_position] and
                        not letter_usage_flags[secret_position]):
                    feedback_scores[guess_position] = 1  # Wrong position
                    letter_usage_flags[secret_position] = True  # Mark as used
                    break

    return feedback_scores


def display_guess_feedback(guessed_word, feedback_scores, attempt_number):
    """
    Display the guess and its feedback to the player.

    Args:
        guessed_word (str): The word that was guessed
        feedback_scores (list): List of feedback scores from evaluate_guess
        attempt_number (int): Current attempt number

    Output format:
        Attempt X/Y
        A B C D E  (guessed letters in uppercase)
        ✓ ? - - ?  (feedback symbols)
    """
    print(f"Attempt {attempt_number}/{GAME_CONFIG['max_attempts']}")

    # Display guessed letters in uppercase
    letters_output = [letter.upper() for letter in guessed_word]
    symbols_output = []

    # Convert numeric feedback to symbols
    for score in feedback_scores:
        if score == 2:
            symbols_output.append(FEEDBACK_SYMBOLS['correct'])
        elif score == 1:
            symbols_output.append(FEEDBACK_SYMBOLS['wrong_position'])
        else:
            symbols_output.append(FEEDBACK_SYMBOLS['not_in_word'])

    # Print formatted output
    print(" ".join(letters_output))
    print(" ".join(symbols_output) + "\n")


# ==========================
# HIGH SCORE SYSTEM
# ==========================

def load_high_scores():
    """
    Load high scores from CSV file with error handling.

    Returns:
        list: List of high score dictionaries, sorted by score (highest first)
              Limited to top 10 scores

    Features:
        - Handles missing or corrupted files gracefully
        - Validates data types (score must be integer)
        - Provides warnings for invalid entries
        - Returns empty list if no valid scores found
    """
    high_scores_file = Path(FILES_CONFIG['high_scores'])

    # Return empty list if file doesn't exist
    if not high_scores_file.exists():
        return []

    try:
        high_scores = []

        with open(high_scores_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row_num, row in enumerate(reader, 1):
                try:
                    # Validate and convert score to integer
                    row['score'] = int(row['score'])
                    high_scores.append(row)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Error in high scores file at line {row_num}: {e}")
                    continue

        # Sort by score (highest first) and return top 10
        return sorted(high_scores, key=lambda x: x['score'], reverse=True)[:10]

    except Exception as e:
        print(f"Error loading high scores: {e}")
        return []


def save_high_score(player_name, score):
    """
    Save a new high score to the CSV file.

    Args:
        player_name (str): Name of the player
        score (int): Score achieved

    Features:
        - Creates file with headers if it doesn't exist
        - Appends new score to existing file
        - Handles file permission and disk space errors
        - Uses current date for timestamp
    """
    fieldnames = ['score', 'name', 'date']
    current_date = datetime.now().strftime('%Y-%m-%d')
    high_scores_file = Path(FILES_CONFIG['high_scores'])

    new_entry = {
        'score': score,
        'name': player_name,
        'date': current_date
    }

    try:
        file_exists = high_scores_file.exists()

        with open(high_scores_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Write header if file is new
            if not file_exists:
                writer.writeheader()

            writer.writerow(new_entry)

    except Exception as e:
        print(f"Error saving high score: {e}")


def display_high_scores():
    """
    Display the top 10 high scores in a formatted table.

    Features:
        - Shows encouraging message if no scores exist
        - Formats scores in a clean table layout
        - Displays player names in uppercase for emphasis
        - Handles empty or missing high scores file
    """
    print("\nTop 10 High Scores")
    print("------------------")

    high_scores_file = Path(FILES_CONFIG['high_scores'])

    # Check if file exists and has content
    if not high_scores_file.exists() or high_scores_file.stat().st_size == 0:
        print("Be the first legend to set a high score!\n")
        return

    high_scores = load_high_scores()

    # Check if any valid scores were loaded
    if not high_scores:
        print("Be the first legend to set a high score!\n")
        return

    # Display formatted high scores table
    print(f"{'Rank':<5} {'Score':<7} {'Name':<15} {'Date'}")
    for index, entry in enumerate(high_scores, start=1):
        print(f"{index:<5} {entry['score']:<7} {entry['name'].upper():<15} {entry['date']}")
    print()


# ==========================
# USER INTERFACE FUNCTIONS
# ==========================

def greet_player():
    """
    Display welcome banner and get player name with validation.

    Returns:
        str: Validated player name

    Features:
        - Shows art banner
        - Displays current high scores
        - Validates player name (not empty, reasonable length)
        - Handles keyboard interrupts gracefully
        - Capitalizes name appropriately
    """
    # Art banner for visual appeal
    wordle_banner = """
W   W  OOO  RRRR   DDDD   L      EEEEE    GGGG     A    M   M  EEEEE
W   W O   O R   R  D   D  L      E       G        A A   MM MM  E    
W W W O   O RRRR   D   D  L      EEEE    G GGG   AAAAA  M M M  EEEE 
W W W O   O R  R   D   D  L      E       G   G   A   A  M   M  E    
 W W   OOO  R   R  DDDD   LLLLL  EEEEE    GGGG   A   A  M   M  EEEEE
"""
    print(wordle_banner)
    display_high_scores()

    # Get valid player name with comprehensive validation
    while True:
        try:
            player_name = input(MESSAGES['welcome']).strip()

            # Check for empty name
            if not player_name:
                print(MESSAGES['invalid_name'])
                continue

            # Check name length (reasonable limit)
            if len(player_name) > 50:
                print(MESSAGES['name_too_long'])
                continue

            # Capitalize first letter only
            player_name = player_name.capitalize()
            break

        except KeyboardInterrupt:
            print(MESSAGES['interrupted'])
            sys.exit(0)
        except EOFError:
            print(MESSAGES['interrupted'])
            sys.exit(0)

    print(f"\nWelcome, {player_name}!")
    show_instructions()
    return player_name


def show_instructions():
    """
    Display game instructions and rules to the player.

    Features:
        - Uses configurable word length and attempt limits
        - Shows feedback symbol meanings
        - Mentions help command availability
        - Clear, concise formatting
    """
    print(f"\nInstructions: Guess the secret {GAME_CONFIG['word_length']}-letter word.")
    print(f"You have a maximum of {GAME_CONFIG['max_attempts']} valid attempts.\n")
    print("Feedback symbols:")
    print(f"{FEEDBACK_SYMBOLS['correct']}  = Correct letter in correct position")
    print(f"{FEEDBACK_SYMBOLS['wrong_position']}  = Correct letter in wrong position")
    print(f"{FEEDBACK_SYMBOLS['not_in_word']}  = Letter not in the word")
    print(f"\nYou can type '{MESSAGES['help_command']}' at any time to see these instructions again.\n")


def get_valid_guess(valid_words):
    """
    Get a valid guess from the player with comprehensive validation.

    Args:
        valid_words (set): Set of valid words that can be guessed

    Returns:
        str: Valid guess word in lowercase

    Features:
        - Handles help command
        - Validates word length, alphabetic characters, and word list inclusion
        - Provides specific error messages for each validation failure
        - Handles keyboard interrupts and EOF gracefully
        - Strips whitespace and converts to lowercase
    """
    while True:
        try:
            guess = input(MESSAGES['guess_prompt']).strip().lower()

            # Handle help command
            if guess == MESSAGES['help_command']:
                show_instructions()
                continue

            # Validate non-empty input
            if not guess:
                print(MESSAGES['enter_word'] + "\n")
                continue

            # Validate word length
            if len(guess) != GAME_CONFIG['word_length']:
                print(MESSAGES['word_length_error'] + "\n")
                continue

            # Validate alphabetic characters only
            if not guess.isalpha():
                print(MESSAGES['letters_only'] + "\n")
                continue

            # Validate word is in allowed list
            if guess not in valid_words:
                print(MESSAGES['word_not_valid'] + "\n")
                continue

            return guess

        except KeyboardInterrupt:
            print(MESSAGES['interrupted'])
            sys.exit(0)
        except EOFError:
            print(MESSAGES['interrupted'])
            sys.exit(0)
        except Exception as e:
            print(f"{MESSAGES['unexpected_error']}: {e}")
            print("Please try again.\n")
            continue


# ==========================
# SCORING SYSTEM
# ==========================

def calculate_score(start_time):
    """
    Calculate final score based on time taken.

    Args:
        start_time (float): Game start time from time.time()

    Returns:
        tuple: (final_score, total_time, score_valid)
               - final_score (int): Score after time penalty
               - total_time (int): Total seconds taken
               - score_valid (bool): Whether score is valid (within time limit)

    Scoring system:
        - Base score: 3600 points
        - Penalty: 1 point per second
        - Minimum score: 0
        - Invalid if over 1 hour
    """
    end_time = time.time()
    total_seconds = int(end_time - start_time)
    raw_score = GAME_CONFIG['base_score']
    penalty = total_seconds * GAME_CONFIG['time_penalty']
    final_score = max(0, raw_score - penalty)
    score_valid = total_seconds <= GAME_CONFIG['max_time']

    return final_score, total_seconds, score_valid


# ==========================
# GAME FLOW FUNCTIONS
# ==========================

def handle_win(player_name, start_time):
    """
    Handle winning scenario - calculate score, save if valid, show results.

    Args:
        player_name (str): Name of the winning player
        start_time (float): Game start time for score calculation

    Features:
        - Calculates and displays final score
        - Saves score to high scores if within time limit
        - Provides encouraging feedback
        - Shows updated high scores
    """
    final_score, total_time, score_valid = calculate_score(start_time)

    print(f"Congratulations, {player_name}! You guessed the word.")
    print(f"Time taken: {total_time} seconds")
    print(f"Final score: {final_score}\n")

    if score_valid:
        save_high_score(player_name, final_score)
    else:
        print(MESSAGES['too_long'])
        print(f"{MESSAGES['try_again']}\n")

    display_high_scores()


def handle_loss(secret_word):
    """
    Handle losing scenario - reveal word and show high scores.

    Args:
        secret_word (str): The secret word that wasn't guessed

    Features:
        - Reveals the correct word in uppercase
        - Shows high scores for motivation
    """
    print(f"The correct word was: {secret_word.upper()}")
    display_high_scores()


def prompt_play_again():
    """
    Ask player if they want to play again with flexible input validation.

    Returns:
        bool: True if player wants to play again, False otherwise

    Features:
        - Accepts multiple forms of yes/no (yes, y, si, s, no, n)
        - Handles keyboard interrupts gracefully
        - Provides clear instructions for invalid input
    """
    while True:
        try:
            answer = input(MESSAGES['play_again']).strip().lower()

            # Accept various forms of "yes"
            if answer in ['yes', 'y', 'si', 's']:
                return True
            # Accept various forms of "no"
            elif answer in ['no', 'n']:
                print(MESSAGES['goodbye'])
                return False
            else:
                print(MESSAGES['yes_no_prompt'])
                continue

        except KeyboardInterrupt:
            print(MESSAGES['interrupted'])
            return False
        except EOFError:
            print(MESSAGES['interrupted'])
            return False


# ==========================
# GAME VALIDATION AND SETUP
# ==========================

def validate_game_files():
    """
    Validate that all required game files exist before starting.

    Returns:
        bool: True if all required files exist, False otherwise

    Features:
        - Checks for both target words and valid words files
        - Provides clear error messages listing missing files
        - Prevents game from starting with missing dependencies
    """
    required_files = [FILES_CONFIG['target_words'], FILES_CONFIG['valid_words']]
    missing_files = []

    # Check each required file
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    # Report missing files if any
    if missing_files:
        print("Error: Missing required game files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("\nMake sure these files exist in the current directory.")
        return False

    return True


# ==========================
# MAIN GAME FUNCTIONS
# ==========================

def play_one_game():
    """
    Play a single game of Wordle.

    Returns:
        bool: True if game completed successfully, False if setup failed

    Game flow:
        1. Validate required files exist
        2. Load word lists
        3. Choose random secret word
        4. Greet player and show instructions
        5. Main game loop (up to MAX_ATTEMPTS guesses)
        6. Handle win/loss scenarios

    Features:
        - Comprehensive error handling for file operations
        - Tracks game history for potential future features
        - Time tracking for scoring system
        - Graceful handling of file loading failures
    """
    # Validate required files before starting
    if not validate_game_files():
        return False

    # Load word lists with error handling
    candidate_secret_words = load_words(FILES_CONFIG['target_words'])
    valid_guess_words = set(load_words(FILES_CONFIG['valid_words']))

    # Ensure word lists loaded successfully
    if not candidate_secret_words or not valid_guess_words:
        print("Error: Could not load required word lists.")
        return False

    # Choose random secret word
    chosen_secret_word = random.choice(candidate_secret_words)
    score_history = []  # Track guesses for potential future features

    # Initialize game
    player_name = greet_player()
    number_of_attempts = 0
    start_time = time.time()

    # Main game loop
    while number_of_attempts < GAME_CONFIG['max_attempts']:
        # Get valid guess from player
        player_guess = get_valid_guess(valid_guess_words)
        number_of_attempts += 1

        # Evaluate guess and provide feedback
        guess_score = evaluate_guess(player_guess, chosen_secret_word)
        display_guess_feedback(player_guess, guess_score, number_of_attempts)

        # Store guess history
        score_history.append((player_guess, guess_score))

        # Check for win condition
        if player_guess == chosen_secret_word:
            handle_win(player_name, start_time)
            return True

    # Handle loss (ran out of attempts)
    handle_loss(chosen_secret_word)
    return True


def play_wordle():
    """
    Main game function - handles multiple games and overall error handling.

    Features:
        - Supports multiple consecutive games
        - Handles keyboard interrupts gracefully
        - Provides overall error handling for unexpected issues
        - Clean exit messages
    """
    try:
        while True:
            # Play one game
            if not play_one_game():
                break

            # Ask if player wants to continue
            if not prompt_play_again():
                break

    except KeyboardInterrupt:
        print(MESSAGES['interrupted'])
    except Exception as e:
        print(f"Unexpected error in game: {e}")
        print("The game will now exit.")


# ==========================
# MAIN EXECUTION
# ==========================

if __name__ == "__main__":

    if RUN_TESTS:
        # Run doctests if enabled
        import doctest

        doctest.testmod()
    else:
        # Start the game
        play_wordle()