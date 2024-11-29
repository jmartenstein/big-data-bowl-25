# Big Data Bowl 2025

This repository is for my initial exploration in the Big Data Bowl 2025 competetion

# Previous Winners

[Uncovering Missed Tackle Opportunities](https://www.kaggle.com/code/matthewpchang/uncovering-missed-tackle-opportunities/)

[Between the Lines](https://www.kaggle.com/code/hassaaninayatali/between-the-lines-how-do-we-measure-pressure)

# Five Interesting Motion Plays

## Patriots at Dolphins, 9/11/22

[Thinking Football Clip](https://youtu.be/aE9i1lq7cZg?t=55)

[ESPN Play-by-Play](https://www.espn.com/nfl/playbyplay/_/gameId/401437630)

1st & 10 at NE 22
(6:48 - 1st) T.Tagovailoa pass deep left to T.Hill to NE 22 for 23 yards (Jo.Jones). FUMBLES (Jo.Jones), ball out of bounds at NE 22.

gameId: 2022091106
playId: 442

`grep -E "2022091106,442" data/kaggle/plays.csv`

## Bills at Dolphins

[Thinking Football Clip](https://youtu.be/aE9i1lq7cZg?t=136)

[ESPN Play-by-Play](https://www.espn.com/nfl/playbyplay/_/gameId/401437738)

[NFL Highlight Video](https://youtu.be/gUvHlA1-JWQ?t=389)

1st & 10 at MIA 25
(15:00 - 3rd) T.Tagovailoa pass deep middle to T.Hill to MIA 47 for 22 yards (D.Hamlin). MIA-G.Little was injured during the play.

gameId: 2022092503
playId: 2132

`grep -E "2022092503,2132" data/kaggle/plays.csv`

# Potential Metrics

Pre-Snap Readiness

Matchup Favorability

Spatial Advantage

# To Do

Correlation of yards gained to expected points added?

Compare normal distributions

Parameterize normal distbituion functions (add to analze play?)

How long betweeen snap and next event?

Use Analyze Play beyond Week 1
