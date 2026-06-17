import os
import random
import webbrowser
import numpy as np
import pandas as pd
from datetime import datetime
from collections import defaultdict
from flask import Flask, render_template, request, jsonify, session
import sklearn.cluster
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

os.environ['OMP_NUM_THREADS'] = '1'

app = Flask(__name__)
app.secret_key = 'bitecraft-secret-2026'

# ─── Dataset ──────────────────────────────────────────────────────────────────
MEAL_TIMES = ['Breakfast', 'Lunch', 'Hi-Tea', 'Dinner']

ITEMS = [
    # ── Breakfast ──────────────────────────────────────────────────────────────
    {"id": 1,  "name": "Paratha with Egg",       "meal": "Breakfast", "category": "Desi",    "price": 80,  "icon": "🫓", "tags": ["heavy","traditional"], "humor": "Classic desi breakfast = NASA-level fuel 🚀"},
    {"id": 2,  "name": "Halwa Puri",              "meal": "Breakfast", "category": "Desi",    "price": 120, "icon": "🍛", "tags": ["heavy","sweet"],       "humor": "The undisputed weekend champion 👑"},
    {"id": 3,  "name": "Nihari with Naan",        "meal": "Breakfast", "category": "Desi",    "price": 220, "icon": "🍲", "tags": ["heavy","spicy"],       "humor": "Start your morning like a champion 💪"},
    {"id": 4,  "name": "Omelette Roll",           "meal": "Breakfast", "category": "Western", "price": 90,  "icon": "🌯", "tags": ["light","quick"],       "humor": "The egg's ultimate glow-up 😎"},
    {"id": 5,  "name": "Cereal & Milk",           "meal": "Breakfast", "category": "Western", "price": 110, "icon": "🥣", "tags": ["light","quick"],       "humor": "A gym bro's morning ritual 🏋️"},
    {"id": 6,  "name": "Avocado Toast",           "meal": "Breakfast", "category": "Western", "price": 180, "icon": "🥑", "tags": ["light","trendy"],      "humor": "Trendy, tasty, and slightly overpriced 😂"},
    {"id": 7,  "name": "Aloo Paratha",            "meal": "Breakfast", "category": "Desi",    "price": 70,  "icon": "🫓", "tags": ["heavy","traditional"], "humor": "Potato perfection on a Monday 🥔"},
    {"id": 8,  "name": "French Toast",            "meal": "Breakfast", "category": "Western", "price": 100, "icon": "🍞", "tags": ["sweet","quick"],       "humor": "Double-decker sweetness in every bite 🗼"},
    {"id": 9,  "name": "Fruit Chaat",             "meal": "Breakfast", "category": "Healthy", "price": 130, "icon": "🍓", "tags": ["light","fresh"],       "humor": "Vitamin C superhero on your plate 🦸"},
    {"id": 10, "name": "Smoothie Bowl",           "meal": "Breakfast", "category": "Healthy", "price": 200, "icon": "🥣", "tags": ["light","trendy"],      "humor": "The breakfast that breaks Instagram 📸"},
    {"id": 11, "name": "Chana with Puri",         "meal": "Breakfast", "category": "Desi",    "price": 100, "icon": "🍛", "tags": ["heavy","spicy"],       "humor": "Lahore's unofficial national breakfast 🇵🇰"},
    {"id": 12, "name": "Pancakes",                "meal": "Breakfast", "category": "Western", "price": 150, "icon": "🥞", "tags": ["sweet","light"],       "humor": "Fluffy clouds you are allowed to eat 😍"},

    # ── Lunch ──────────────────────────────────────────────────────────────────
    {"id": 13, "name": "Chicken Biryani",         "meal": "Lunch",     "category": "Desi",    "price": 320, "icon": "🍚", "tags": ["heavy","spicy"],       "humor": "Friday's God-given right 🎉"},
    {"id": 14, "name": "Daal Chawal",             "meal": "Lunch",     "category": "Desi",    "price": 160, "icon": "🍱", "tags": ["light","vegetarian"],  "humor": "Home-cooked comfort in a bowl ❤️"},
    {"id": 15, "name": "Chicken Karahi",          "meal": "Lunch",     "category": "Desi",    "price": 450, "icon": "🥘", "tags": ["spicy","gravy"],       "humor": "Finger-licking guaranteed 🤌"},
    {"id": 16, "name": "Club Sandwich",           "meal": "Lunch",     "category": "Western", "price": 230, "icon": "🥪", "tags": ["light","quick"],       "humor": "The coolest lunch in the office 💼"},
    {"id": 17, "name": "Zinger Burger",           "meal": "Lunch",     "category": "Fast Food","price": 290, "icon": "🍔", "tags": ["heavy","crispy"],      "humor": "Diet? Never heard of it 🙈"},
    {"id": 18, "name": "Chow Mein",               "meal": "Lunch",     "category": "Chinese", "price": 250, "icon": "🍝", "tags": ["main","noodles"],      "humor": "Noodle happiness delivered 🥢"},
    {"id": 19, "name": "Mutton Karahi",           "meal": "Lunch",     "category": "Desi",    "price": 550, "icon": "🥘", "tags": ["spicy","heavy"],       "humor": "Worth every rupee of delicious guilt 💸"},
    {"id": 20, "name": "Caesar Salad",            "meal": "Lunch",     "category": "Healthy", "price": 200, "icon": "🥗", "tags": ["light","fresh"],       "humor": "Your gym trainer's dream meal 🥦"},
    {"id": 21, "name": "Fried Rice",              "meal": "Lunch",     "category": "Chinese", "price": 240, "icon": "🍚", "tags": ["main","rice"],         "humor": "Rice, but make it fashion 🎨"},
    {"id": 22, "name": "Beef Burger",             "meal": "Lunch",     "category": "Fast Food","price": 260, "icon": "🍔", "tags": ["heavy","grilled"],     "humor": "Moo-ve over — burger time! 🐄"},
    {"id": 23, "name": "Haleem",                  "meal": "Lunch",     "category": "Desi",    "price": 280, "icon": "🍲", "tags": ["heavy","traditional"], "humor": "One bowl = food coma guaranteed 😴"},
    {"id": 24, "name": "Vegan Wrap",              "meal": "Lunch",     "category": "Healthy", "price": 250, "icon": "🌯", "tags": ["light","vegan"],       "humor": "Plants wrapped lovingly in plants 🌱"},

    # ── Hi-Tea ─────────────────────────────────────────────────────────────────
    {"id": 25, "name": "Samosa",                  "meal": "Hi-Tea",    "category": "Snacks",  "price": 30,  "icon": "🔺", "tags": ["crispy","snack"],      "humor": "Tea's best friend for life 🤝"},
    {"id": 26, "name": "Pakora",                  "meal": "Hi-Tea",    "category": "Snacks",  "price": 50,  "icon": "🧆", "tags": ["crispy","spicy"],      "humor": "Rainy day essential — life sorted ☔"},
    {"id": 27, "name": "Sandwiches Platter",      "meal": "Hi-Tea",    "category": "Western", "price": 300, "icon": "🥪", "tags": ["light","fancy"],       "humor": "The MVP of every fancy gathering 👸"},
    {"id": 28, "name": "Pastry",                  "meal": "Hi-Tea",    "category": "Bakery",  "price": 120, "icon": "🧁", "tags": ["sweet","baked"],       "humor": "Happiness compressed into one bite 💕"},
    {"id": 29, "name": "Cream Roll",              "meal": "Hi-Tea",    "category": "Bakery",  "price": 80,  "icon": "🥐", "tags": ["sweet","creamy"],      "humor": "A whole ocean of cream inside 🌊"},
    {"id": 30, "name": "Dahi Puri",               "meal": "Hi-Tea",    "category": "Snacks",  "price": 90,  "icon": "🍥", "tags": ["tangy","cold"],        "humor": "A full flavor explosion in one bite 💥"},
    {"id": 31, "name": "Cake Slice",              "meal": "Hi-Tea",    "category": "Bakery",  "price": 150, "icon": "🎂", "tags": ["sweet","baked"],       "humor": "Because every day deserves a celebration 🎈"},
    {"id": 32, "name": "Mini Burgers",            "meal": "Hi-Tea",    "category": "Western", "price": 200, "icon": "🍔", "tags": ["light","snack"],       "humor": "Big taste packed in a tiny bun 🤏"},
    {"id": 33, "name": "Chaat",                   "meal": "Hi-Tea",    "category": "Snacks",  "price": 70,  "icon": "🍿", "tags": ["tangy","spicy"],       "humor": "Tangy, spicy, and absolutely addictive 😄"},
    {"id": 34, "name": "Fruit Tart",              "meal": "Hi-Tea",    "category": "Bakery",  "price": 180, "icon": "🥧", "tags": ["sweet","fresh"],       "humor": "A piece of art you can eat 🎨"},
    {"id": 35, "name": "Spring Rolls",            "meal": "Hi-Tea",    "category": "Snacks",  "price": 150, "icon": "🥚", "tags": ["crispy","light"],      "humor": "Crispy on the outside, joy on the inside 🎲"},
    {"id": 36, "name": "Scones",                  "meal": "Hi-Tea",    "category": "Bakery",  "price": 160, "icon": "🫖", "tags": ["baked","traditional"], "humor": "British elegance on your tea table ☕"},

    # ── Dinner ─────────────────────────────────────────────────────────────────
    {"id": 37, "name": "Chicken Tikka",           "meal": "Dinner",    "category": "BBQ",     "price": 350, "icon": "🍗", "tags": ["grilled","spicy"],     "humor": "Smoke and spice — the ultimate combo 🔥"},
    {"id": 38, "name": "Seekh Kebab Platter",     "meal": "Dinner",    "category": "BBQ",     "price": 400, "icon": "🍢", "tags": ["grilled","heavy"],     "humor": "Joy on a stick — no explanation needed 🥹"},
    {"id": 39, "name": "Beef Steak",              "meal": "Dinner",    "category": "Western", "price": 750, "icon": "🥩", "tags": ["grilled","heavy"],     "humor": "Well done = well fed 🎯"},
    {"id": 40, "name": "Pizza",                   "meal": "Dinner",    "category": "Fast Food","price": 400, "icon": "🍕", "tags": ["heavy","cheesy"],      "humor": "Cheese pull longer than your patience 🧀"},
    {"id": 41, "name": "Manchurian Rice",         "meal": "Dinner",    "category": "Chinese", "price": 320, "icon": "🍚", "tags": ["spicy","gravy"],       "humor": "Sweet-spicy identity crisis on a plate 😵"},
    {"id": 42, "name": "Chicken Shawarma",        "meal": "Dinner",    "category": "Desi",    "price": 180, "icon": "🌯", "tags": ["heavy","grilled"],     "humor": "Midnight hunger? Consider it handled 🌙"},
    {"id": 43, "name": "Grilled Fish",            "meal": "Dinner",    "category": "Western", "price": 500, "icon": "🐟", "tags": ["light","grilled"],     "humor": "Healthy AND delicious — yes, it exists 🌟"},
    {"id": 44, "name": "Beef Biryani",            "meal": "Dinner",    "category": "Desi",    "price": 380, "icon": "🍚", "tags": ["heavy","spicy"],       "humor": "Eid vibes every single night 🌙"},
    {"id": 45, "name": "Chicken Pasta",           "meal": "Dinner",    "category": "Western", "price": 350, "icon": "🍝", "tags": ["creamy","main"],       "humor": "Italian dreams served in a bowl 🇮🇹"},
    {"id": 46, "name": "Malai Boti",              "meal": "Dinner",    "category": "BBQ",     "price": 420, "icon": "🧇", "tags": ["grilled","creamy"],    "humor": "Creamy, tender, skewered perfection 💭"},
    {"id": 47, "name": "Thai Curry",              "meal": "Dinner",    "category": "Asian",   "price": 450, "icon": "🍛", "tags": ["spicy","exotic"],      "humor": "A spicy journey to Thailand 🌶️"},
    {"id": 48, "name": "Nihari",                  "meal": "Dinner",    "category": "Desi",    "price": 380, "icon": "🍲", "tags": ["heavy","spicy"],       "humor": "Slow-cooked all night, gone in minutes 😋"},

    # ── Beverages (all meals) ──────────────────────────────────────────────────
    {"id": 49, "name": "Chai",                    "meal": "All",       "category": "Beverages","price": 40,  "icon": "☕", "tags": ["hot","traditional"],  "humor": "The glue that holds Pakistan together 🇵🇰"},
    {"id": 50, "name": "Coffee",                  "meal": "All",       "category": "Beverages","price": 100, "icon": "☕", "tags": ["hot","energizing"],   "humor": "Official wake-up juice ⚡"},
    {"id": 51, "name": "Mango Shake",             "meal": "All",       "category": "Beverages","price": 120, "icon": "🥭", "tags": ["cold","sweet"],       "humor": "Mango season captured in a glass 🌴"},
    {"id": 52, "name": "Lassi",                   "meal": "All",       "category": "Beverages","price": 90,  "icon": "🥛", "tags": ["cold","traditional"], "humor": "Yogurt's greatest life achievement 🏆"},
    {"id": 53, "name": "Green Tea",               "meal": "All",       "category": "Beverages","price": 60,  "icon": "🍵", "tags": ["hot","healthy"],      "humor": "Fancy leaf water with health benefits 🍃"},
    {"id": 54, "name": "Lemonade",                "meal": "All",       "category": "Beverages","price": 80,  "icon": "🍋", "tags": ["cold","refreshing"],  "humor": "Life gave lemons — we made this 🍋"},
    {"id": 55, "name": "Cold Coffee",             "meal": "All",       "category": "Beverages","price": 130, "icon": "🧋", "tags": ["cold","sweet"],       "humor": "Iced, shaken, and dangerously good 😎"},
    {"id": 56, "name": "Fresh Juice",             "meal": "All",       "category": "Beverages","price": 100, "icon": "🍹", "tags": ["cold","healthy"],     "humor": "Fruits in their finest disguise 🥷"},
]

