import pandas as pd
import plotly.express as px
import mysql
import mysql.connector
import streamlit as st             

mycon = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345"
)
mycursor = mycon.cursor()
mycursor.execute('select distinct year from phonepe_pulse.aggregate_transaction')
years = mycursor.fetchall()
years = tuple( t[0] for t in years)
mycursor.execute('select distinct state from phonepe_pulse.aggregate_transaction')
states = mycursor.fetchall()
states = tuple(s[0] for s in states)

selected_State = st.sidebar.selectbox("Select state", states)
selected_Year = st.sidebar.selectbox("Select year", years)

# MySQL queries
query1 = f'''SELECT year,Transaction_Name,sum(Count) as Transactions_Count FROM phonepe_pulse.aggregate_transaction
             where state="{selected_State}" group by state,year,Transaction_Name'''
query2 = 'select Device_Brand, sum(device_count) as Device_Count from phonepe_pulse.aggregate_users group by Device_Brand'
query3 = 'select state, sum(Registered_Users) as Registered_Users from phonepe_pulse.map_users group by state'
query4 = '''select Year,Transaction_Name,sum(Amount) as Transactions_Amount FROM phonepe_pulse.aggregate_transaction
                group by Year,Transaction_Name'''
query5 = f'select state,year,district,sum(count) as Transaction_Count from phonepe_pulse.top_transactions where state="{selected_State}" and year="{selected_Year}" group by district'

if st.sidebar.button('Submit'):

    mycursor.execute(query1)
    result = mycursor.fetchall()
    df_result = pd.DataFrame(result)
    df_result.rename(columns = {0:'Year', 1:'Transaction_Name', 2:'Transactions_Count'},inplace = True)
    fig1 = px.line(df_result, x='Year', y='Transactions_Count', color='Transaction_Name')
    fig1.update_layout(
        title=f'State:{selected_State}')
    
    mycursor.execute(query2)
    result = mycursor.fetchall()
    df_result = pd.DataFrame(result)
    df_result.rename(columns = {0:'Device_Brand', 1:'Device_Count'},inplace = True)
    fig2 = px.pie(df_result,names=df_result['Device_Brand'],values=df_result['Device_Count'],title='Device market share %')
    fig2.update_traces(textposition='inside', textinfo='percent')

    mycursor.execute(query3)
    result = mycursor.fetchall()
    df_result = pd.DataFrame(result)
    df_result.rename(columns = {0:'State', 1:'Registered_Users'},inplace = True)
    df_result.State = df_result.State.str.title()
    df_result['State'] = df_result['State'].str.replace(r'-', ' ', regex=True)
    df_result['State'] = df_result['State'].str.replace(r'Islands', '', regex=True)
    df_result['State'] = df_result['State'].str.replace('Dadra & Nagar Haveli & Daman & Diu','Dadra and Nagar Haveli and Daman and Diu',regex=True)
    fig3 = px.choropleth(
        df_result,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations=df_result['State'],
        color=df_result['Registered_Users'],
        color_continuous_scale='Reds',
        title='Registered Users in India'
        )
    fig3.update_geos(fitbounds="locations", visible=False)

    mycursor.execute(query4)
    result = mycursor.fetchall()
    df_result = pd.DataFrame(result)
    df_result.rename(columns = {0:'Year', 1:'Transaction_Name', 2:'Transaction_Amount'},inplace = True)
    fig4 = px.scatter(df_result,x=df_result['Year'],y=df_result['Transaction_Amount'],color=df_result['Transaction_Name'],size_max=60,hover_name=df_result['Transaction_Name'])
    fig4.update_layout(
        title='Transaction-Amount over the years',
        xaxis=dict(
            title='Year',           
        ),
        yaxis=dict(
            title='Transaction-Amount',            
        ))

    mycursor.execute(query5)
    result = mycursor.fetchall()
    df_result = pd.DataFrame(result)
    df_result.rename(columns = {0:'State', 1:'Year', 2:'District', 3:'Transactions_Count'},inplace = True)
    z1 = df_result['District']
    z2 = df_result['Transactions_Count']
    #st.write(z)
    fig5 = px.bar(df_result, x=z1, y=z2,
             color='District',title='Transaction Count over the years')
    fig5.update_layout(
        title=f'State-{selected_State} in Year-{selected_Year}')


# Dashboard layout
    col1,col2 = st.columns((3.5, 3.5), gap='small')
    col3 = st.container()
    col4 = st.container()
    col5 = st.container()
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
    with col3:
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        st.plotly_chart(fig4, use_container_width=True)
    with col5:
        st.plotly_chart(fig5, use_container_width=True)


    


