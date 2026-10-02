# Consolidated Data v3 Key Map

The file `consolidated_data_v3.csv` contains records from the 2000 season onward. Each row represents a player, season, team, league, and stint combination with matching fielding and salary data when available.

| Column | Meaning | Source |
|---|---|---|
| `playerID` | Unique player identifier. | Batting, Fielding, Salaries |
| `yearID` | Baseball season year. | Batting, Fielding, Salaries |
| `stint` | Player's sequential team stint during the season. | Batting, Fielding |
| `teamID` | Team identifier. | Batting, Fielding, Salaries |
| `lgID` | League identifier. | Batting, Fielding, Salaries |
| `G` | Games played. | Batting, Fielding |
| `AB` | At-bats. | Batting |
| `R` | Runs scored. | Batting |
| `H` | Hits. | Batting |
| `2B` | Doubles. | Batting |
| `3B` | Triples. | Batting |
| `HR` | Home runs. | Batting |
| `RBI` | Runs batted in. | Batting |
| `SB` | Stolen bases. | Batting, Fielding |
| `CS` | Caught stealing. | Batting, Fielding |
| `BB` | Bases on balls, or walks. | Batting |
| `SO` | Strikeouts. | Batting |
| `IBB` | Intentional bases on balls. | Batting |
| `HBP` | Times hit by pitch. | Batting |
| `SH` | Sacrifice hits, or sacrifice bunts. | Batting |
| `SF` | Sacrifice flies. | Batting |
| `GIDP` | Grounded into double plays. | Batting |
| `POS` | Defensive position. | Fielding |
| `GS` | Games started in the field. | Fielding |
| `InnOuts` | Defensive innings represented as outs recorded. Divide by 3 for innings. | Fielding |
| `PO` | Putouts recorded. | Fielding |
| `A` | Assists recorded. | Fielding |
| `E` | Errors committed. | Fielding |
| `DP` | Double plays participated in. | Fielding |
| `salary` | Player salary for the season and team. | Salaries |

`PB` (passed balls) and `WP` (wild pitches) were excluded from the v3 output as requested. `ZR` (zone rating) was removed earlier because it contained no usable values in the source data.
