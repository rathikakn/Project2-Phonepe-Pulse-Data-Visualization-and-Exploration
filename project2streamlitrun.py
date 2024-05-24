import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import streamlit as st
import plotly.express as px

mydb = mysql.connector.connect(host="localhost",user="root",password="")

mycursor = mydb.cursor(buffered=True)

db_connection_str = f"mysql+mysqlconnector://root@localhost/phonepe"
db_engine = create_engine(db_connection_str)



aggregated_transaction_df = pd.read_sql_table("Agg_transaction",con=db_engine)
aggregated_user_df = pd.read_sql_table("Agg_user",con=db_engine)
map_transaction_df = pd.read_sql_table("Map_transaction",con=db_engine)
map_user_df = pd.read_sql_table("Map_user",con=db_engine)
top_transaction_df = pd.read_sql_table("Top_transaction",con=db_engine)
top_user_df = pd.read_sql_table("Top_users",con=db_engine)


aggregated_transaction_df['avg_amount'] = (aggregated_transaction_df['Transaction_amount'] / aggregated_transaction_df['Transaction_count']).astype(int)

map_transaction_df['avg_amount'] = (map_transaction_df['Total_payment_value']/ map_transaction_df['All_Transactions']).astype(int)

top_transaction_df['avg_amount_district'] = (top_transaction_df['Districts_total_amount']/top_transaction_df['Districts_total_count']).astype(int)

top_transaction_df['avg_amount_postcode'] = (top_transaction_df['Postalcodes_total_amount']/top_transaction_df['Postalcodes_total_count']).astype(int)

st.title("Phonepe Pulse") # project title

with st.sidebar:
    st.header("Payments")

transaction_parts = ['Transaction','Users']
Payments = st.sidebar.selectbox('Payments',transaction_parts)

years = aggregated_transaction_df['Year'].unique()
quater_agg = aggregated_transaction_df['Quater'].unique()
categories = aggregated_transaction_df['Transaction_type'].unique()
state = map_transaction_df['State'].unique() 

selected_year = st.sidebar.selectbox('Select year',sorted(years))
selected_quater = st.sidebar.selectbox('Select quater',sorted(quater_agg))

