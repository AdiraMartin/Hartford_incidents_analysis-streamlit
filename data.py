import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt
import plotly.graph_objects as go

st.set_page_config(page_title='Incidents Analysis in Hartford',  layout='wide', page_icon=':police_car:')
st.title("Incidents Analysis in Hartford, Connecticut: Patterns and Trends from May 2021 to June 2023👮")

data = pd.read_csv('Final_Police_Incidents_2021-May2023.csv')

incidents = data[~data['Neighborhood'].isnull()]

data_neighborhood = list(incidents["Neighborhood"].unique())
data_neighborhood.insert(0, "All")

data_category = list(incidents['Category'].unique())
data_category.insert(0, "All")

with st.sidebar.form(key='my_form'):
    selected_neighborhoods = st.selectbox("Select Neighborhood", data_neighborhood)
    characteristics = st.radio('See Top Crimes in Each Neighborhood', ['Yes', 'No'])
    pressed = st.form_submit_button("Click to run the data")

if characteristics == 'No':
    selected_incidents = st.selectbox("Select Incident", data_category)
else:
    selected_incidents = None


incidents['Lat'] = incidents['Geometry'].astype(str).apply(lambda x: x.split(',')[0].strip('()')).astype(float)
incidents['Long'] = incidents['Geometry'].astype(str).apply(lambda x: x.split(',')[1].strip('()') if len(x.split(',')) > 1 else np.nan).astype(float)

if characteristics == 'Yes':
    if "All" in selected_neighborhoods:
        filtered_data = incidents
    else:
        filtered_data = incidents[incidents['Neighborhood'] == selected_neighborhoods]
else: 
    if "All" in selected_neighborhoods:
        filtered_data = incidents
    else:
        filtered_data = incidents[incidents['Neighborhood'] == selected_neighborhoods]

    if selected_incidents is None or "All" in selected_incidents:
        filtered_data = incidents
    else:
        filtered_data = filtered_data[filtered_data['Category'] == selected_incidents]


if filtered_data is None or len(filtered_data) == 0:
    st.warning("No incidents of the selected category in this neighborhood.")
