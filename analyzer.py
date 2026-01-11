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
                t1, t2 = raw_tokens[i], raw_tokens[i+1]
                two_word = f"{t1} {t2}"
                found_type = None
                
                # Check for predefined phrases first (All categories)
                if two_word in KETERANGAN: found_type = "KETERANGAN"
                elif two_word in PREDIKAT: found_type = "PREDIKAT"
                elif two_word in AUX: found_type = "AUX"
                elif two_word in SUBJEK: found_type = "SUBJEK"
                elif two_word in OBJEK: found_type = "OBJEK"
                
                # Generalized logic: AUX + (SUBJEK/PREDIKAT/OBJEK/KETERANGAN)
                if not found_type and t1 in AUX:
                    # Priority 1: Prepositions (di/ka) -> KETERANGAN
                    if t1 in ["di", "ka", "dari", "pas"]:
                        found_type = "KETERANGAN"
                    # Priority 2: Time Markers (so/mo/da/ada) -> PREDIKAT (if t2 is likely predikat)
                    elif t1 in ["so", "mo", "da", "ada", "bolom", "blum", "bulum"]:
                        if t2 in PREDIKAT:
                            found_type = "PREDIKAT"
                        elif t2 in KETERANGAN:
                            found_type = "KETERANGAN"
                        elif t2 in SUBJEK:
                            # If it matches SUBJEK (like "da orang"), it might be a single token later
                            # or caught by phrase detection above. 
                            # If we are here, phrase detection missed it.
                            found_type = None # Let it fall through to single token logic
                        else:
                            found_type = "PREDIKAT" # Default for markers
                    # Priority 3: Fallback based on t2
                    elif t2 in PREDIKAT: found_type = "PREDIKAT"
                    elif t2 in KETERANGAN: found_type = "KETERANGAN"
                    elif t2 in SUBJEK: found_type = "SUBJEK"
                    elif t2 in OBJEK: found_type = "OBJEK"
                
                if found_type:
                    # Determine sub-token types
                    t1_type = "AUX" if t1 in AUX or t1 in ["di", "ka", "mo", "ada", "so"] else found_type
                    t2_type = "KETERANGAN" if found_type == "KETERANGAN" and t2 in OBJEK else found_type
                    
                    tokenized.append({
                        "text": two_word, 
                        "type": found_type,
                        "sub_tokens": [
                            {"text": t1, "type": t1_type},
                            {"text": t2, "type": t2_type}
                        ]
                    })
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
        
        # 1. Cek Tipe Kalimat & Ragam Dasar
        sentence_type = "Kalimat Berita (Deklaratif)"
        voice_type = "Aktif (Active)"
        
        # Cek Kalimat Tanya
        question_words = ["sapa", "apa", "dimane", "kiapa", "bagimana", "kapan", "barapa", "mana"]
        question_particles = ["kang", "dang", "sto"]
        is_question = any(t["text"] in question_words for t in tokenized) or \
                      (tokenized and tokenized[-1]["text"] in question_particles) or \
                      "?" in kalimat
        if is_question:
            sentence_type = "Kalimat Tanya (Interogatif)"
            
        # Cek Kalimat Perintah
        imperative_particles = ["jo", "mari", "coba"]
        is_imperative = (tokenized and tokenized[-1]["text"] == "jo") or \
                        any(t["text"] in imperative_particles for t in tokenized) or \
                        "!" in kalimat
        if is_imperative and not is_question:
            sentence_type = "Kalimat Perintah (Imperatif)"

        # Cek Ragam (Aktif/Pasif/Nominal)
        has_passive_marker = False
        for t in predikat_tokens:
            if t["text"].startswith("ta") or t["text"] == "dapa" or t["text"].startswith("ka"):
                has_passive_marker = True
        
        if has_passive_marker:
            voice_type = "Pasif (Passive)"
        elif not predikat_tokens:
            voice_type = "Nominal / Tidak Lengkap"
        else:
            voice_type = "Aktif (Active)"

        # 2. Time Marker & Prefix Ba- Logic
        aux_tokens = [t for t in tokenized if t["type"] == "AUX"]
        has_time_marker = any(t["text"] in ["so", "mo", "ada", "sedang", "akan", "sudah"] for t in aux_tokens)
        has_ba_prefix = any(t["text"].startswith("ba") for t in predikat_tokens)
        
        if has_time_marker or has_ba_prefix:
            marker = "Prefix ba-" if has_ba_prefix else f"Partikel '{aux_tokens[0]['text']}'" if aux_tokens else "Time Marker"
            analysis_report.append(f"✔ Kala/Waktu terdeteksi ({marker}).")
        elif predikat_tokens and voice_type == "Aktif (Active)":
            analysis_report.append("⚠ Peringatan: Absen penanda waktu (so/mo/ada/ba-).")

        # 3. Pattern 'pe' & Negation Logic
        for idx, t in enumerate(tokenized):
            if t["text"] == "pe":
                if idx > 0 and idx < len(tokenized)-1:
                    analysis_report.append(f"✔ Pola kepemilikan '{tokenized[idx-1]['text']} pe {tokenized[idx+1]['text']}' valid.")
                else:
                    analysis_report.append("✖ Pola 'pe' gantung/tidak lengkap.")
                    rule_violations += 1
            if t["text"] in ["tidak", "tak", "nggak", "gak"]:
                analysis_report.append(f"✖ Negasi '{t['text']}' tidak baku.")
                recommendations.append(f"Ganti '{t['text']}' dengan 'nyanda' atau 'nda'.")
                rule_violations += 1

        # 4. SPOK sequence validation
        seq_tokens = [t for t in tokenized if t["type"] in ["SUBJEK", "PREDIKAT", "OBJEK", "KETERANGAN"]]
        seq_types = [t["type"] for t in seq_tokens]
        
        if not subjek_tokens or not predikat_tokens:
            if not subjek_tokens and not predikat_tokens:
                if voice_type != "Nominal / Tidak Lengkap":
                    analysis_report.append("✖ Struktur tidak ditemukan (Harus ada Subjek dan Predikat).")
                    rule_violations += 1
            elif not subjek_tokens:
                analysis_report.append("✖ Subjek tidak ditemukan.")
                rule_violations += 1
            else:
                analysis_report.append("✖ Predikat tidak ditemukan.")
                rule_violations += 1
        else:
            if voice_type == "Aktif (Active)":
                s_idx = seq_types.index("SUBJEK") if "SUBJEK" in seq_types else -1
                p_idx = seq_types.index("PREDIKAT") if "PREDIKAT" in seq_types else -1
                o_idx = seq_types.index("OBJEK") if "OBJEK" in seq_types else -1
                
                if p_idx < s_idx:
                    analysis_report.append(f"✖ Urutan salah: Predikat '{seq_tokens[p_idx]['text']}' mendahului Subjek '{seq_tokens[s_idx]['text']}'.")
                    rule_violations += 1
                elif o_idx != -1 and o_idx < p_idx:
                    analysis_report.append(f"✖ Urutan salah: Objek '{seq_tokens[o_idx]['text']}' mendahului Predikat '{seq_tokens[p_idx]['text']}'.")
                    rule_violations += 1
                else:
                    analysis_report.append("✔ Urutan SPOK valid (Kalimat Aktif).")
            elif voice_type == "Pasif (Passive)":
                analysis_report.append("✔ Urutan valid (Kalimat Pasif).")

        # Pronoun Check
        invalid_pronouns = {"saya": "kita", "aku": "kita", "anda": "ngana", "kamu": "ngana", "mereka": "dorang", "kami": "torang"}
        for s in subjek_tokens:
             if s["text"] in invalid_pronouns:
                replacement = invalid_pronouns[s["text"]]
                analysis_report.append(f"✖ Kata ganti formal: '{s['text']}'.")
                recommendations.append(f"Ganti '{s['text']}' dengan '{replacement}' (Standard BMM).")
                rule_violations += 1

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
            # Replace any non-alphanumeric character with underscore
            clean_text = re.sub(r'[^a-zA-Z0-9]', '_', text)
            # Ensure it doesn't start with a number (CSS selector safety)
            return f"{prefix}_{clean_text}_{idx}"

        TYPE_LABELS = { # Tier 1: Full Names
            "SUBJEK": "Subjek S", "AUX": "Kata Bantu Aux", "PREDIKAT": "Predikat P", 
            "OBJEK": "Objek O", "KETERANGAN": "Keterangan K", "PARTIKEL": "Partikel Pel",
            "POSSESSIVE": "Possessive", "UNKNOWN": "Unknown"
        }
        
        ABBR_LABELS = { # Tier 2/3: Abbreviations
            "SUBJEK": "S", "AUX": "Aux", "PREDIKAT": "P", 
            "OBJEK": "O", "KETERANGAN": "K", "PARTIKEL": "Pel",
            "POSSESSIVE": "Poss", "UNKNOWN": "?"
        }

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
                
                if "sub_tokens" in t:
                    # Intermediate Phrase Node
                    phrase_node_id = f"PHRASE_{word_id}"
                    mermaid_lines.append(f"{cat_id} --> {phrase_node_id}(\"{t['text']}\"):::phrase")
                    
                    sub_types_abbr = []
                    for s_idx, st in enumerate(t["sub_tokens"]):
                        sub_id = safe_id(f"{phrase_node_id}_SUB", st['text'], s_idx)
                        st_label = ABBR_LABELS.get(st['type'], st['type'])
                        mermaid_lines.append(f"{phrase_node_id} --> {sub_id}[\"{st['text']} ({st_label})\"]:::word")
                        sub_types_abbr.append(st_label)
                    
                    # Derivation split using abbreviations for Tier 2+
                    derivation.append(f"{step_counter}. {TYPE_LABELS.get(type_code, type_code)} → {' '.join(sub_types_abbr)}")
                    step_counter += 1
                    for s_idx, st in enumerate(t["sub_tokens"]):
                        st_label = ABBR_LABELS.get(st['type'], st['type'])
                        derivation.append(f"{step_counter}. {st_label} → '{st['text']}'")
                        step_counter += 1
                else:
                    mermaid_lines.append(f"{cat_id} --> {word_id}[\"{t['text']}\"]:::word")
                    derivation.append(f"{step_counter}. {TYPE_LABELS.get(type_code, type_code)} → '{t['text']}'")
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
        mermaid_lines.append("classDef phrase fill:#fff7ed,stroke:#f97316,stroke-width:2px,color:#9a3412,rx:8,ry:8;")
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
