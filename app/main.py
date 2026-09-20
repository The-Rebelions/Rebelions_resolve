from app.core.config import load_config
from app.inference.engine import InferenceEngine
from app.verification.code import CodeVerifier, VerificationError
from app.verification.extractor import CodeExtractionError, CodeExtractor


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

    extractor = CodeExtractor()
    verifier = CodeVerifier()

    print("Local Code AI")
    print("=============")

    prompt = input("You: ")

    response,performance = engine.generate(prompt)

    try:
        code = extractor.extract_python(response)
        verifier.verify_python_syntax(code)

        print("\nAI:")
        print(code)
        print("\nVerification: PASSED")

        if performance:
                    print("\nPerformance:")
                    print(
                        f"Prompt: {performance['prompt_tokens_per_second']:.1f} t/s"
                    )
                    print(
                        f"Generation: {performance['generation_tokens_per_second']:.1f} t/s"
                    )

    except (CodeExtractionError, VerificationError) as error:
        print("\nAI:")
        print(response)
        print("\nVerification: FAILED")
        print(error)


if __name__ == "__main__":
    main()