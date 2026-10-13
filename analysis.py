import pandas as pd
from enumerate import *

# ----------------------------------------------------------------------

df = pd.read_csv("data/schemes.csv")
len(df)

# ----------------------------------------------------------------------

df.head()

# ----------------------------------------------------------------------

score_columns: list[str] = [
    "husband_wife", "brother_sister",
    "brother_brother", "sister_sister",
    "son_father", "daughter_father",
    "son_mother", "daughter_mother"
]

df["score"] = df.apply(lambda row: row[score_columns].sum(), axis = 1)
df.head()

# ----------------------------------------------------------------------

df.score.max()

# ----------------------------------------------------------------------

df.groupby("score")[["scheme"]].count().rename(columns = dict(scheme = "num_schemes"))

# ----------------------------------------------------------------------

len(df[score_columns].drop_duplicates())

# ----------------------------------------------------------------------

df[df.score == 6.25]

# ----------------------------------------------------------------------

distinct_scores: pd.DataFrame = (
    df.groupby(score_columns, as_index = False)
    .scheme.count()
    .sort_values("scheme", ascending = False) # type: ignore
)

distinct_scores.head()

# ----------------------------------------------------------------------

distinct_scores.scheme.describe()

# ----------------------------------------------------------------------

print(list(enumerate(distinct_scores.scheme.head(30))))

# ----------------------------------------------------------------------

schemes: list[type[Scheme]] = \
    import_schemes_from_dataframe(df.loc[:, Family._fields], df.scheme) # type: ignore

[scheme.__name__ for scheme in schemes[:5]]

# ----------------------------------------------------------------------

target_family = Family(
    father_birth = "A-B",
    father_married = "A-D",
    mother_birth = "C-D",
    mother_married = "A-D",
    son_birth = "A-D",
    daughter_birth = "A-D"
)

if any(
    (target_index := i) == i and export_scheme_to_family(scheme) == target_family
    for i, scheme in enumerate(schemes)
):
    print(target_index)

# ----------------------------------------------------------------------

df.iloc[target_index]

# ----------------------------------------------------------------------

df[df.score == 6]

# ----------------------------------------------------------------------

from schemes import *

schemes: set[type[Scheme]] = {
    value for value in globals().values()
    if isinstance(value, type) and issubclass(value, Scheme) and value is not Scheme
    and not value.__name__.startswith("Scheme_")
}

schemes

# ----------------------------------------------------------------------

COLUMNS: list[str] = list(Family._fields)
VALUES: list[list[str]] = [list(export_scheme_to_family(scheme)) for scheme in schemes]

manual_schemes: pd.DataFrame = df[df.set_index(COLUMNS).index.isin(VALUES)]
manual_schemes

# ----------------------------------------------------------------------

manual_schemes["manual"] = [[] for i in range(len(manual_schemes))]

for i in manual_schemes.index:
    row_scheme: type[Scheme] = import_scheme_from_series(manual_schemes.loc[i, COLUMNS]) # type: ignore
    for scheme in schemes:
        if export_scheme_to_family(scheme) == export_scheme_to_family(row_scheme):
            manual_schemes.loc[i, "manual"].append(scheme.__name__)

manual_schemes