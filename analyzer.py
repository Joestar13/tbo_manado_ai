import re
import difflib
from data import SUBJEK, AUX, PREDIKAT, OBJEK, KETERANGAN, PARTIKEL, POSSESSIVE

ALL_WORDS = set(SUBJEK) | set(AUX) | set(PREDIKAT) | set(OBJEK) | set(KETERANGAN) | set(PARTIKEL) | set(POSSESSIVE)

class ManadoAnalyzer:
    def analyze(self, kalimat: str) -> dict:
        clean_kalimat = re.sub(r'[^\w\s\-]', '', kalimat.lower())
        raw_tokens = clean_kalimat.split()
        
        tokenized = []
        suggestions = {}
        
        i = 0
        while i < len(raw_tokens):
            t = raw_tokens[i]
            
            if i + 1 < len(raw_tokens):
                two_word = f"{t} {raw_tokens[i+1]}"
                if two_word in KETERANGAN:
                    tokenized.append({"text": two_word, "type": "KETERANGAN"})
                    i += 2
                    continue
            
            if t in SUBJEK: type_ = "SUBJEK"
            elif t in AUX: type_ = "AUX"
            elif t in PREDIKAT: type_ = "PREDIKAT"
            elif t in OBJEK: type_ = "OBJEK"
            elif t in KETERANGAN: type_ = "KETERANGAN"
            elif t in PARTIKEL: type_ = "PARTIKEL"
            elif t in POSSESSIVE: type_ = "POSSESSIVE"
            elif (t.startswith("ba") or t.startswith("ta") or t.startswith("ma")) and len(t) > 3:
                type_ = "PREDIKAT"
            else:
                type_ = "UNKNOWN"
                # Ensure ALL_WORDS is a list for difflib
                matches = difflib.get_close_matches(t, sorted(list(ALL_WORDS)), n=3, cutoff=0.75)
                if matches:
                    suggestions[t] = matches

            tokenized.append({"text": t, "type": type_})
            i += 1

        analysis_report = []
        recommendations = []
        rule_violations = 0
        
        subjek_tokens = [t for t in tokenized if t["type"] == "SUBJEK"]
        predikat_tokens = [t for t in tokenized if t["type"] == "PREDIKAT"]
        
        if not subjek_tokens or not predikat_tokens:
            analysis_report.append("✖ Struktur tidak lengkap (Minimal S + P).")
            rule_violations += 1
        else:
            invalid_pronouns = {"saya": "kita", "aku": "kita", "anda": "ngana", "kamu": "ngana", "mereka": "dorang", "kami": "torang"}
            for s in subjek_tokens:
                if s["text"] in invalid_pronouns:
                    replacement = invalid_pronouns[s["text"]]
                    analysis_report.append(f"✖ Kata ganti formal: '{s['text']}'.")
                    recommendations.append(f"Ganti '{s['text']}' dengan '{replacement}' (Standard BMM).")
                    rule_violations += 1
                else:
                    analysis_report.append(f"✔ Subjek '{s['text']}' valid.")

        aux_tokens = [t for t in tokenized if t["type"] == "AUX"]
        has_time_marker = any(t["text"] in ["so", "mo", "ada", "sedang", "akan", "sudah"] for t in aux_tokens)
        has_ba_prefix = any(t["text"].startswith("ba") for t in predikat_tokens)
        
        if has_time_marker or has_ba_prefix:
            marker = "Prefix ba-" if has_ba_prefix else f"Partikel '{aux_tokens[0]['text']}'" if aux_tokens else "Time Marker"
            analysis_report.append(f"✔ Kala/Waktu terdeteksi ({marker}).")
        else:
            if predikat_tokens:
                analysis_report.append("⚠ Peringatan: Absen penanda waktu (so/mo/ada/ba-).")
        
        for idx, t in enumerate(tokenized):
            if t["text"] == "pe":
                if idx > 0 and idx < len(tokenized)-1:
                    analysis_report.append(f"✔ Pola kepemilikan '{tokenized[idx-1]['text']} pe {tokenized[idx+1]['text']}' valid.")
                else:
                    analysis_report.append("✖ Pola 'pe' gantung/tidak lengkap.")
                    rule_violations += 1
        
        for t in tokenized:
            if t["text"] in ["tidak", "tak", "nggak", "gak"]:
                analysis_report.append(f"✖ Negasi '{t['text']}' tidak baku.")
                recommendations.append(f"Ganti '{t['text']}' dengan 'nyanda' atau 'nda'.")
                rule_violations += 1
        
        # DETEKSI TIPE KALIMAT & RAGAM (MOVED HERE - BEFORE message_html)
        sentence_type = "Kalimat Berita (Deklaratif)"
        voice_type = "Aktif (Active)"
        
        # 1. Cek Kalimat Tanya
        question_words = ["sapa", "apa", "dimane", "kiapa", "bagimana", "kapan", "barapa", "mana"]
        question_particles = ["kang", "dang", "sto"]
        is_question = any(t["text"] in question_words for t in tokenized) or \
                      (tokenized and tokenized[-1]["text"] in question_particles) or \
                      "?" in kalimat
                      
        if is_question:
            sentence_type = "Kalimat Tanya (Interogatif)"
            
        # 2. Cek Kalimat Perintah
        imperative_particles = ["jo", "mari", "coba"]
        is_imperative = (tokenized and tokenized[-1]["text"] == "jo") or \
                        any(t["text"] in imperative_particles for t in tokenized) or \
                        "!" in kalimat
                        
        if is_imperative and not is_question:
            sentence_type = "Kalimat Perintah (Imperatif)"

        # 3. Cek Ragam (Aktif/Pasif/Nominal)
        has_passive_marker = False
        
        for t in predikat_tokens:
            if t["text"].startswith("ta") or t["text"] == "dapa" or t["text"].startswith("ka"):
                has_passive_marker = True
        
        if has_passive_marker:
            voice_type = "Pasif (Passive)"
        elif not predikat_tokens:
             voice_type = "Nominal / Tidak Lengkap"

        # Add to report BEFORE generating HTML
        analysis_report.append(f"ℹ Tipe: {sentence_type} | Ragam: {voice_type}")
        
        is_valid = rule_violations == 0
        message_html = "<br/>".join(analysis_report)
        if recommendations:
            message_html += "<br/><br/><b>Rekomendasi Perbaikan:</b><br/>" + "<br/>".join(recommendations)

        # DERIVATION & MERMAID
        derivation = []
        mermaid_lines = ["graph TD"]
        mermaid_lines.append("ROOT[Struktur Kalimat SPOK]")
        
        def safe_id(prefix, text, idx):
            clean_text = re.sub(r'[^a-zA-Z0-9]', '_', text)
            return f"{prefix}_{clean_text}_{idx}"

        structure_map = [
            ("SUBJEK", subjek_tokens, "Subjek S"),
            ("AUX", aux_tokens, "Kata Bantu Aux"),
            ("PREDIKAT", predikat_tokens, "Predikat P"),
            ("OBJEK", [t for t in tokenized if t["type"] == "OBJEK"], "Objek O"),
            ("KETERANGAN", [t for t in tokenized if t["type"] == "KETERANGAN"], "Keterangan K"),
            ("PARTIKEL", [t for t in tokenized if t["type"] == "PARTIKEL"], "Partikel Pel")
        ]
        
        found_components = [item[0] for item in structure_map if item[1]]
        if not found_components:
             base_rule = "S → ?"
        else:
             base_rule = "S → " + " ".join(found_components)
        
        derivation.append(f"1. {base_rule}")
        
        step_counter = 2
        
        for type_code, tokens, label in structure_map:
            if not tokens:
                continue
                
            cat_id = f"NODE_{type_code}"
            mermaid_lines.append(f"ROOT --> {cat_id}(\"{label}\"):::grammar")
            
            for idx, t in enumerate(tokens):
                word_id = safe_id(type_code, t['text'], idx)
                mermaid_lines.append(f"{cat_id} --> {word_id}[\"{t['text']}\"]:::word")
                
                derivation.append(f"{step_counter}. {type_code} → '{t['text']}'")
                step_counter += 1

        # TRANSLASI (INDONESIA)
        ALL_DICTS = {**SUBJEK, **AUX, **PREDIKAT, **OBJEK, **KETERANGAN, **PARTIKEL, **POSSESSIVE}
        
        translated_words = []
        for t in tokenized:
            word = t["text"]
            if word in ALL_DICTS:
                translated_words.append(ALL_DICTS[word])
            else:
                translated_words.append(word)

        translation = " ".join(translated_words)
        translation = translation.capitalize()

        # Add Styling
        mermaid_lines.append("classDef default fill:#fff,stroke:#ec4899,stroke-width:2px,rx:10,ry:10,color:#831843,font-family:'Outfit';")
        mermaid_lines.append("classDef root fill:#831843,stroke:#ec4899,stroke-width:4px,color:#fff,rx:15,ry:15;")
        mermaid_lines.append("classDef grammar fill:#fdf2f8,stroke:#ec4899,stroke-width:2px,color:#831843;")
        mermaid_lines.append("classDef word fill:#fff1f2,stroke:#db2777,stroke-width:1px,stroke-dasharray: 5 5,color:#be185d;")
        
        # Apply classes
        # ROOT is implicitly defined earlier, we append class match
        mermaid_lines.append("class ROOT root;")
        
        return {
            "valid_sintaks": is_valid,
            "message": message_html,
            "tokens": tokenized,
            "suggestions": suggestions,
            "parse_tree": {}, 
            "derivation": derivation,
            "mermaid": "\n".join(mermaid_lines),
            "translation": translation 
        }
