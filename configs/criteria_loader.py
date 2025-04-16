import yaml
import os

def load_criteria(file_path="configs/job_criteria.yaml"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Criteria file not found at {file_path}")

    with open(file_path, "r") as f:
        config = yaml.safe_load(f)

    return config["job_preferences"]

# Example usage
if __name__ == "__main__":
    prefs = load_criteria()
    print("Target job titles:", prefs["titles"])
    print("Required skills:", prefs["required_skills"])
    print("Excluded titles:", prefs["exclude"]["titles"])
