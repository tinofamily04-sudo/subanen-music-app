from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

import os
import subprocess
import whisper
import time
import re


# -------------------------
# Config
# -------------------------
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}

app = Flask(__name__)

from flask_cors import CORS

CORS(app, resources={
    r"/*": {
        "origins": [
            "https://subanen-music-app-1.onrender.com",
            "https://subanen-app.onrender.com",
            "http://localhost:3000"
        ]
    }
})

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------------------------
# Load Whisper once
# -------------------------
print("Loading Whisper model...")
model = whisper.load_model("tiny")
print("Whisper loaded.")

# -------------------------
# Subanen Dictionary (CLEANED)
# -------------------------
SUBANEN_DICTIONARY = {
    # PHRASES FIRST
    "i love you": "dilamin uh yaa",
    "i know": "sunan uh ra",
    "you know": "sunan mo ra",
    "only you": "yaa lak",
    "all of you": "lonin nyo",
    "i need you": "kinahanglan uh yaa",
    "i want you": "gusto yaa",
    "i remember you": "hinumdum yaa",
    "do you love me": "dilamin yaa inan",
    "please stay": "palihog pabilin",
    "come back to me": "balik inan",
    "i can't forget you": "dili makalimot yaa",
    "you are beautiful": "matahum ah",
    "you are special": "espesyal ah",
    "hold on": "padayon lang",
    "don't cry": "ayaw hilak",
    "i feel you": "bati yaa",
    "listen to me": "paminaw dinan",
    "i will wait": "ma gilat uh ra",
    "don't be afraid": "ayaw kahadlok",
    "i'm here": "kini uh ra",
    "you are here": "rini ah ra",
    "stay strong": "kusgan pabilin",
    "never leave": "dili gayud biya",
    "always here": "permi rini",
    "i am yours": "akoa yaa",
    "you are mine forever": "yaa dinan hangtod",
    "stay by my side": "pabilin daplin inan",
    "don't go": "ayaw adto",
    "come with me": "uban inan",
    "i still love you": "padayon dilamin yaa",
    "i can feel it": "bati a kini",
    "you changed me": "giusab a yaa",
    "i gave you everything": "gihatag tanan yaa",
    "you broke my heart": "guba kasingkasing dinan",
    "i'm lost": "mi biling uh",
    "find me": "paningaw mo inan",
    "follow me": "sunod inan",
    "don't look back": "di ah glingi talyuran",
    "this is love": "kini dilamin",
    "this is real": "kini matud",
    "you and me": "yaa ug inan",
    "me and you": "inan ug yaa",
    "we are together": "uban kita",
    "we will stay": "pabilin kita",
    "i belong to you": "akoa yaa hangtod",
    "you belong to me": "yaa dinan hangtod",
    "don't hurt me": "ayaw pasakiti inan",
    "you make me happy": "yaa nagpasaya inan",
    "you make me cry": "yaa nagpa hilak inan",
    "i trust you": "salig a yaa",
    "i don't trust you": "dili a salig yaa",
    "i feel empty": "walay sulod bati a",
    "i feel alive": "buhi bati a",
    "you are far away": "yaa layo kaayo",
    "i hear your voice": "dungog a tingog yaa",
    "i see you in my dreams": "kita yaa sa damgo",
    "dream of me": "damgohi a",
    "i think of you": "hunahuna a yaa",
    "you never cared": "wala ka nagtagad",
    "i cared for you": "nagtagad a yaa",
    "why did you leave": "ngano biya yaa",
    "don't lie to me": "ayaw bakak inan",
    "tell me the truth": "sulti kamatuoran inan",
    "i will never forget": "dili gayud kalimot a",
    "i cannot let you go": "dili a makabiya yaa",
    "you are my reason": "yaa rason dinan",
    "i lost myself in you": "nawala a sa yaa",
    "you are my world": "yaa kalibutan dinan",
    "i was wrong": "sayop a",
    "you were right": "sakto yaa",
    "don't change": "ayaw usab",
    "stay the same": "pabilin pareho",
    "i feel broken": "bali bati a",
    "you healed me": "ayo yaa inan",
    "i'm still here waiting": "ania a naghulat",
    "don't forget me": "ayaw kalimot inan",
    "remember us": "hinumdum kita",
    "we were happy": "malipay kita",
    "we were wrong": "sayop kita",
    "love is pain": "dilamin kasakit",
    "love is real": "dilamin matud",
    "hold my hand": "kupot kamot inan",
    "look at me": "tan-aw inan",
    "don't ignore me": "ayaw balewala inan",
    "i feel your absence": "bati a kawalay yaa",
    "you are my silence": "yaa hilom dinan",
    "my soul is yours": "kalag dinan yaa",
    "don't leave me alone": "ayaw biya inan usa",
    "i still believe in us": "padayon tuod a kita",
    "we are fading away": "hinay nawala kita",
    "you are my past": "yaa kagahapon dinan",
    "you are my future": "yaa ugma dinan",
    "i can't reach you": "dili a makaabot yaa",
    "you are slipping away": "hinay biya yaa",
    "i hear you in silence": "dungog a sa hilom yaa",
    "my heart calls you": "kasingkasing nagtawag yaa",
    "you live in me": "naa ka sulod dinan",
    "i'm drowning in love": "nalumos a dilamin",
    "don't let go of me": "ayaw buhian inan",
    "i am still yours": "akoa pa yaa",
    "you are still mine": "yaa pa dinan",
    "we were never meant to end": "dili kita katapusan",
    "cracked sky": "gisi langit",
    "burning horizon": "nasunog horizon",
    "silent ocean": "hilom dagat",
    "dark horizon": "ngitngit horizon",

    "floating light": "lutaw kahayag",
    "falling stars": "nahulog bituon",

    "empty heavens": "walay sulod langit",
    "crying sky": "naghilak langit",

    "shadow world": "kalibutan anino",
    "broken sunrise": "guba pagsubang",

    "lost horizon": "nawala horizon",
    "endless night": "walay katapusan gabii",

    "whispering wind": "hinay hangin nagsulti",
    "screaming wind": "singgit hangin",




    # WORDS
    "love": "dilamin",
    "you": "yaa",
    "me": "inan",
    "my": "dinan",
    "heart": "kasingkasing",
    "your": "dini-ah",

    "night": "gabii",
    "day": "adlaw",
    "no": "deen",
    "cause": "kay",
    "fine": "okay",
    

    "look": "tangian",
    "know": "sunan",
    "found": "minita",

    "back": "likod",
    "here": "rini",
    "there": "rito",

    "sleep": "tulog",
    "sing": "babat",

    "good": "masiba",
    "true": "matud",
    "for": "para",

    "water": "tubig",
    "blood": "dugo",
    "dog": "aso",
    "cat": "kuting",
    "fish": "sira",
    "horse": "kura",

    "drink": "inum",
    "eat": "kaon",
    "all": "lonin",

    "time": "oras",
    "problem": "problema",
    "beautiful": "matahum",
    "ugly": "bati",
    "strong": "ma sihig",
    "weak": "lubay",
    "mouth": "baba",
    "drawing": "bintingin",
    "in": "pasilid",
    "kicking": "sipa-in",
    "kidding": "biro",

    "voice": "tingog",
    "song": "babat",
    "music": "musika",
    "smart": "brait",

    "walk": "lakaw",
    "run": "dagan",
    "stand": "gindig",
    "sit": "ginghud",
    "mind": "gutik",

    "open": "abri",
    "close": "sirado",
    "out": "lyawa",
    

    "light": "kahayag",
    "dark": "ngitngit",

    "fire": "gapoy",
    "earth": "lupa",

    "friend": "higala",
    "enemy": "kuntra",

    "family": "pamilya",
    "child": "bata",
    "man": "lai",
    "woman": "glibon",

    "face": "mulo",
    "eyes": "mata",
    "hand": "kamit",

    "road": "dalan",
    "home": "balay",

    "far": "luyo",
    "near": "duol",

    "fast": "paspas",
    "slow": "mlumbat",

    "new": "bag-o",
    "old": "daan",

    "big": "dako",
    "small": "gamay",
    "spinning": "pa libit",

    "many": "malon",
    "few": "gamay",

    "because": "kay",
    "but": "apan",
    "and": "muha",

    "if": "ba",
    "then": "dayon",
    "crazy": "buneg",
    "hit": "mi sugat",

    "yes": "waa",
    "what": "alan",
    "what's": "alan",
    "no": "di",
    "shadow": "anino",
    "lightning": "kilat",
    "thunder": "dalugdog",
    "storm": "bagyo",
    "cloud": "panganod",
    "down": "dialim",
    "up": "ditas",
    "that": "hin",

    "firelight": "kahayag sa kalayo",
    "sunrise": "pagsubang adlaw",
    "sunset": "pagsalop adlaw",

    "whisper": "hinay pa talo",
    "what's going on": "alan mi hitabo",

    "path": "agianan",
    "journey": "panaw",
    "destination": "padulngan",
    "morning dew": "yamog buntag",
    "evening sky": "langit gabii",
    "dark clouds": "ngitngit panganod",
    "clear sky": "klaro langit",
    "you got my head": "ulo uh miha",

    "falling leaves": "nahulog dahon",
    "dry wind": "uga hangin",
    "soft wind": "hinay hangin",

    "river flow": "dagan suba",
    "deep ocean": "lalom dagat",

    "bright star": "hayag bituon",
    "lonely star": "usa bituon",
    "confused": "libog",
    "understanding": "pagsabot",
    "acceptance": "dawat",
    "rejection": "balibad",

    "absence": "kawalay",
    "presence": "anaa",

    "truthful": "matinud-anon",
    "dishonest": "dili matinud-anon",

    "attachment": "kapit",
    "detachment": "buhian",

    "yearning": "panggihanglan",
    "desire": "gusto",

    "faith": "pagtuo",
    "doubt": "duhaduha",
    "without": "da",

    "memory pain": "kasakit panumduman",
    "silent pain": "hilom kasakit",

    "deep love": "lalom dilamin",
    "lost love": "nawala dilamin",

    "fate": "kapalaran",
    "destiny": "tadhana",

    "broken trust": "guba salig",
    "strong bond": "kusgan koneksyon",
    "would i do": "balin uh ba",

    "loneliness inside": "sulod mingaw",

#imagery
    "endless sky": "walay katapusan langit",
    "falling rain": "nahulog ulan",
    "heavy rain": "kusog ulan",
    "stormy night": "bagyo gabii",

    "empty road": "walay sulod dalan",
    "long journey": "taas panaw",

    "fading light": "nawala kahayag",
    "burning sky": "nasunog langit",

    "quiet forest": "hilom lasang",
    "deep forest": "lalom lasang",

    "broken mirror": "guba salamin",
    "lost path": "nawala agianan",

    "soft touch": "hinay hikap",
    "cold wind": "bugnaw hangin",
    "fragile": "luya",
    "invisible": "dili makita",
    "endless": "walay katapusan",
    "infinite": "walay limit",

    "connection lost": "nawala koneksyon",
    "signal": "signal",
    "distance grows": "mohalayo",

    "emptiness": "kawalay sulod",
    "fulfillment": "kakompleto",

    "betrayal": "pagluib",
    "loyalty": "katapusan nga salig",

    "memory fades": "hinay mawala panumduman",
    "heart aches": "sakit kasingkasing",

    "hidden feelings": "tinago bati",
    "spoken feelings": "gipamulong bati",

    "eternal": "walay katapusan",
    "temporary": "temporaryo",

    "broken silence": "guba hilom",
    "heavy silence": "bug-at hilom",

    "cold heart": "bugnaw kasingkasing",
    "warm heart": "init kasingkasing",

    "lost voice": "nawala tingog",
    "fading memory": "hinay panumduman",





}