COMBO_RULES = {
    1:  [49, 52],       2:  [49, 52, 54],   3:  [49, 52],
    7:  [49, 52],       11: [49, 54],        12: [50, 54],
    13: [52, 51, 49],   14: [49, 52],        15: [52, 49],
    17: [55, 54],       18: [55, 54],        22: [55, 54],
    25: [49, 52],       26: [49, 53],        27: [50, 53],
    28: [50, 53, 55],   29: [50, 49],        33: [49, 54],
    37: [52, 54, 51],   38: [52, 49],        40: [55, 54],
    42: [54, 55],       44: [52, 49, 51],    48: [49, 52],
}

ITEM_BY_ID = {item['id']: item for item in ITEMS}

def get_meal_time():
    h = datetime.now().hour
    if   5  <= h < 11: return 'Breakfast'
    elif 11 <= h < 16: return 'Lunch'
    elif 16 <= h < 20: return 'Hi-Tea'
    else:              return 'Dinner'

MEAL_CATEGORIES = {
    'Breakfast': ['Desi', 'Western', 'Healthy'],
    'Lunch':     ['Desi', 'Western', 'Fast Food', 'Chinese', 'Healthy'],
    'Hi-Tea':    ['Snacks', 'Bakery', 'Western'],
    'Dinner':    ['BBQ', 'Desi', 'Western', 'Fast Food', 'Chinese', 'Asian'],
}

