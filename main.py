import random

best_score = None

while True:
    n = random.randint(0, 100)
    guesses = 0
    a = -1

    print("\n🎯 New Game Started!")
    print("Guess the number between 0 and 100")

    while a != n:
        try:
            a = int(input("Your guess: "))
        except ValueError:
            print("❌ Please enter a valid number")
            continue

        guesses += 1

        if a == n:
            if guesses == 1:
                print("🔥 Wow! First attempt! Lucky guess!")
            else:
                print("✅ Correct guess!")
        elif a > n:
            print("⬇️ Guess a lower number")
        else:
            print("⬆️ Guess a higher number")

    print(f"🎉 You guessed the number {n} in {guesses} attempts")

    # Best score logic
    if best_score is None or guesses < best_score:
        best_score = guesses
        print("🏆 New best score!")

    print(f"🥇 Best Score: {best_score} attempts")

    # Replay option
    play_again = input("\nPlay again? (y/n): ").lower()
    if play_again != 'y':
        print("👋 Thanks for playing!")
        break
