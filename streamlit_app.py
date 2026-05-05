import streamlit as st
import pandas as pd  # Add this import
import requests
from snowflake.snowpark.functions import col  # Remove unused when_matched

st.title("Smoothie room :strawberry:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
if not name_on_order.strip():
    st.warning("Please enter a name.")

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()  # Convert to Pandas for multiselect

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'].tolist(),  # Use list for options
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Cleaner join
    st.write('Selected: ', ingredients_string)

    # Optional: Preview API data in expander
    with st.expander("Preview fruit details"):
        for fruit in ingredients_list:
            try:
                response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit)
                if response.status_code == 200:
                    data = response.json()
                    st.dataframe(pd.DataFrame([data]))  # Wrap in DataFrame
            except:
                st.error(f"API error for {fruit}")

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if len(ingredients_list) > 0 and name_on_order.strip():
            # Safe parameterized insert
            session.sql(
                """INSERT INTO smoothies.public.orders(ingredients, name_on_order) 
                   VALUES (?, ?)""",
                params=[ingredients_string, name_on_order.strip()]
            ).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        else:
            st.error("Please select ingredients and enter a name.")

