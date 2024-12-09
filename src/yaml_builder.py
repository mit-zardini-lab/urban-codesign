import yaml

from src.layout_logic import Layout, Tile


def generate_poset_file(layouts: list[Layout], output_file: str) -> None:
    """
    Generate a poset file from the given list of layouts in a chain format.

    Args:
        layouts: List of Layout objects.
        output_file: Path to the output poset file.
    """
    with open(output_file, "w") as file:
        file.write("poset {\n\t")
        file.write(" <= ".join(f"{layout.pretty_flat}" for layout in layouts))
        file.write("\n}\n")

    print(f"Poset file successfully written to {output_file}")

def generate_cost_yaml(layouts: list[Layout], output_file: str) -> None:
    """
    Generate a YAML file for the given list of Layout objects.

    Args:
        layouts: List of Layout objects.
        output_file: Path to the output YAML file.
    """
    yaml_data = {
        "F": ["`layout"],
        "R": ["Nat", "Nat", "Nat", "$", "Nat", "Int"],
        "implementations": {}
    }

    for layout in layouts:
        layout_data = {
            "f_max": [f"`layout: {layout.pretty_flat}"],
            "r_min": [
                f"{layout.pretty_flat.count("T")} Nat",
                f"{layout.pretty_flat.count("P")} Nat",
                f"{layout.pretty_flat.count("B")} Nat",
                f"{layout.cost_yearly} $",
                f"{layout.co2_cost_upfront} Nat",
                f"{layout.co2_absorption_yearly - layout.co2_cost_yearly} Int"
            ]
        }
        yaml_data["implementations"][layout.pretty_flat] = layout_data

    with open(output_file, "w") as file:
        yaml.dump(yaml_data, file, default_flow_style=False, sort_keys=False)

    print(f"YAML file successfully written to {output_file}")

def generate_quality_yaml(layouts: list[Layout], output_file: str) -> None:
    """
    Generate a YAML file for layouts with F, R, and implementations.

    Args:
        layouts: List of Layout objects.
        output_file: Path to the output YAML file.
    """
    yaml_data = {
        "F": ["dimensionless", "dimensionless"],
        "R": ["`layout"],
        "implementations": {}
    }

    for layout in layouts:
        yaml_data["implementations"][layout.pretty_flat] = {
            "f_max": [
                f"{layout.accessibility()} dimensionless",
                f"{layout.greenery()} dimensionless"
            ],
            "r_min": [
                f"`layout: {layout.pretty_flat}"
            ]
        }

    with open(output_file, "w") as file:
        yaml.dump(yaml_data, file, default_flow_style=False, sort_keys=False)

    print(f"YAML file successfully written to {output_file}")