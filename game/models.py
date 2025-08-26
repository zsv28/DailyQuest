from django.db import models
from django.utils import timezone


class Player(models.Model):
    username = models.CharField(max_length=50, unique=True)
    points = models.IntegerField(default=0)
    first_login = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    days = models.IntegerField(default=0)

    def login(self):
        """Фиксирует вход пользователя и начисляет баллы"""
        today = timezone.now().date()

        if not self.first_login:
            self.first_login = timezone.now()

        if self.last_login and self.last_login.date() == today:
            return

        # подсчёт серии входов
        if not self.last_login:
            self.days = 1
        elif (today - self.last_login.date()).days == 1:
            self.days += 1
        else:
            self.days = 1

        self.last_login = timezone.now()
        self.points += 10
        self.save()

    def add_boost(self, boost, source="manual"):
        """Назначает игроку буст"""
        PlayerBoost.objects.create(player=self, boost=boost, source=source)

    def __str__(self):
        return f"{self.username} (баллы: {self.points})"


class Boost(models.Model):
    BOOST_TYPES = [
        ("speed", "Ускорение"),
        ("shield", "Щит"),
        ("extra_life", "Доп. жизнь"),
    ]

    name = models.CharField(max_length=50, choices=BOOST_TYPES, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.get_name_display()


class PlayerBoost(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="boosts")
    boost = models.ForeignKey(Boost, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(
        max_length=20,
        choices=[("manual", "Назначено вручную"), ("level", "За уровень")],
        default="manual",
    )

    def __str__(self):
        return f"{self.player.username} → {self.boost} ({self.source})"


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Prize(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)

    def assign_prize(self, prize):
        """Назначить игроку приз за прохождение уровня"""
        if not self.is_completed:
            raise ValueError("Игрок ещё не завершил уровень.")

        LevelPrize.objects.create(
            level=self.level,
            prize=prize,
            received=timezone.now().date()
        )
        return prize

    def __str__(self):
        return f"{self.player.username} → {self.level.title}"


class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()

    def __str__(self):
        return f"{self.level.title} → {self.prize.title}"
