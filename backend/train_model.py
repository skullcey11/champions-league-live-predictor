import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load the extracted match data
matches = pd.read_csv("data/matches.csv")

print("loaded", matches.shape)

#keep only relevant columns for modeling
required_cols = ["date",'home_team_goal', 'away_team_goal']

df = matches[required_cols].dropna()

#result label #0 home win, 1 draw, 2 away win
def get_result(row):
    if row['home_team_goal'] > row['away_team_goal']:
        return 0  # home win
    elif row['home_team_goal'] < row['away_team_goal']:
        return 2  # away win
    else:
        return 1  # draw
    
df['result'] = df.apply(get_result, axis=1)

# features
X = df[["home_team_goal", "away_team_goal"]]
y = df["result"]

# split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# train a simple Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
# evaluate the model
accuracy = model.score(X_test, y_test)
print(f"Model accuracy: {accuracy:.2f}")
# save the trained model
joblib.dump(model, "match_predictor.pkl")
print("Model training complete. Model saved to 'match_predictor.pkl'.")