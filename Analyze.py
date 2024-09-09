import streamlit as st
import requests
from flask import Flask, render_template
import pandas as pd
import altair as alt

# Azure Cognitive Services configuration
AZURE_KEY = '77950da9f3aa4e7382b4c3be0f635c4e'
AZURE_ENDPOINT = 'https://teamshubham.cognitiveservices.azure.com/'
sentiment_url = AZURE_ENDPOINT + "/text/analytics/v3.1/sentiment"

# Header
st.title("Customer Feedback Sentiment Analysis")
st.write("Analyze customer feedback and get real-time sentiment insights.")

# Feedback input (multi-line text area)
feedback = st.text_area("Enter your feedback below:", "")

# A button to trigger analysis
if st.button("Analyze Feedback"):
    if feedback:
        # Prepare data for API call
        headers = {"Ocp-Apim-Subscription-Key": AZURE_KEY, "Content-Type": "application/json"}
        documents = {"documents": [{"id": "1", "language": "en", "text": feedback}]}
        
        # Call Azure Text Analytics API for sentiment analysis
        response = requests.post(sentiment_url, headers=headers, json=documents)
        
        if response.status_code == 200:
            result = response.json()
            sentiment = result['documents'][0]['sentiment']
            scores = result['documents'][0]['confidenceScores']
            
            # Display sentiment result
            st.subheader("Sentiment Result:")
            st.write(f"Sentiment: **{sentiment.capitalize()}**")
            st.write(f"Confidence Scores: Positive: {scores['positive']:.2f}, Neutral: {scores['neutral']:.2f}, Negative: {scores['negative']:.2f}")
            
            # Visualize confidence scores with a bar chart
            score_data = pd.DataFrame({
                'Sentiment': ['Positive', 'Neutral', 'Negative'],
                'Confidence': [scores['positive'], scores['neutral'], scores['negative']]
            })
            st.write("### Confidence Score Visualization")
            chart = alt.Chart(score_data).mark_bar().encode(
                x='Sentiment',
                y='Confidence',
                color='Sentiment'
            )
            st.altair_chart(chart, use_container_width=True)
            
        else:
            st.error("Error occurred while processing the feedback.")
    else:
        st.warning("Please enter feedback to analyze.")

# Feedback history
if 'feedback_list' not in st.session_state:
    st.session_state['feedback_list'] = []

# Store feedback and result
if feedback and response.status_code == 200:
    st.session_state['feedback_list'].append({
        'Feedback': feedback,
        'Sentiment': sentiment,
        'Positive': scores['positive'],
        'Neutral': scores['neutral'],
        'Negative': scores['negative']
    })

# Show history of feedback submissions and analysis
if st.session_state['feedback_list']:
    st.write("### Feedback History")
    feedback_df = pd.DataFrame(st.session_state['feedback_list'])
    st.dataframe(feedback_df)
    
    # Optional: Download feedback data as CSV
    csv = feedback_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Feedback Data as CSV",
        data=csv,
        file_name='feedback_analysis.csv',
        mime='text/csv',
    )