ALL_CATEGORIES = ['Desi', 'Western', 'Healthy', 'Fast Food', 'Chinese', 'Snacks', 'Bakery', 'BBQ', 'Asian', 'Beverages']

# ─── 1. K-Means Clustering ────────────────────────────────────────────────────
def make_synth_users(n=200):
    np.random.seed(42)
    rows = []
    for _ in range(n):
        r = random.random()
        v = np.zeros(len(ALL_CATEGORIES))
        if r < 0.25:
            v[ALL_CATEGORIES.index('Fast Food')] = random.randint(5, 15)
            v[ALL_CATEGORIES.index('Beverages')] = random.randint(2, 8)
        elif r < 0.50:
            v[ALL_CATEGORIES.index('Healthy')]   = random.randint(5, 15)
            v[ALL_CATEGORIES.index('Beverages')] = random.randint(1, 4)
        elif r < 0.75:
            v[ALL_CATEGORIES.index('Desi')]      = random.randint(4, 12)
            v[ALL_CATEGORIES.index('Beverages')] = random.randint(2, 6)
        else:
            v[ALL_CATEGORIES.index('BBQ')]       = random.randint(3, 10)
            v[ALL_CATEGORIES.index('Desi')]      = random.randint(2, 6)
        rows.append(v)
    return np.array(rows)

