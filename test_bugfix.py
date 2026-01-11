from analyzer import ManadoAnalyzer

analyzer = ManadoAnalyzer()
test_sentences = [
    "Kita di pasar",      # 'di pasar' should be KETERANGAN
    "Dia ka skolah",     # 'ka skolah' should be KETERANGAN
    "Torang mo makang",   # 'mo makang' should be PREDIKAT
    "Kita ambe nasi"     # 'nasi' should be OBJEK (individual)
]

for sentence in test_sentences:
    print(f"\n--- Testing: {sentence} ---")
    result = analyzer.analyze(sentence)
    print(f"Valid: {result['valid_sintaks']}")
    print("Tokens:")
    for t in result['tokens']:
        sub = f" (sub types: {[st['type'] for st in t['sub_tokens']]})" if "sub_tokens" in t else ""
        print(f"  - {t['text']} [{t['type']}]{sub}")
