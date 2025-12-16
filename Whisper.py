import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import whisper
import os
import threading
import time

class AudioTranscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcriptor de Audio con IA")
        self.root.geometry("730x850")
        self.root.resizable(True, True)
        self.root.configure(bg='#1e1e1e')
        
        # Variables
        self.audio_file = tk.StringVar()
        self.model_size = tk.StringVar(value="base")
        self.language_option = tk.StringVar(value="auto")
        self.is_processing = False
        self.model = None
        self.summary_time = tk.StringVar(value="7")
        
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """Configurar estilos modernos en modo oscuro"""
        style = ttk.Style()
        
        # Paleta de colores modo oscuro
        self.colors = {
            'primary': '#00D4FF',          # Cyan brillante
            'primary_dark': '#00B8E6',     # Cyan oscuro
            'success': '#00E676',          # Verde neón
            'danger': '#FF5252',           # Rojo brillante
            'warning': '#FFB74D',          # Naranja suave
            'background': '#121212',       # Negro profundo
            'surface': '#1e1e1e',          # Gris muy oscuro
            'card': '#2d2d2d',            # Gris oscuro para tarjetas
            'card_hover': '#3d3d3d',      # Gris para hover
            'text': '#ffffff',            # Texto blanco
            'text_secondary': '#b3b3b3',  # Texto gris claro
            'text_muted': '#808080',      # Texto gris
            'border': '#404040',          # Bordes grises
            'input_bg': '#383838',        # Fondo de inputs
            'accent': '#BB86FC'           # Púrpura de acento
        }
        
        # Configurar tema
        style.theme_use('clam')
        
        # Estilo para frames principales (tarjetas)
        style.configure('Card.TFrame', 
                       background=self.colors['card'],
                       relief='flat',
                       borderwidth=0)
        
        # Estilos de texto
        style.configure('Title.TLabel',
                       font=('Segoe UI', 26, 'bold'),
                       foreground=self.colors['text'],
                       background=self.colors['background'])
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 14, 'bold'),
                       foreground=self.colors['text'],
                       background=self.colors['card'])
        
        style.configure('Body.TLabel',
                       font=('Segoe UI', 10),
                       foreground=self.colors['text_secondary'],
                       background=self.colors['card'])
        
        # Estilo para botones principales
        style.configure('Primary.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       foreground='#000000',
                       focuscolor='none',
                       borderwidth=0,
                       relief='flat')
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_dark']),
                           ('!active', self.colors['primary'])])
        
        # Estilo para el progreso
        style.configure('Modern.Horizontal.TProgressbar',
                       troughcolor=self.colors['border'],
                       background=self.colors['primary'],
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
        
    def create_card_frame(self, parent, title=None, **kwargs):
        """Crear un frame con aspecto de tarjeta moderna con efecto glassmorphism"""
        # Frame contenedor con efecto de elevación
        container = tk.Frame(parent, bg=self.colors['background'], **kwargs)
        
        # Frame de sombra (simulada con gradiente)
        shadow = tk.Frame(container, bg='#0d0d0d', height=2)
        shadow.pack(fill='x', pady=(4, 0))
        
        # Frame principal (tarjeta) con bordes redondeados simulados
        card_outer = tk.Frame(container, bg=self.colors['border'], padx=1, pady=1)
        card_outer.pack(fill='both', expand=True)
        
        card = tk.Frame(card_outer, bg=self.colors['card'], padx=25, pady=20)
        card.pack(fill='both', expand=True)
        
        if title:
            title_frame = tk.Frame(card, bg=self.colors['card'])
            title_frame.pack(fill='x', pady=(0, 20))
            
            # Icono y título en línea
            title_label = tk.Label(title_frame, text=title, 
                                  font=('Segoe UI', 14, 'bold'),
                                  fg=self.colors['text'], bg=self.colors['card'])
            title_label.pack(side='left')
            
            # Línea decorativa
            line = tk.Frame(title_frame, height=2, bg=self.colors['primary'])
            line.pack(side='left', fill='x', expand=True, padx=(15, 0))
            
        return container, card
        
    def create_modern_button(self, parent, text, command=None, style='primary', state='normal', **kwargs):
        """Crear botones modernos con efectos"""
        colors = {
            'primary': {'bg': self.colors['primary'], 'fg': '#000000', 'active': self.colors['primary_dark']},
            'success': {'bg': self.colors['success'], 'fg': '#000000', 'active': '#00C853'},
            'warning': {'bg': self.colors['warning'], 'fg': '#000000', 'active': '#FF9800'},
            'secondary': {'bg': self.colors['card_hover'], 'fg': self.colors['text'], 'active': '#4d4d4d'},
            'danger': {'bg': self.colors['danger'], 'fg': '#ffffff', 'active': '#E53935'}
        }
        
        color_config = colors.get(style, colors['primary'])
        
        btn = tk.Button(parent, text=text, command=command, state=state,
                       font=('Segoe UI', 10, 'bold' if style == 'primary' else 'normal'),
                       fg=color_config['fg'], bg=color_config['bg'],
                       activeforeground=color_config['fg'], activebackground=color_config['active'],
                       relief='flat', bd=0, cursor='hand2', 
                       pady=12 if style == 'primary' else 8,
                       **kwargs)
        
        # Efectos hover
        def on_enter(e):
            btn.configure(bg=color_config['active'])
        def on_leave(e):
            if btn['state'] == 'normal':
                btn.configure(bg=color_config['bg'])
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
    def setup_ui(self):
        # Frame principal con color de fondo oscuro
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header con gradiente simulado
        header_frame = tk.Frame(main_container, bg=self.colors['background'])
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Título principal con efecto neón
        title_container = tk.Frame(header_frame, bg=self.colors['background'])
        title_container.pack()
        
        title_label = tk.Label(title_container, text="⚡ Transcriptor de Audio con IA", 
                              font=('Segoe UI', 28, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['background'])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Transcripción inteligente con IA • Versión 1.0 • creado por Pablo", 
                                 font=('Segoe UI', 12), 
                                 fg=self.colors['text_secondary'], bg=self.colors['background'])
        subtitle_label.pack(pady=(5, 0))
        
        # Frame principal con scroll
        canvas = tk.Canvas(main_container, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # --- TARJETA 1: Configuración de archivo ---
        file_container, file_card = self.create_card_frame(scrollable_frame, "📂 Selección de Archivo")
        file_container.pack(fill='x', pady=(0, 20))
        
        tk.Label(file_card, text="Archivo de audio:", 
                font=('Segoe UI', 10), fg=self.colors['text_secondary'], 
                bg=self.colors['card']).pack(anchor='w', pady=(0, 8))
        
        entry_frame = tk.Frame(file_card, bg=self.colors['card'])
        entry_frame.pack(fill='x', pady=(0, 10))
        
        self.file_entry = tk.Entry(entry_frame, textvariable=self.audio_file, 
                                  font=('Segoe UI', 11), relief='flat', 
                                  bg=self.colors['input_bg'], fg=self.colors['text'],
                                  bd=0, highlightthickness=2, insertbackground=self.colors['primary'],
                                  highlightcolor=self.colors['primary'], highlightbackground=self.colors['border'])
        self.file_entry.pack(side='left', fill='x', expand=True, padx=(0, 15), ipady=12)
        
        self.create_modern_button(entry_frame, "📂 Examinar", 
                                 command=self.browse_file).pack(side='right')
        
        # --- TARJETA 2: Configuración del modelo ---
        model_container, model_card = self.create_card_frame(scrollable_frame, "🧠 Configuración del Modelo")
        model_container.pack(fill='x', pady=(0, 20))
        
        # Modelo Whisper
        tk.Label(model_card, text="Modelo Whisper:", 
                font=('Segoe UI', 10), fg=self.colors['text_secondary'], 
                bg=self.colors['card']).pack(anchor='w', pady=(0, 12))
        
        model_frame = tk.Frame(model_card, bg=self.colors['card'])
        model_frame.pack(fill='x', pady=(0, 20))
        
        models = [("⚡ Tiny (Ultra rápido)", "tiny"), ("🚀 Base (Equilibrado)", "base"), 
                 ("🎯 Small (Preciso)", "small"), ("💎 Medium (Superior)", "medium"), ("🏆 Large (Óptimo)", "large")]
        
        for i, (text, value) in enumerate(models):
            rb = tk.Radiobutton(model_frame, text=text, variable=self.model_size, value=value,
                               font=('Segoe UI', 10), bg=self.colors['card'], fg=self.colors['text'],
                               selectcolor=self.colors['primary'], activebackground=self.colors['card'],
                               activeforeground=self.colors['text'], bd=0, highlightthickness=0)
            rb.pack(anchor='w', pady=3)
        
        # Idioma
        tk.Label(model_card, text="Idioma del audio:", 
                font=('Segoe UI', 10), fg=self.colors['text_secondary'], 
                bg=self.colors['card']).pack(anchor='w', pady=(0, 12))
        
        lang_frame = tk.Frame(model_card, bg=self.colors['card'])
        lang_frame.pack(fill='x')
        
        languages = [("🔍 Detección automática", "auto"), 
                    ("🇪🇸 Español", "es"), ("🇺🇸 Inglés", "en")]
        
        for text, value in languages:
            rb = tk.Radiobutton(lang_frame, text=text, variable=self.language_option, value=value,
                               font=('Segoe UI', 10), bg=self.colors['card'], fg=self.colors['text'],
                               selectcolor=self.colors['primary'], activebackground=self.colors['card'],
                               activeforeground=self.colors['text'], bd=0, highlightthickness=0)
            rb.pack(anchor='w', pady=3)
        
        # --- TARJETA 3: Configuración del resumen ---
        summary_container, summary_card = self.create_card_frame(scrollable_frame, "⏱️ Configuración del Resumen")
        summary_container.pack(fill='x', pady=(0, 20))
        
        duration_frame = tk.Frame(summary_card, bg=self.colors['card'])
        duration_frame.pack(fill='x')
        
        tk.Label(duration_frame, text="Duración deseada del resumen:", 
                font=('Segoe UI', 10), fg=self.colors['text_secondary'], 
                bg=self.colors['card']).pack(side='left')
        
        duration_entry = tk.Entry(duration_frame, textvariable=self.summary_time, 
                                 font=('Segoe UI', 11), width=8, relief='flat',
                                 bg=self.colors['input_bg'], fg=self.colors['text'], bd=0,
                                 highlightthickness=2, highlightcolor=self.colors['primary'], 
                                 highlightbackground=self.colors['border'], insertbackground=self.colors['primary'])
        duration_entry.pack(side='left', padx=(15, 8), ipady=8)
        
        tk.Label(duration_frame, text="minutos", 
                font=('Segoe UI', 10), fg=self.colors['text_secondary'], 
                bg=self.colors['card']).pack(side='left')
        
        # --- TARJETA 4: Controles principales ---
        controls_container, controls_card = self.create_card_frame(scrollable_frame, "🚀 Panel de Control")
        controls_container.pack(fill='x', pady=(0, 20))
        
        buttons_frame = tk.Frame(controls_card, bg=self.colors['card'])
        buttons_frame.pack(fill='x')
        
        self.transcribe_btn = self.create_modern_button(buttons_frame, "🎤 Iniciar Transcripción", 
                                                       command=self.start_transcription, style='primary')
        self.transcribe_btn.pack(fill='x', pady=(0, 12))
        
        self.create_modern_button(buttons_frame, "🤖 Generar Prompt para ChatGPT", 
                                 command=self.generate_prompt, style='secondary').pack(fill='x')
        
        # Barra de progreso moderna
        progress_container = tk.Frame(controls_card, bg=self.colors['card'])
        progress_container.pack(fill='x', pady=(20, 0))
        
        progress_label_frame = tk.Frame(progress_container, bg=self.colors['card'])
        progress_label_frame.pack(fill='x', pady=(0, 8))
        
        tk.Label(progress_label_frame, text="Progreso:", 
                font=('Segoe UI', 9, 'bold'), fg=self.colors['text_secondary'], 
                bg=self.colors['card']).pack(side='left')
        
        self.progress_label = tk.Label(progress_label_frame, text="0%", 
                                      font=('Segoe UI', 9, 'bold'), 
                                      fg=self.colors['primary'], bg=self.colors['card'])
        self.progress_label.pack(side='right')
        
        # Contenedor de barra con bordes redondeados simulados
        progress_bg = tk.Frame(progress_container, bg=self.colors['border'], height=8)
        progress_bg.pack(fill='x', pady=(0, 8))
        
        self.progress = ttk.Progressbar(progress_bg, style='Modern.Horizontal.TProgressbar',
                                       mode='determinate')
        self.progress.pack(fill='x', padx=1, pady=1)
        
        self.time_label = tk.Label(progress_container, text="", 
                                  font=('Segoe UI', 9), 
                                  fg=self.colors['text_muted'], bg=self.colors['card'])
        self.time_label.pack(pady=(0, 8))
        
        self.status_label = tk.Label(controls_card, text="✨ Listo para transcribir", 
                                    font=('Segoe UI', 11, 'bold'),
                                    fg=self.colors['success'], bg=self.colors['card'])
        self.status_label.pack(pady=(8, 0))
        
        # --- TARJETA 5: Resultados ---
        results_container, results_card = self.create_card_frame(scrollable_frame, "📝 Transcripción / Prompt")
        results_container.pack(fill='both', expand=True, pady=(0, 20))
        
        # Área de texto principal con diseño moderno
        text_container = tk.Frame(results_card, bg=self.colors['border'], padx=1, pady=1)
        text_container.pack(fill='both', expand=True, pady=(0, 15))
        
        inner_text_container = tk.Frame(text_container, bg=self.colors['input_bg'])
        inner_text_container.pack(fill='both', expand=True)
        
        self.result_text = tk.Text(inner_text_container, wrap=tk.WORD, height=20, 
                                  font=('JetBrains Mono', 10), bg=self.colors['input_bg'], 
                                  fg=self.colors['text'], relief='flat', bd=0, 
                                  highlightthickness=0, insertbackground=self.colors['primary'],
                                  selectbackground=self.colors['primary'], selectforeground='#000000')
        self.result_text.pack(side='left', fill='both', expand=True, padx=15, pady=15)
        
        result_scrollbar = ttk.Scrollbar(inner_text_container, orient=tk.VERTICAL, 
                                        command=self.result_text.yview)
        result_scrollbar.pack(side='right', fill='y')
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        # Botones de acción modernos
        action_frame = tk.Frame(results_card, bg=self.colors['card'])
        action_frame.pack(fill='x')
        
        self.save_btn = self.create_modern_button(action_frame, "💾 Guardar TXT", 
                                                 command=self.save_transcription, 
                                                 style='secondary', state='disabled')
        self.save_btn.pack(side='left', padx=(0, 12))
        
        self.clear_btn = self.create_modern_button(action_frame, "🗑️ Limpiar", 
                                                  command=self.clear_results, 
                                                  style='danger', state='disabled')
        self.clear_btn.pack(side='left', padx=(0, 12))
        
        self.copy_prompt_btn = self.create_modern_button(action_frame, "📋 Copiar Prompt", 
                                                        command=self.copy_prompt, 
                                                        style='warning', state='disabled')
        self.copy_prompt_btn.pack(side='left')
        
        # --- TARJETA 6: SRT opcional ---
        srt_container, srt_card = self.create_card_frame(scrollable_frame, "🎬 SRT generado por ChatGPT")
        srt_container.pack(fill='both', expand=True)
        
        # Área de texto SRT
        srt_text_container = tk.Frame(srt_card, bg=self.colors['border'], padx=1, pady=1)
        srt_text_container.pack(fill='both', expand=True, pady=(0, 15))
        
        inner_srt_container = tk.Frame(srt_text_container, bg=self.colors['input_bg'])
        inner_srt_container.pack(fill='both', expand=True)
        
        self.srt_text = tk.Text(inner_srt_container, wrap=tk.WORD, height=12, 
                               font=('JetBrains Mono', 10), bg=self.colors['input_bg'], 
                               fg=self.colors['text'], relief='flat', bd=0, 
                               highlightthickness=0, insertbackground=self.colors['primary'],
                               selectbackground=self.colors['primary'], selectforeground='#000000')
        self.srt_text.pack(side='left', fill='both', expand=True, padx=15, pady=15)
        
        srt_scrollbar = ttk.Scrollbar(inner_srt_container, orient=tk.VERTICAL, 
                                     command=self.srt_text.yview)
        srt_scrollbar.pack(side='right', fill='y')
        self.srt_text.configure(yscrollcommand=srt_scrollbar.set)
        
        # Botón guardar SRT
        self.create_modern_button(srt_card, "💾 Guardar como SRT", 
                                 command=self.save_srt, style='success').pack(anchor='w')
        
        # Configurar canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # --- Funciones de audio y transcripción ---
    def browse_file(self):
        filetypes = [
            ("Todos los audios", "*.mp3 *.wav *.m4a *.flac *.aac *.ogg *.mp4 *.mkv *.avi"),
            ("MP3", "*.mp3"),
            ("WAV", "*.wav"),
            ("M4A", "*.m4a"),
            ("FLAC", "*.flac"),
            ("Todos", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=filetypes,
            initialdir=os.path.expanduser("~/Downloads")  # Start in Downloads folder
        )
        if filename:
            # Convert to absolute path and normalize it
            abs_path = os.path.abspath(filename)
            if os.path.exists(abs_path):
                self.audio_file.set(abs_path)
                self.update_status(f"Archivo seleccionado: {os.path.basename(abs_path)}", "green")
            else:
                messagebox.showerror("Error", f"No se pudo encontrar el archivo:\n{abs_path}")
                self.audio_file.set("")
            
    def format_timestamp(self, seconds):
        minutes = int(seconds//60)
        seconds = int(seconds%60)
        return f"({minutes}:{seconds:02d})"
    
    def update_status(self, message, color="text"):
        color_map = {
            "text": self.colors['text'],
            "blue": self.colors['primary'],
            "green": self.colors['success'],
            "red": self.colors['danger']
        }
        icons = {
            "text": "ℹ",
            "blue": "",
            "green": "",
            "red": ""
        }
        self.status_label.config(text=f"{icons.get(color, 'ℹ️')} {message}", 
                               foreground=color_map.get(color, color))
        self.root.update_idletasks()
        
    def start_transcription(self):
        audio_path = self.audio_file.get().strip()
        if not audio_path:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo de audio")
            return
            
        # Normalize the path and check if it exists
        try:
            audio_path = os.path.abspath(audio_path)
            if not os.path.exists(audio_path):
                messagebox.showerror("Error", f"No se pudo encontrar el archivo:\n{audio_path}")
                self.audio_file.set("")
                return
                
            # Check if file is accessible
            try:
                with open(audio_path, 'rb') as f:
                    pass
            except IOError as e:
                messagebox.showerror("Error", f"No se puede acceder al archivo:\n{str(e)}")
                return
                
            # Check file size
            file_size = os.path.getsize(audio_path) / (1024 * 1024)  # in MB
            if file_size > 100:  # 100MB limit
                if not messagebox.askyesno("Advertencia", 
                                         f"El archivo es grande ({file_size:.1f} MB). "
                                         "La transcripción puede tardar mucho tiempo. ¿Deseas continuar?"):
                    return
            
            # Start transcription in a new thread
            self.update_status("Iniciando transcripción...", "blue")
            thread = threading.Thread(target=self.transcribe_audio)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el archivo:\n{str(e)}")
            self.update_status("Error al procesar el archivo", "red")
        
    def transcribe_audio(self):
        try:
            start_time = time.time()
            self.is_processing = True
            self.transcribe_btn.config(state='disabled', bg='#666666')
            self.progress.config(value=0)
            self.progress_label.config(text="0%")
            self.update_status("Cargando modelo Whisper...", "blue")
            self.time_label.config(text="Estimando tiempo...")
            
            model_name = self.model_size.get()
            if self.model is None or getattr(self,'current_model',None)!=model_name:
                self.model = whisper.load_model(model_name)
                self.current_model = model_name
            
            self.root.after(0, lambda:self.progress.config(value=20))
            self.root.after(0, lambda:self.progress_label.config(text="20%"))
            
            self.update_status(f"Analizando audio con modelo {model_name}...", "blue")
            
            result = self.model.transcribe(
                self.audio_file.get(),
                verbose=False,
                language=self.language_option.get() if self.language_option.get()!="auto" else None
            )
            
            self.root.after(0, lambda:self.progress.config(value=80))
            self.root.after(0, lambda:self.progress_label.config(text="80%"))
            
            transcript_text = self.generate_transcript_text(result)
            self.root.after(0, lambda:self.display_results(transcript_text))
            
            total_time = time.time()-start_time
            self.root.after(0, lambda:self.time_label.config(text=f"Completado en {total_time:.1f}s"))
            self.root.after(0, lambda:self.progress.config(value=100))
            self.root.after(0, lambda:self.progress_label.config(text="100%"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.update_status("Error en la transcripción","red"))
            self.root.after(0, lambda:self.progress.config(value=0))
            self.root.after(0, lambda:self.progress_label.config(text="Error"))
        finally:
            self.is_processing=False
            self.root.after(0,self.finish_transcription)
            
    def generate_transcript_text(self,result):
        text_parts=[]
        for segment in result.get("segments",[]):
            timestamp=self.format_timestamp(segment["start"])
            text=segment["text"].strip()
            text_parts.append(f"{timestamp} {text}")
        return " ".join(text_parts)
    
    def display_results(self, transcript_text):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, transcript_text)
        self.save_btn.config(state='normal')
        self.clear_btn.config(state='normal')
        self.update_status("¡Transcripción completada exitosamente!", "green")
        
    def finish_transcription(self):
        self.transcribe_btn.config(state='normal', bg=self.colors['primary'])
        
    def save_transcription(self):
        if not self.result_text.get(1.0, tk.END).strip():
            return
        filename = filedialog.asksaveasfilename(title="Guardar transcripción", defaultextension=".txt",
                                                filetypes=[("Archivos de texto","*.txt"),("Todos","*.*")])
        if filename:
            try:
                with open(filename,'w',encoding='utf-8') as f:
                    f.write(self.result_text.get(1.0,tk.END))
                messagebox.showinfo("Éxito", f"Transcripción guardada en:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar archivo:\n{str(e)}")
                
    def clear_results(self):
        self.result_text.delete(1.0, tk.END)
        self.save_btn.config(state='disabled')
        self.clear_btn.config(state='disabled')
        self.copy_prompt_btn.config(state='disabled')
        self.progress.config(value=0)
        self.progress_label.config(text="0%")
        self.time_label.config(text="")
        self.update_status("✨ Listo para nueva transcripción", "green")
        
    def generate_prompt(self):
        duration = self.summary_time.get()
        try:
            duration_int = int(duration)
        except ValueError:
            messagebox.showerror("Error", "Introduce un número válido de minutos")
            return

        transcript_text = self.result_text.get(1.0, tk.END).strip()
        if not transcript_text:
            messagebox.showwarning("Atención", "Primero transcribe el audio antes de generar el prompt")
            return

        prompt = f"""Analiza esta transcripción y selecciona únicamente los fragmentos más relevantes e interesantes para editar un video. 
El resultado debe estar en español y en formato de lista, siguiendo exactamente este estilo, que es compatible con CapCut en SRT para yo imporarlo a capcut y saber que cortar y que dejar para que dure los minutos que marque: 

- Explicación resumida en 1–5 frases. 

Instrucciones adicionales:
- Mantén el orden cronológico de la transcripción.
- Marca solo los momentos clave (impactantes, informativos o entretenidos).
- Resume cada punto de forma concisa y clara.
- La suma total de la duración de los fragmentos debe ser aproximadamente {duration_int} minutos.
- Devuélvelo siempre en formato SRT listo para descargar y importarlo en capcut
- No agregues texto fuera del formato solicitado.

Transcripción completa:
{transcript_text}"""

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, prompt)
        self.update_status("Prompt optimizado generado. Listo para ChatGPT", "blue")
        self.copy_prompt_btn.config(state='normal')

    def copy_prompt(self):
        prompt_text = self.result_text.get(1.0, tk.END).strip()
        if prompt_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(prompt_text)
            messagebox.showinfo("Copiado", "Prompt copiado al portapapeles")

    def save_srt(self):
        if not self.srt_text.get(1.0, tk.END).strip():
            return
        filename = filedialog.asksaveasfilename(title="Guardar SRT", defaultextension=".srt",
                                                filetypes=[("Archivos SRT","*.srt"),("Todos","*.*")])
        if filename:
            try:
                with open(filename,'w',encoding='utf-8') as f:
                    f.write(self.srt_text.get(1.0,tk.END))
                messagebox.showinfo("Éxito", f"SRT guardado en:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar archivo:\n{str(e)}")

def main():
    root = tk.Tk()
    try:
        root.iconbitmap('icon.ico')
    except: 
        pass
    app = AudioTranscriberGUI(root)
    root.update_idletasks()
    x=(root.winfo_screenwidth()//2)-(root.winfo_width()//2)
    y=(root.winfo_screenheight()//2)-(root.winfo_height()//2)
    root.geometry(f"+{x}+{y}")
    root.mainloop()

if __name__=="__main__":
    main()

    