if Payments == 'Transaction':
    aggregated_transaction_sum =aggregated_transaction_df.groupby(by='Year').sum().reset_index()
    aggregated_transaction_sum["avg_amount"] = (aggregated_transaction_sum['Transaction_amount'] / aggregated_transaction_sum['Transaction_count']).astype(int)

    fig_bar_aggregated_transaction_sum = px.bar(
        aggregated_transaction_sum,
        x = 'Year',
        y = 'Transaction_amount',
        color='Transaction_count',
        text_auto='.2s',
        color_continuous_scale="plasma",
        title="Total Transacation value over the years"
        )
    fig_bar_aggregated_transaction_sum.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

    st.plotly_chart(fig_bar_aggregated_transaction_sum)


    aggregated_transaction_df2 = aggregated_transaction_df[(aggregated_transaction_df['Year'] == selected_year) & (aggregated_transaction_df['Quater'] == selected_quater) ]

    st.subheader(f'Categories and Transaction value for_{selected_quater}_{selected_year}')

    aggregated_transaction_df3 = aggregated_transaction_df2.groupby(['Transaction_type']).sum().reset_index()
    aggregated_transaction_df3.drop(['Year','Quater','Transaction_count','State','avg_amount'],axis=1,inplace=True)
    aggregated_transaction_df4 = aggregated_transaction_df3[['Transaction_type','Transaction_amount']].sort_values(by='Transaction_amount',ascending=False).reset_index(drop=True)
    st.dataframe(aggregated_transaction_df4)

    tab1, tab2 = st.tabs(["Categories by Selection", "all Categories"])


    selected_categories =  tab1.selectbox("categories", categories)

    aggregated_transaction_df1 = aggregated_transaction_df[(aggregated_transaction_df['Year'] == selected_year) & (aggregated_transaction_df['Quater'] == selected_quater) & (aggregated_transaction_df['Transaction_type'] == selected_categories) ]

    categories_agg = aggregated_transaction_df1.sort_values(by='Transaction_amount',ascending=False).head(10).reset_index(drop=True)

    fig = px.choropleth(
        aggregated_transaction_df1,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        hover_name = 'State',
        hover_data = ['avg_amount'],        
        color='Transaction_amount',
        color_continuous_scale="plasma",
        title=f'{selected_categories}_{selected_quater}_{selected_year}'
    )
    fig.update_geos(fitbounds="locations", visible=False)

    tab1.plotly_chart(fig)


    fig_bar = px.bar(
        categories_agg,
        x = 'State',
        y = 'Transaction_amount',
        color='avg_amount',
        text_auto='.2s',
        color_continuous_scale="plasma",
        title=f'{selected_quater}_{selected_year}_Top 10 States in {selected_categories} by Transacation_Amount_'
        )
    fig_bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    tab1.plotly_chart(fig_bar)

    for n in categories:
        aggregated_transaction_df1 = aggregated_transaction_df[(aggregated_transaction_df['Year'] == selected_year) & (aggregated_transaction_df['Quater'] == selected_quater) & (aggregated_transaction_df['Transaction_type'] == n) ]

        fig = px.choropleth(
            aggregated_transaction_df1,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locations='State',
            hover_name = 'State',
            hover_data = ['avg_amount'],        
            color='Transaction_amount',
            color_continuous_scale="plasma",
            title=f'{n}_{selected_quater}_{selected_year}'
        )
        fig.update_geos(fitbounds="locations", visible=False)

        tab2.plotly_chart(fig)

    for n in categories:

        fig_bar = px.bar(
            categories_agg,
            x = 'State',
            y = 'Transaction_amount',
            color='avg_amount',
            text_auto='.2s',
            color_continuous_scale="plasma",
            title=f'{selected_quater}_{selected_year}_Top 10 States in {n} by Transacation_Amount_'
            )
        fig_bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        tab2.plotly_chart(fig_bar)


    fig_agg_pie= px.pie(
        aggregated_transaction_df2,
        values='Transaction_amount',
        names='Transaction_type',
        title=f'Categories_{selected_quater}_{selected_year}',
        hover_data = ['avg_amount'] )
    fig_agg_pie.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig_agg_pie)    


    map_transaction_df1 = map_transaction_df[(map_transaction_df['Year']==selected_year) & (map_transaction_df['Quater']==selected_quater)].reset_index(drop=True)
    

    map_transaction_df2 = map_transaction_df1.groupby(['State']).sum().reset_index()
    map_transaction_df3 = map_transaction_df2.drop(['Year','Quater','District','avg_amount'],axis=1)
    map_transaction_df3['avg_amount'] = (map_transaction_df3['Total_payment_value'] / map_transaction_df3['All_Transactions']).astype(int)
    map_transaction_df4 = map_transaction_df3.drop(['All_Transactions'],axis=1)
    map_transaction_df5 = map_transaction_df4.sort_values(by = 'Total_payment_value',ascending=False).reset_index(drop=True).head(10)
    map_transaction_df5.index = map_transaction_df5.index + 1
    map_transaction_df5.index = map_transaction_df5.index.rename("Sl.No")

    map_transaction_df4.index = map_transaction_df4.index + 1
    map_transaction_df4.index = map_transaction_df4.index.rename("Sl.No")
    
    map_amount_sum = int(map_transaction_df4['Total_payment_value'].sum())
    map_total_transaction = map_transaction_df3['Total_payment_value'].sum()
    map_total_transaction_count = map_transaction_df3['All_Transactions'].sum()
    map_avg_amount= int(map_total_transaction/ map_total_transaction_count)

    st.subheader(f"{selected_year}_{selected_quater} Transaction summary")
    st.write(f"Total Transaction = **₹{map_total_transaction:,}**")
    st.write(f"Total Transaction count = **{map_total_transaction_count:,}**")
    st.write(f"Average amount per Transaction = **₹{map_avg_amount }**")
    st.subheader(f'Top 10 States in {selected_year}_{selected_quater}')
    st.dataframe(map_transaction_df5,use_container_width=True)

    fig_map = px.choropleth(
        map_transaction_df1,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        hover_name = 'State',
        hover_data = ['avg_amount','Total_payment_value'],        
        color='All_Transactions',
        color_continuous_scale="plasma",
        title=f"{selected_year}_{selected_quater} Transaction history for each state"
        )
    fig_map.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig_map)
    st.dataframe(map_transaction_df4,use_container_width=True)

    fig_map_transacation = px.treemap(
        map_transaction_df1 , 
        path = ['State','District'], 
        values='Total_payment_value',
        color='Total_payment_value',
        color_continuous_scale="blues",
        title=f"{selected_year}_{selected_quater} Transaction summary for each state"
        )
    fig_map_transacation.update_traces(textinfo='label+value+percent parent')
    st.plotly_chart(fig_map_transacation,use_container_width=True) 

    st.subheader(f"{selected_year}_{selected_quater} Top Transaction by Districts and pincode's for each state")

    tab1, tab3 = st.tabs(["Top District in Each State by selection","Top District in Each State"])
    tab2, tab4 = st.tabs(["Top Pincode's in Each State by selection","Top Pincode's in Each State"])


    selected_states_tab1 = tab1.selectbox("**Select State for Top Transaction by District**", state)
    selected_states_tab2 = tab2.selectbox("**Select State for Top Transaction by Pincode**", state)    
    
    top_transaction_dist_df1 = top_transaction_df[(top_transaction_df['Year']==selected_year) & (top_transaction_df['Quater']==selected_quater) & (top_transaction_df['State']== selected_states_tab1)].reset_index(drop=True)
    fig_bar_top_dist = px.bar(
        top_transaction_dist_df1.head(10),
        x = 'District',
        y = 'Districts_total_amount',
        color='avg_amount_district',
        text_auto='.2s',
        color_continuous_scale="plasma",
        title=f'Top District in "{selected_states_tab1}_{selected_quater}_{selected_year}"'
        )
    fig_bar_top_dist.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    tab1.plotly_chart(fig_bar_top_dist) 

    top_transaction_pincode_df1 = top_transaction_df[(top_transaction_df['Year']==selected_year) & (top_transaction_df['Quater']==selected_quater) & (top_transaction_df['State']== selected_states_tab2)].reset_index(drop=True)
    top_transaction_pincode_df1.index = top_transaction_pincode_df1.index + 1

    top_transaction_pincode_df1.index = top_transaction_pincode_df1.index.rename("Sl.No")

    tab2.markdown(f'**Top Pincodes in "{selected_states_tab2}_{selected_quater}_{selected_year}"**')
    tab2.dataframe(top_transaction_pincode_df1[['Postalcodes','Postalcodes_total_amount','avg_amount_postcode']],use_container_width=True)


    for i in state:
        top_transaction_dist_df3 = top_transaction_df[(top_transaction_df['Year']==selected_year) & (top_transaction_df['Quater']==selected_quater) & (top_transaction_df['State']== i)].reset_index(drop=True)
        fig_bar_top_dist = px.bar(
            top_transaction_dist_df3.head(10),
            x = 'District',
            y = 'Districts_total_amount',
            color='avg_amount_district',
            text_auto='.2s',
            color_continuous_scale="plasma",
            title=f'Top District in "{i}_{selected_quater}_{selected_year}"'
            )
        fig_bar_top_dist.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        tab3.plotly_chart(fig_bar_top_dist) 

    for i in state:
        top_transaction_pincode_df4 = top_transaction_df[(top_transaction_df['Year']==selected_year) & (top_transaction_df['Quater']==selected_quater) & (top_transaction_df['State']== i)].reset_index(drop=True)
        top_transaction_pincode_df4.index = top_transaction_pincode_df4.index + 1

        top_transaction_pincode_df4.index = top_transaction_pincode_df4.index.rename("Sl.No")

        tab4.markdown(f'**Top Pincodes in "{i}_{selected_quater}_{selected_year}"**')
        tab4.dataframe(top_transaction_pincode_df4[['Postalcodes','Postalcodes_total_amount','avg_amount_postcode']],use_container_width=True)



