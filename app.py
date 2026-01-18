import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sv_ttk
from algorithms import entrenar_modelo, preparar_datos_prediccion
from user_mode import UserModeTab
import time
from datetime import datetime
import pandas as pd
import joblib
import threading
from threading import Thread
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

try:
    import folium
    import webbrowser
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False

try:
    import darkdetect
except ImportError:
    darkdetect = None

class LoadingDialog(tk.Toplevel):
    """Diálogo de carga con spinner animado."""
    def __init__(self, parent, title="Cargando", message="Por favor espera..."):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Centrar ventana
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 150
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 75
        self.geometry(f"+{x}+{y}")
        
        # Frame principal con padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Label del mensaje
        msg_label = ttk.Label(main_frame, text=message, font=("Segoe UI", 11), justify="center")
        msg_label.pack(pady=(0, 20))
        
        # Frame para el spinner
        spinner_frame = ttk.Frame(main_frame)
        spinner_frame.pack(expand=True)
        
        # Label del spinner con fuente más grande
        self.spinner_label = ttk.Label(spinner_frame, text="", font=("Segoe UI", 20), foreground="blue")
        self.spinner_label.pack()
        
        # Caracteres para animar
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.spinner_index = 0
        self.is_running = True
        
        # Iniciar animación
        self.animate()
        
        # Evitar que se cierre con el botón X
        self.protocol("WM_DELETE_WINDOW", lambda: None)
    
    def animate(self):
        """Anima el spinner."""
        if self.is_running:
            char = self.spinner_chars[self.spinner_index % len(self.spinner_chars)]
            self.spinner_label.config(text=char)
            self.spinner_index += 1
            self.after(100, self.animate)
    
    def close(self):
        """Cierra el diálogo de carga."""
        self.is_running = False
        self.destroy()

class SafeDriveApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- CARGAR ZONAS DE TRÁFICO ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        zones_path = os.path.join(base_dir, "12-2024_TrafficZones.csv")
        try:
            self.traffic_zones = pd.read_csv(zones_path, sep=";", encoding="latin-1")
            # Crear diccionario para búsqueda rápida por id
            self.zones_dict = {int(row['id']): row for idx, row in self.traffic_zones.iterrows()}
        except Exception as e:
            print(f"No se pudo cargar zonas de tráfico: {e}")
            self.traffic_zones = None
            self.zones_dict = {}
        # ---------------------------

        # --- ICONO DE LA VENTANA ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, "SafeDriveLogo_64x64.png")

        try:
            self.icon_image = tk.PhotoImage(file=icon_path)
            self.iconphoto(True, self.icon_image)
        except Exception as e:
            print("No se pudo cargar el icono:", e)
        # ---------------------------

        self.title("SafeDrive")
        self.geometry("1100x650")
        self.minsize(950, 600)

        self.header_bg = "#1d4ed8" 

        # --- detectar tema del sistema y aplicarlo ---
        system_theme = "light"
        if darkdetect is not None:
            try:
                detected = darkdetect.theme().lower()
                if detected in ("dark", "light"):
                    system_theme = detected
            except Exception:
                pass

        sv_ttk.set_theme(system_theme)
        # ----------------------------------------------------------

        self._create_style()
        self._create_layout()

    # ------------------ ESTILOS ------------------ #
    def _create_style(self):
        style = ttk.Style(self)

        # Fuente por defecto
        style.configure(".", font=("Segoe UI", 10))

        # HEADER azul
        header_bg = "#1d4ed8"
        style.configure("Header.TFrame", background=header_bg)
        style.configure(
            "HeaderTitle.TLabel",
            background=header_bg,
            foreground="white",
            font=("Segoe UI Semibold", 18)
        )
        style.configure(
            "HeaderSub.TLabel",
            background=header_bg,
            foreground="#bfdbfe",
            font=("Segoe UI", 11)
        )

        # Tarjetas
        style.configure("Card.TFrame", padding=(10, 8))
        style.configure("Card.TLabelframe", padding=(10, 8))
        style.configure("Card.TLabelframe.Label",
                        font=("Segoe UI", 10, "bold"))

        # Botones acento
        style.configure("Accent.TButton",
                        padding=(12, 6),
                        font=("Segoe UI Semibold", 10))

        # Pestañas Notebook
        style.configure("TNotebook.Tab",
                        padding=(18, 8),
                        font=("Segoe UI", 10))
    
    # ------------------ LAYOUT PRINCIPAL ------------------ #
    def _create_layout(self):
        # HEADER azul
        header = tk.Frame(self, bg=self.header_bg)
        header.pack(side="top", fill="x")

        # Contenedor izquierda (título + subtítulo)
        left_header = tk.Frame(header, bg=self.header_bg)
        left_header.pack(side="left")

        lbl_title = tk.Label(
            left_header,
            text="SafeDrive",
            bg=self.header_bg,
            fg="white",
            font=("Segoe UI Semibold", 18)
        )
        lbl_title.pack(side="left", padx=20, pady=10)

        self.lbl_sub = tk.Label(
            left_header,
            text="Entrenamiento",
            bg=self.header_bg,
            fg="white",
            font=("Segoe UI", 11)
        )
        self.lbl_sub.pack(side="left", pady=(8, 0))

        # Botón de tema arriba a la derecha
        self.btn_theme = tk.Button(
            header,
            text="🌙",                      
            bg=self.header_bg,
            fg="white",
            activebackground=self.header_bg,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 12),
            command=self._toggle_theme
        )
        self.btn_theme.pack(side="right", padx=20)

        # Contenedor principal con Notebook
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        self.train_tab = ttk.Frame(self.notebook)
        self.pred_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.train_tab, text="Entrenamiento")
        self.notebook.add(self.pred_tab, text="Predicción (Técnico)")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._build_train_tab()
        self._build_pred_tab()
        
        # Agregar pestaña de Usuario Normal
        if self.traffic_zones is not None:
            self.user_mode_tab = UserModeTab(self.notebook, self.traffic_zones)
        else:
            print("⚠️ No se pudo cargar zonas de tráfico para modo Usuario Normal")

        # Ajustar icono del botón según el tema actual
        self._update_theme_button_icon()

    # ------------------ CAMBIO DE PESTAÑA ------------------ #
    def _on_tab_changed(self, event):
        notebook = event.widget
        current_tab = notebook.tab(notebook.select(), "text")
        self.lbl_sub.config(text=current_tab)

    def _on_combo_select(self, event):
        cb = event.widget
        cb.selection_clear()
        self.focus()

    def _update_theme_button_icon(self):
        # Cambiar icono según tema actual
        if sv_ttk.get_theme() == "dark":
            self.btn_theme.config(text="☀") 
        else:
            self.btn_theme.config(text="🌙") 

    def _toggle_theme(self):
        sv_ttk.toggle_theme()
        self._create_style()
        self._update_theme_button_icon()
        # Actualizar el tema del gráfico en Predicción (Técnico)
        if MATPLOTLIB_AVAILABLE and hasattr(self, 'pie_fig'):
            self._apply_pie_theme()
            # Re-dibujar el gráfico con los datos actuales o vacío si no hay
            if hasattr(self, 'last_predictions') and self.last_predictions is not None:
                try:
                    niveles = self.last_predictions['nivel_trafico'].tolist()
                    bajos = niveles.count('Bajo')
                    medios = niveles.count('Medio')
                    altos = niveles.count('Alto')
                    self._update_pie_chart(bajos, medios, altos)
                except Exception:
                    pass
            else:
                # Si no hay predicciones, mostrar gráfico vacío con el tema actualizado
                self._update_pie_chart(0, 0, 0)
        
        # Actualizar el tema del gráfico en Usuario Normal
        if hasattr(self, 'user_mode_tab'):
            try:
                self.user_mode_tab.refresh_theme()
            except Exception:
                pass

    # ------------------ PESTAÑA ENTRENAMIENTO ------------------ #
    def _build_train_tab(self):
        tab = self.train_tab
        tab.columnconfigure(1, weight=1)
        tab.columnconfigure(2, weight=0)

        # Fuente de datos
        lbl_datos = ttk.Label(tab, text="Fuente de datos:")
        lbl_datos.grid(row=0, column=0, sticky="e", padx=(15, 5), pady=(15, 5))

        self.entry_fuente = ttk.Entry(tab)
        self.entry_fuente.grid(row=0, column=1, sticky="ew", pady=(15, 5))

        btn_fuente = ttk.Button(
            tab, text="Seleccionar",
            command=lambda: self._select_file(self.entry_fuente, "selected_file_train", ".csv")
        )
        btn_fuente.grid(row=0, column=2, padx=(10, 15), pady=(15, 5))

        # Selector de algoritmo
        lbl_alg = ttk.Label(tab, text="Seleccionar algoritmo:")
        lbl_alg.grid(row=1, column=0, sticky="e", padx=(15, 5), pady=(15, 5))

        self.combo_algoritmo = ttk.Combobox(
            tab, state="readonly",
            values=[
                "Random Forest Mejorado",
                "Gradient Boosting",
                "Deep Learning Mejorado",
                "Árbol de decisión optimizado"
            ]
        )
        self.combo_algoritmo.current(0)
        self.combo_algoritmo.grid(row=1, column=1, sticky="w", pady=(15, 5))

        self.combo_algoritmo.bind("<<ComboboxSelected>>", self._on_combo_select)

        # Botón Ejecutar
        btn_ejecutar = ttk.Button(
            tab, text="Ejecutar", style="Accent.TButton",
            command=self._ejecutar_train
        )
        btn_ejecutar.grid(row=1, column=2, padx=(10, 15), pady=(15, 5), sticky="e")

        # Vista previa de resultados
        preview_card = ttk.Labelframe(
            tab, text="VISTA PREVIA", style="Card.TLabelframe"
        )
        preview_card.grid(row=2, column=0, columnspan=3,
                          padx=15, pady=(15, 5), sticky="nsew")
        tab.rowconfigure(2, weight=0)

        for i in range(2):
            preview_card.columnconfigure(i, weight=1)

        self.lbl_fecha = ttk.Label(preview_card, text="Fecha: -")
        self.lbl_fecha.grid(row=0, column=0, sticky="w", padx=(5, 10))

        self.lbl_ejemplares = ttk.Label(preview_card, text="Ejemplares: -")
        self.lbl_ejemplares.grid(row=1, column=0, sticky="w", padx=(5, 10), pady=2)

        self.lbl_tiempo = ttk.Label(preview_card, text="Tiempo de entrenamiento: -")
        self.lbl_tiempo.grid(row=2, column=0, sticky="w", padx=(5, 10), pady=2)

        self.lbl_alg_seleccionado = ttk.Label(
            preview_card, text="Algoritmo seleccionado: -"
        )
        self.lbl_alg_seleccionado.grid(row=3, column=0, sticky="w",
                               padx=(5, 10), pady=(2, 0))

        # Resultado
        resultado_card = ttk.Labelframe(
            tab, text="Resultado", style="Card.TLabelframe"
        )
        resultado_card.grid(row=3, column=0, columnspan=3,
                            padx=15, pady=(10, 5), sticky="nsew")
        tab.rowconfigure(3, weight=1)
        resultado_card.columnconfigure(0, weight=3)
        resultado_card.columnconfigure(1, weight=1)

        self.lbl_resultado = ttk.Label(
            resultado_card,
            text="RMSE: -\nR²: -\nMAE: -\nMAPE: -",
            anchor="nw",
            justify="left"
        )
        self.lbl_resultado.grid(row=0, column=0, sticky="nsew",
                                padx=(5, 10), pady=5)

        # Se eliminan gráficos de muestra en entrenamiento

        # Guardar modelo
        lbl_guardar = ttk.Label(tab, text="Guardar modelo:")
        lbl_guardar.grid(row=4, column=0, sticky="e",
                         padx=(15, 5), pady=(10, 15))

        self.entry_modelo_path = ttk.Entry(tab)
        self.entry_modelo_path.grid(row=4, column=1, sticky="ew", pady=(10, 15))

        btn_guardar_modelo = ttk.Button(
            tab, text="Guardar", style="Accent.TButton",
            command=self._save_model
        )
        btn_guardar_modelo.grid(row=4, column=2, padx=(10, 15), pady=(10, 15))

    # ------------------ PESTAÑA PREDICCIÓN ------------------ #
    def _build_pred_tab(self):
        tab = self.pred_tab
        tab.columnconfigure(1, weight=1)
        tab.columnconfigure(2, weight=0)

        # Ficheros
        lbl_ej = ttk.Label(tab, text="Ejemplares a predecir:")
        lbl_ej.grid(row=0, column=0, sticky="e", padx=(15, 5), pady=(15, 5))

        self.entry_ejemplares = ttk.Entry(tab)
        self.entry_ejemplares.grid(row=0, column=1, sticky="ew", pady=(15, 5))

        btn_ejemplares = ttk.Button(
            tab, text="Seleccionar",
            command=lambda: self._select_file(self.entry_ejemplares, None, ".csv")
        )
        btn_ejemplares.grid(row=0, column=2, padx=(10, 15), pady=(15, 5))

        lbl_modelo = ttk.Label(tab, text="Modelo a aplicar:")
        lbl_modelo.grid(row=1, column=0, sticky="e", padx=(15, 5), pady=5)

        self.entry_modelo_pred = ttk.Entry(tab)
        self.entry_modelo_pred.grid(row=1, column=1, sticky="ew", pady=5)

        btn_modelo = ttk.Button(
            tab, text="Seleccionar",
            command=lambda: self._select_file(self.entry_modelo_pred, None, ".mdl")
        )
        btn_modelo.grid(row=1, column=2, padx=(10, 15), pady=5)

        # Acción de predicción y indicador de carga
        btn_predecir = ttk.Button(
            tab, text="Predecir", style="Accent.TButton",
            command=self._ejecutar_pred
        )
        btn_predecir.grid(row=2, column=2, padx=(10, 15), pady=(10, 5), sticky="e")

        # Tabla y resumen
        center_frame = ttk.Frame(tab)
        center_frame.grid(row=3, column=0, columnspan=3,
                  padx=15, pady=(10, 5), sticky="nsew")
        tab.rowconfigure(3, weight=1)
        center_frame.columnconfigure(0, weight=3)
        center_frame.columnconfigure(1, weight=1)

        # Tabla de resultados
        table_frame = ttk.Frame(center_frame, style="Card.TFrame")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        center_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("ejemplar", "pred_trafico", "interpretacion")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.tree.heading("ejemplar", text="Ejemplar")
        self.tree.heading("pred_trafico", text="Pred. Tráfico")
        self.tree.heading("interpretacion", text="Nivel")

        self.tree.column("ejemplar", width=140, minwidth=140, anchor="center", stretch=True)
        self.tree.column("pred_trafico", width=120, minwidth=120, anchor="center", stretch=True)
        self.tree.column("interpretacion", width=120, minwidth=120, anchor="center", stretch=True)

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        table_frame.rowconfigure(0, weight=1)

        # Resumen
        resumen_card = ttk.Labelframe(
            center_frame, text="RESUMEN", style="Card.TLabelframe"
        )
        resumen_card.grid(row=0, column=1, sticky="nsew")
        resumen_card.rowconfigure(5, weight=1)

        self.lbl_total = ttk.Label(resumen_card, text="Total casos: 0")
        self.lbl_total.grid(row=0, column=0, sticky="w", pady=(2, 0), padx=5)

        self.lbl_vender = ttk.Label(resumen_card, text="Bajo: 0")
        self.lbl_vender.grid(row=1, column=0, sticky="w", pady=2, padx=5)

        self.lbl_comprar = ttk.Label(resumen_card, text="Medio: 0")
        self.lbl_comprar.grid(row=2, column=0, sticky="w", pady=2, padx=5)

        self.lbl_alto = ttk.Label(resumen_card, text="Alto: 0")
        self.lbl_alto.grid(row=3, column=0, sticky="w", pady=2, padx=5)

        ttk.Separator(resumen_card, orient="horizontal").grid(
            row=6, column=0, sticky="ew", padx=5, pady=(6, 4)
        )

        self.lbl_tiempo_pred = ttk.Label(resumen_card, text="Tiempo: -")
        self.lbl_tiempo_pred.grid(row=7, column=0, sticky="w", pady=2, padx=5)

        # Gráfico real: pie chart Bajo/Medio/Alto
        if MATPLOTLIB_AVAILABLE:
            self.pie_fig = Figure(figsize=(2.6, 2.2), dpi=100)
            self.pie_ax = self.pie_fig.add_subplot(111)
            self.pie_ax.axis('equal')
            self._apply_pie_theme()
            self.pie_canvas = FigureCanvasTkAgg(self.pie_fig, master=resumen_card)
            self.pie_canvas.get_tk_widget().grid(row=5, column=0, pady=(12, 12), padx=12, sticky="nsew")
            # Inicial vacío (con tema ya aplicado)
            self._update_pie_chart(0, 0, 0)
        else:
            self.lbl_chart_placeholder = ttk.Label(resumen_card, text="Instala matplotlib para ver el gráfico")
            self.lbl_chart_placeholder.grid(row=5, column=0, pady=(8, 5))

        # Mapa
        bottom_map = ttk.Frame(tab)
        bottom_map.grid(row=4, column=0, columnspan=3,
                padx=15, pady=(10, 5), sticky="ew")
        for i in range(3):
            bottom_map.columnconfigure(i, weight=1)

        btn_mapa = ttk.Button(
            bottom_map, text="Mapa", style="Accent.TButton",
            command=self._show_map
        )
        btn_mapa.grid(row=0, column=1, pady=(0, 0))

        # Guardar resultados
        lbl_guardar_res = ttk.Label(tab, text="Guardar resultados:")
        lbl_guardar_res.grid(row=5, column=0, sticky="e",
                     padx=(15, 5), pady=(5, 15))

        self.entry_guardar_res = ttk.Entry(tab)
        self.entry_guardar_res.grid(row=5, column=1, sticky="ew", pady=(5, 15))

        btn_guardar_res = ttk.Button(
            tab, text="Guardar", style="Accent.TButton",
            command=self._save_results
        )
        btn_guardar_res.grid(row=5, column=2, padx=(10, 15), pady=(5, 15))

    # ------------------ FUNCIONES AUXILIARES ------------------ #
    def _select_file(self, target_entry, attr_name=None, extension=None):
        filetypes = [("Todos los archivos", "*.*")]
        
        if extension == ".csv":
            filetypes = [("CSV files", "*.csv"), ("Todos los archivos", "*.*")]
        elif extension == ".mdl":
            filetypes = [("MDL files", "*.mdl"), ("Todos los archivos", "*.*")]
        
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=filetypes
        )
        if filename:
            target_entry.delete(0, "end")
            target_entry.insert(0, filename)
            if attr_name:
                setattr(self, attr_name, filename)

    def _ejecutar_train(self):
        file_a = getattr(self, "selected_file_train", None)
        algoritmo = self.combo_algoritmo.get()

        if not file_a:
            messagebox.showwarning("Atención", "Selecciona un archivo antes de ejecutar.")
            return

        # Crear diálogo de carga
        loading_dialog = LoadingDialog(self, title="Entrenamiento", message="Entrenando modelo...\nEsto puede tardar varios minutos")
        
        # Iniciar entrenamiento en un hilo separado
        thread = Thread(target=self._train_worker, args=(file_a, algoritmo, loading_dialog), daemon=True)
        thread.start()

    def _train_worker(self, file_a, algoritmo, loading_dialog):
        """Función que se ejecuta en un hilo separado para entrenar el modelo."""
        try:
            # Medir tiempo de ejecución
            start_time = time.time()
            resultados, df = entrenar_modelo(file_a, algoritmo)
            end_time = time.time()
            tiempo_segundos = end_time - start_time

            # Guardar modelo y resultados para predicciones y guardado
            self.trained_model = resultados.get("modelo")
            self.trained_results = resultados
            self.trained_df = df
            self.last_predictions = None
            
            # Actualizar UI desde el hilo principal
            self.after(0, lambda: self._update_train_results(tiempo_segundos, resultados, df, algoritmo))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            # Cerrar el diálogo de carga
            self.after(100, lambda: loading_dialog.close())

    def _update_train_results(self, tiempo_segundos, resultados, df, algoritmo):
        """Actualiza los resultados en la UI (llamado desde el hilo principal con after)."""
        # Fecha actual
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Número de ejemplares
        num_ejemplares = len(df) if df is not None else "Desconocido"

        # Actualizar labels
        self.lbl_fecha.config(text=f"Fecha: {fecha_actual}")
        self.lbl_ejemplares.config(text=f"Ejemplares: {num_ejemplares}")
        self.lbl_tiempo.config(text=f"Tiempo de entrenamiento: {tiempo_segundos:.2f} s")
        self.lbl_alg_seleccionado.config(text=f"Algoritmo seleccionado: {algoritmo}")

        # Actualizar resultados
        self.lbl_resultado.config(
            text=(
                f"RMSE: {resultados['rmse']:.2f}\n"
                f"R²: {resultados['r2']:.2f}\n"
                f"MAE: {resultados['mae']:.2f}\n"
                f"MAPE: {resultados['mape']*100:.2f}%\n"
                f"Modelo entrenado correctamente."
            )
        )

        messagebox.showinfo("Entrenamiento", "Modelo entrenado correctamente")

    def _redondear_hora_a_15(self, fecha_str):
        """
        Redondea una hora al :15 más cercano.
        
        Entrada: "14/01/2026 08:27" → Salida: "14/01/2026 08:30"
        Entrada: "14/01/2026 14:12" → Salida: "14/01/2026 14:15"
        
        Args:
            fecha_str: String en formato "DD/MM/YYYY HH:MM"
            
        Returns:
            String en formato "DD/MM/YYYY HH:MM" redondeado al :15 más cercano
        """
        try:
            from math import ceil
            
            # Dividir fecha y hora
            if ' ' in str(fecha_str):
                fecha_parte, hora_parte = str(fecha_str).rsplit(' ', 1)
                h, m = map(int, hora_parte.split(':'))
                
                # Redondear minutos a múltiplo de 15
                m_redondeado = ceil(m / 15) * 15
                
                # Ajustar hora si minutos pasan de 60
                if m_redondeado >= 60:
                    try:
                        dt = pd.to_datetime(fecha_str, format='%d/%m/%Y %H:%M')
                        dt_ajustado = dt + pd.Timedelta(minutes=m_redondeado - m)
                        return dt_ajustado.strftime('%d/%m/%Y %H:%M')
                    except:
                        h = (h + 1) % 24
                        m_redondeado = 0
                
                return f"{fecha_parte} {h:02d}:{m_redondeado:02d}"
            else:
                return fecha_str
        except Exception:
            return fecha_str

    def _ejecutar_pred(self):
        file_pred = self.entry_ejemplares.get()
        file_model = self.entry_modelo_pred.get()

        if not file_pred:
            messagebox.showwarning("Atención", "Selecciona un archivo de ejemplares a predecir.")
            return

        # Crear diálogo de carga
        loading_dialog = LoadingDialog(self, title="Predicción", message="Realizando predicción...\nPor favor espera")
        
        # Iniciar predicción en un hilo separado
        thread = Thread(target=self._pred_worker, args=(file_pred, file_model, loading_dialog), daemon=True)
        thread.start()

    def _pred_worker(self, file_pred, file_model, loading_dialog):
        """Función que se ejecuta en un hilo separado para hacer predicciones."""
        try:
            modelo_cargado = getattr(self, "trained_model", None)
            resultados_entrenamiento = getattr(self, "trained_results", None)

            # Intentar cargar modelo si se proporciona ruta
            if file_model and file_model.strip():
                try:
                    model_package = joblib.load(file_model)
                    if isinstance(model_package, dict) and "modelo" in model_package:
                        modelo_cargado = model_package["modelo"]
                        resultados_entrenamiento = model_package
                    else:
                        # Por compatibilidad con modelos antiguos (solo modelo, sin metadatos)
                        modelo_cargado = model_package
                        self.after(0, lambda: messagebox.showwarning("Atención", "Modelo cargado pero sin metadatos. Puede fallar la predicción."))
                except Exception as e:
                    self.after(0, lambda: messagebox.showerror("Error", f"No se pudo cargar el modelo: {e}"))
                    self.after(0, lambda: loading_dialog.close())
                    return

            if modelo_cargado is None or resultados_entrenamiento is None:
                self.after(0, lambda: messagebox.showwarning("Atención", "Primero entrena un modelo o carga uno guardado antes de predecir."))
                self.after(0, lambda: loading_dialog.close())
                return

            try:
                df_pred = pd.read_csv(file_pred, sep=";")
                # Redondear automáticamente las horas al :15 más cercano
                if 'fecha' in df_pred.columns:
                    df_pred['fecha'] = df_pred['fecha'].apply(self._redondear_hora_a_15)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"No se pudo leer el CSV: {e}"))
                self.after(0, lambda: loading_dialog.close())
                return

            try:
                df_pred_ready = preparar_datos_prediccion(df_pred, resultados_entrenamiento)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"No se pudo preparar el CSV para predecir: {e}"))
                self.after(0, lambda: loading_dialog.close())
                return

            try:
                start_time = time.time()
                pred = modelo_cargado.predict(df_pred_ready)
                elapsed = time.time() - start_time
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"No se pudo predecir: {e}"))
                self.after(0, lambda: loading_dialog.close())
                return

            # Llamar a actualización de UI desde el hilo principal
            self.after(0, lambda: self._update_pred_results(df_pred, df_pred_ready, pred, elapsed, resultados_entrenamiento))
            
            # Cerrar el diálogo de carga
            self.after(100, lambda: loading_dialog.close())
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: loading_dialog.close())

    def _update_pred_results(self, df_pred, df_pred_ready, pred, elapsed, resultados_entrenamiento):
        """Actualiza los resultados de predicción en la UI."""
        # Guardar predicciones para exportar
        df_out = df_pred.copy()
        df_out["prediccion_intensidad"] = pred

        # Interpretación del nivel de tráfico por id usando estadísticas
        bajos = medios = altos = 0
        niveles = []
        zona_defaults = resultados_entrenamiento.get("zona_defaults", {})
        default_mean = zona_defaults.get("zona_intensidad_media", float(pd.Series(pred).median()))
        default_std = zona_defaults.get("zona_intensidad_std", float(pd.Series(pred).std()) or 1.0)

        for i, p in enumerate(pred):
            try:
                mean_i = df_pred_ready.iloc[i]["zona_intensidad_media"] if "zona_intensidad_media" in df_pred_ready.columns else default_mean
                std_i = df_pred_ready.iloc[i]["zona_intensidad_std"] if "zona_intensidad_std" in df_pred_ready.columns else default_std
                std_i = std_i if std_i and std_i > 0 else default_std
            except Exception:
                mean_i, std_i = default_mean, default_std

            z = (p - mean_i) / std_i
            if z <= -0.5:
                nivel = "Bajo"
                bajos += 1
            elif z >= 0.5:
                nivel = "Alto"
                altos += 1
            else:
                nivel = "Medio"
                medios += 1
            niveles.append(nivel)

        df_out["nivel_trafico"] = niveles
        
        # Función para convertir números con formato de separador de miles
        def parse_coordinate(value):
            """Extrae coordenadas WGS84 con máxima precisión.
            Detecta automáticamente si es latitud o longitud.
            Madrid: latitud ~40.4°, longitud ~-3.7°
            """
            if pd.isna(value):
                return None
            try:
                str_val = str(value).strip()
                # Remover el signo
                is_negative = str_val.startswith('-')
                str_clean = str_val.lstrip('-').replace('.', '')
                
                # Detectar si es latitud o longitud basándose en el primer dígito
                if str_clean.startswith('4'):
                    # Es latitud (40.xxx...)
                    # Poner punto después de los 2 primeros dígitos
                    if len(str_clean) >= 2:
                        coord = float(str_clean[0:2] + '.' + str_clean[2:])
                    else:
                        coord = float(str_clean)
                elif str_clean.startswith('3'):
                    # Es longitud (3.xxx...)
                    # Poner punto después del primer dígito
                    if len(str_clean) >= 1:
                        coord = float(str_clean[0:1] + '.' + str_clean[1:])
                    else:
                        coord = float(str_clean)
                else:
                    # Fallback: asumir que es latitud
                    if len(str_clean) >= 2:
                        coord = float(str_clean[0:2] + '.' + str_clean[2:])
                    else:
                        coord = float(str_clean)
                
                if is_negative:
                    coord = -coord
                
                return coord
            except Exception as e:
                return None
        
        # Enriquecer con información de zonas
        if self.zones_dict and "id" in df_pred.columns:
            zone_names = []
            zone_coords = []
            for idx in df_pred["id"]:
                if int(idx) in self.zones_dict:
                    zone_info = self.zones_dict[int(idx)]
                    zone_names.append(zone_info.get("nombre", "Desconocida"))
                    
                    lat = parse_coordinate(zone_info.get("latitud"))
                    lon = parse_coordinate(zone_info.get("longitud"))
                    
                    # Fallback a Madrid center (Sol km0) si falla la conversión
                    if lat is None:
                        lat = 40.4168
                    if lon is None:
                        lon = -3.7038
                    
                    zone_coords.append({
                        "id": idx,
                        "nombre": zone_info.get("nombre", "Desconocida"),
                        "lat": lat,
                        "lon": lon
                    })
                else:
                    zone_names.append("Desconocida")
                    zone_coords.append({"id": idx, "nombre": "Desconocida", "lat": 40.4168, "lon": -3.7038})
            df_out["zona_nombre"] = zone_names
            self.last_zone_coords = zone_coords
        else:
            df_out["zona_nombre"] = "Desconocida"
            self.last_zone_coords = []
        
        self.last_predictions = df_out

        # Actualizar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Mostrar id como ejemplar si existe, si no usar índice
        use_id = "id" in df_pred.columns
        for idx, valor in enumerate(pred):
            ejemplar = df_pred.iloc[idx]["id"] if use_id else f"Muestra {idx+1}"
            self.tree.insert("", "end", values=(str(ejemplar), f"{valor:.1f}", niveles[idx]))

        total = len(pred)
        media = float(pd.Series(pred).mean()) if total > 0 else 0
        maximo = float(pd.Series(pred).max()) if total > 0 else 0

        self.lbl_total.config(text=f"Total casos: {total}")
        self.lbl_vender.config(text=f"Bajo: {bajos}")
        self.lbl_comprar.config(text=f"Medio: {medios}")
        self.lbl_alto.config(text=f"Alto: {altos}")
        self.lbl_tiempo_pred.config(text=f"Tiempo: {elapsed:.2f} s")
        
        # Actualizar gráfico
        try:
            self._update_pie_chart(bajos, medios, altos)
        except Exception:
            pass
        
        messagebox.showinfo("Predicción", "Predicciones generadas correctamente.\n\nNota: Los datos meteorológicos se obtienen mediante scraping/mapeo desde AEMET.")

    def _apply_pie_theme(self):
        """Aplica los colores del tema actual al gráfico pie."""
        if not MATPLOTLIB_AVAILABLE or not hasattr(self, 'pie_fig'):
            return
        
        current_theme = sv_ttk.get_theme()
        if current_theme == "dark":
            bg_color = "#1c1c1c"
            text_color = "white"
        else:
            bg_color = "white"
            text_color = "black"
        
        self.pie_fig.patch.set_facecolor(bg_color)
        self.pie_ax.set_facecolor(bg_color)
        self.pie_text_color = text_color

    def _update_pie_chart(self, bajos: int, medios: int, altos: int):
        if MATPLOTLIB_AVAILABLE and hasattr(self, "pie_ax"):
            self.pie_ax.clear()
            
            # Obtener color de texto actual
            text_color = getattr(self, 'pie_text_color', 'black')
            
            sizes = [bajos, medios, altos]
            labels = ["Bajo", "Medio", "Alto"]
            colors = ["#60a5fa", "#fbbf24", "#ef4444"]
            if sum(sizes) == 0:
                sizes = [1]
                labels = ["Sin datos"]
                colors = ["#9ca3af"]
            
            self.pie_ax.pie(
                sizes,
                labels=labels,
                autopct='%1.0f%%' if sum(sizes) > 0 else None,
                startangle=90,
                colors=colors,
                textprops={"fontsize": 8, "color": text_color},
                labeldistance=1.15,
                pctdistance=0.65
            )
            self.pie_ax.axis('equal')
            self.pie_canvas.draw()
        elif hasattr(self, "lbl_chart_placeholder"):
            self.lbl_chart_placeholder.config(text=f"Bajo: {bajos} | Medio: {medios} | Alto: {altos}")

    def _save_model(self):
        if not hasattr(self, "trained_model") or self.trained_model is None:
            messagebox.showwarning("Atención", "Primero entrena un modelo antes de guardarlo.")
            return

        if not hasattr(self, "trained_results") or self.trained_results is None:
            messagebox.showwarning("Atención", "No hay metadatos de entrenamiento disponibles.")
            return

        filename = filedialog.asksaveasfilename(
            title="Guardar modelo",
            defaultextension=".mdl",
            filetypes=[("Modelo SafeDrive", "*.mdl"), ("Todos", "*.*")]
        )
        if filename:
            try:
                # Guardar modelo + metadatos juntos
                model_package = {
                    "modelo": self.trained_model,
                    "features_numericas": self.trained_results.get("features_numericas", []),
                    "features_categoricas": self.trained_results.get("features_categoricas", []),
                    "median_values": self.trained_results.get("median_values", {}),
                    "zona_stats": self.trained_results.get("zona_stats"),
                    "hora_stats": self.trained_results.get("hora_stats"),
                    "zona_defaults": self.trained_results.get("zona_defaults", {}),
                    "hora_defaults": self.trained_results.get("hora_defaults", {}),
                }
                joblib.dump(model_package, filename)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el modelo: {e}")
                return

            self.entry_modelo_path.delete(0, "end")
            self.entry_modelo_path.insert(0, filename)
            messagebox.showinfo("Guardar modelo",
                                f"Modelo guardado en:\n{filename}")

    def _save_results(self):
        if not hasattr(self, "last_predictions") or self.last_predictions is None:
            messagebox.showwarning("Atención", "No hay predicciones para guardar. Ejecuta una predicción primero.")
            return

        filename = filedialog.asksaveasfilename(
            title="Guardar resultados",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")]
        )
        if filename:
            try:
                self.last_predictions.to_csv(filename, index=False, sep=";")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el CSV: {e}")
                return

            self.entry_guardar_res.delete(0, "end")
            self.entry_guardar_res.insert(0, filename)
            messagebox.showinfo("Guardar resultados",
                                f"Resultados guardados en:\n{filename}")

    def _show_map(self):
        if not hasattr(self, 'last_zone_coords') or not self.last_zone_coords:
            messagebox.showwarning("Mapa", "No hay predicciones para mostrar. Ejecuta una predicción primero.")
            return
        
        if not FOLIUM_AVAILABLE:
            messagebox.showerror("Error", "Instala folium para ver el mapa: pip install folium")
            return
        
        # Crear diálogo de carga
        loading_dialog = LoadingDialog(self, title="Mapa", message="Generando mapa...\nEsto puede tardar un momento")
        
        # Iniciar generación de mapa en hilo separado
        thread = Thread(target=self._map_worker, args=(loading_dialog,), daemon=True)
        thread.start()

    def _map_worker(self, loading_dialog):
        """Función que se ejecuta en un hilo separado para generar el mapa."""
        try:
            # Centro en Madrid
            madrid_center = [40.4168, -3.7038]
            
            # Crear mapa
            m = folium.Map(
                location=madrid_center,
                zoom_start=11,
                tiles="OpenStreetMap"
            )
            
            # Colores por nivel de tráfico
            color_map = {
                "Bajo": "blue",
                "Medio": "orange",
                "Alto": "red"
            }
            
            # Agregar marcadores
            if hasattr(self, 'last_predictions') and self.last_predictions is not None:
                for idx, row in self.last_predictions.iterrows():
                    # Buscar coordenadas
                    coords = None
                    for coord_info in self.last_zone_coords:
                        if coord_info['id'] == row.get('id'):
                            coords = coord_info
                    
                    if coords is not None:
                        nivel = row.get('nivel_trafico', 'Desconocido')
                        intensidad = row.get('prediccion_intensidad', 0)
                        zona = row.get('zona_nombre', 'Desconocida')
                        
                        color = color_map.get(nivel, "gray")
                        
                        popup_text = f"""
                        <b>Zona:</b> {zona}<br>
                        <b>ID:</b> {row.get('id')}<br>
                        <b>Intensidad:</b> {intensidad:.1f}<br>
                        <b>Nivel:</b> {nivel}
                        """
                        
                        folium.CircleMarker(
                            location=[coords['lat'], coords['lon']],
                            radius=8,
                            popup=folium.Popup(popup_text, max_width=250),
                            color=color,
                            fill=True,
                            fillColor=color,
                            fillOpacity=0.7,
                            weight=2
                        ).add_to(m)
            
            # Guardar y abrir
            map_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapa_trafico.html")
            m.save(map_file)
            
            # Cerrar diálogo y abrir el mapa
            self.after(0, lambda: loading_dialog.close())
            webbrowser.open(f"file://{map_file}")
            
        except Exception as e:
            self.after(0, lambda: loading_dialog.close())
            self.after(0, lambda: messagebox.showerror("Error", f"No se pudo generar el mapa: {e}"))
            
        except Exception as e:
            self.after(0, lambda: loading_dialog.close())
            self.after(0, lambda: messagebox.showerror("Error", f"No se pudo generar el mapa: {e}"))


if __name__ == "__main__":
    app = SafeDriveApp()
    app.mainloop()