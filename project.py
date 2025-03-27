import random
import sqlite3

# Game data - towers and their defenders
TOWERS = [
    # Easy towers
    {"name": "Eiffel Tower", "defender": "Iron Lady", "health": 100, "damage": 10},
    {"name": "Leaning Tower", "defender": "Slant Flyer", "health": 100, "damage": 10},
    {"name": "Sydney Opera", "defender": "Harbour Hawk", "health": 100, "damage": 10},
    
    # Normal towers  
    {"name": "Big Ben", "defender": "Clockwork", "health": 120, "damage": 15},
    {"name": "Christ Statue", "defender": "The Redeemer", "health": 120, "damage": 15},
    {"name": "Tokyo Skytree", "defender": "Sky Sentinel", "health": 120, "damage": 15},
    
    # Hard towers
    {"name": "Statue of Liberty", "defender": "Lady Freedom", "health": 150, "damage": 20},
    {"name": "Burj Khalifa", "defender": "Desert Falcon", "health": 150, "damage": 20},
    {"name": "Great Wall", "defender": "Dragon Flyer", "health": 150, "damage": 20}
]

# Shop items with costs
SHOP_ITEMS = {
    "health": 20,
    "damage": 15,
    "special": 25
}

def setup_database():
    """Initialize the database and return a connection"""
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                      (name TEXT, score INTEGER)''')
    conn.commit()
    return conn

def show_leaderboard(cursor):
    """Display the current leaderboard"""
    print("\n--- Top Scores ---")
    cursor.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 5")
    for name, score in cursor.fetchall():
        print(f"{name}: {score} points")
    print()

def run_shop(points, ship):
    """Handle the shop interactions"""
    print(f"\nYou have {points} points")
    print("Shop items:")
    for item, cost in SHOP_ITEMS.items():
        print(f"- {item}: {cost} points")
    
    choice = input("\nWhat to buy? (or 'back'): ").lower()
    
    if choice == 'back':
        return points
    
    if choice in SHOP_ITEMS and points >= SHOP_ITEMS[choice]:
        points -= SHOP_ITEMS[choice]
        if choice == "health":
            ship["health"] += 20
            print("Health upgraded!")
        elif choice == "damage":
            ship["damage"] += 10
            print("Damage increased!")
        elif choice == "special":
            print("Special ability unlocked!")
    else:
        print("Can't buy that.")
    
    return points

def battle_round(player, enemy):
    """Handle one round of combat"""
    # Player's turn
    print(f"\nYour health: {player['health']}")
    print(f"Enemy health: {enemy['health']}")
    
    choice = input("(A)ttack, (D)odge, (C)harge, (S)hop? ").upper()
    
    if choice == "A":
        damage = player['damage'] * (2 if player['charged'] else 1)
        enemy['health'] -= damage
        print(f"You hit for {damage} damage!")
        player['charged'] = False
        
        # Enemy counter-attack
        if random.random() < 0.3:  # 30% chance
            player['health'] -= enemy['damage']
            print(f"{enemy['defender']} counter-attacked!")
    
    elif choice == "D":
        if random.random() < 0.2:  # 20% dodge chance
            print("Dodged successfully!")
        else:
            player['health'] -= enemy['damage']
            print("Dodge failed!")
    
    elif choice == "C":
        player['charged'] = True
        print("Powering up for next attack...")
    
    elif choice == "S":
        return "shop"
    
    # Enemy's turn (if still alive)
    if enemy['health'] > 0 and choice != "S":
        if random.random() < 0.15:  # 15% dodge chance
            print(f"{enemy['defender']} dodged!")
        else:
            player['health'] -= enemy['damage']
            print(f"{enemy['defender']} attacked!")
    
    return "continue"

def main():
    """Main game loop"""
    conn = setup_database()
    cursor = conn.cursor()
    points = 0
    
    print("\nALIEN TOWER ATTACK\n")
    
    while True:
        # Show tower selection
        print("\nChoose a tower to attack:")
        for i, tower in enumerate(TOWERS):
            diff = "Easy" if i < 3 else "Normal" if i < 6 else "Hard"
            print(f"{i+1}. {tower['name']} ({diff})")
        
        try:
            choice = int(input("\nEnter tower number: ")) - 1
            if choice < 0 or choice >= len(TOWERS):
                print("Invalid choice.")
                continue
        except ValueError:
            print("Enter a number.")
            continue
        
        tower = TOWERS[choice]
        enemy = {
            "defender": tower["defender"],
            "health": tower["health"],
            "damage": tower["damage"]
        }
        
        player = {
            "health": 100,
            "damage": 20,
            "charged": False
        }
        
        # Battle loop
        while player["health"] > 0 and enemy["health"] > 0:
            result = battle_round(player, enemy)
            
            if result == "shop":
                points = run_shop(points, player)
            
            if player["health"] <= 0:
                break
        
        # Battle outcome
        if player["health"] > 0:
            points += tower['health']
            print(f"\nYou defeated {tower['defender']}!")
            print(f"Earned {tower['health']} points (Total: {points})")
        else:
            print("\nYour ship was destroyed!")
        
        # Save score
        name = input("Enter your name: ")
        cursor.execute("INSERT INTO scores VALUES (?, ?)", (name, points))
        conn.commit()
        
        show_leaderboard(cursor)
        
        if input("Play again? (y/n): ").lower() != 'y':
            break
    
    conn.close()
    print("\nThanks for playing!")

if __name__ == "__main__":
    main()