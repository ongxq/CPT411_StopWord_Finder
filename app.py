from flask import Flask, request, jsonify,render_template

from flask_cors import CORS
import re
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")
# =========================
# DFA CLASS
# =========================
class DFA:
    def __init__(self):
        self.transitions = {}
        self.accept_states = set()
        self.start_state = "q0"
        self.trap_state = "TRAP"

    def add_transition(self, state, char, next_state):
        self.transitions[(state, char)] = next_state

    def set_accept(self, state):
        self.accept_states.add(state)

    def run(self, word):
        state = self.start_state

        buffer_trace = []
        progressive_paths = []

        current = ""
        path = ["q0"]   # start from q0

        for char in word:
            current += char

            key = (state, char)

            if key in self.transitions:
                state = self.transitions[key]
            else:
                state = self.trap_state

            # update path AFTER transition
            path.append(state)

            # store buffer
            buffer_trace.append(current)

            # store progressive path
            progressive_paths.append(" → ".join(path))

            # STOP if trap
            if state == "TRAP":
                break

        return {
            "accepted": state in self.accept_states,
            "buffer": buffer_trace,
            "paths": progressive_paths
        }
# =========================
# BUILD DFA (CLEAN STATES)
# =========================
# =========================
# BUILD DFA
# =========================
dfa = DFA()

# --- "a"
dfa.add_transition("q0", "a", "q1")
dfa.set_accept("q1")

# --- "and"
dfa.add_transition("q0", "a", "q1")
dfa.add_transition("q1", "n", "q2")
dfa.add_transition("q2", "d", "q3")
dfa.set_accept("q3")

# --- "are"
dfa.add_transition("q0", "a", "q1")
dfa.add_transition("q1", "r", "q4")
dfa.add_transition("q4", "e", "q5")
dfa.set_accept("q5")

# --- "as"
dfa.add_transition("q0", "a", "q1")
dfa.add_transition("q1", "s", "q6")
dfa.set_accept("q6")


# --- "for"
dfa.add_transition("q0", "f", "q7")
dfa.add_transition("q7", "o", "q8")
dfa.add_transition("q8", "r", "q9")
dfa.set_accept("q9")

# --- "he"
dfa.add_transition("q0", "h", "q10")
dfa.add_transition("q10", "e", "q11")
dfa.set_accept("q11")

# --- "his"
dfa.add_transition("q0", "h", "q10")
dfa.add_transition("q10", "i", "q12")
dfa.add_transition("q12", "s", "q13")
dfa.set_accept("q13")

# --- "i"
dfa.add_transition("q0", "i", "q14")
dfa.set_accept("q14")

# --- "in"
dfa.add_transition("q0", "i", "q14")
dfa.add_transition("q14", "n", "q15")
dfa.set_accept("q15")

# --- "is"
dfa.add_transition("q0", "i", "q14")
dfa.add_transition("q14", "s", "q16")
dfa.set_accept("q16")

# --- "it"
dfa.add_transition("q0", "i", "q14")
dfa.add_transition("q14", "t", "q17")
dfa.set_accept("q17")

# --- "of"
dfa.add_transition("q0", "o", "q18")
dfa.add_transition("q18", "f", "q19")
dfa.set_accept("q19")

# --- "on"
dfa.add_transition("q0", "o", "q18")
dfa.add_transition("q18", "n", "q20")
dfa.set_accept("q20")


# --- "that"
dfa.add_transition("q0", "t", "q21")
dfa.add_transition("q21", "h", "q22")
dfa.add_transition("q22", "a", "q23")
dfa.add_transition("q23", "t", "q24")
dfa.set_accept("q24")

# --- "they"
dfa.add_transition("q0", "t", "q21")
dfa.add_transition("q21", "h", "q22")
dfa.add_transition("q22", "e", "q25")
dfa.add_transition("q25", "y", "q26")
dfa.set_accept("q26")

# --- "to"
dfa.add_transition("q0", "t", "q21")
dfa.add_transition("q21", "o", "q27")
dfa.set_accept("q27")

# --- "was"
dfa.add_transition("q0", "w", "q28")
dfa.add_transition("q28", "a", "q29")
dfa.add_transition("q29", "s", "q30")
dfa.set_accept("q30")

# --- "with"
dfa.add_transition("q0", "w", "q28")
dfa.add_transition("q28", "i", "q31")
dfa.add_transition("q31", "t", "q32")
dfa.add_transition("q32", "h", "q33")
dfa.set_accept("q33")

# --- "you"
dfa.add_transition("q0", "y", "q34")
dfa.add_transition("q34", "o", "q35")
dfa.add_transition("q35", "u", "q36")
dfa.set_accept("q36")


# =========================
# TEXT PROCESSING
# =========================
def process_text(text):
    words = re.findall(r'\b\w+\b', text.lower())

    results = []
    counts = {}
    accepted_counts = {}
    highlighted = []

    for i, word in enumerate(words, start=1):
        result = dfa.run(word)

        counts[word] = counts.get(word, 0) + 1
        status = "ACCEPT" if result["accepted"] else "REJECT"

         # ✅ count ONLY accepted words
        if result["accepted"]:
            accepted_counts[word] = accepted_counts.get(word, 0) + 1

        results.append({
            "word": word,
            "position": i,
            "status": status,
            "buffer": result["buffer"],
            "paths": result["paths"]
            #"path": " → ".join(result["path"]),
            #"trace": result["trace"]   # 👈 ADD THIS
        })

        if result["accepted"]:
            highlighted.append(f"<span class='highlight'>{word}</span>")
        else:
            highlighted.append(word)

    return results, counts,accepted_counts, " ".join(highlighted)

# =========================
# API
# =========================
@app.route("/process", methods=["POST"])
def process():
    data = request.json
    text = data["text"]

    results, counts, accepted_counts, highlighted = process_text(text)

    return jsonify({
        "results": results,
        "counts": counts,
        "accepted_counts": accepted_counts,
        "highlighted": highlighted
    })

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)




