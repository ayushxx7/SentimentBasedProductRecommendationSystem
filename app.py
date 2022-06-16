from flask import Flask, render_template, request
from model import get_sentiment_recommendations

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    user = request.form.get('user')
    recommendation_resp = get_sentiment_recommendations(user)

    if "doesn't exist" in recommendation_resp.lower():
        return render_template('index.html', user=user)
    else:
        return render_template('index.html', user=user, recommendation=recommendation_resp)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