_synth = make_synth_users()
kmeans = sklearn.cluster.KMeans(n_clusters=4, random_state=42, n_init=10).fit(_synth)
CLUSTER_LABELS = {
    0: 'Fast Food Fanatic 🍔',
    1: 'Health Guru 🥗',
    2: 'Desi Foodie 🍛',
    3: 'BBQ Master 🔥',
}

def get_segment(_mood, hunger, pref):
    v = np.zeros(len(ALL_CATEGORIES))
    pref_map = {
        'spicy':  ('Desi',      8),
        'heavy':  ('Desi',      8),
        'sweet':  ('Bakery',    6),
        'light':  ('Healthy',   10),
        'fast':   ('Fast Food', 8),
        'grilled':('BBQ',       8),
    }
    cat, base = pref_map.get(pref, ('Fast Food', 6))
    v[ALL_CATEGORIES.index(cat)]          = base
    v[ALL_CATEGORIES.index('Beverages')]  = 3
    scale = {'high': 1.5, 'medium': 1.0, 'low': 0.6}.get(hunger, 1.0)
    v *= scale
    cid = int(kmeans.predict([v])[0])
    return CLUSTER_LABELS.get(cid, 'Mixed Taste 🤷')

# ─── 2. Random Forest Classifier ─────────────────────────────────────────────
def build_rf_data(n=1500):
    rows = []
    for _ in range(n):
        meal = random.choice(MEAL_TIMES)
        pref = random.choice(['spicy','heavy','sweet','light','fast','grilled'])
        mood = random.choice(['happy','sad','tired','excited','hungry'])
        cats = MEAL_CATEGORIES[meal]

        if mood == 'sad':       nxt = random.choice(['Bakery', 'Desi', 'Beverages'])
        elif mood == 'tired':   nxt = random.choice(['Healthy', 'Beverages', 'Snacks'])
        elif mood == 'excited': nxt = random.choice(['Fast Food', 'BBQ', 'Desi'])
        elif mood == 'hungry':  nxt = random.choice(['Desi', 'BBQ', 'Fast Food'])
        elif pref == 'grilled': nxt = 'BBQ'
        elif pref == 'light':   nxt = 'Healthy'
        elif pref == 'sweet':   nxt = 'Bakery'
        elif pref == 'spicy':   nxt = random.choice(['Desi', 'Chinese'])
        else:                   nxt = random.choice(cats)
        rows.append({'meal': meal, 'pref': pref, 'mood': mood, 'nxt': nxt})
    return pd.DataFrame(rows)

