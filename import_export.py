from surnames import *
from typing import NamedTuple, Callable
from collections.abc import Iterable
import pandas as pd

class SingleLetterNameGenerator:

    def __init__(self) -> None:
        self.curr: int = ord("A") - 1

    def generate_component(self) -> str:
        self.curr += 1
        return chr(self.curr)

    def generate_name(self, num_components: int) -> str:
        assert 1 <= num_components <= 2
        return "-".join(self.generate_component() for i in range(num_components))

# -------------------------------------------------------------------------------

class Family(NamedTuple):
    father_birth: str
    father_married: str
    mother_birth: str
    mother_married: str
    son_birth: str
    daughter_birth: str

# -------------------------------------------------------------------------------

def export_scheme_to_family(scheme: type[Scheme]) -> Family:
    name_generator = SingleLetterNameGenerator()
    husband_birth: str = name_generator.generate_name(scheme.stable_num_components_at_birth("M"))
    wife_birth: str = name_generator.generate_name(scheme.stable_num_components_at_birth("F"))
    husband_married, wife_married = marry(husband_birth, wife_birth, scheme)
    son_birth: str = scheme.get_child_name(husband_married, wife_married, "M")
    daughter_birth: str = scheme.get_child_name(husband_married, wife_married, "F")
    return Family(
        husband_birth, husband_married, wife_birth, wife_married, son_birth, daughter_birth
    )

def get_combined_components(name_1: str, name_2: str) -> list[str]:
    return list(dict.fromkeys(get_components(name_1) + get_components(name_2)))

def get_component_indices(result_name: str, input_name_1: str, input_name_2: str) -> list[int]:
    result_components: list[str] = get_components(result_name)
    input_components: list[str] = get_combined_components(input_name_1, input_name_2)
    return [input_components.index(component) for component in result_components]

def get_result_name(input_name_1: str, input_name_2: str, indices: list[int]) -> str:
    input_components: list[str] = get_combined_components(input_name_1, input_name_2)
    return "-".join(input_components[index] for index in indices)

def get_son_name_maker(family: Family) -> Callable[[str, str], str]:
    indices: list[int] = \
        get_component_indices(family.son_birth, family.father_married, family.mother_married)
    def get_son_name(father_name: str, mother_name) -> str:
        return get_result_name(father_name, mother_name, indices)
    return get_son_name

def get_daughter_name_maker(family: Family) -> Callable[[str, str], str]:
    indices: list[int] = \
        get_component_indices(family.daughter_birth, family.father_married, family.mother_married)
    def get_daughter_name(father_name: str, mother_name) -> str:
        return get_result_name(father_name, mother_name, indices)
    return get_daughter_name

def get_child_name_maker(family: Family) -> Callable[[str, str, Gender], str]:
    def get_child_name(father_name: str, mother_name: str, child_gender: Gender) -> str:
        return (
            get_son_name_maker(family)(father_name, mother_name)
            if child_gender == "M"
            else get_daughter_name_maker(family)(father_name, mother_name)
        )
    return get_child_name

def get_husband_name_maker(family: Family) -> Callable[[str, str], str]:
    indices: list[int] = \
        get_component_indices(family.father_married, family.father_birth, family.mother_birth)
    def get_husband_name(husband_orig_name: str, wife_orig_name: str) -> str:
        return get_result_name(husband_orig_name, wife_orig_name, indices)
    return get_husband_name

def get_wife_name_maker(family: Family) -> Callable[[str, str], str]:
    indices: list[int] = \
        get_component_indices(family.mother_married, family.mother_birth, family.father_birth)
    def get_wife_name(wife_orig_name: str, husband_orig_name: str) -> str:
        return get_result_name(wife_orig_name, husband_orig_name, indices)
    return get_wife_name

def get_marital_name_maker(family: Family) -> Callable[[str, str, Gender], str]:
    def get_marital_name(
        original_name: str, spouse_original_name: str, self_gender: Gender
    ) -> str:
        return (
            get_husband_name_maker(family)(original_name, spouse_original_name)
            if self_gender == "M"
            else get_wife_name_maker(family)(original_name, spouse_original_name)
        )
    return get_marital_name

def stable_num_components_at_birth_maker(family: Family) -> Callable[[Gender], int]:
    def stable_num_components_at_birth(gender: Gender) -> int:
        return (
            len(get_components(family.father_birth))
            if gender == "M"
            else len(get_components(family.mother_birth))
        )
    return stable_num_components_at_birth

def import_scheme_from_family(family: Family, scheme_name: str | None = None) -> type[Scheme]:
    if scheme_name is None:
        scheme_name = "Scheme_" + random_name(set(), 1)
    return type(scheme_name, (Scheme,), {
        "get_child_name": staticmethod(get_child_name_maker(family)),
        "get_marital_name": staticmethod(get_marital_name_maker(family)),
        "stable_num_components_at_birth": staticmethod(
            stable_num_components_at_birth_maker(family)
        )
    })

def import_scheme_from_series(series: pd.Series, scheme_name: str | None = None) -> type[Scheme]:
    return import_scheme_from_family(Family(*series), scheme_name)

def import_schemes_from_dataframe(
    df: pd.DataFrame, scheme_names: Iterable[str] | None = None
) -> list[type[Scheme]]:
    if scheme_names is None:
        return [import_scheme_from_family(Family(*row)) for row in df.to_numpy()]
    else:
        return [
            import_scheme_from_family(Family(*row), scheme_name)
            for row, scheme_name in zip(df.to_numpy(), scheme_names)
        ]