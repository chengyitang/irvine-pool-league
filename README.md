## Pool League Rankings

| Rank | Player   | Wins | Losses | Total | Win Rate |
|------|----------|------|--------|-------|----------|
| 1    | Jaylon   | 3    | 0      | 3     | 100.0%   |
| 2    | Thomas   | 10   | 4      | 14    | 71.4%    |
| 3    | Jerry    | 1    | 1      | 2     | 50.0%    |
| 4    | Raymond  | 4    | 4      | 8     | 50.0%    |
| 5    | Kyle     | 7    | 9      | 16    | 43.8%    |
| 6    | Roger    | 3    | 10     | 13    | 23.1%    |

## Commands

### Important Note
Before running the commands, ensure the `pool` script is executable. You can set the executable permission with the following command:

```bash
chmod +x pool
```

### Add a Match Result
Record a match result where one player defeats another.

```bash
./pool PlayerA - PlayerB
```

### Add a Match with Date
Record a match result with a specific date.

```bash
./pool PlayerA - PlayerB -d YYYY-MM-DD
```

### Show Rankings
Display the current rankings of all players.

```bash
./pool show
```

### Show Match History
Display the history of matches played.

```bash
./pool history
```

### Show Player Statistics
Display detailed statistics for a specific player.

```bash
./pool stats PlayerName
```
