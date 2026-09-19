from app.verification.code import CodeVerifier, VerificationError
from app.verification.extractor import CodeExtractor

def main():
    text = """Here is the function:

    ```python
    def broken(a, b):
    return a + b
    ```

    This function adds two numbers."""


    extractor = CodeExtractor()
    verifier = CodeVerifier()

    code = extractor.extract_python(text)

    print("EXTRACTED CODE:")
    print(code)
    print("VERIFICATION:", verifier.verify_python_syntax(code))
if __name__ == "__main__":
    main()
