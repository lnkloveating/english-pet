import re
from typing import ClassVar

from shengsheng_contracts import PetSpecification


class PetSafetyRewriter:
    """Conservative MVP rewrite; production must add model and image moderation."""

    _unsafe_terms = ("blood", "gore", "sexy", "gun", "鲜血", "血腥", "性感", "枪")
    _copyright_terms = (
        "pikachu",
        "hello kitty",
        "mickey",
        "皮卡丘",
        "凯蒂猫",
        "米奇",
    )

    def rewrite(self, text: str) -> str:
        safe = text
        for term in (*self._unsafe_terms, *self._copyright_terms):
            safe = re.sub(re.escape(term), "cute", safe, flags=re.IGNORECASE)
        return safe.strip()


class PetDescriptionParser:
    _species: ClassVar[dict[str, tuple[str, ...]]] = {
        "cat": ("cat", "kitten", "猫"),
        "dog": ("dog", "puppy", "狗"),
        "fox": ("fox", "狐狸"),
        "dinosaur": ("dinosaur", "dino", "恐龙"),
        "dragon": ("dragon", "龙"),
    }
    _colors: ClassVar[dict[str, tuple[str, ...]]] = {
        "light purple": ("light purple", "lavender", "淡紫", "浅紫"),
        "blue": ("blue", "蓝"),
        "pink": ("pink", "粉"),
        "green": ("green", "绿"),
        "orange": ("orange", "橙"),
        "white": ("white", "白"),
    }
    _personalities: ClassVar[dict[str, tuple[str, ...]]] = {
        "gentle": ("gentle", "温柔"),
        "brave": ("brave", "勇敢"),
        "curious": ("curious", "好奇"),
        "playful": ("playful", "活泼", "爱玩"),
    }
    _accessories: ClassVar[dict[str, tuple[str, ...]]] = {
        "star tail": ("star tail", "星星尾巴"),
        "wings": ("wing", "翅膀"),
        "school bag": ("school bag", "backpack", "书包"),
        "scarf": ("scarf", "围巾"),
        "glasses": ("glasses", "眼镜"),
    }

    def parse(self, text: str) -> PetSpecification:
        normalized = text.casefold()
        species = self._match(normalized, self._species, "cat")
        color = self._match(normalized, self._colors, "sky blue")
        personality = self._match(normalized, self._personalities, "friendly")
        accessories = [
            label
            for label, terms in self._accessories.items()
            if any(term in normalized for term in terms)
        ][:3]
        theme = "reading" if "read" in normalized or "书" in normalized else "island adventure"
        return PetSpecification(
            species=species,
            primary_color=color,
            personality=personality,
            theme=theme,
            accessories=accessories,
        )

    @staticmethod
    def _match(text: str, choices: dict[str, tuple[str, ...]], default: str) -> str:
        for label, terms in choices.items():
            if any(term in text for term in terms):
                return label
        return default
