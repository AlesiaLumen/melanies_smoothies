import streamlit as st
import pandas as pd  # Required for DataFrame
import requests
from snowflake.snowpark.functions import col  # Drop unused when_matched

st.title("Smoothie room :strawberry:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = (st.text_input('Name on Smoothie:') or '').strip()
st.write('The name on your Smoothie will be:', name_on_order or '[None]')

cnx = st.connection("snowflake")
session = cnx.session()

fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()
fruit_options = fruit_df['FRUIT_NAME'].tolist()  # List for multiselect

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list).strip()  # Proper join, no trailing space
    st.write('Selected:', ingredients_string)

    for fruit_chosen in ingredients_list:
        st.subheader(fruit_chosen + ' Nutrition Information')
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                st.dataframe(pd.DataFrame([data]), use_container_width=True)  # Fix: Wrap in pd.DataFrame
            else:
                st.error(f"API error {response.status_code} for {fruit_chosen}")
        except Exception as e:
            st.error(f"Failed to fetch {fruit_chosen}: {str(e)}")

    if st.button('Submit Order') and ingredients_list and name_on_order:
        # Secure parameterized insert
        session.sql(
            """INSERT INTO smoothies.public.orders (ingredients, name_on_order) 
               VALUES (?, ?)""",
            params=[ingredients_string, name_on_order]
        ).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
    elif st.button('Submit Order'):
        st.warning("Select ingredients and enter a name first.")
