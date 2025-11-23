import tkinter as tk
from tkinter import ttk, messagebox
import threading
import psycopg2
import webview
from PIL import Image, ImageTk
import requests
from io import BytesIO
import webbrowser
import os
from dotenv import load_dotenv
import hashlib
import bcrypt
try:
    from tkinterweb import HtmlFrame
    TKINTERWEB_AVAILABLE = True
except ImportError:
    TKINTERWEB_AVAILABLE = False

try:
    from cefpython3 import cefpython as cef
    import platform
    CEF_AVAILABLE = True
except ImportError:
    CEF_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Global flag to track login status
login_successful = threading.Event()

# Avatar URL
AVATAR_URL = "https://stunning-crisp-51ccb2.netlify.app/"

# ============================================================
#   CONFIG DB - Docker PostgreSQL
# ============================================================
DB_CONFIG = {
    "host": os.getenv("DB_HOST", os.getenv("POSTGRES_HOST", "localhost")),
    "port": int(os.getenv("DB_PORT", os.getenv("POSTGRES_PORT", "5432"))),
    "dbname": os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "medico_db")),
    "user": os.getenv("DB_USER", os.getenv("POSTGRES_USER", "admin")),
    "password": os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "admin123"))
}

def db_connect():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        error_msg = f"Error de conexión a la base de datos:\n{str(e)}\n\nVerifica que:\n- Docker esté corriendo\n- PostgreSQL esté accesible en {DB_CONFIG['host']}:{DB_CONFIG['port']}\n- Las credenciales en .env sean correctas"
        messagebox.showerror("Error de Conexión", error_msg)
        return None
    except Exception as e:
        messagebox.showerror("DB Error", f"Error inesperado: {str(e)}")
        return None


# ============================================================
#   COLORS
# ============================================================
BG1 = "#0b1220"
BG2 = "#0a1730"
CARD = "#1a2333"
TEXT = "#e6f0ff"
MUTED = "#9bb3d1"
PRIMARY = "#52e5ff"
DANGER = "#ff5c7c"


# ============================================================
#   FILE PREVIEW
# ============================================================
def open_preview(url, tipo):
    modal = tk.Toplevel()
    modal.title("Vista de archivo")
    modal.geometry("700x600")
    modal.configure(bg=BG2)

    tk.Label(modal, text=tipo, fg=TEXT, bg=BG2,
             font=("Segoe UI", 18, "bold")).pack(pady=10)

    if tipo.lower() in ["imagen", "jpg", "png", "jpeg"]:
        try:
            img_data = requests.get(url).content
            img = Image.open(BytesIO(img_data))
            img = img.resize((650, 500))
            img_tk = ImageTk.PhotoImage(img)

            label = tk.Label(modal, image=img_tk, bg=BG2)
            label.image = img_tk
            label.pack()
        except:
            tk.Label(modal, text="No se pudo cargar la imagen.",
                     fg=TEXT, bg=BG2).pack(pady=30)

    else:
        tk.Label(modal, text="No se puede renderizar PDF aquí.\nAbriré el archivo en el navegador.",
                 fg=TEXT, bg=BG2, font=("Segoe UI", 14)).pack(pady=30)
        tk.Button(modal, text="Abrir PDF", bg=PRIMARY, fg="black",
                  command=lambda: webbrowser.open(url),
                  padx=20, pady=10).pack()


# ============================================================
#   LOGIN
# ============================================================
def validate_user(username, password):
    conn = db_connect()
    if not conn:
        return None, "No se pudo conectar a la base de datos."

    try:
        cur = conn.cursor()

        # First, get the user by username to retrieve password_hash
        cur.execute("""
            SELECT id, username, rol_id, password_hash FROM usuario
            WHERE username = %s
        """, (username,))

        row = cur.fetchone()
        
        if not row:
            conn.close()
            return None, f"Usuario '{username}' no encontrado en la base de datos."

        user_id, db_username, rol_id, stored_hash = row[0], row[1], row[2], row[3]
        
        if not stored_hash:
            conn.close()
            return None, "El usuario no tiene password_hash configurado."

        # Check if it's a bcrypt hash (starts with $2a$, $2b$, or $2y$)
        password_valid = False
        
        if stored_hash.startswith(('$2a$', '$2b$', '$2y$')):
            # It's a bcrypt hash - use bcrypt to verify
            try:
                password_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            except Exception as e:
                password_valid = False
        else:
            # Try other hash algorithms (SHA256, MD5, SHA1)
            password_hash_sha256 = hashlib.sha256(password.encode('utf-8')).hexdigest()
            password_hash_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
            password_hash_sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest()
            
            stored_hash_lower = stored_hash.lower()
            stored_hash_upper = stored_hash.upper()
            
            password_valid = (
                stored_hash == password_hash_sha256 or
                stored_hash == password_hash_md5 or
                stored_hash == password_hash_sha1 or
                stored_hash_lower == password_hash_sha256 or
                stored_hash_lower == password_hash_md5 or
                stored_hash_lower == password_hash_sha1 or
                stored_hash_upper == password_hash_sha256.upper() or
                stored_hash_upper == password_hash_md5.upper() or
                stored_hash_upper == password_hash_sha1.upper()
            )

        if password_valid:
            conn.close()
            return {"id": user_id, "username": db_username, "rol": rol_id}, None
        else:
            conn.close()
            return None, "Contraseña incorrecta. Verifica tu contraseña."
        
    except Exception as e:
        if conn:
            conn.close()
        return None, f"Error al validar usuario: {str(e)}"