# -------------------------
# Helpers
# -------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------
# CLEAN TEXT (NEW)
# -------------------------
def clean_english_text(text):
    text = text.lower()

    # remove weird characters
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    # remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# -------------------------
# TRANSLATION ENGINE (FIXED)
# -------------------------
def translate_to_subanen(text):
    text = clean_english_text(text)

    # longest phrases first
    sorted_dict = sorted(SUBANEN_DICTIONARY.items(), key=lambda x: len(x[0]), reverse=True)

    for english, subanen in sorted_dict:
        pattern = r"\b" + re.escape(english) + r"\b"
        text = re.sub(pattern, subanen, text)

    return text


# -------------------------
# FORMAT LYRICS (NEW)
# -------------------------
def format_lyrics(text):
    words = text.split()
    lines = []

    for i in range(0, len(words), 8):
        line = " ".join(words[i:i+8])
        lines.append(line)

    return "\n".join(lines)


# -------------------------
# Home route
# -------------------------
@app.route('/')
def home():
    return "Backend is working!"


# -------------------------
# Upload route
# -------------------------
@app.route('/upload', methods=['POST'])
def upload_file():

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filename = f"{int(time.time())}_{secure_filename(file.filename)}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    print("Processing:", file_path)

    try:
        # STEP 1: Normalize Audio
        fixed_path = file_path + "_fixed.wav"

        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", file_path,
            "-ac", "1",
            "-ar", "16000",
            "-f", "wav",
            fixed_path
        ], check=True)

        print("Audio normalized")

        # STEP 2: Transcribe
        print("Running Whisper...")
        result = model.transcribe(fixed_path)
        extracted_lyrics = result.get("text", "").strip()

        print("Whisper output:", extracted_lyrics)

        if not extracted_lyrics:
            return jsonify({'error': 'No speech detected'}), 400

        # STEP 3: Translate
        print("Translating to Subanen...")

        translated = translate_to_subanen(extracted_lyrics)
        subanen_lyrics = format_lyrics(translated)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

    return jsonify({
        "original_lyrics": extracted_lyrics,
        "subanen_lyrics": subanen_lyrics,
        "filename": filename
    })


# -------------------------
# Download route
# -------------------------
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )


# -------------------------
# Run server
# -------------------------
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)