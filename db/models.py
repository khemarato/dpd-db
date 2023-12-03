"""Datebase model for use by SQLAlchemy."""
import re

from typing import List
from typing import Optional

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import object_session
from sqlalchemy import Column, Integer, Table

from tools.link_generator import generate_link
from tools.pali_sort_key import pali_sort_key


class Base(DeclarativeBase):
    pass

assoc_pali_words_to_family_compounds = Table(
    'pali_words_to_family_compounds',
    Base.metadata,
    Column('pali_word_id', Integer, ForeignKey("pali_words.id", ondelete="CASCADE"), primary_key=True, nullable=False),
    Column('family_compound_id', Integer, ForeignKey("family_compound.id", ondelete="CASCADE"), primary_key=True, nullable=False),
)

assoc_pali_words_to_family_sets = Table(
    'pali_words_to_family_sets',
    Base.metadata,
    Column('pali_word_id', Integer, ForeignKey("pali_words.id", ondelete="CASCADE"), primary_key=True, nullable=False),
    Column('family_set_set', Integer, ForeignKey("family_set.set", ondelete="CASCADE"), primary_key=True, nullable=False),
)

class InflectionTemplates(Base):
    __tablename__ = "inflection_templates"

    pattern: Mapped[str] = mapped_column(primary_key=True)
    like: Mapped[str] = mapped_column(default='')
    data: Mapped[str] = mapped_column(default='')

    def __repr__(self) -> str:
        return f"InflectionTemplates: {self.pattern} {self.like} {self.data}"


class PaliRoot(Base):
    __tablename__ = "pali_roots"

    root: Mapped[str] = mapped_column(primary_key=True)
    root_in_comps: Mapped[str] = mapped_column(default='')
    root_has_verb: Mapped[str] = mapped_column(default='')
    root_group: Mapped[int] = mapped_column(default=0)
    root_sign: Mapped[str] = mapped_column(default='')
    root_meaning: Mapped[str] = mapped_column(default='')
    sanskrit_root: Mapped[str] = mapped_column(default='')
    sanskrit_root_meaning: Mapped[str] = mapped_column(default='')
    sanskrit_root_class: Mapped[str] = mapped_column(default='')
    root_example: Mapped[str] = mapped_column(default='')
    dhatupatha_num: Mapped[str] = mapped_column(default='')
    dhatupatha_root: Mapped[str] = mapped_column(default='')
    dhatupatha_pali: Mapped[str] = mapped_column(default='')
    dhatupatha_english: Mapped[str] = mapped_column(default='')
    dhatumanjusa_num: Mapped[int] = mapped_column(default=0)
    dhatumanjusa_root: Mapped[str] = mapped_column(default='')
    dhatumanjusa_pali: Mapped[str] = mapped_column(default='')
    dhatumanjusa_english: Mapped[str] = mapped_column(default='')
    dhatumala_root: Mapped[str] = mapped_column(default='')
    dhatumala_pali: Mapped[str] = mapped_column(default='')
    dhatumala_english: Mapped[str] = mapped_column(default='')
    panini_root: Mapped[str] = mapped_column(default='')
    panini_sanskrit: Mapped[str] = mapped_column(default='')
    panini_english: Mapped[str] = mapped_column(default='')
    note: Mapped[str] = mapped_column(default='')
    matrix_test: Mapped[str] = mapped_column(default='')
    root_info: Mapped[str] = mapped_column(default='')
    root_matrix: Mapped[str] = mapped_column(default='')
    # ru_root_meaning: Mapped[str] = mapped_column(default='')
    # ru_sk_root_meaning: Mapped[str] = mapped_column(default='')

    created_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now())

    pw: Mapped[List["PaliWord"]] = relationship(
        back_populates="rt")

    @property
    def root_clean(self) -> str:
        return re.sub(r" \d.*$", "", self.root)

    @property
    def root_no_sign(self) -> str:
        return re.sub(r"\d| |√", "", self.root)

    @property
    def root_(self) -> str:
        return self.root.replace(" ", "_")

    @property
    def root_link(self) -> str:
        return self.root.replace(" ", "%20")

    @property
    def root_count(self) -> int:
        db_session = object_session(self)
        if db_session is None:
            raise Exception("No db_session")

        return db_session.query(
            PaliWord
            ).filter(
                PaliWord.root_key == self.root
            ).count()

    @property
    def root_family_list(self) -> list:
        db_session = object_session(self)
        if db_session is None:
            raise Exception("No db_session")

        results = db_session.query(
            PaliWord
        ).filter(
            PaliWord.root_key == self.root
        ).group_by(
            PaliWord.family_root
        ).all()
        family_list = [i.family_root for i in results if i.family_root is not None]
        family_list = sorted(family_list, key=lambda x: pali_sort_key(x))
        return family_list

    def __repr__(self) -> str:
        return f"""PaliRoot: {self.root} {self.root_group} {self.root_sign} ({self.root_meaning})"""


