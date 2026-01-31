import sys
import os
import argparse

import pandas as pd
import matplotlib.pyplot as plt

### CONSTANTS ###

RAW_DATA_DIR = "data/kaggle"

### FUNCTIONS ###


def load_plays_for_game(target_game_id):
    plays_file = f"{RAW_DATA_DIR}/plays.csv"
    if not os.path.exists(plays_file):
        print(f"Error: {plays_file} not found.")
        sys.exit(1)
    plays_df = pd.read_csv(plays_file)
    return plays_df[plays_df["gameId"] == target_game_id].copy()


def load_game_info(target_game_id):
    games_file = f"{RAW_DATA_DIR}/games.csv"
    if not os.path.exists(games_file):
        print(f"Error: {games_file} not found.")
        sys.exit(1)
    df_games = pd.read_csv(games_file)
    return df_games[df_games["gameId"] == target_game_id]


def game_clock_to_seconds(clock_str):
    """Converts mm:ss to total seconds remaining in quarter."""
    if pd.isna(clock_str) or not isinstance(clock_str, str):
        return 0
    parts = clock_str.split(":")
    if len(parts) != 2:
        return 0
    try:
        m, s = map(int, parts)
        return m * 60 + s
    except ValueError:
        return 0


def get_sorted_plays(df):
    """Sorts plays chronologically by quarter and clock."""
    df["seconds_remaining"] = df["gameClock"].apply(game_clock_to_seconds)
    # Calculate elapsed time in game (0 to 3600 seconds for regulation)
    df["game_seconds_elapsed"] = (df["quarter"] - 1) * 900 + (
        900 - df["seconds_remaining"]
    )
    # Quarter ASC, Seconds DESC (clock counts down)
    return df.sort_values(by=["quarter", "seconds_remaining"], ascending=[True, False])


def plot_scores(
    df,
    target_game_id,
    home_team_name,
    visitor_team_name,
    final_home_score,
    final_visitor_score,
    output_path=None,
):
    """Generates and displays (or saves) a plot of scores and net difference over time."""
    # Calculate Expected Scores
    # EP is points for the possession team
    df["home_expected"] = df.apply(
        lambda row: row["preSnapHomeScore"]
        + (row["expectedPoints"] if row["possessionTeam"] == home_team_name else 0),
        axis=1,
    )
    df["visitor_expected"] = df.apply(
        lambda row: row["preSnapVisitorScore"]
        + (row["expectedPoints"] if row["possessionTeam"] == visitor_team_name else 0),
        axis=1,
    )

    # Determine leading team (winner) for the Y-axis reference
    if final_home_score >= final_visitor_score:
        pos_team, neg_team = home_team_name, visitor_team_name
        df["net_actual"] = df["preSnapHomeScore"] - df["preSnapVisitorScore"]
        df["net_expected"] = df["home_expected"] - df["visitor_expected"]
        pos_color, neg_color = "blue", "red"
    else:
        pos_team, neg_team = visitor_team_name, home_team_name
        df["net_actual"] = df["preSnapVisitorScore"] - df["preSnapHomeScore"]
        df["net_expected"] = df["visitor_expected"] - df["home_expected"]
        pos_color, neg_color = "red", "blue"

    # Create subplots with shared X axis and different height ratios
    _, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]}
    )

    # --- Top Subplot: Scores ---
    # Plot Actual Scores
    ax1.step(
        df["game_seconds_elapsed"],
        df["preSnapHomeScore"],
        label=f"{home_team_name} Actual",
        where="post",
        color="blue",
        alpha=0.3,
    )
    ax1.step(
        df["game_seconds_elapsed"],
        df["preSnapVisitorScore"],
        label=f"{visitor_team_name} Actual",
        where="post",
        color="red",
        alpha=0.3,
    )

    # Plot Expected Scores
    ax1.plot(
        df["game_seconds_elapsed"],
        df["home_expected"],
        label=f"{home_team_name} Expected",
        color="blue",
        linewidth=2,
    )
    ax1.plot(
        df["game_seconds_elapsed"],
        df["visitor_expected"],
        label=f"{visitor_team_name} Expected",
        color="red",
        linewidth=2,
    )

    ax1.set_title(
        f"Score and Expected Points: {visitor_team_name} at {home_team_name} ({target_game_id})"
    )
    ax1.set_ylabel("Points")
    ax1.legend()
    ax1.grid(True, linestyle="--", alpha=0.7)

    # --- Bottom Subplot: Net Difference (Winner is Positive) ---
    ax2.step(
        df["game_seconds_elapsed"],
        df["net_actual"],
        label="Actual Diff",
        where="post",
        color="black",
        alpha=0.2,
    )
    ax2.plot(
        df["game_seconds_elapsed"],
        df["net_expected"],
        label="Expected Diff",
        color="purple",
        linewidth=1.5,
    )

    # Shade regions to show who is "leading"
    ax2.fill_between(
        df["game_seconds_elapsed"],
        0,
        df["net_expected"],
        where=(df["net_expected"] >= 0),
        color=pos_color,
        alpha=0.2,
        label=f"{pos_team} Lead",
        interpolate=True,
    )
    ax2.fill_between(
        df["game_seconds_elapsed"],
        0,
        df["net_expected"],
        where=(df["net_expected"] < 0),
        color=neg_color,
        alpha=0.2,
        label=f"{neg_team} Lead",
        interpolate=True,
    )

    ax2.axhline(y=0, color="black", linestyle="-", linewidth=1.0)  # Baseline

    ax2.set_ylabel(f"Lead Magnitude\n({pos_team} Lead +)")
    ax2.set_xlabel("Game Seconds Elapsed")
    ax2.legend(loc="upper right", fontsize="x-small")
    ax2.grid(True, linestyle="--", alpha=0.7)

    # Add vertical lines for quarter breaks to both subplots
    for ax in [ax1, ax2]:
        for q in range(1, 5):
            ax.axvline(x=q * 900, color="gray", linestyle="-", alpha=0.5)
            if ax == ax1:
                ax.text(
                    q * 900 - 450,
                    ax.get_ylim()[1] * 0.95,
                    f"Q{q}",
                    horizontalalignment="center",
                )

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Graph saved to {output_path}")
    else:
        plt.show()


### MAIN ###

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot scores and expected points over time for a specific game."
    )
    parser.add_argument("game_id", type=int, help="The ID of the game to plot.")
    parser.add_argument(
        "-o",
        "--output",
        help="Path to save the output graph file (e.g., 'output.png'). " +
             "If not provided, the graph will be displayed.",
    )

    args = parser.parse_args()
    game_id = args.game_id
    output_arg = args.output

    # Load game metadata
    df_game = load_game_info(game_id)
    if df_game.empty:
        print(f"Could not find game {game_id}")
        sys.exit(1)

    home_team = df_game["homeTeamAbbr"].values[0]
    visitor_team = df_game["visitorTeamAbbr"].values[0]
    home_final = df_game["homeFinalScore"].values[0]
    visitor_final = df_game["visitorFinalScore"].values[0]

    # Load plays
    df_plays = load_plays_for_game(game_id)
    if df_plays.empty:
        print(f"No plays found for game {game_id}")
        sys.exit(1)

    # Sort plays temporally
    df_sorted = get_sorted_plays(df_plays)

    # Generate Plot
    plot_scores(
        df_sorted,
        game_id,
        home_team,
        visitor_team,
        home_final,
        visitor_final,
        output_path=output_arg,
    )