def get_patient_by_user(user_id):
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, fecha_nacimiento, sexo, altura, peso,
               estilo_vida, id_tipo_sangre, id_ocupacion,
               id_estado_civil, id_medico_gen
        FROM paciente
        WHERE usuario_id = %s
    """, (user_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None
    return {
        "id": row[0],
        "fecha_nac": str(row[1]),
        "sexo": row[2],
        "altura": str(row[3]),
        "peso": str(row[4]),
        "estilo": row[5],
        "tipo_sangre": row[6],
        "ocupacion": row[7],
        "estado_civil": row[8],
        "medico_gen": row[9]
    }


def get_general_info(patient_id):
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT u.correo, u.telefono
        FROM usuario u 
        JOIN paciente p ON p.usuario_id = u.id
        WHERE p.id = %s
    """, (patient_id,))
    u = cur.fetchone()

    cur.execute("""
        SELECT tipo FROM tipo_sangre WHERE id = (
            SELECT id_tipo_sangre FROM paciente WHERE id = %s
        );
    """, (patient_id,))
    sangre = (cur.fetchone() or ["N/A"])[0]

    cur.execute("""
        SELECT nombre FROM ocupacion WHERE id = (
            SELECT id_ocupacion FROM paciente WHERE id = %s
        );
    """, (patient_id,))
    ocup = (cur.fetchone() or ["N/A"])[0]

    cur.execute("""
        SELECT nombre FROM estado_civil WHERE id = (
            SELECT id_estado_civil FROM paciente WHERE id = %s
        );
    """, (patient_id,))
    civil = (cur.fetchone() or ["N/A"])[0]

    # Try to get address, but handle if table doesn't exist
    d = None
    try:
        cur.execute("""
            SELECT calle, numero_ext, numero_int
            FROM direccion_paciente
            WHERE paciente_id = %s
        """, (patient_id,))
        d = cur.fetchone()
    except Exception as e:
        # Table doesn't exist or other error, skip address
        # Check if it's an undefined table error
        error_str = str(e)
        if "direccion_paciente" in error_str.lower() or "does not exist" in error_str.lower():
            pass  # Table doesn't exist, that's okay
        else:
            pass  # Other error, skip address

    conn.close()

    # Format address if available
    address = "N/A"
    if d and len(d) >= 3 and d[0] and d[1]:
        address = f"{d[0]} #{d[1]}"
        if d[2]:
            address += f" Int:{d[2]}"

    return {
        "Correo": u[0] if u else "N/A",
        "Teléfono": u[1] if u else "N/A",
        "Tipo de Sangre": sangre,
        "Ocupación": ocup,
        "Estado Civil": civil,
        "Dirección": address
    }


