#!/usr/bin/env python3
"""
Pool League Ranking Management Tool
Usage:
  pool Thomas > Raymond    # Add match result (Thomas wins)
  pool show               # Show rankings
  pool history            # Show match history
  pool stats Raymond      # Show player statistics
"""

import json
import sys
from datetime import datetime
from pathlib import Path

class PoolLeague:
    def __init__(self, data_file="match_data.json"):
        self.data_file = Path(data_file)
        self.data = self.load_data()
    
    def load_data(self):
        """Load data file"""
        if not self.data_file.exists() or self.data_file.stat().st_size == 0:
            # Initialize with default data if file doesn't exist or is empty
            initial_data = {"matches": [], "players": {}}
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)
            return initial_data
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_data(self):
        """Save data to file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    # Function to parse date and convert to ISO format
    def parse_date(self, date_str):
        try:
            # Try parsing the date in 'YYYY-M-D' format
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            # If parsing fails, return None
            return None
        return date_obj.isoformat()
    
    def add_match(self, winner, loser, date=None):
        """Add match result"""
        print(f"Adding match: {winner} beats {loser}")  # Debugging print statement
        # Record match
        match_date = self.parse_date(date) if date else datetime.now().isoformat()
        if not match_date:
            print(f"❌ Invalid date format: {date}")
            return False
        match = {
            "date": match_date,
            "winner": winner,
            "loser": loser
        }
        self.data["matches"].append(match)
        
        # Update player statistics
        self.update_player_stats(winner, loser)
        self.save_data()
        
        # Update README.md with current rankings
        self.update_readme_with_rankings()
        
        print(f"✅ Match recorded: {winner} defeated {loser}")
        return True
    
    def update_player_stats(self, winner, loser):
        """Update player statistics"""
        # Initialize player data
        for player in [winner, loser]:
            if player not in self.data["players"]:
                self.data["players"][player] = {"wins": 0, "losses": 0}
        
        # Update win/loss records
        self.data["players"][winner]["wins"] += 1
        self.data["players"][loser]["losses"] += 1
    
    def get_rankings(self):
        """Get rankings"""
        rankings = []
        for player, stats in self.data["players"].items():
            wins = stats["wins"]
            losses = stats["losses"]
            total = wins + losses
            win_rate = wins / total if total > 0 else 0
            
            rankings.append({
                "player": player,
                "wins": wins,
                "losses": losses,
                "total": total,
                "win_rate": win_rate
            })
        
        # Sort by win rate, then by number of wins if win rates are equal
        rankings.sort(key=lambda x: (x["win_rate"], x["wins"]), reverse=True)
        return rankings
    
    def show_rankings(self):
        """Display rankings"""
        rankings = self.get_rankings()
        
        if not rankings:
            print("📊 No match records available")
            return
        
        print("\n🏆 Pool League Rankings")
        print("=" * 60)
        print(f"{'Rank':^4} {'Player':^10} {'Wins':^6} {'Losses':^6} {'Total':^6} {'Win Rate':^8}")
        print("-" * 60)
        
        for i, player in enumerate(rankings, 1):
            win_rate_str = f"{player['win_rate']*100:.1f}%"
            print(f"{i:^4} {player['player']:^10} {player['wins']:^6} "
                  f"{player['losses']:^6} {player['total']:^6} {win_rate_str:^8}")
        
        print("=" * 60)
    
    def show_history(self, limit=10):
        """Show match history"""
        matches = self.data["matches"][-limit:]  # Recent matches
        
        if not matches:
            print("📝 No match records available")
            return
        
        print(f"\n📝 Last {len(matches)} matches")
        print("=" * 50)
        
        for match in reversed(matches):  # Newest first
            date = datetime.fromisoformat(match["date"]).strftime("%m/%d %H:%M")
            print(f"{date} | {match['winner']} > {match['loser']}")
        
        print("=" * 50)
    
    def show_player_stats(self, player):
        """Show player statistics"""
        if player not in self.data["players"]:
            print(f"❌ Player not found: {player}")
            return
        
        stats = self.data["players"][player]
        wins = stats["wins"]
        losses = stats["losses"]
        total = wins + losses
        win_rate = wins / total if total > 0 else 0
        
        print(f"\n👤 {player}'s Statistics")
        print("=" * 30)
        print(f"Wins: {wins}")
        print(f"Losses: {losses}")
        print(f"Total matches: {total}")
        print(f"Win rate: {win_rate*100:.1f}%")
        
        # Find head-to-head records
        vs_stats = {}
        for match in self.data["matches"]:
            if match["winner"] == player:
                opponent = match["loser"]
                vs_stats[opponent] = vs_stats.get(opponent, {"wins": 0, "losses": 0})
                vs_stats[opponent]["wins"] += 1
            elif match["loser"] == player:
                opponent = match["winner"]
                vs_stats[opponent] = vs_stats.get(opponent, {"wins": 0, "losses": 0})
                vs_stats[opponent]["losses"] += 1
        
        if vs_stats:
            print("\nHead-to-head records:")
            for opponent, record in vs_stats.items():
                print(f"  vs {opponent}: {record['wins']}W {record['losses']}L")
        
        print("=" * 30)

    def update_readme_with_rankings(self):
        """Generate markdown table of rankings and update README.md"""
        rankings = self.get_rankings()
        
        # Generate markdown table
        md_table = "\n## Pool League Rankings\n\n"
        md_table += "| Rank | Player   | Wins | Losses | Total | Win Rate |\n"
        md_table += "|------|----------|------|--------|-------|----------|\n"
        
        for i, player in enumerate(rankings, 1):
            win_rate_str = f"{player['win_rate']*100:.1f}%"
            md_table += f"| {i}    | {player['player']} | {player['wins']}  | {player['losses']}   | {player['total']}  | {win_rate_str} |\n"
        
        # Read the current README.md
        readme_path = Path('README.md')
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        else:
            readme_content = ""
        
        # Replace or add the rankings section
        if "## Pool League Rankings" in readme_content:
            readme_content = readme_content.split("## Pool League Rankings")[0] + md_table
        else:
            readme_content += md_table
        
        # Write updated content back to README.md
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("✅ README.md updated with current rankings.")

def print_help():
    print("🎱 Pool League Management Tool")
    print("\nUsage:")
    print("  pool Thomas > Raymond     # Add match (Thomas wins)")
    print("  pool show                # Show rankings")
    print("  pool history             # Show match history")
    print("  pool stats Thomas        # Show player statistics")

def main():
    league = PoolLeague()
    
    # No arguments, show rankings
    if len(sys.argv) == 1:
        print("No arguments provided, showing rankings.")  # Debugging print statement
        league.show_rankings()
        return
    
    args = sys.argv[1:]
   #print(f"Arguments received: {args}")  # Debugging print statement
    
    # Handle adding match with optional date: Thomas - Raymond -d 2025-5-20
    if len(args) >= 3 and args[1] == '-':
        #print("Adding match with arguments:", args)  # Debugging print statement
        winner, arrow, loser = args[:3]
        date = None
        
        # Check for -d flag
        if len(args) > 4 and args[3] == '-d':
            date = args[4]
            print(f"Date specified: {date}")  # Debugging print statement
        
        league.add_match(winner, loser, date)
        league.show_rankings()  # Show rankings after adding
        return
    
    # Handle other commands
    if len(args) == 1:
        command = args[0].lower()
        print(f"Single command received: {command}")  # Debugging print statement
        
        if command == 'show':
            league.show_rankings()
        elif command == 'history':
            league.show_history()
        elif command == 'help':
            print_help()
        else:
            print(f"❌ Unknown command: {command}")
            print_help()
    
    elif len(args) == 2 and args[0].lower() == 'stats':
        print(f"Stats command for player: {args[1]}")  # Debugging print statement
        league.show_player_stats(args[1])
    
    else:
        print("❌ Invalid command format")
        print_help()

if __name__ == "__main__":
    main()