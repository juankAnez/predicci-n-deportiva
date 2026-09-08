from dataclasses import dataclass


@dataclass
class Probability:
    home_win: float = 0.0
    draw: float = 0.0
    away_win: float = 0.0

    @property
    def is_calibrated(self) -> bool:
        total = self.home_win + self.draw + self.away_win
        return abs(total - 1.0) < 0.01

    def normalize(self) -> "Probability":
        total = self.home_win + self.draw + self.away_win
        if total > 0:
            return Probability(
                home_win=self.home_win / total,
                draw=self.draw / total,
                away_win=self.away_win / total,
            )
        return self