class PaliWord(Base):
    __tablename__ = "pali_words"

    id: Mapped[int] = mapped_column(primary_key=True)
    pali_1: Mapped[str] = mapped_column(unique=True)
    pali_2: Mapped[str] = mapped_column(default='')
    pos: Mapped[str] = mapped_column(default='')
    grammar: Mapped[str] = mapped_column(default='')
    derived_from: Mapped[str] = mapped_column(default='')
    neg: Mapped[str] = mapped_column(default='')
    verb: Mapped[str] = mapped_column(default='')
    trans:  Mapped[str] = mapped_column(default='')
    plus_case:  Mapped[str] = mapped_column(default='')

    meaning_1: Mapped[str] = mapped_column(default='')
    meaning_lit: Mapped[str] = mapped_column(default='')
    meaning_2: Mapped[str] = mapped_column(default='')

    non_ia: Mapped[str] = mapped_column(default='')
    sanskrit: Mapped[str] = mapped_column(default='')

    root_key: Mapped[str] = mapped_column(
        ForeignKey("pali_roots.root"), default='')
    root_sign: Mapped[str] = mapped_column(default='')
    root_base: Mapped[str] = mapped_column(default='')

    family_root: Mapped[str] = mapped_column(default='')
    # ForeignKey("family_root.root_family"))
    family_word: Mapped[str] = mapped_column(
        ForeignKey("family_word.word_family"), default='')
    family_compound: Mapped[str] = mapped_column(default='')
    family_set: Mapped[str] = mapped_column(
        ForeignKey("family_set.set"), default='')

    construction:  Mapped[str] = mapped_column(default='')
    derivative: Mapped[str] = mapped_column(default='')
    suffix: Mapped[str] = mapped_column(default='')
    phonetic: Mapped[str] = mapped_column(default='')
    compound_type: Mapped[str] = mapped_column(default='')
    compound_construction: Mapped[str] = mapped_column(default='')
    non_root_in_comps: Mapped[str] = mapped_column(default='')

    source_1: Mapped[str] = mapped_column(default='')
    sutta_1: Mapped[str] = mapped_column(default='')
    example_1: Mapped[str] = mapped_column(default='')

    source_2: Mapped[str] = mapped_column(default='')
    sutta_2: Mapped[str] = mapped_column(default='')
    example_2: Mapped[str] = mapped_column(default='')

    antonym: Mapped[str] = mapped_column(default='')
    synonym: Mapped[str] = mapped_column(default='')
    variant: Mapped[str] = mapped_column(default='')
    commentary: Mapped[str] = mapped_column(default='')
    notes: Mapped[str] = mapped_column(default='')
    cognate: Mapped[str] = mapped_column(default='')
    link: Mapped[str] = mapped_column(default='')
    origin: Mapped[str] = mapped_column(default='')

    stem: Mapped[str] = mapped_column(default='')
    pattern: Mapped[str] = mapped_column(
        ForeignKey("inflection_templates.pattern"), default='')

    created_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now())

    rt: Mapped[PaliRoot] = relationship(uselist=False)

    dd = relationship("DerivedData", uselist=False)

    sbs = relationship("SBS", uselist=False)

    ru = relationship("Russian", uselist=False)

    it: Mapped[InflectionTemplates] = relationship()

    family_compounds: Mapped[List["FamilyCompound"]] = \
        relationship("FamilyCompound",
                     secondary=assoc_pali_words_to_family_compounds,
                     back_populates="pali_words")

    family_sets: Mapped[List["FamilySet"]] = \
        relationship("FamilySet",
                     secondary=assoc_pali_words_to_family_sets,
                     back_populates="pali_words")

    @property
    def is_draft(self) -> bool:
        return (self.meaning_1 is None or self.meaning_1 == "")

    @property
    def is_family_compound(self) -> bool:
        test1 = re.findall(r"\bcomp\b", self.grammar) != []
        test2 = "sandhi" in self.pos
        test3 = "idiom" in self.pos
        test4 = len(re.sub(r" \d.*$", "", self.pali_1)) < 30
        test5 = (not self.is_draft)

        return ((test1 or test2 or test3) and test4 and test5)

    @property
    def pali_1_(self) -> str:
        return self.pali_1.replace(" ", "_").replace(".", "_")

    @property
    def pali_link(self) -> str:
        return self.pali_1.replace(" ", "%20")

    @property
    def pali_clean(self) -> str:
        return re.sub(r" \d.*$", "", self.pali_1)

    @property
    def root_clean(self) -> str:
        try:
            if self.root_key is None:
                return ""
            else:
                return re.sub(r" \d.*$", "", self.root_key)
        except Exception as e:
            print(f"{self.pali_1}: {e}")
            return ""

    @property
    def family_compounds_keys_from_ssv(self) -> List[str]:
        if self.family_compound is None or self.family_compound == "":
            return []
        return self.family_compound.split(" ")

    @property
    def family_sets_keys_from_ssv(self) -> List[str]:
        if self.family_set is None or self.family_set == "":
            return []
        return self.family_set.split("; ")

    @property
    def family_compounds_sorted(self) -> list:
        """Sort by the order defined in family compound string list
        """
        if len(self.family_compounds) == 1:
            return self.family_compounds

        if self.family_compound is None:
            return []

        word_order = self.family_compounds_keys_from_ssv
        fc = sorted(self.family_compounds, key=lambda x: word_order.index(x.compound_family))
        return fc

    @property
    def family_sets_sorted(self) -> list:
        """Sort by the order defined in family set string list
        """
        if len(self.family_sets) == 1:
            return self.family_sets

        if self.family_set is None:
            return []

        word_order = self.family_sets_keys_from_ssv
        fs = sorted(self.family_sets, key=lambda x: word_order.index(x.set))
        return fs

    @property
    def family_compound_key_list(self) -> List[str]:
        return [i.compound_family for i in self.family_compounds_sorted]

    @property
    def family_set_key_list(self) -> List[str]:
        return [i.set for i in self.family_sets_sorted]

    @property
    def root_count(self) -> int:
        db_session = object_session(self)
        if db_session is None:
            raise Exception("No db_session")

        return db_session.query(
            PaliWord.id
        ).filter(
            PaliWord.root_key == self.root_key
        ).count()

    @property
    def pos_list(self) -> list:
        db_session = object_session(self)
        if db_session is None:
            raise Exception("No db_session")

        pos_db = db_session.query(
            PaliWord.pos
        ).group_by(
            PaliWord.pos
        ).all()
        return sorted([i.pos for i in pos_db])

    @property
    def synonym_list(self) -> list:
        if self.synonym:
            return self.synonym.split(", ")
        else:
            return [self.synonym]

    @property
    def variant_list(self) -> list:
        if self.variant:
            return self.variant.split(", ")
        else:
            return [self.variant]

    @property
    def source_link_1(self) -> str:
        return generate_link(self.source_1) if self.source_1 else ""

    @property
    def source_link_2(self) -> str:
        return generate_link(self.source_2) if self.source_2 else ""

    def __repr__(self) -> str:
        return f"""PaliWord: {self.id} {self.pali_1} {self.pos} {
            self.meaning_1}"""

