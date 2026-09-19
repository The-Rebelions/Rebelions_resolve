from app.core.config import load_config


def main():
    config = load_config()

    print("Application:", config["application"]["name"])
    print("Version:", config["application"]["version"])
    print("Model:", config["model"]["path"])


if __name__ == "__main__":
    main()