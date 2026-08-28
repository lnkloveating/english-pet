from shengsheng_pet_pipeline.description import PetDescriptionParser, PetSafetyRewriter


def test_chinese_description_becomes_controlled_spec() -> None:
    spec = PetDescriptionParser().parse("一只淡紫色的小猫，有星星尾巴，性格温柔，喜欢读书。")
    assert spec.species == "cat"
    assert spec.primary_color == "light purple"
    assert spec.personality == "gentle"
    assert spec.theme == "reading"
    assert spec.accessories == ["star tail"]


def test_copyright_character_is_generalized() -> None:
    rewritten = PetSafetyRewriter().rewrite("A yellow Pikachu cat")
    assert "pikachu" not in rewritten.casefold()
