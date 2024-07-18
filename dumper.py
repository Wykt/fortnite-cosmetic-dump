from typing import Dict

import os
import json
import requests

FORTNITE_API = "https://fortnite-api.com/v2"
COSMETIC_ENDPOINT = f"{FORTNITE_API}/cosmetics/br?responseOptions=ignore_null"


def create_dump_dir():
    if not os.path.exists("dump"):
        os.mkdir("dump")


def query_cosmetic_api() -> dict:
    return requests.get(url=COSMETIC_ENDPOINT).json()


def get_cosmetic_type(cosmetic: dict) -> str:
    return cosmetic["type"]["backendValue"]


# Warning: this only gets variant styles, nothing else.
def get_cosmetic_variants(cosmetic: dict) -> list:
    variants = []

    if "variants" not in cosmetic:
        return variants

    for variant in cosmetic["variants"]:
        if "channel" not in variant:
            continue

        variant_type = variant["channel"]

        if variant_type != "Material" and variant_type != "ClothingColor":
            continue

        variant_options = variant["options"]
        for variant_option in variant_options:
            variants.append({
                "tag": variant_option["tag"],
                "name": variant_option.get("name", "no name provided"),
            })

    return variants


def write_file(cosmetic_dict: Dict[str, list]) -> None:
    for cosmetic_type, cosmetics in cosmetic_dict.items():
        with open(f"./dump/{cosmetic_type}.json", "w") as file:
            file.write(json.dumps(cosmetics, separators=(',', ':')))
            file.close()


def parse(response_cosmetics: dict):
    # Cosmetic type -> list of cosmetics
    cosmetics: Dict[str, list] = {}

    for response_cosmetic in response_cosmetics:
        cosmetic_type = get_cosmetic_type(response_cosmetic)
        cosmetic_id = response_cosmetic["id"]
        cosmetic_name = response_cosmetic["name"]
        cosmetic_variants = get_cosmetic_variants(response_cosmetic)

        cosmetics.setdefault(cosmetic_type, []).append(
            {
                "id": cosmetic_id,
                "name": cosmetic_name,
                "variants": cosmetic_variants,
            }
        )

    return cosmetics


def dump():
    create_dump_dir()
    response = query_cosmetic_api()

    if response["status"] != 200:
        raise Exception("unexpected status code while querying cosmetic api:", response["status"])

    cosmetics = response["data"]
    print("Found", len(cosmetics), "cosmetics")

    write_file(parse(cosmetics))


if __name__ == "__main__":
    dump()