class DerivedData(Base):
    __tablename__ = "derived_data"

    id: Mapped[int] = mapped_column(
        ForeignKey('pali_words.id'), primary_key=True)
    # pali_1: Mapped[str] = mapped_column(unique=True)
    inflections: Mapped[str] = mapped_column(default='')
    sinhala: Mapped[str] = mapped_column(default='')
    devanagari: Mapped[str] = mapped_column(default='')
    thai: Mapped[str] = mapped_column(default='')
    html_table: Mapped[str] = mapped_column(default='')
    freq_html: Mapped[str] = mapped_column(default='')
    ebt_count: Mapped[int] = mapped_column(default='')

    @property
    def inflections_list(self) -> list:
        if self.inflections:
            return self.inflections.split(",")
        else:
            return []

    @property
    def sinhala_list(self) -> list:
        if self.sinhala:
            return self.sinhala.split(",")
        else:
            return []

    @property
    def devanagari_list(self) -> list:
        if self.devanagari:
            return self.devanagari.split(",")
        else:
            return []

    @property
    def thai_list(self) -> list:
        if self.thai:
            return self.thai.split(",")
        else:
            return []

    def __repr__(self) -> str:
        return f"DerivedData: {self.id} {PaliWord.pali_1} {self.inflections}"


class Sandhi(Base):
    __tablename__ = "sandhi"
    id: Mapped[int] = mapped_column(primary_key=True)
    sandhi: Mapped[str] = mapped_column(unique=True)
    split: Mapped[str] = mapped_column(default='')
    sinhala: Mapped[str] = mapped_column(default='')
    devanagari: Mapped[str] = mapped_column(default='')
    thai: Mapped[str] = mapped_column(default='')

    @property
    def split_list(self) -> list:
        return self.split.split(",")

    @property
    def sinhala_list(self) -> list:
        if self.sinhala:
            return self.sinhala.split(",")
        else:
            return []

    @property
    def devanagari_list(self) -> list:
        if self.devanagari:
            return self.devanagari.split(",")
        else:
            return []

    @property
    def thai_list(self) -> list:
        if self.thai:
            return self.thai.split(",")
        else:
            return []

    def __repr__(self) -> str:
        return f"Sandhi: {self.id} {self.sandhi} {self.split}"


