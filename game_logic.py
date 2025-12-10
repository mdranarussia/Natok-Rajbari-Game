import streamlit as st
import random
import json
import base64

# --- অ্যাডমিন/মালিকের গোপন তথ্য ---
ADMIN_PASSWORD = "your_secret_password_123"

def load_data():
    """Reads game data from a 'database' (placeholder)."""
    if 'user_data' not in st.session_state:
        st.session_state['user_data'] = {}
    return st.session_state['user_data']

def save_data(data):
    """Saves game data (placeholder)."""
    st.session_state['user_data'] = data

# --- গেমের লজিক ---
def play_dice_game(user_id, current_data):
    """Handles the main game logic."""
    
    if user_id not in current_data:
        current_data[user_id] = {'coins': 100}
    
    user = current_data[user_id]
    BET_AMOUNT = 5
    
    if user['coins'] < BET_AMOUNT:
        st.error(f"⚠️ কম কয়েন! আপনার আছে {user['coins']} কয়েন। খেলার জন্য প্রয়োজন {BET_AMOUNT} কয়েন।")
        return None, None

    user['coins'] -= BET_AMOUNT
    
    dice = [random.randint(1, 6) for _ in range(3)]
    
    # উইনিং লজিক: তিনটি ডাইসই এক হলে
    if dice[0] == dice[1] and dice[1] == dice[2]:
        payout = 5
        result_message = f"🎉 অভিনন্দন, ট্রিপল ম্যাচ! আপনি {BET_AMOUNT * payout} কয়েন জিতলেন!"
    else:
        payout = -1
        result_message = "😔 দুঃখিত, আবার চেষ্টা করুন। কোনো ম্যাচ হয়নি।"

    if payout > 0:
        user['coins'] += BET_AMOUNT * (payout + 1)
    
    save_data(current_data)
    
    return dice, result_message

# --- Streamlit UI (ইউজার ইন্টারফেস) ---
def main_app():
    st.set_page_config(page_title="নাটক রাজবাড়ি গেম 👑", layout="centered")
    
    st.markdown("""
    <style>
        .stButton>button {
            background-color: #FF5733; 
            color: white;
            font-size: 20px;
            font-weight: bold;
            border-radius: 8px;
            padding: 10px 20px;
            width: 100%;
            margin-top: 15px;
        }
        .balance-display {
            font-size: 24px;
            color: #1E90FF;
            font-weight: bold;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("ডাইস বোনাস গেম 💎 (নাটক রাজবাড়ি)")
    st.markdown("---")
    
    user_data = load_data()
    user_id = st.text_input("আপনার ইউজার আইডি দিন:", value="Natok Rajbari")
    st.markdown(f"প্রতি রোলে: **5 কয়েন** বাজি")

    if not user_id:
        st.warning("দয়া করে আপনার ইউজার আইডি দিন।")
        return

    current_coins = user_data.get(user_id, {}).get('coins', 0)
    st.markdown(f'<div class="balance-display">বর্তমান কয়েন: 🪙 **{current_coins}**</div>', unsafe_allow_html=True)
    
    if st.button("ডাইস রোল করুন 🎲"):
        with st.spinner('রোল হচ্ছে...'):
            dice, result_message = play_dice_game(user_id, user_data)
        
        if dice:
            dice_icons = [get_dice_icon(d) for d in dice]
            st.markdown(f"## ফলাফল: {' '.join(dice_icons)}")
            
            if "অভিনন্দন" in result_message:
                st.balloons()
                st.success(result_message)
            else:
                st.error(result_message)

            current_coins_after = user_data.get(user_id, {}).get('coins', 0)
            st.markdown(f"#### নতুন ব্যালেন্স: **{current_coins_after}**")

def get_dice_icon(number):
    icons = {
        1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'
    }
    return icons.get(number, str(number))

# --- অ্যাডমিন প্যানেল ---
def admin_panel(data):
    st.set_page_config(page_title="🛡️ অ্যাডমিন প্যানেল 🛡️", layout="wide")
    st.title("🛡️ গেম অ্যাডমিন প্যানেল (মালিক: নাটক রাজবাড়ি) 👑")
    
    st.header("ব্যবহারকারীর কয়েন ডেটা")
    display_data = [{'ইউজার আইডি': uid, 'কয়েন': data[uid]['coins']} for uid in data]
    st.dataframe(display_data, use_container_width=True)
    
    st.markdown("---")
    st.header("কয়েন ম্যানুয়ালি পরিবর্তন করুন")
    with st.form("coin_update_form"):
        target_user = st.selectbox("ইউজার আইডি নির্বাচন করুন:", options=list(data.keys()))
        new_coins = st.number_input(f"'{target_user}' এর জন্য নতুন কয়েন দিন:", min_value=0, value=data.get(target_user, {}).get('coins', 0))
        submit_button = st.form_submit_button("কয়েন আপডেট করুন")

        if submit_button:
            data[target_user]['coins'] = new_coins
            save_data(data)
            st.success(f"{target_user} এর কয়েন সফলভাবে {new_coins} এ আপডেট করা হয়েছে।")
            st.experimental_rerun()

# --- অ্যাপের এন্ট্রি পয়েন্ট ---
if "pass" in st.query_params:
    if st.query_params["pass"][0] == ADMIN_PASSWORD:
        admin_panel(load_data())
    else:
        st.error("ভুল অ্যাডমিন পাসওয়ার্ড।")
else:
    main_app()
