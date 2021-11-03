from sections.title import TitleSection
from sections.users import UsersSection
from sections.predictions import PredictionsSection

SECTIONS = [TitleSection, UsersSection, PredictionsSection]


def draw_sections():
    for s in SECTIONS:
        section = s()
        section.draw()