_df = build_rf_data()
le_meal, le_pref, le_mood, le_cat = LabelEncoder(), LabelEncoder(), LabelEncoder(), LabelEncoder()
_df['meal_e'] = le_meal.fit_transform(_df['meal'])
_df['pref_e'] = le_pref.fit_transform(_df['pref'])
_df['mood_e'] = le_mood.fit_transform(_df['mood'])
_y            = le_cat.fit_transform(_df['nxt'])
classifier    = RandomForestClassifier(n_estimators=100, random_state=42).fit(
    _df[['meal_e', 'pref_e', 'mood_e']], _y
)

def predict_category(meal_time, mood, pref):
    mt = meal_time if meal_time in le_meal.classes_ else 'Lunch'
    pr = pref      if pref      in le_pref.classes_ else 'spicy'
    mo = mood      if mood      in le_mood.classes_ else 'happy'
    mt_e = le_meal.transform([mt])[0]
    pr_e = le_pref.transform([pr])[0]
    mo_e = le_mood.transform([mo])[0]
    row  = pd.DataFrame([[mt_e, pr_e, mo_e]], columns=['meal_e', 'pref_e', 'mood_e'])
    pred = classifier.predict(row)[0]
    return le_cat.inverse_transform([pred])[0]

# ─── 3. Q-Learning ───────────────────────────────────────────────────────────
Q            = defaultdict(lambda: 0.5)
ALPHA, GAMMA = 0.1, 0.9

def update_q(b, e, r):
    Q[(b, e)] += ALPHA * (r - Q[(b, e)])

def top_extras(bid, k=3):
    pool = COMBO_RULES.get(bid, [])
    return sorted(pool, key=lambda e: -Q[(bid, e)])[:k]