class FamilyRoot(Base):
    __tablename__ = "family_root"
    id: Mapped[int] = mapped_column(primary_key=True)
    root_id: Mapped[str] = mapped_column(default='')
    root_family: Mapped[str] = mapped_column(default='')
    html: Mapped[str] = mapped_column(default='')
    count: Mapped[int] = mapped_column(default=0)

    @property
    def root_family_link(self) -> str:
        return self.root_family.replace(" ", "%20")

    @property
    def root_family_(self) -> str:
        return self.root_family.replace(" ", "_")

    def __repr__(self) -> str:
        return f"FamilyRoot: {self.id} {self.root_id} {self.root_family} {self.count}"


class FamilyCompound(Base):
    __tablename__ = "family_compound"
    id: Mapped[int] = mapped_column(primary_key=True)
    compound_family: Mapped[str] = mapped_column(unique=True)
    html: Mapped[str] = mapped_column(default='')
    count: Mapped[int] = mapped_column(default=0)

    pali_words: Mapped[List[PaliWord]] = \
        relationship("PaliWord",
                     secondary=assoc_pali_words_to_family_compounds,
                     back_populates="family_compounds")

    def __repr__(self) -> str:
        return f"FamilyCompound: {self.id} {self.compound_family} {self.count}"


class FamilyWord(Base):
    __tablename__ = "family_word"
    word_family: Mapped[str] = mapped_column(primary_key=True)
    html: Mapped[str] = mapped_column(default='')
    count: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return f"FamilyWord: {self.word_family} {self.count}"