elif Payments == 'Users':
    aggregated_user_sum =aggregated_user_df.groupby(by='Year').sum().reset_index()
    
    registered_users = aggregated_user_sum['Registered_PhonePe_users'].sum()


    fig_bar_aggregated_user_sum = px.bar(
        aggregated_user_sum,
        x = 'Year',
        y = 'Registered_PhonePe_users',
        color='PhonePe_app_opens',
        text_auto='.2s',
        color_continuous_scale="plasma",
        title="Registered Users over the years"
        )
    fig_bar_aggregated_user_sum.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_bar_aggregated_user_sum)
    st.subheader(f'**Total Registered Users = {registered_users:,}**')


    aggregated_user_df1 = aggregated_user_df[(aggregated_user_df['Year'] == selected_year) & (aggregated_user_df['Quater'] == selected_quater) ]

    fig = px.choropleth(
        aggregated_user_df1,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        hover_name = 'State',
        hover_data = ['PhonePe_app_opens'],        
        color='Registered_PhonePe_users',
        color_continuous_scale="plasma",
        title=f'Registered Users till {selected_quater}_{selected_year}'
    )
    fig.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig)

    fig_agg_pie= px.pie(
        aggregated_user_df1,
        values='Registered_PhonePe_users',
        names='State',
        title=f'Registered Users till _{selected_quater}_{selected_year}',
        hover_data = ['PhonePe_app_opens'] )
    fig_agg_pie.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig_agg_pie)

    aggregated_user_df2 = aggregated_user_df.groupby(['State']).sum().reset_index()

    year = list(aggregated_user_df['Year'].unique())

    fig_user = px.choropleth(
        aggregated_user_df2,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        hover_name = 'State',
        hover_data = ['PhonePe_app_opens'],        
        color='Registered_PhonePe_users',
        color_continuous_scale="plasma",
        title=f'Registered Users till {year[-1]}'
    )
    fig_user.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig_user)


    st.subheader(f"Sum of User details for Each State till {year[-1]} ")

    fig_bar_aggregated_user = px.bar(
        aggregated_user_df2,
        x = 'State',
        y = 'Registered_PhonePe_users',
        color='PhonePe_app_opens',
        text_auto='.2s',
        color_continuous_scale="plasma",
        )
    fig_bar_aggregated_user.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    
    st.plotly_chart(fig_bar_aggregated_user,use_container_width=True)    


    map_user_df1 = map_user_df[(map_user_df['Year']==selected_year) & (map_user_df['Quater']==selected_quater)].reset_index(drop=True)

    fig_map_user = px.treemap(
        map_user_df1 , 
        path = ['State','District'], 
        values='Total_registered_users',
        color='Total_app_opens',
        color_continuous_scale="Greens",
        title=f"{selected_year}_{selected_quater} Registered Users for each state"
        )
    fig_map_user.update_traces(textinfo='label+value+percent parent')
    st.plotly_chart(fig_map_user)    

    st.subheader(f"{selected_year} {selected_quater} Top Registered Users in Each state by District and pincode") 
    
    tab1, tab3 = st.tabs(["Top District in Each State by selection","Top District in Each State"])
    tab2, tab4 = st.tabs(["Top Pincode's in Each State by selection","Top Pincode's in Each State"])


    selected_states_tab1 = tab1.selectbox("**Select State for Top Transaction by District**", state)
    selected_states_tab2 = tab2.selectbox("**Select State for Top Transaction by Pincode**", state) 
    
    top_user_dist_df1 = top_user_df[(top_user_df['Year']==selected_year) & (top_user_df['Quater']==selected_quater) & (top_user_df['State']== selected_states_tab1)].reset_index(drop=True)
    fig_bar_top_dist = px.bar(
        top_user_dist_df1,
        x = 'District',
        y = 'Districts_registered_user',
        text_auto='.2s',
        color_continuous_scale="plasma",
        title=f'Top District in "{selected_states_tab1}_{selected_quater}_{selected_year}"'
        )
    fig_bar_top_dist.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    tab1.plotly_chart(fig_bar_top_dist)     
    
    top_user_pincode_df1 = top_user_df[(top_user_df['Year']==selected_year) & (top_user_df['Quater']==selected_quater) & (top_user_df['State']== selected_states_tab2)].reset_index(drop=True)
    top_user_pincode_df1.index = top_user_pincode_df1.index + 1

    top_user_pincode_df1.index = top_user_pincode_df1.index.rename("Sl.No")

    tab2.markdown(f'**Top Pincodes in "{selected_states_tab2}_{selected_quater}_{selected_year}"**')
    tab2.dataframe(top_user_pincode_df1[['Postalcodes','Postalcodes_registered_user']],use_container_width=True)

    

    for i in state:
        top_user_dist_df2 = top_user_df[(top_user_df['Year']==selected_year) & (top_user_df['Quater']==selected_quater) & (top_user_df['State']== i)].reset_index(drop=True)
        fig_bar_top_dist = px.bar(
            top_user_dist_df2,
            x = 'District',
            y = 'Districts_registered_user',
            text_auto='.2s',
            color_continuous_scale="plasma",
            title=f'Top District in "{i}_{selected_quater}_{selected_year}"'
            )
        fig_bar_top_dist.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        tab3.plotly_chart(fig_bar_top_dist) 

    for i in state:
        top_user_pincode_df2 = top_user_df[(top_user_df['Year']==selected_year) & (top_user_df['Quater']==selected_quater) & (top_user_df['State']== i)].reset_index(drop=True)
        top_user_pincode_df2.index = top_user_pincode_df2.index + 1

        top_user_pincode_df2.index = top_user_pincode_df2.index.rename("Sl.No")

        tab4.markdown(f'**Top Pincodes in "{i}_{selected_quater}_{selected_year}"**')
        tab4.dataframe(top_user_pincode_df1[['Postalcodes','Postalcodes_registered_user']],use_container_width=True)