def get_files(patient_id):
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT a.tipo, a.url, aa.descripcion
        FROM archivo_asociacion aa
        JOIN archivo a ON a.id = aa.archivo_id
        WHERE aa.entidad = 'paciente' AND aa.entidad_id = %s
    """, (patient_id,))

    rows = cur.fetchall()
    conn.close()

    return [(desc or "Archivo", tipo, url) for tipo, url, desc in rows]


# ============================================================
#   DASHBOARD
# ============================================================
def show_dashboard(root, user, paciente):

    for w in root.winfo_children():
        w.destroy()

    root.configure(bg=BG1)

    # Header with welcome message
    header = tk.Frame(root, bg=BG2, height=80)
    header.pack(fill="x", padx=0, pady=0)
    header.pack_propagate(False)
    
    header_content = tk.Frame(header, bg=BG2)
    header_content.pack(fill="both", expand=True, padx=30, pady=15)
    
    welcome_text = tk.Label(header_content, 
                           text=f"Bienvenido, {user['username']}", 
                           fg=TEXT, bg=BG2, font=("Segoe UI", 24, "bold"))
    welcome_text.pack(side="left")
    
    # Logout button
    def logout():
        login_successful.clear()
        show_login(root)
    
    logout_btn = tk.Button(header_content, text="Cerrar Sesión", 
                          bg=DANGER, fg="white", font=("Segoe UI", 11, "bold"),
                          padx=20, pady=8, command=logout, relief="flat",
                          cursor="hand2", activebackground="#ff3d5c")
    logout_btn.pack(side="right")

    # Main container
    main_container = tk.Frame(root, bg=BG1)
    main_container.pack(fill="both", expand=True, padx=20, pady=20)

    # LEFT PANEL w/ scroll
    left_panel = tk.Frame(main_container, bg=CARD)
    left_panel.pack(side="left", fill="both", expand=True)
    
    main_frame = tk.Frame(left_panel, bg=CARD)
    main_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(main_frame, bg=CARD, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    scroll_frame = tk.Frame(canvas, bg=CARD)
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    def update_region(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scroll_frame.bind("<Configure>", update_region)

    def wheel(e):
        canvas.yview_scroll(int(-e.delta / 120), "units")
    canvas.bind_all("<MouseWheel>", wheel)

    # TABS with better styling
    active_tab = tk.StringVar(value="paciente")

    tab_frame = tk.Frame(scroll_frame, bg=CARD)
    tab_frame.pack(fill="x", pady=20, padx=15)

    def switch(tab):
        active_tab.set(tab)
        # Update button styles
        if tab == "paciente":
            paciente_btn.config(bg=PRIMARY, fg="black")
            partes_btn.config(bg=BG2, fg=TEXT)
        else:
            paciente_btn.config(bg=BG2, fg=TEXT)
            partes_btn.config(bg=PRIMARY, fg="black")
        draw()

    paciente_btn = tk.Button(tab_frame, text="📋 Información del Paciente", 
                            fg="black", bg=PRIMARY, relief="flat",
                            font=("Segoe UI", 14, "bold"), padx=25, pady=12,
                            command=lambda: switch("paciente"), cursor="hand2",
                            activebackground="#3dd5f3")
    paciente_btn.pack(side="left", padx=5)

    partes_btn = tk.Button(tab_frame, text="📁 Archivos Médicos", 
                          fg=TEXT, bg=BG2, relief="flat",
                          font=("Segoe UI", 14, "bold"), padx=25, pady=12,
                          command=lambda: switch("partes"), cursor="hand2",
                          activebackground=BG1)
    partes_btn.pack(side="left", padx=5)

    # Content
    content = tk.Frame(scroll_frame, bg=CARD)
    content.pack(fill="both", expand=True)

    def clear():
        for w in content.winfo_children():
            w.destroy()

    def draw():
        clear()

        if active_tab.get() == "paciente":
            # Title with icon
            title_frame = tk.Frame(content, bg=CARD)
            title_frame.pack(fill="x", pady=(0, 20))
            tk.Label(title_frame, text="👤 Información del Paciente",
                     fg=TEXT, bg=CARD,
                     font=("Segoe UI", 26, "bold")).pack(side="left")

            # Summary card with better styling
            card = tk.Frame(content, bg=BG2, relief="flat")
            card.pack(fill="x", pady=15, padx=10)
            
            # Add padding inside card
            card_inner = tk.Frame(card, bg=BG2)
            card_inner.pack(fill="both", expand=True, padx=20, pady=15)

            info_items = [
                ("Sexo", paciente['sexo']),
                ("Fecha de Nacimiento", paciente['fecha_nac']),
                ("Altura", f"{paciente['altura']} cm"),
                ("Peso", f"{paciente['peso']} kg")
            ]
            
            for label, value in info_items:
                item_frame = tk.Frame(card_inner, bg=BG2)
                item_frame.pack(fill="x", pady=8)
                tk.Label(item_frame, text=f"{label}:", fg=MUTED, bg=BG2, 
                        font=("Segoe UI", 12), width=20, anchor="w").pack(side="left")
                tk.Label(item_frame, text=value, fg=TEXT, bg=BG2, 
                        font=("Segoe UI", 13, "bold")).pack(side="left")

            # General Info
            info = get_general_info(paciente["id"])

            tk.Label(content, text="📋 Información General",
                     fg=TEXT, bg=CARD, font=("Segoe UI", 22, "bold")
                     ).pack(anchor="w", pady=(30, 15), padx=10)

            # Info cards
            info_card = tk.Frame(content, bg=BG2, relief="flat")
            info_card.pack(fill="x", pady=10, padx=10)
            
            info_inner = tk.Frame(info_card, bg=BG2)
            info_inner.pack(fill="both", expand=True, padx=20, pady=20)

            r = 0
            for k, v in info.items():
                item_frame = tk.Frame(info_inner, bg=BG2)
                item_frame.pack(fill="x", pady=10)
                tk.Label(item_frame, text=k, fg=MUTED, bg=BG2,
                         font=("Segoe UI", 12), width=18, anchor="w").pack(side="left")
                tk.Label(item_frame, text=v, fg=TEXT, bg=BG2,
                         font=("Segoe UI", 13, "bold")).pack(side="left", padx=10)
                r += 1

        else:
            tk.Label(content, text="📁 Archivos Médicos",
                     fg=TEXT, bg=CARD, font=("Segoe UI", 26, "bold")).pack(anchor="w", pady=(0, 20), padx=10)

            files = get_files(paciente["id"])

            if not files:
                empty_frame = tk.Frame(content, bg=CARD)
                empty_frame.pack(fill="both", expand=True, pady=50)
                tk.Label(empty_frame, text="📭", font=("Segoe UI", 60), 
                        bg=CARD, fg=MUTED).pack()
                tk.Label(empty_frame, text="No hay archivos asociados.",
                         fg=MUTED, bg=CARD, font=("Segoe UI", 16)
                         ).pack(pady=10)
            else:
                for name, tipo, url in files:
                    f = tk.Frame(content, bg=BG2, relief="flat")
                    f.pack(fill="x", pady=10, padx=10)

                    file_info = tk.Frame(f, bg=BG2)
                    file_info.pack(side="left", fill="x", expand=True, padx=20, pady=15)
                    
                    tk.Label(file_info, text=f"📄 {tipo}", fg=PRIMARY, bg=BG2,
                             font=("Segoe UI", 12, "bold")).pack(anchor="w")
                    tk.Label(file_info, text=name, fg=TEXT, bg=BG2,
                             font=("Segoe UI", 13)).pack(anchor="w", pady=2)

                    tk.Button(f, text="Ver archivo", bg=PRIMARY, fg="black",
                              command=lambda u=url, t=tipo: open_preview(u, t),
                              padx=20, pady=10, font=("Segoe UI", 11, "bold"),
                              relief="flat", cursor="hand2",
                              activebackground="#3dd5f3"
                              ).pack(side="right", padx=20, pady=15)

    draw()
    
    # Open avatar after successful login using subprocess
    def open_avatar_after_login():
        """Open avatar in webview after login using subprocess"""
        try:
            import subprocess
            import sys
            import os
            
            # Get path to avatar_window.py script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            avatar_script = os.path.join(script_dir, "avatar_window.py")
            
            # Check if avatar_window.py exists, if not create it
            if not os.path.exists(avatar_script):
                # Create the avatar script
                avatar_script_content = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Separate script to run avatar in webview window"""