def prob_extra(bid):
    pool = COMBO_RULES.get(bid, [])
    if not pool: return None
    q = np.array([Q[(bid, e)] for e in pool])
    if q.max() - q.min() < 0.01: return random.choice(pool)
    ex = np.exp((q - q.max()) / 0.3)
    return int(np.random.choice(pool, p=ex / ex.sum()))

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html', meal_times=MEAL_TIMES, items=ITEMS)

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        d         = request.get_json()
        mood      = d.get('mood', 'happy')
        hunger    = d.get('hunger', 'medium')
        pref      = d.get('preference', 'spicy')
        meal_time = d.get('meal_time', get_meal_time())
    except Exception:
        return jsonify({'error': 'Bad request'}), 400

    try:
        seg = get_segment(mood, hunger, pref)
        cat = predict_category(meal_time, mood, pref)
    except Exception as e:
        return jsonify({'error': f'Model error: {e}'}), 500

    # items for the predicted category within the chosen meal_time
    pool = [it for it in ITEMS if it['meal'] in (meal_time, 'All') and it['category'] == cat]
    if len(pool) < 4:
        pool += [it for it in ITEMS if it['meal'] in (meal_time, 'All') and it['category'] != cat]
    random.shuffle(pool)
    recs = pool[:6]

    combos = {}
    for it in recs[:3]:
        ex = top_extras(it['id'])
        if ex:
            combos[str(it['id'])] = [ITEM_BY_ID[e] for e in ex if e in ITEM_BY_ID]

    MSGS = {
        'happy':   "Great mood + great food = perfect day! 😄",
        'sad':     "Don't worry — good food fixes everything! 🍫",
        'tired':   "Feeling tired? Eat well and recharge! ⚡",
        'excited': "Excitement and good food — the ultimate combo! 🎉",
        'hungry':  "Hunger has been detected — let's fix that! 🔥",
    }
    MEAL_MSGS = {
        'Breakfast': "Start your day right with a great breakfast! 🌅",
        'Lunch':     "Midday hunger? We've got you covered! 🌤️",
        'Hi-Tea':    "Chai time is always the best time! ☕",
        'Dinner':    "End your day with a delicious dinner! 🌙",
    }

    return jsonify({
        'segment':         seg,
        'category':        cat,
        'meal_time':       meal_time,
        'recommendations': recs,
        'combos':          combos,
        'mood_message':    MSGS.get(mood, "Sahi khana aa raha hai! 🍽️"),
        'meal_message':    MEAL_MSGS.get(meal_time, ""),
        'current_meal':    get_meal_time(),
    })

@app.route('/browse', methods=['GET'])
def browse():
    meal = request.args.get('meal', 'All')
    if meal == 'All':
        items = ITEMS
    else:
        items = [it for it in ITEMS if it['meal'] in (meal, 'All')]
    return jsonify({'items': items})

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    iid = request.get_json().get('item_id')
    if iid not in ITEM_BY_ID:
        return jsonify({'success': False}), 400
    cart = session.get('cart', [])
    cart.append(iid)
    session['cart'] = cart
    cart_items = [ITEM_BY_ID[i] for i in cart if i in ITEM_BY_ID]
    return jsonify({
        'success': True,
        'count':   len(cart),
        'total':   sum(x['price'] for x in cart_items),
        'cart':    cart_items,
    })

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    iid  = request.get_json().get('item_id')
    cart = session.get('cart', [])
    if iid in cart: cart.remove(iid)
    session['cart'] = cart
    cart_items = [ITEM_BY_ID[i] for i in cart if i in ITEM_BY_ID]
    return jsonify({
        'success': True,
        'count':   len(cart),
        'total':   sum(x['price'] for x in cart_items),
        'cart':    cart_items,
    })

@app.route('/clear-cart', methods=['POST'])
def clear_cart():
    session['cart'] = []
    return jsonify({'success': True})

@app.route('/get-cart', methods=['GET'])
def get_cart():
    cart = session.get('cart', [])
    cart_items = [ITEM_BY_ID[i] for i in cart if i in ITEM_BY_ID]
    return jsonify({
        'cart':  cart_items,
        'count': len(cart_items),
        'total': sum(x['price'] for x in cart_items),
    })

@app.route('/spin-wheel', methods=['POST'])
def spin_wheel():
    bid = request.get_json().get('base_item_id')
    if bid not in ITEM_BY_ID:
        return jsonify({'success': False}), 404
    eid = prob_extra(bid)
    if eid is None:
        return jsonify({'success': False, 'msg': 'No combo available'})
    return jsonify({'success': True, 'extra_item': ITEM_BY_ID[eid]})

@app.route('/feedback', methods=['POST'])
def feedback():
    d = request.get_json()
    update_q(d.get('base_item_id'), d.get('extra_item_id'), 1.0 if d.get('accepted') else 0.0)
    return jsonify({'success': True})

if __name__ == '__main__':
    webbrowser.open_new_tab('http://localhost:5001')
    app.run(debug=True, port=5001)
