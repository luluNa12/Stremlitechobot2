import streamlit as st, requests

drinks=requests.get(
  f'https://thecocktaildb.com/api/json/v1/1/list.php?i=list'
).json()
ingredients=[]
for drink in drinks['drinks']:
  ingredients.append(drink['strIngredient1'])

st.title('The Cocktail DB API')
st.markdown('---')
selected=st.selectbox('Select an Ingredient', ingredients)
st.markdown('---')
if selected:
  st.header(f'Drinks with {selected}')
  r=requests.get(
    f'https://thecocktaildb.com/api/json/v1/1/filter.php?i={selected}'
  ).json()
  for drink in r['drinks']:
    st.subheader(drink['strDrink'])
    st.image(drink['strDrinkThumb'])
