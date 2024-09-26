import sqlite3

def create_connection():
    conn = sqlite3.connect('habits.db')
    return conn

# Funciones para manejar los hábitos

def add_habit(name, frequency, description):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO habits (name, frequency, description) VALUES (?, ?, ?)', (name, frequency, description))
    conn.commit()
    conn.close()

def delete_habit(habit_id):
    conn = create_connection()
    cursor = conn.cursor()

    # Eliminar todos los registros de progreso asociados al hábito
    cursor.execute('DELETE FROM progress WHERE habit_id = ?', (habit_id,))

    # Eliminar el hábito
    cursor.execute('DELETE FROM habits WHERE id = ?', (habit_id,))

    conn.commit()
    conn.close()

def get_all_habits():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM habits')
    habits = cursor.fetchall()
    conn.close()
    return habits

# Funciones para manejar el progreso

def add_progress(habit_id, date, status):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO progress (habit_id, date, status) VALUES (?, ?, ?)', (habit_id, date, status))
    conn.commit()
    conn.close()

def get_progress_for_habit(habit_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM progress WHERE habit_id = ?', (habit_id,))
    progress = cursor.fetchall()
    conn.close()
    return progress

# Funciones para manejar la mascota

def get_pet():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pet')
    pet = cursor.fetchone()
    conn.close()
    return pet

def update_pet_points(points_change):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Obtener el ID y los puntos actuales de la mascota
    cursor.execute('SELECT id, points FROM pet')
    pet = cursor.fetchone()  # Obtener el primer registro de la tabla 'pet'
    
    if pet:
        pet_id = pet[0]  # El ID de la mascota
        current_points = pet[1]  # Los puntos actuales de la mascota
        
        # Actualizar los puntos según el cambio, evitando que bajen de 0
        new_points = max(0, current_points + points_change)
        cursor.execute('UPDATE pet SET points = ? WHERE id = ?', (new_points, pet_id))
        conn.commit()
    
    conn.close()

    # Lógica para cambiar la imagen según los puntos
    return get_pet_image(new_points)


def get_pet_image(points):
    """Devuelve el nombre del archivo de imagen según los puntos"""
    if points == 0:
        return "5-removebg-preview.png"  # Imagen para 0 puntos
    elif points >= 10 and points < 70:
        return "1-removebg-preview.png"  # Imagen para 10 puntos
    elif points >= 70 and points < 150:
        return "2-removebg-preview.png"  # Imagen para 70 puntos
    elif points >= 150 and points < 300:
        return "3-removebg-preview.png"  # Imagen para 150 puntos
    else:
        return "4-removebg-preview.png"  # Imagen para 300 puntos

def delete_pet():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pet')
    conn.commit()
    conn.close()
