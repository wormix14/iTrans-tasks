import os
import streamlit as st
import matplotlib.pyplot as plt

from services.orders_service import process_orders
from services.books_service import process_books
from services.users_service import process_users
from services.db_service import StoreDatabase
from llm import ask_assistant


st.set_page_config(
    page_title="Bookstore Analytics",
    layout="wide",
)

st.title("Bookstore Analytics")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

if not os.path.exists(DATA_DIR):
    st.error(f"Directory '{DATA_DIR}' not found. Please ensure your datasets exist.")
    st.stop()

# limit 3 stores
available_stores = sorted(
    [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
)[:3]

selected_store = st.sidebar.selectbox("Select Store", available_stores)
store_dir = os.path.join(DATA_DIR, selected_store)

# --- Session State: Database & Chat Cache ---
if ("current_store" not in st.session_state or st.session_state.current_store != selected_store):
    st.session_state.current_store = selected_store
    st.session_state.messages = []
    
    with st.spinner("Initializing in-memory database..."):
        st.session_state.db = StoreDatabase(store_dir)


tab_orders, tab_books, tab_users, tab_chat = st.tabs(
    ["Orders", "Books", "Users", "Сhat-assistant"]
)


# 1. Orders Tab
with tab_orders:
    st.header("Orders Analytics")
    try:
        top_5_days, fig = process_orders(store_dir)

        col1, col2 = st.columns([3, 2])
        with col1:
            st.subheader("Daily Revenue Trend")
            st.pyplot(fig)
            plt.close(fig)

        with col2:
            st.subheader("Top Revenue Days")
            st.dataframe(
                top_5_days.reset_index().rename(
                    columns={"date": "Date", "paid_price": "Revenue ($)"}
                ),
                width="stretch",
                hide_index=True,
            )
    except Exception as e:
        st.error(f"Failed to process orders: {e}")


# 2. Books Tab
with tab_books:
    st.header("Books Analytics")
    try:
        author_set_count, most_sold_authors = process_books(store_dir)

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="Unique Author Combinations / Sets", value=author_set_count
            )

        with col2:
            st.subheader("Most Sold Authors")
            st.dataframe(
                most_sold_authors,
                width="stretch",
            )
    except Exception as e:
        st.error(f"Failed to process books: {e}")


# 3. Users Tab
with tab_users:
    st.header("Users & Identity Resolution")
    try:
        unique_users_count, best_ids, best_name = process_users(store_dir)

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Resolved Unique Users", value=unique_users_count)

        with col2:
            st.subheader("Top Spender")
            st.write(f"**Name:** {best_name}")
            st.write(f"**Associated IDs:** {best_ids}")
    except Exception as e:
        st.error(f"Failed to process users: {e}")


# 4. Chat-assistant Tab
with tab_chat:
    st.header(f"Store Chatbot: {selected_store}")

    # Render persistent conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle input prompt
    if prompt := st.chat_input("Ask a question about orders, books, or revenue..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Process through Agent Service
        with st.chat_message("assistant"):
            with st.spinner("Analyzing database via SQL..."):
                try:
                    reply = ask_assistant(
                        user_message=prompt,
                        db=st.session_state.db,
                        chat_history=st.session_state.messages[:-1],
                    )
                    st.markdown(reply)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": reply}
                    )
                except Exception as e:
                    err_msg = f"Error during agent execution: {e}"
                    st.error(err_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": err_msg}
                    )