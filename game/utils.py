import csv

from .models import LevelPrize, PlayerLevel


def save_csv(file_path):
    """Сохраняет данные об игроках и уровнях в CSV."""
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["player_id", "level", "is_completed", "prizes"])

        player_levels = PlayerLevel.objects.select_related(
            "player", "level").iterator(
            chunk_size=2000)

        for player_level in player_levels:
            prizes = LevelPrize.objects.filter(
                level=player_level.level).select_related(
                "prize")
            titles = ", ".join(
                reward.prize.title for reward in prizes) if prizes else "—"

            writer.writerow(
                [
                    player_level.player.username,
                    player_level.level.title,
                    "yes" if player_level.is_completed else "no",
                    titles
                ])
