import joblib
import pandas as pd
import numpy as np

# loading required objects
train = joblib.load('dataset.gz')
mnb = joblib.load('mnb.gz')
user_final_rating = joblib.load('user_final_rating.gz')
vectorizer = joblib.load('vectorizer.gz')


def get_sentiment_recommendations(user):
    """
    - Predict the sentiment of all the reviews for a product using classifier
    - Group the information over product name
    - Extract total positive ratio to sort the products from most popular to least popular.
    """
    if (user in user_final_rating.index):
        # get top recommendations
        recommendations = list(user_final_rating.loc[user].sort_values(ascending=False)[0:20].index)

        # analyze sentiment of reviews for the recommended products
        temp = train[train.name.isin(recommendations)].copy()
        X = vectorizer.transform(temp["reviews_clean"].values.astype(str))
        temp["predicted_sentiment"] = mnb.predict(X)
        temp = temp[['name', 'predicted_sentiment']]
        temp_grouped = temp.groupby('name', as_index=False).count()
        temp_grouped["pos_review_count"] = temp_grouped.name.apply(lambda x: temp[(temp.name==x) & (temp.predicted_sentiment==1)]["predicted_sentiment"].count())
        temp_grouped["total_review_count"] = temp_grouped['predicted_sentiment']
        temp_grouped['pos_sentiment_percent'] = np.round(temp_grouped["pos_review_count"]/temp_grouped["total_review_count"]*100,2)
        temp_grouped.drop('predicted_sentiment', axis=1, inplace=True)

        # filter out top 5 products and update column names
        sorted_top_5 = temp_grouped.sort_values('pos_sentiment_percent', ascending=False)[0:5]
        top_5_products = pd.merge(
            train[['name', 'brand', 'manufacturer']].drop_duplicates(),
            sorted_top_5[['name', 'pos_sentiment_percent']], on='name'
        ).sort_values('pos_sentiment_percent', ascending=False).rename(
            columns={
                'pos_sentiment_percent': 'Positive Sentiment %',
                'name': 'Name',
                'brand': 'Brand',
                'manufacturer': 'Manufacturer'
            }
        ).reset_index(drop=True)
        top_5_products.index = np.arange(1, len(top_5_products)+1)
        top_5_products.columns.name = 'S. No.'

        # return formatted html response
        return dataframe_to_html(top_5_products)

    else:
        return f"Username {user} doesn't exist"


def dataframe_to_html(df):
    """
    Convert the dataframe into a nice presentable table for the end user
    """
    html_resp = df.to_html().replace(
        'table border="1"', 'table border="1" style="border-collapse:collapse"'
    ).replace(
        'tr style="text-align: right;"', 'tr style="text-align: center; background-color: beige;"'
    ).replace(
        '<td>', '<td style="text-align:center; padding: 0.5em;">'
    ).replace(
        '<th>', '<th style="text-align:center; padding: 0.3em;">'
    )

    return html_resp


if __name__ == "__main__":
    # user does not exist
    print(get_sentiment_recommendations('does-not-exist'))

    # user exists
    print(get_sentiment_recommendations('00sab00'))
