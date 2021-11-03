from sections.header import HeaderSection
from sections.users import UsersSection
from sections.predictions import PredictionsSection

SECTIONS = [HeaderSection, UsersSection, PredictionsSection]


def draw_sections():
    for s in SECTIONS:
        section = s()
        section.draw()