else:


    # Kotak Total Incidents

    total_incidents = aggregated_data['cases'].sum()

    t1, t2, t3, t4, t5 = st.columns([1,1,1,1,1])

    t1.write('')
    t2.write('')
    t3.metric('Total Incidents',total_incidents)
    t4.write('')
    t5.write('')


    # Kotak Top Crimes
    top_crime = pd.read_csv('top_crime.csv')

    if pressed and characteristics == 'Yes' and selected_neighborhoods != 'All':
        selected_top_crime = top_crime[top_crime['Neighborhood'] == selected_neighborhoods]
        if not selected_top_crime.empty:
            for index, row in selected_top_crime.iterrows():
                top_crime_1 = row['Top Crime 1']
                worried_time_1 = row['Worried Time 1']
                top_crime_2 = row['Top Crime 2']
                worried_time_2 = row['Worried Time 2']
                top_crime_3 = row['Top Crime 3']
                worried_time_3 = row['Worried Time 3']

                # Define the grid layout
                t1, t2, t3, t4, t5 = st.columns([0.05, 1, 1, 1, 0.05])

                # Display the components in the grid layout
                t1.empty()

                # Define Markdown strings for each top crime
                top_crime_1_text = (
                    f"<h3 style='text-align: center;'>Top Crime 1</h3>\n"
                    f"<p align='center'>{top_crime_1}\n\n"
                    f"<p align='center'><span style='color: #FF8080; font-weight: bold;'>Worried Time</span>\n" 
                    f"<p align='center'>{worried_time_1}</p>\n"
                )

                top_crime_2_text = (
                    f"<h3 style='text-align: center;'>Top Crime 2</h3>\n"
                    f"<p align='center'>{top_crime_2}\n\n"
                    f"<p align='center'><span style='color: #FF8080; font-weight: bold;'>Worried Time</span>\n" 
                    f"<p align='center'>{worried_time_2}</p>\n"
                )

                top_crime_3_text = (
                    f"<h3 style='text-align: center;'>Top Crime 3</h3>\n"
                    f"<p align='center'>{top_crime_3}\n\n"
                    f"<p align='center'><span style='color: #FF8080; font-weight: bold;'>Worried Time</span>\n"
                    f"<p align='center'>{worried_time_3}</p>\n"
                )


                # Display Top Crime 1
                t2.empty()
                t2.markdown(top_crime_1_text, unsafe_allow_html=True)
                t2.empty()

                # Display Top Crime 2
                t3.empty()
                t3.markdown(top_crime_2_text, unsafe_allow_html=True)
                t3.empty()

                # Display Top Crime 3
                t4.empty()
                t4.markdown(top_crime_3_text, unsafe_allow_html=True)
                t4.empty()

                t5.empty()


    # Seasonal incidents

    st.header('Seasonal Incidents')

    filtered_data['Date'] = pd.to_datetime(filtered_data['Date'])
    filtered_data['month'] = filtered_data['Date'].dt.to_period('M')
    filtered_data['month'] = filtered_data['month'].dt.strftime('%b')

    import calendar

    def get_season(date):
        month = date.month
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Autumn'

    filtered_data['Season'] = filtered_data['Date'].apply(get_season)




    order_season = ['Winter', 'Autumn', 'Spring', 'Summer']
    seasonal = filtered_data.groupby(['Season']).agg(
        cases=('CaseNum', 'count')).reset_index()
    st.bar_chart(data=seasonal, x='Season', y='cases', use_container_width=True)



    with st.expander("Fun Fact"):
        st.markdown(
            """
            <div style="background-color: #f0f5ff; padding: 10px; border-radius: 5px;">
            <small>Did you know?
            Higher temperatures can affect a person's emotional and psychological state. Hot temperatures can increase restlessness, fatigue, and irritability, which can in turn influence a person's behavior and increase the likelihood of criminal actions. But The relationship between temperature and crime is complex and can be influenced by various other factors as well. </small>
            </div>
            """,
            unsafe_allow_html=True
        )



    # Daily incidents
    st.header('Daily Incidents')
    filtered_data['day_name'] = filtered_data['Date'].dt.day_name()

    daily_data = filtered_data.groupby(['day_name']).size().reset_index(name='cases_daily')

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    chart = alt.Chart(daily_data).mark_bar().encode(
        x=alt.X('day_name:O', sort=day_order),
        y='cases_daily'
    )

    st.altair_chart(chart, use_container_width=True)



    # Hourly Incidents
    st.header('Hourly Incidents')

    filtered_data['day'] = filtered_data['day_name'].apply(lambda x: 'weekend' if x in ['Saturday', 'Sunday'] else 'weekday')
    filtered_data['hour_digit'] = filtered_data['Time'].map(lambda x: int(str(x)[:2]))

    hourly_incidents = filtered_data.groupby(['day', 'hour_digit']).size().reset_index(name='cases_hourly')

    # Calculate the total cases for each hour
    total_cases_hourly = hourly_incidents.pivot(index='hour_digit', columns='day', values='cases_hourly')
    total_cases_hourly = total_cases_hourly.fillna(0)  # Replace NaN values with 0

    # Determine if weekend incidents are higher than weekday incidents for each hour
    if 'weekend' in total_cases_hourly.columns:
        higher_weekend_hour = total_cases_hourly[total_cases_hourly['weekend'] > total_cases_hourly['weekday']].index.tolist()
    else:
        higher_weekend_hour = []

    # Define the base bar chart
    base_chart = alt.Chart(hourly_incidents).mark_bar().encode(
        x="hour_digit:N",
        y="cases_hourly:Q",
        xOffset="day:N",
        color="day:N"
    )

    # Create a separate chart to display arrow markers for higher weekend incidents
    arrow_chart = alt.Chart(hourly_incidents.loc[hourly_incidents['hour_digit'].isin(higher_weekend_hour)]).mark_text(
        align='center',
        baseline='middle',
        dx=0,
        dy=-10,
        fontSize=12,
        fontWeight='bold',
        text='⇩'
    ).transform_filter(
        alt.datum.day == 'weekend'
    ).encode(
        x="hour_digit:N",
        y="cases_hourly:Q"
    )

    # Combine the base chart and the arrow chart
    chart = (base_chart + arrow_chart).configure_view(
        stroke=None
    )

    # Display the chart
    st.altair_chart(chart, use_container_width=True)

    if higher_weekend_hour:
        if selected_incidents is not None:
            st.info(f"In a week, there are fewer weekend days, but the incidents {selected_incidents} during this hour are higher compared to weekdays. Therefore, extra attention is needed during this hour on weekends, without neglecting the important time periods with the highest number of incidents.")
        else:
            st.info("In a week, there are fewer weekend days, but the incidents during this hour are higher compared to weekdays. Therefore, extra attention is needed during this hour on weekends, without neglecting the important time periods with the highest number of incidents.")
    else:
        if selected_incidents is not None:
            st.info(f"It is important to pay attention to the hour with the highest {selected_incidents} incidents as it may indicate a higher risk of crime.")
        else:
            st.info("It is important to pay attention to the hour with the highest incidents as it may indicate a higher risk of crime.")

    # Aggregate Hourly Incidents

    def get_time_label(hour):
        if hour >= 6 and hour <= 8:
            return 'Early Morning Commute (6-8 AM)'
        elif hour >= 9 and hour <= 11:
            return 'Before Lunch Break (9-11 AM)'
        elif hour >= 12 and hour <= 14:
            return 'During Lunch Break (12-2 PM)'
        elif hour >= 15 and hour <= 17:
            return 'After Lunch Break (3-5 PM)'
        elif hour >= 18 and hour <= 20:
            return 'Evening Commute (6-8 PM)'
        elif hour >= 21 and hour <= 23:
            return 'After-Work Activities (9-11 PM)'
        elif hour >= 0 and hour <= 2:
            return 'Late Night (12-2 AM)'
        elif hour >= 3 and hour <= 5:
            return 'Early Morning/Dawn (3-5 AM)'
        else:
            return 'Other'


    filtered_data['time_aggregation'] = filtered_data['hour_digit'].apply(get_time_label)

    time_agg_incidents = filtered_data.groupby(['day', 'time_aggregation']).size().reset_index(name='cases')

    time_categories = ['Early Morning Commute (6-8 AM)', 'Before Lunch Break (9-11 AM)', 'During Lunch Break (12-2 PM)',
                    'After Lunch Break (3-5 PM)', 'Evening Commute (6-8 PM)', 'After-Work Activities (9-11 PM)',
                    'Late Night (12-2 AM)', 'Early Morning/Dawn (3-5 AM)']


    chart = alt.Chart(time_agg_incidents).mark_bar().encode(
    x=alt.X('time_aggregation', axis=alt.Axis(labelAngle=0), sort=time_categories),
    xOffset='day',
    y=alt.Y('cases', axis=alt.Axis(grid=False)),
    color='day'
    ).configure_view(
        stroke=None,
    )
    chart

    # Determine the most frequent time aggregation categories
    most_frequent_time_aggs = filtered_data['time_aggregation'].value_counts()
    max_freq = most_frequent_time_aggs.max()
    most_frequent_time_agg = most_frequent_time_aggs[most_frequent_time_aggs == max_freq].index.tolist()

    # Create the st.info message
    if len(most_frequent_time_agg) > 1:
        time_agg_text = f"{' and '.join(most_frequent_time_agg)} are the periods"
    else:
        time_agg_text = f"{most_frequent_time_agg[0]} is the period"

    info_message = f"Based on the data, it is evident that crimes occur predominantly during {time_agg_text} when crimes are most pronounced. It is crucial to remain vigilant and prioritize personal safety during these times by taking necessary precautions."

    # Display the st.info message
    st.info(info_message)


    # Additional information about crime patterns during midday
    with st.expander("Fun Fact"):
        st.markdown(
            """
            <div style="background-color: #f0f5ff; padding: 10px; border-radius: 5px;">
            <small>
            In this data, it is noticeable that the majority of incidents occur during working hours, specifically before lunch (9-11 AM), during lunch (12-2 PM), and after lunch (3-5 PM). This observation aligns with the routine activity approach, which suggests that crime is more likely to occur during midday due to the convergence of three elements: a motivated offender, suitable targets, and the absence of capable guardians. During midday, there may be an increase in potential offenders who are active and looking for opportunities to commit crimes. Additionally, there may be more potential targets available during this time, such as unattended homes or businesses        </div>
            """,
            unsafe_allow_html=True
        )


    if pressed and characteristics == 'Yes':
        offense = filtered_data[filtered_data['Category'] != 'Not Criminal'].copy()
        neighborhood_crime_top_agg = offense.groupby(['Neighborhood', 'Category', 'time_aggregation']).size().reset_index(name='Cases')


        # Group the DataFrame by 'Neighborhood'
        grouped_neighborhood = neighborhood_crime_top_agg.groupby('Neighborhood')

        # Initialize an empty DataFrame to store the results
        top_categories_df = pd.DataFrame(columns=['Neighborhood', 'Category', 'time_aggregation', 'Cases'])
        top_crimes_list = []

        # Iterate over each group
        for neighborhood, group_df in grouped_neighborhood:
            # Sort the group by 'Cases' column in descending order
            sorted_group = group_df.sort_values('Cases', ascending=False)

            # Retrieve the top 3 categories with the highest cases
            top_categories = sorted_group.head(3)

            # Check if there are any duplicate time_aggregation values
            if top_categories['time_aggregation'].nunique() != len(top_categories):
                # Get the category with the highest cases
                highest_cases_category = top_categories.loc[top_categories['Cases'].idxmax(), 'Category']

                # Update the category for rows with duplicate time_aggregation values
                duplicated_time_agg = top_categories['time_aggregation'].duplicated(keep=False)
                top_categories.loc[duplicated_time_agg, 'Category'] = highest_cases_category

            # Append the top categories to the results DataFrame
            top_categories_df = pd.concat([top_categories_df, top_categories], ignore_index=True)

            # Extract the top categories and worried times
            top_crime_1 = top_categories.iloc[0]['Category']
            worried_time_1 = top_categories.iloc[0]['time_aggregation']
            top_crime_2 = top_categories.iloc[1]['Category']
            worried_time_2 = top_categories.iloc[1]['time_aggregation']
            top_crime_3 = top_categories.iloc[2]['Category']
            worried_time_3 = top_categories.iloc[2]['time_aggregation']

            # Create a dictionary for the top crimes
            top_crimes_dict = {
                'Neighborhood': neighborhood,
                'Top Crime 1': top_crime_1,
                'Worried Time 1': worried_time_1,
                'Top Crime 2': top_crime_2,
                'Worried Time 2': worried_time_2,
                'Top Crime 3': top_crime_3,
                'Worried Time 3': worried_time_3
                }
            
            # Append the dictionary to the list
            top_crimes_list.append(top_crimes_dict)

        # Create the top crimes DataFrame from the list of dictionaries
        top_crimes_df = pd.DataFrame(top_crimes_list)

        # Filter the DataFrame based on the selected neighborhood
        if selected_neighborhoods != 'All':
            top_categories_df = top_categories_df[top_categories_df['Neighborhood'] == selected_neighborhoods]
            top_crimes_df = top_crimes_df[top_crimes_df['Neighborhood'] == selected_neighborhoods]

        # Display the top crimes DataFrame
        st.subheader('Top Crimes Table in Each Neighborhood')
        st.dataframe(top_crimes_df)

    




# Display disclaimer
disclaimer_text = """This app allows users to view incidents in Hartford, Connecticut between neighborhoods from May 19, 2021, to June 9, 2023 (when this data was downloaded). 

The following analysis is based on data obtained from https://data.hartford.gov/, a public data repository. The information provided in this analysis is intended for informational purposes only and should not be considered as professional or legal advice. 

The analysis is conducted using the available data, and any conclusions drawn are based on the assumptions and methodologies employed.

Please note that the accuracy, completeness, and reliability of the data cannot be guaranteed. The data may be subject to errors, omissions, or inaccuracies. Furthermore, the analysis is limited to the data provided and may not encompass all relevant factors or variables.
"""

with st.sidebar.expander("Disclaimer"):
    st.write(disclaimer_text)
