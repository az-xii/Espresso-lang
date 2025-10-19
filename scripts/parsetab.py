
MOD_MAP: dict = {
    1: "private",
    2: "public",
    3: "protected",
    4: "const",
    5: "constexpr",
    6: "consteval",
    7: "static",
    8: "abstract",
    9: "override",
    0: "virtual"
}

for v in MOD_MAP.values():
   print(v)