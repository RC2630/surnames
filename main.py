from schemes import *

if __name__ == "__main__":
    scheme_list: list[type[Scheme]] = [
        value for value in globals().values()
        if isinstance(value, type) and issubclass(value, Scheme) and value is not Scheme
    ]
    padding_length: int = max(len(scheme.__name__) for scheme in scheme_list)
    for scheme in scheme_list:
        scores: list[float] = evaluate_scheme(scheme)
        print(f"{scheme.__name__.rjust(padding_length)}: {sum(scores):.2f} -> "
              f"[{', '.join(f'{score:.2f}' for score in scores)}]")