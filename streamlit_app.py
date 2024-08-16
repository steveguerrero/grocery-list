import streamlit as st
import pandas as pd
# Strike text
def strike_text(text):
    return f"~~{text}~~"
# CSV file path
CSV_FILE = 'articles.csv'
# Function to load articles from a CSV file
def load_articles():
    if not os.path.exists(CSV_FILE):
        return []
    return pd.read_csv(CSV_FILE).to_dict(orient='records')
# Function to save articles to a CSV file
def save_articles(articles):
    pd.DataFrame(articles).to_csv(CSV_FILE, index=False)
# Function to clear articles and reset the CSV file
def clear_articles():
    st.session_state.articles = []
    file = open(CSV_FILE, "w")
    file.write("name,category,price,is_bought\n")
    file.close()
    st.rerun()
# Function to sort the articles according to the category order
def sort_articles(articles, categories):
    df = pd.DataFrame(articles)
    category_order = {category: i for i, category in enumerate(categories)}
    df['CategoryOrder'] = df['category'].map(category_order)
    df = df.sort_values(by='CategoryOrder').drop(columns=['CategoryOrder'])
    return df.to_dict(orient='records')
# Load articles on first run or if session state is missing
if 'articles' not in st.session_state:
    st.session_state.articles = load_articles()
if 'edit_idx' not in st.session_state:
    st.session_state.edit_idx = None
# Define categories and category order
categories = [
    "Recipes", "Produce", "Hot Drinks", "Nuts", "Snacks", "Beverages",
    "Bakery", "Grains & Pasta", "Sauces and condiments", "Milk products",
    "Spices & Herbs", "Meat", "Ready-made sauces", "Canned Goods",
    "Frozen Foods", "Fish", "Personal Care", "Household & Cleaning Supplies",
    "Other"
]
# Title of the app
st.title("Article Price Calculator")
# Input fields for new article
with st.form(key='article_form', clear_on_submit=True):
    name = st.text_input('Article Name')
    category = st.selectbox('Category', categories)
    price_input = st.text_input('Price (use comma as decimal separator)')
    submit_button = st.form_submit_button(label='Add Article')
# Add new article to the list
if submit_button:
    try:
        price = float(price_input.strip().replace(',', '.')) if price_input else 0
        if not name.strip():
            st.error("Please input a valid name, category, and price!")
        else:
            article_to_add = {
                'name': name.strip(), 
                'category': category, 
                'price': price, 
                'is_bought': False
            }
            st.session_state.articles.append(article_to_add)
            st.session_state.articles = sort_articles(st.session_state.articles, categories)
            save_articles(st.session_state.articles)
            st.success(f"Added article {name} with price {price:.2f} in category {category}")
    except ValueError:
        st.error("Please input a valid price using a comma as the decimal separator.")
# Function to update an article's details
def update_article(article_idx, new_name, new_category, new_price):
    article = st.session_state.articles[article_idx]
    article['name'] = new_name.strip()
    article['category'] = new_category
    article['price'] = new_price
    st.session_state.articles[article_idx] = article
    st.session_state.articles = sort_articles(st.session_state.articles, categories)
    save_articles(st.session_state.articles)
    st.session_state.edit_idx = None
    st.rerun()
# Function to mark an article as bought
def set_is_bought(article_idx):
    article = st.session_state.articles[article_idx]
    article['is_bought'] = not article['is_bought']
    st.session_state.articles[article_idx] = article
    save_articles(st.session_state.articles)
    st.rerun()
# Display the list of articles with remove and update buttons
if st.session_state.articles:
    st.subheader('Articles:')
    df_articles = pd.DataFrame(st.session_state.articles)
    
    used_categories = set(df_articles['category'])
    visible_categories = [category for category in categories if category in used_categories]
    
    for category in visible_categories:
        st.write(f"**{category}:**")
        category_articles = df_articles[df_articles['category'] == category]
        
        edited_df = st.data_editor(category_articles, num_rows='dynamic')
        
        if edited_df is not None:
            edited_articles = edited_df.to_dict(orient='records')
            st.session_state.articles = sort_articles(edited_articles, categories)
            save_articles(st.session_state.articles)
    
    # Calculate and display the total sum
    total_price = df_articles['price'].sum()
    st.write(f"**Total: {total_price:.2f} EUR**")
else:
    st.write(f":green[All articles have been cleared!]")
# Option to clear the list of articles
if st.button('Clear All Articles'):
    clear_articles()