class FamilySet(Base):
    __tablename__ = "family_set"
    set: Mapped[str] = mapped_column(primary_key=True)
    html: Mapped[str] = mapped_column(default='')
    count: Mapped[int] = mapped_column(default=0)

    pali_words: Mapped[List[PaliWord]] = \
        relationship("PaliWord",
                     secondary=assoc_pali_words_to_family_sets,
                     back_populates="family_sets")

    def __repr__(self) -> str:
        return f"FamilySet: {self.set} {self.count}"


class SBS(Base):
    __tablename__ = "sbs"

    id: Mapped[int] = mapped_column(
        ForeignKey('pali_words.id'), primary_key=True)
    sbs_class_anki: Mapped[int] = mapped_column(default='')
    sbs_class: Mapped[int] = mapped_column(default='')
    sbs_meaning: Mapped[str] = mapped_column(default='')
    sbs_notes: Mapped[str] = mapped_column(default='')
    sbs_source_1: Mapped[str] = mapped_column(default='')
    sbs_sutta_1: Mapped[str] = mapped_column(default='')
    sbs_example_1: Mapped[str] = mapped_column(default='')
    sbs_chant_pali_1: Mapped[str] = mapped_column(default='')
    sbs_chant_eng_1: Mapped[str] = mapped_column(default='')
    sbs_chapter_1: Mapped[str] = mapped_column(default='')
    sbs_source_2: Mapped[str] = mapped_column(default='')
    sbs_sutta_2: Mapped[str] = mapped_column(default='')
    sbs_example_2: Mapped[str] = mapped_column(default='')
    sbs_chant_pali_2: Mapped[str] = mapped_column(default='')
    sbs_chant_eng_2: Mapped[str] = mapped_column(default='')
    sbs_chapter_2: Mapped[str] = mapped_column(default='')
    sbs_source_3: Mapped[str] = mapped_column(default='')
    sbs_sutta_3: Mapped[str] = mapped_column(default='')
    sbs_example_3: Mapped[str] = mapped_column(default='')
    sbs_chant_pali_3: Mapped[str] = mapped_column(default='')
    sbs_chant_eng_3: Mapped[str] = mapped_column(default='')
    sbs_chapter_3: Mapped[str] = mapped_column(default='')
    sbs_source_4: Mapped[str] = mapped_column(default='')
    sbs_sutta_4: Mapped[str] = mapped_column(default='')
    sbs_example_4: Mapped[str] = mapped_column(default='')
    sbs_chant_pali_4: Mapped[str] = mapped_column(default='')
    sbs_chant_eng_4: Mapped[str] = mapped_column(default='')
    sbs_chapter_4: Mapped[str] = mapped_column(default='')
    sbs_category: Mapped[str] = mapped_column(default='')

    def __repr__(self) -> str:
        return f"SBS: {self.id} {self.sbs_chant_pali_1} {self.sbs_class}"

    @declared_attr
    def sbs_chapter_flag(cls):
        return Column(Integer, nullable=True)  # Allow null values

    def calculate_chapter_flag(self):
        for i in range(1, 5):
            chapter_attr = getattr(self, f'sbs_chapter_{i}')
            if chapter_attr and chapter_attr.strip():
                return 1
        return None



class Russian(Base):
    __tablename__ = "russian"

    id: Mapped[int] = mapped_column(
        ForeignKey('pali_words.id'), primary_key=True)
    ru_meaning: Mapped[str] = mapped_column(default="")
    ru_meaning_lit: Mapped[str] = mapped_column(default="")
    ru_notes: Mapped[str] = mapped_column(default='')

    def __repr__(self) -> str:
        return f"Russian: {self.id} {self.ru_meaning}"
