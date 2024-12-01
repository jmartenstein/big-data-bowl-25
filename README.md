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

Matchup Favorability

Pre-Snap Readiness

Spatial Advantage

# To Do

Predict receiver / defense match ups

Adapt distribution weights, so that 0.0 lines up line of scrimmage
  at line set; how far does this move at snap?

~~Correlation of yards gained to expected points added in week1~~

How long betweeen snap and next event?

If a player is in motion before the snap, what are the chances they get the ball?

Compare normal distributions

~~Parameterize normal distribution functions (add to analze play?)~~

Use Analyze Play beyond Week 1

Move df_players to lookup class / data object