import webview
import sys

AVATAR_URL = "{AVATAR_URL}"

if __name__ == "__main__":
    try:
        # Get position from command line arguments if provided
        x = int(sys.argv[1]) if len(sys.argv) > 1 else None
        y = int(sys.argv[2]) if len(sys.argv) > 2 else None
        width = int(sys.argv[3]) if len(sys.argv) > 3 else 600
        height = int(sys.argv[4]) if len(sys.argv) > 4 else 650
        
        window_config = {{
            "title": "Avatar Medico - Asistente Virtual",
            "url": AVATAR_URL,
            "width": width,
            "height": height,
            "background_color": "#000000",
            "resizable": True,
            "min_size": (600, 600)
        }}
        
        if x is not None and y is not None:
            window_config["x"] = x
            window_config["y"] = y
        
        webview.create_window(**window_config)
        webview.start(gui="edgechromium", debug=False)
    except Exception as e:
        print(f"Error: {{e}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
'''
                with open(avatar_script, 'w', encoding='utf-8') as f:
                    f.write(avatar_script_content)
            
            # Get window position
            root.update_idletasks()
            main_x = root.winfo_x()
            main_y = root.winfo_y()
            main_width = root.winfo_width()
            
            # Position window to the right of main window
            window_width = 600
            window_height = 650
            x_position = main_x + main_width + 10
            y_position = main_y
            
            # Run avatar script in separate process (hide console window on Windows)
            if sys.platform == 'win32':
                # Use CREATE_NO_WINDOW to hide the console
                subprocess.Popen(
                    [sys.executable, avatar_script, str(x_position), str(y_position), 
                     str(window_width), str(window_height)],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                subprocess.Popen(
                    [sys.executable, avatar_script, str(x_position), str(y_position), 
                     str(window_width), str(window_height)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        except Exception as e:
            print(f"Error opening avatar: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: open in browser
            webbrowser.open(AVATAR_URL)
    
    # Open avatar after a short delay to ensure dashboard is fully loaded
    root.after(500, open_avatar_after_login)


# ============================================================
#   SHOW LOGIN
# ============================================================
def show_login(root):

    for w in root.winfo_children():
        w.destroy()

    root.configure(bg=BG1)

    # Main container with gradient effect
    main_container = tk.Frame(root, bg=BG1)
    main_container.pack(fill="both", expand=True)

    # Left side with branding
    left_panel = tk.Frame(main_container, bg=BG2)
    left_panel.pack(side="left", fill="both", expand=True, padx=0, pady=0)
    
    brand_frame = tk.Frame(left_panel, bg=BG2)
    brand_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    tk.Label(brand_frame, text="🏥", font=("Segoe UI", 80), bg=BG2, fg=PRIMARY).pack()
    tk.Label(brand_frame, text="Portal del Paciente", font=("Segoe UI", 32, "bold"), 
             bg=BG2, fg=TEXT).pack(pady=10)
    tk.Label(brand_frame, text="Accede a tu información médica", 
             font=("Segoe UI", 14), bg=BG2, fg=MUTED).pack(pady=5)

    # Right side with login form
    right_panel = tk.Frame(main_container, bg=CARD)
    right_panel.pack(side="right", fill="both", expand=True)

    login_frame = tk.Frame(right_panel, bg=CARD)
    login_frame.place(relx=0.5, rely=0.5, anchor="center", width=450)

    # Welcome text
    tk.Label(login_frame, text="Bienvenido", fg=TEXT, bg=CARD,
             font=("Segoe UI", 28, "bold")).pack(pady=(0, 10))
    tk.Label(login_frame, text="Ingresa tus credenciales para continuar", 
             fg=MUTED, bg=CARD, font=("Segoe UI", 12)).pack(pady=(0, 30))

    # Username field
    user_label = tk.Label(login_frame, text="Usuario", fg=TEXT, bg=CARD, 
                         font=("Segoe UI", 11), anchor="w")
    user_label.pack(fill="x", padx=40, pady=(0, 5))
    
    e_user = tk.Entry(login_frame, width=35, font=("Segoe UI", 13), 
                     bg=BG2, fg=TEXT, insertbackground=TEXT, relief="flat", bd=0)
    e_user.pack(padx=40, pady=(0, 20), ipady=10)

    # Password field
    pass_label = tk.Label(login_frame, text="Contraseña", fg=TEXT, bg=CARD, 
                         font=("Segoe UI", 11), anchor="w")
    pass_label.pack(fill="x", padx=40, pady=(0, 5))
    
    e_pass = tk.Entry(login_frame, width=35, font=("Segoe UI", 13), 
                     bg=BG2, fg=TEXT, insertbackground=TEXT, show="•", 
                     relief="flat", bd=0)
    e_pass.pack(padx=40, pady=(0, 30), ipady=10)

    # Login button
    def login():
        username = e_user.get().strip()
        password = e_pass.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos.")
            return
        
        user, error = validate_user(username, password)

        if error:
            messagebox.showerror("Error de inicio de sesión", error)
            return

        paciente = get_patient_by_user(user["id"])
        if not paciente:
            messagebox.showerror("Error", "Este usuario no es un paciente.")
            return

        # Mark login as successful and show dashboard
        login_successful.set()
        show_dashboard(root, user, paciente)

    login_btn = tk.Button(login_frame, text="Iniciar Sesión", bg=PRIMARY, fg="black",
                         font=("Segoe UI", 14, "bold"), pady=12, width=25,
                         command=login, relief="flat", cursor="hand2",
                         activebackground="#3dd5f3", activeforeground="black")
    login_btn.pack(pady=(0, 20))

    # Bind Enter key to login
    e_pass.bind("<Return>", lambda e: login())
    e_user.bind("<Return>", lambda e: e_pass.focus())
    
    # Focus on username field
    e_user.focus_set()


# ============================================================
#   TKINTER THREAD + AVATAR MAIN
# ============================================================
def start_tk():
    root = tk.Tk()
    root.title("Portal del Paciente")
    root.geometry("1500x900")
    show_login(root)
    root.mainloop()


# Start Tkinter in main thread (GUI should be in main thread)
if __name__ == "__main__":
    try:
        start_tk()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
