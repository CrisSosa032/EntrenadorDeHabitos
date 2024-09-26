from flask import Flask, render_template, request, redirect, url_for
from database import create_connection, add_habit, delete_habit, add_progress, update_pet_points, get_all_habits, get_progress_for_habit, get_pet, delete_pet, get_pet_image

from recommendations import get_progress_data, train_recommendation_model, recommend_habits



app = Flask(__name__)

@app.route('/')
def index():
    conn = create_connection()
    cursor = conn.cursor()
    
    # Obtener hábitos y mascota
    cursor.execute('SELECT * FROM habits')
    habits = cursor.fetchall()
    cursor.execute('SELECT * FROM pet')
    pet = cursor.fetchone()
    conn.close()

    # Obtener la imagen según los puntos de la mascota
    pet_image = None
    if pet:
        pet_image = get_pet_image(pet[2])  # Suponiendo que el puntaje está en la columna 3 (índice 2)

    return render_template('index.html', habits=habits, pet=pet, pet_image=pet_image)



@app.route('/recommendations')
def recommendations():
    df = get_progress_data()  # Obtener datos de progreso del usuario
    model, le = train_recommendation_model(df)
    
    # Pasamos df a la función recommend_habits
    recommendations = recommend_habits(model, le, df)

    # Analizar el progreso y generar el mensaje motivacional
    advice = analyze_habit_performance(df)

    return render_template('recommendations.html', recommendations=recommendations, advice=advice)





@app.route('/add_habit', methods=['POST'])
def add_new_habit():
    name = request.form['name']
    frequency = request.form['frequency']
    description = request.form['description']
    add_habit(name, frequency, description)
    return redirect(url_for('index'))

@app.route('/delete_habit/<int:id>')
def remove_habit(id):
    delete_habit(id)
    return redirect(url_for('index'))


#Funcion para el seguimiento de los habitos

@app.route('/add_progress', methods=['POST'])
def add_new_progress():
    habit_id = request.form['habit_id']
    date = request.form['date']
    status = request.form['status']

    # Añadir progreso
    add_progress(habit_id, date, status)
    
    # Verificar y crear la mascota si no existe
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pet')
    pet = cursor.fetchone()
    
    if pet is None:
        # Crear mascota con nombre por defecto y puntos iniciales
        cursor.execute('INSERT INTO pet (name, points) VALUES (?, ?)', ('Pinky', 10))  # Empezamos con 10 puntos
        conn.commit()
    
    conn.close()

    # Actualizar puntos de la mascota
    if status == '1':  # Progreso completado
        pet_image = update_pet_points(10)  # Sumar 10 puntos
    else:  # Progreso no completado
        pet_image = update_pet_points(-10)  # Restar 10 puntos

    return redirect(url_for('index'))



#eliminando la mascota
@app.route('/delete_pet', methods=['POST'])
def remove_pet():
    delete_pet()
    return redirect(url_for('index'))







def analyze_habit_performance(df):
    
    #Analiza el rendimiento del usuario con sus hábitos y ofrece un mensaje motivacional basado en su progreso.
    
    if df.empty:
        return "Aún no has comenzado con tus hábitos. ¡Empieza hoy, el primer paso es el más importante!"

    # Calcula el porcentaje de hábitos completados
    completed_habits = df[df['status'] == 1].shape[0]
    total_habits = df.shape[0]
    completion_rate = completed_habits / total_habits if total_habits > 0 else 0

    # Clasificar el rendimiento y devolver el mensaje adecuado
    if completion_rate > 0.8:
        return "¡Increíble! Has sido muy constante con tus hábitos. ¡Sigue así!"
    elif completion_rate > 0.5:
        return "Estás avanzando, pero podrías ser más regular. ¿Por qué no pruebas crear un entorno que te ayude a no olvidar tus hábitos?"
    else:
        return "No te preocupes si no has sido tan constante. Lo importante es que vuelvas a intentarlo. ¡Haz que sea fácil para ti!"



if __name__ == '__main__':
    app.run(debug=True)



