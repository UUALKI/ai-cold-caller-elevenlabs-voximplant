import sqlite3
import json
from datetime import datetime

class CallDatabase:
    def __init__(self, db_path='calls.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица звонков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                call_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                duration INTEGER DEFAULT 0,
                status TEXT DEFAULT 'completed',
                
                -- Кто взял трубку
                secretary_name TEXT,
                secretary_mood TEXT,
                
                -- Информация о компании
                company_name TEXT,
                company_industry TEXT,
                
                -- Контакты ЛПР
                lpr_name TEXT,
                lpr_position TEXT,
                lpr_email TEXT,
                lpr_phone TEXT,
                
                -- Бизнес-информация
                current_carrier TEXT,
                cargo_volume TEXT,
                directions TEXT, -- JSON массив
                pain_points TEXT, -- JSON массив
                
                -- Результат звонка
                outcome TEXT DEFAULT 'pending',
                next_action TEXT,
                follow_up_date TEXT,
                
                -- Дополнительная информация
                objections TEXT, -- JSON массив
                notes TEXT,
                
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_call(self, call_data):
        """Сохранение данных о звонке"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO calls (
                phone_number, duration, status,
                secretary_name, secretary_mood,
                company_name, company_industry,
                lpr_name, lpr_position, lpr_email, lpr_phone,
                current_carrier, cargo_volume, directions, pain_points,
                outcome, next_action, follow_up_date,
                objections, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            call_data.get('phone_number'),
            call_data.get('duration', 0),
            call_data.get('status', 'completed'),
            call_data.get('secretary_name'),
            call_data.get('secretary_mood'),
            call_data.get('company_name'),
            call_data.get('company_industry'),
            call_data.get('lpr_name'),
            call_data.get('lpr_position'),
            call_data.get('lpr_email'),
            call_data.get('lpr_phone'),
            call_data.get('current_carrier'),
            call_data.get('cargo_volume'),
            json.dumps(call_data.get('directions', [])),
            json.dumps(call_data.get('pain_points', [])),
            call_data.get('outcome', 'pending'),
            call_data.get('next_action'),
            call_data.get('follow_up_date'),
            json.dumps(call_data.get('objections', [])),
            call_data.get('notes')
        ))
        
        call_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return call_id
    
    def get_all_calls(self):
        """Получение всех звонков"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM calls ORDER BY call_timestamp DESC
        ''')
        
        columns = [description[0] for description in cursor.description]
        calls = []
        
        for row in cursor.fetchall():
            call = dict(zip(columns, row))
            # Преобразуем JSON поля обратно в списки
            call['directions'] = json.loads(call['directions']) if call['directions'] else []
            call['pain_points'] = json.loads(call['pain_points']) if call['pain_points'] else []
            call['objections'] = json.loads(call['objections']) if call['objections'] else []
            calls.append(call)
        
        conn.close()
        return calls
    
    def get_call_by_id(self, call_id):
        """Получение конкретного звонка"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM calls WHERE id = ?', (call_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            call = dict(zip(columns, row))
            call['directions'] = json.loads(call['directions']) if call['directions'] else []
            call['pain_points'] = json.loads(call['pain_points']) if call['pain_points'] else []
            call['objections'] = json.loads(call['objections']) if call['objections'] else []
        else:
            call = None
        
        conn.close()
        return call
