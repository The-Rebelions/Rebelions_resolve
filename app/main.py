from app.core.config import load_config
from app.inference.engine import InferenceEngine


def main():
    config = load_config()

    engine = InferenceEngine(
        model_path=config["model"]["path"],
        llama_path=config["runtime"]["executable"],
        context_size=config["model"]["context_size"],
        max_tokens=config["model"]["max_tokens"],
        temperature=config["model"]["temperature"],
        gpu_layers=config["runtime"]["gpu_layers"],
    )

    print("Local Code AI")
    print("=============")

    prompt = input("You: ")

    response = engine.generate(prompt)

    print("\nAI:")
    print(response)


if __name__ == "__main__":
    main()