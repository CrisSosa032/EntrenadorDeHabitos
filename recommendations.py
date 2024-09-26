# recommendation.py

import sqlite3
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier

def get_progress_data():
    conn = sqlite3.connect('habits.db')
    query = '''
    SELECT h.name, p.date, p.status
    FROM habits h
    LEFT JOIN progress p ON h.id = p.habit_id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def prepare_data(df):
    df['status'] = df['status'].fillna(0).astype(int)
    df['date'] = pd.to_datetime(df['date'].fillna(pd.Timestamp('today')))
    df['day_of_week'] = df['date'].dt.dayofweek
    
    le = LabelEncoder()
    df['habit_encoded'] = le.fit_transform(df['name'])
    
    return df, le

def train_recommendation_model(df):
    df, le = prepare_data(df)
    
    X = df[['habit_encoded', 'day_of_week']]
    y = df['status']
    
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(X, y)
    
    return model, le

def recommend_habits(model, le, df):
    """
    Recomendaciones de hábitos en función del modelo y datos de progreso (df).
    """
    day_of_week = pd.to_datetime('today').dayofweek
    habit_names = df['name'].unique()  # Obtener nombres de hábitos desde df en lugar de una lista fija
    habits_encoded = le.transform(habit_names)
    
    recommendations = []
    for habit_encoded in habits_encoded:
        prediction = model.predict([[habit_encoded, day_of_week]])
        if prediction == 1:
            recommendations.append(habit_names[habits_encoded.tolist().index(habit_encoded)])
    
    return recommendations

