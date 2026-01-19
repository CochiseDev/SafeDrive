"""
Componentes y funcionalidad para el modo Predicción (Usuario) en SafeDrive.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pandas as pd
import json
from aemet_scraper import AemetScraper
from aemet_mapper import AemetMapper
from algorithms import preparar_datos_prediccion
import joblib
import os
import webbrowser
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
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False


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


class ZoneSelector:
    """Widget para seleccionar zonas de tráfico con búsqueda."""
    
    def __init__(self, parent, traffic_zones_df: pd.DataFrame):
        """
        Args:
            parent: widget padre
            traffic_zones_df: DataFrame con zonas de tráfico
        """
        self.traffic_zones = traffic_zones_df
        self.selected_ids = set()
        self.updating_list = False  # Flag para evitar bucles
        self.frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del selector."""
        
        # Barra de búsqueda
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Buscar zona:").pack(side="left", padx=5)
        
        self.search_var = tk.StringVar()
        
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # Botones
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Seleccionar todos", command=self._select_all).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Deseleccionar todos", command=self._deselect_all).pack(side="left", padx=2)
        
        # Listbox con zonas
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.zone_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode="multiple",
            height=10,
            exportselection=False
        )
        self.zone_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.zone_listbox.yview)
        
        # Bind para actualizar selección
        self.zone_listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
        
        # Cargar zonas inicialmente
        self._update_zone_list()
    
    def _update_zone_list(self, filter_text: str = ""):
        """Actualiza la lista de zonas con filtro opcional."""
        if self.updating_list:
            return
        
        self.updating_list = True
        self.zone_listbox.delete(0, "end")
        
        filter_lower = filter_text.lower()
        
        for _, row in self.traffic_zones.iterrows():
            zone_id = int(row['id'])
            zone_name = str(row['nombre'])  # Convertir a string por si es float
            
            # Filtro por nombre
            if not filter_lower or filter_lower in zone_name.lower():
                # Mostrar ID + Nombre
                display = f"[{zone_id}] {zone_name}"
                self.zone_listbox.insert("end", display)
                
                # Marcar como seleccionado si está en selected_ids (mantener selección anterior)
                if zone_id in self.selected_ids:
                    self.zone_listbox.selection_set("end")
        
        self.updating_list = False
    
    def _on_search(self, event=None):
        """Callback para búsqueda."""
        filter_text = self.search_var.get()
        self._update_zone_list(filter_text)
    
    def _on_listbox_select(self, *args):
        """Actualiza IDs seleccionados cuando cambia la selección."""
        if self.updating_list:
            return
        
        # Solo actualizar los IDs que están en la lista actual
        # No limpiar completamente para mantener zonas no visibles en la búsqueda
        visible_ids = set()
        for index in range(self.zone_listbox.size()):
            display_text = self.zone_listbox.get(index)
            try:
                zone_id = int(display_text.split("]")[0][1:])
                visible_ids.add(zone_id)
            except:
                pass
        
        # Remover solo los IDs visibles que estaban en selected_ids
        # y mantener los que no están en la lista actual (búsqueda anterior)
        self.selected_ids = self.selected_ids - visible_ids
        
        # Agregar los IDs que están actualmente seleccionados en el listbox
        for index in self.zone_listbox.curselection():
            display_text = self.zone_listbox.get(index)
            try:
                zone_id = int(display_text.split("]")[0][1:])
                self.selected_ids.add(zone_id)
            except:
                pass
    
    def _select_all(self):
        """Selecciona todas las zonas visibles (agrégalas a las ya seleccionadas)."""
        # Extraer IDs de las zonas visibles actualmente
        visible_zones_ids = set()
        for index in range(self.zone_listbox.size()):
            display_text = self.zone_listbox.get(index)
            try:
                zone_id = int(display_text.split("]")[0][1:])
                visible_zones_ids.add(zone_id)
            except:
                pass
        
        # Agregar todos los IDs visibles a la selección
        self.selected_ids.update(visible_zones_ids)
        
        # Seleccionar en la UI
        self.zone_listbox.selection_set(0, "end")
    
    def _deselect_all(self):
        """Deselecciona todas las zonas visibles."""
        # Extraer IDs de las zonas visibles actualmente
        visible_zones_ids = set()
        for index in range(self.zone_listbox.size()):
            display_text = self.zone_listbox.get(index)
            try:
                zone_id = int(display_text.split("]")[0][1:])
                visible_zones_ids.add(zone_id)
            except:
                pass
        
        # Remover solo los IDs visibles de la selección
        self.selected_ids -= visible_zones_ids
        
        # Deseleccionar en la UI
        self.zone_listbox.selection_clear(0, "end")
    
    def get_selected_ids(self) -> list:
        """Retorna lista de IDs seleccionados."""
        return sorted(list(self.selected_ids))
    
    def pack(self, **kwargs):
        """Packer para el widget."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid para el widget."""
        self.frame.grid(**kwargs)


class UserModeTab:
    """Pestaña de modo Predicción (Usuario) para SafeDrive."""
    
    def __init__(self, parent_notebook: ttk.Notebook, traffic_zones: pd.DataFrame):
        """
        Args:
            parent_notebook: Notebook ttk donde agregar la pestaña
            traffic_zones: DataFrame con zonas de tráfico
        """
        self.traffic_zones = traffic_zones
        self.tab = ttk.Frame(parent_notebook)
        parent_notebook.add(self.tab, text="Predicción (Usuario)")
        
        # Crear diccionario para búsqueda rápida
        self.zones_dict = {int(row['id']): row for idx, row in traffic_zones.iterrows()}
        
        self.trained_model = None
        self.trained_results = None
        self.last_aemet_data = None
        self.last_predictions = None
        self.last_zone_coords = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets de la pestaña."""
        tab = self.tab
        tab.columnconfigure(1, weight=1)
        tab.columnconfigure(2, weight=0)
        
        # Fila 0: Modelo
        lbl_modelo = ttk.Label(tab, text="Modelo:")
        lbl_modelo.grid(row=0, column=0, sticky="e", padx=(15, 5), pady=(15, 5))
        
        model_inner = ttk.Frame(tab)
        model_inner.grid(row=0, column=1, sticky="ew", pady=(15, 5))
        
        ttk.Button(
            model_inner,
            text="Cargar modelo...",
            style="Accent.TButton",
            command=self._load_model
        ).pack(side="left", padx=5)
        
        self.lbl_model_status = ttk.Label(model_inner, text="Ningún modelo cargado")
        self.lbl_model_status.pack(side="left", padx=10)
        
        # Fila 1: Fecha y Hora
        lbl_datetime = ttk.Label(tab, text="Fecha y Hora:")
        lbl_datetime.grid(row=1, column=0, sticky="e", padx=(15, 5), pady=5)
        
        datetime_frame = ttk.Frame(tab)
        datetime_frame.grid(row=1, column=1, sticky="w", pady=5)
        
        ttk.Label(datetime_frame, text="Fecha:").pack(side="left", padx=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        ttk.Entry(datetime_frame, textvariable=self.date_var, width=12).pack(side="left", padx=5)
        
        ttk.Label(datetime_frame, text="Hora:").pack(side="left", padx=5)
        self.hour_var = tk.StringVar(value="12")
        ttk.Spinbox(datetime_frame, from_=0, to=23, textvariable=self.hour_var, width=5).pack(side="left", padx=5)
        
        ttk.Label(datetime_frame, text="Min:").pack(side="left", padx=5)
        self.minute_var = tk.StringVar(value="00")
        ttk.Spinbox(datetime_frame, from_=0, to=45, increment=15, textvariable=self.minute_var, width=5).pack(side="left", padx=5)
        
        # Fila 2: Zonas
        lbl_zones = ttk.Label(tab, text="Zonas:")
        lbl_zones.grid(row=2, column=0, sticky="ne", padx=(15, 5), pady=5)
        
        zones_frame = ttk.Frame(tab)
        zones_frame.grid(row=2, column=1, columnspan=2, sticky="nsew", pady=5, padx=(0, 15))
        tab.rowconfigure(2, weight=1, minsize=120)
        
        self.zone_selector = ZoneSelector(zones_frame, self.traffic_zones)
        self.zone_selector.pack(fill="both", expand=True)
        
        # Fila 3: Botón Predecir
        btn_predict = ttk.Button(
            tab, text="Predecir", style="Accent.TButton",
            command=self._make_prediction
        )
        btn_predict.grid(row=3, column=2, padx=(10, 15), pady=(10, 5), sticky="e")
        
        # Fila 4: Tabla y Resumen
        center_frame = ttk.Frame(tab)
        center_frame.grid(row=4, column=0, columnspan=3, padx=15, pady=(10, 5), sticky="nsew")
        tab.rowconfigure(4, weight=2, minsize=180)
        center_frame.columnconfigure(0, weight=2)
        center_frame.columnconfigure(1, weight=1, minsize=220)
        
        # Tabla de resultados
        table_frame = ttk.Frame(center_frame, style="Card.TFrame")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        center_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        columns = ("zona", "pred_trafico", "nivel")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.tree.heading("zona", text="Zona")
        self.tree.heading("pred_trafico", text="Pred. Tráfico")
        self.tree.heading("nivel", text="Nivel")
        
        self.tree.column("zona", width=200, minwidth=150, anchor="w", stretch=True)
        self.tree.column("pred_trafico", width=120, minwidth=100, anchor="center", stretch=True)
        self.tree.column("nivel", width=100, minwidth=80, anchor="center", stretch=True)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        table_frame.rowconfigure(0, weight=1)
        
        # Resumen
        resumen_card = ttk.Labelframe(center_frame, text="RESUMEN", style="Card.TLabelframe")
        resumen_card.grid(row=0, column=1, sticky="nsew")
        resumen_card.rowconfigure(5, weight=1)
        
        self.lbl_total = ttk.Label(resumen_card, text="Total casos: 0")
        self.lbl_total.grid(row=0, column=0, sticky="w", pady=(2, 0), padx=5)
        
        self.lbl_bajo = ttk.Label(resumen_card, text="Bajo: 0")
        self.lbl_bajo.grid(row=1, column=0, sticky="w", pady=2, padx=5)
        
        self.lbl_medio = ttk.Label(resumen_card, text="Medio: 0")
        self.lbl_medio.grid(row=2, column=0, sticky="w", pady=2, padx=5)
        
        self.lbl_alto = ttk.Label(resumen_card, text="Alto: 0")
        self.lbl_alto.grid(row=3, column=0, sticky="w", pady=2, padx=5)
        
        ttk.Separator(resumen_card, orient="horizontal").grid(
            row=6, column=0, sticky="ew", padx=5, pady=(6, 4)
        )
        
        self.lbl_tiempo_pred = ttk.Label(resumen_card, text="Tiempo: -")
        self.lbl_tiempo_pred.grid(row=7, column=0, sticky="w", pady=2, padx=5)
        
        # Gráfico pie chart
        if MATPLOTLIB_AVAILABLE:
            self.pie_fig = Figure(figsize=(3.5, 3.0), dpi=100)
            self.pie_ax = self.pie_fig.add_subplot(111)
            self.pie_ax.axis('equal')
            self._apply_pie_theme()
            self.pie_canvas = FigureCanvasTkAgg(self.pie_fig, master=resumen_card)
            self.pie_canvas.get_tk_widget().grid(row=5, column=0, pady=(8, 8), padx=8, sticky="nsew")
            self._update_pie_chart(0, 0, 0)
        else:
            self.lbl_chart_placeholder = ttk.Label(resumen_card, text="Instala matplotlib para ver el gráfico")
            self.lbl_chart_placeholder.grid(row=5, column=0, pady=(8, 5))
        
        # Fila 5: Mapa
        bottom_map = ttk.Frame(tab)
        bottom_map.grid(row=5, column=0, columnspan=3, padx=15, pady=(10, 5), sticky="ew")
        for i in range(3):
            bottom_map.columnconfigure(i, weight=1)
        
        btn_mapa = ttk.Button(
            bottom_map, text="Mapa", style="Accent.TButton",
            command=self._show_map
        )
        btn_mapa.grid(row=0, column=1, pady=(0, 0))
        
        # Fila 6: Guardar resultados
        lbl_guardar = ttk.Label(tab, text="Guardar resultados:")
        lbl_guardar.grid(row=6, column=0, sticky="e", padx=(15, 5), pady=(5, 15))
        
        self.entry_guardar = ttk.Entry(tab)
        self.entry_guardar.grid(row=6, column=1, sticky="ew", pady=(5, 15))
        
        btn_guardar = ttk.Button(
            tab, text="Guardar", style="Accent.TButton",
            command=self._save_results
        )
        btn_guardar.grid(row=6, column=2, padx=(10, 15), pady=(5, 15))
    
    def _load_model(self):
        """Carga un modelo entrenado."""
        filepath = filedialog.askopenfilename(
            title="Seleccionar modelo entrenado",
            filetypes=[("Model files", "*.pkl *.mdl"), ("PKL files", "*.pkl"), ("MDL files", "*.mdl"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            model_package = joblib.load(filepath)
            self.trained_model = model_package
            self.trained_results = {
                'modelo': model_package['modelo'],
                'features_numericas': model_package.get('features_numericas', []),
                'features_categoricas': model_package.get('features_categoricas', []),
                'zona_stats': model_package.get('zona_stats', {}),
                'hora_stats': model_package.get('hora_stats', {}),
                'median_values': model_package.get('median_values', {}),
            }
            
            model_name = os.path.basename(filepath)
            self.lbl_model_status.config(
                text=f"✓ Modelo cargado: {model_name}",
                foreground="green"
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el modelo:\n{e}")
            self.lbl_model_status.config(text="Error cargando modelo", foreground="red")
    
    def _fetch_aemet_data(self) -> dict:
        """Obtiene datos meteorológicos de AEMET.
        
        Returns:
            dict: {
                'success': bool,
                'error_type': str ('network', 'no_data', None)
            }
        """
        try:
            scraper = AemetScraper()
            
            if not scraper.test_connection():
                # Error de conexión/red
                return {'success': False, 'error_type': 'network'}
            
            # Validar que la fecha esté en el rango válido para AEMET
            # AEMET tiene datos actuales y predicciones hasta ~7 días en el futuro
            try:
                date_obj = datetime.strptime(self.date_var.get(), "%d/%m/%Y")
                today = datetime.now().date()
                date_selected = date_obj.date()
                
                # Calcular diferencia de días
                days_diff = (date_selected - today).days
                
                # AEMET solo tiene datos desde hoy hasta ~7 días en el futuro
                if days_diff < 0:  # Fecha pasada
                    return {'success': False, 'error_type': 'no_data'}
                if days_diff > 7:  # Más de 7 días en el futuro
                    return {'success': False, 'error_type': 'no_data'}
            except:
                return {'success': False, 'error_type': 'no_data'}
            
            # Obtener hora
            try:
                hour = int(self.hour_var.get())
                if not 0 <= hour <= 23:
                    return {'success': False, 'error_type': 'no_data'}
            except:
                return {'success': False, 'error_type': 'no_data'}
            
            # Obtener datos horarios
            hourly_data = scraper.get_hourly_data()
            
            hour_str = str(hour).zfill(2)
            if hour_str not in hourly_data:
                return {'success': False, 'error_type': 'no_data'}
            
            self.last_aemet_data = hourly_data[hour_str]
            return {'success': True, 'error_type': None}
            
        except Exception as e:
            # Cualquier excepción no controlada probablemente sea de red
            return {'success': False, 'error_type': 'network'}
    
    def _make_prediction(self):
        """Realiza predicción con datos seleccionados."""
        # Validaciones
        if not self.trained_model:
            messagebox.showerror("Error", "Debe cargar un modelo primero")
            return
        
        selected_zones = self.zone_selector.get_selected_ids()
        if not selected_zones:
            messagebox.showerror("Error", "Debe seleccionar al menos una zona")
            return

        # Crear diálogo de carga
        loading_dialog = LoadingDialog(self.tab.master.master, title="Predicción", message="Realizando predicción...\nPor favor espera")
        
        # Iniciar predicción en un hilo separado
        thread = Thread(target=self._prediction_worker, args=(selected_zones, loading_dialog), daemon=True)
        thread.start()

    def _prediction_worker(self, selected_zones, loading_dialog):
        """Función que se ejecuta en un hilo separado para hacer predicciones."""
        try:
            import time
            
            # Validar formato de fecha PRIMERO antes de intentar obtener datos de AEMET
            try:
                date_obj = datetime.strptime(self.date_var.get(), "%d/%m/%Y")
                hour = int(self.hour_var.get())
                minute = int(self.minute_var.get())
                fecha_str = date_obj.strftime("%d/%m/%Y") + f" {hour:02d}:{minute:02d}"
            except:
                self.tab.after(0, lambda: messagebox.showerror("Error", "Formato de fecha inválido (DD/MM/YYYY)"))
                self.tab.after(0, lambda: loading_dialog.close())
                return
            
            # Obtener datos de AEMET automáticamente
            aemet_result = self._fetch_aemet_data()
            aemet_available = aemet_result['success']
            error_type = aemet_result['error_type']
            
            if not aemet_available:
                # Mostrar advertencia según el tipo de error
                if error_type == 'network':
                    # Error de red
                    self.tab.after(0, lambda: messagebox.showwarning(
                        "Error de Conexión", 
                        "No se pudo conectar con AEMET debido a un problema de red.\n\n" +
                        "Verifica tu conexión a internet.\n\n" +
                        "Se usarán valores meteorológicos por defecto.\n" +
                        "Las predicciones pueden ser menos precisas."
                    ))
                else:
                    # Sin datos para esa fecha/hora
                    self.tab.after(0, lambda: messagebox.showwarning(
                        "Datos AEMET no disponibles", 
                        "No se pudieron obtener datos de AEMET para la fecha/hora seleccionada.\n\n" +
                        "Se usarán valores meteorológicos por defecto.\n" +
                        "Las predicciones pueden ser menos precisas."
                    ))
            
            start_time = time.time()
            
            # Mapear datos AEMET o usar valores por defecto
            if aemet_available:
                mapper = AemetMapper()
                aemet_mapped = mapper.create_prediction_dict(self.last_aemet_data)
            else:
                # Usar valores por defecto razonables (mismas claves que AemetMapper)
                aemet_mapped = {
                    'temp': 15.0,           # Temperatura media
                    'feelslike': 15.0,      # Sensación térmica
                    'dew': 10.0,            # Punto de rocío
                    'humidity': 60.0,       # Humedad media
                    'precip': 0.0,          # Sin precipitación
                    'precipprob': 0.0,      # Probabilidad de precipitación
                    'windgust': 15.0,       # Ráfaga de viento
                    'windspeed': 10.0,      # Velocidad del viento moderada
                    'winddir': 180.0,       # Dirección del viento (Sur)
                    'cloudcover': 50.0,     # Parcialmente nublado
                    'visibility': 10.0,     # Buena visibilidad (km)
                    'conditionsDay': 'Partially cloudy'  # Condición del día
                }
            
            # Crear filas para cada zona
            rows = []
            for zone_id in selected_zones:
                row = {'id': zone_id, 'fecha': fecha_str}
                row.update(aemet_mapped)
                rows.append(row)
            
            df_pred = pd.DataFrame(rows)
            
            # Preparar datos para predicción
            df_prepared = preparar_datos_prediccion(df_pred, self.trained_results)
            
            # Realizar predicción
            modelo = self.trained_results['modelo']
            pred = modelo.predict(df_prepared)
            
            elapsed = time.time() - start_time
            
            # Actualizar resultados en el hilo principal, pasando si AEMET está disponible
            self.tab.after(0, lambda: self._update_prediction_results(df_pred, selected_zones, pred, elapsed, aemet_available))
            
            # Cerrar el diálogo de carga
            self.tab.after(100, lambda: loading_dialog.close())
            
        except Exception as e:
            import traceback
            self.tab.after(0, lambda: messagebox.showerror("Error", f"Error en predicción:\n{traceback.format_exc()}"))
            self.tab.after(0, lambda: loading_dialog.close())

    def _update_prediction_results(self, df_pred, selected_zones, pred, elapsed, aemet_available=True):
        """Actualiza los resultados de predicción en la UI.
        
        Args:
            df_pred: DataFrame con datos de predicción
            selected_zones: Lista de IDs de zonas seleccionadas
            pred: Array con predicciones
            elapsed: Tiempo transcurrido
            aemet_available: Si los datos de AEMET estaban disponibles
        """
        try:
            # Guardar predicciones
            df_out = df_pred.copy()
            df_out["prediccion_intensidad"] = pred
            
            # Clasificar nivel de tráfico
            bajos = medios = altos = 0
            niveles = []
            zona_stats = self.trained_results.get('zona_stats', {})
            
            for i, p in enumerate(pred):
                zone_id = selected_zones[i]
                if zone_id in zona_stats:
                    media = zona_stats[zone_id].get('mean', 150)
                    std = zona_stats[zone_id].get('std', 100)
                else:
                    media = 150
                    std = 100
                
                std = std if std > 0 else 100
                z = (p - media) / std
                
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
            
            # Enriquecer con información de zonas y coordenadas
            zone_names = []
            zone_coords = []
            for zone_id in selected_zones:
                if int(zone_id) in self.zones_dict:
                    zone_info = self.zones_dict[int(zone_id)]
                    zone_names.append(str(zone_info.get("nombre", "Desconocida")))
                    
                    lat = self._parse_coordinate(zone_info.get("latitud"))
                    lon = self._parse_coordinate(zone_info.get("longitud"))
                    
                    if lat is None:
                        lat = 40.4168
                    if lon is None:
                        lon = -3.7038
                    
                    zone_coords.append({
                        "id": zone_id,
                        "nombre": str(zone_info.get("nombre", "Desconocida")),
                        "lat": lat,
                        "lon": lon
                    })
                else:
                    zone_names.append("Desconocida")
                    zone_coords.append({"id": zone_id, "nombre": "Desconocida", "lat": 40.4168, "lon": -3.7038})
            
            df_out["zona_nombre"] = zone_names
            self.last_zone_coords = zone_coords
            self.last_predictions = df_out
            
            # Actualizar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for idx, row in df_out.iterrows():
                self.tree.insert("", "end", values=(
                    row['zona_nombre'],
                    f"{row['prediccion_intensidad']:.1f}",
                    row['nivel_trafico']
                ))
            
            # Actualizar resumen
            total = len(pred)
            self.lbl_total.config(text=f"Total casos: {total}")
            self.lbl_bajo.config(text=f"Bajo: {bajos}")
            self.lbl_medio.config(text=f"Medio: {medios}")
            self.lbl_alto.config(text=f"Alto: {altos}")
            self.lbl_tiempo_pred.config(text=f"Tiempo: {elapsed:.2f} s")
            
            # Actualizar gráfico
            if MATPLOTLIB_AVAILABLE:
                self._update_pie_chart(bajos, medios, altos)
            
            # Solo mostrar mensaje de éxito si AEMET estaba disponible
            # (si no estaba, ya se mostró la advertencia)
            if aemet_available:
                messagebox.showinfo("Predicción", "Predicciones generadas correctamente.\n\nNota: Los datos meteorológicos se obtienen mediante scraping/mapeo desde AEMET.")
        
        except Exception as e:
            import traceback
            messagebox.showerror("Error", f"Error al actualizar resultados:\n{traceback.format_exc()}")
    
    def refresh_theme(self):
        """Actualiza el tema del pie chart cuando cambia el tema de la app."""
        if MATPLOTLIB_AVAILABLE and hasattr(self, 'pie_ax'):
            self._apply_pie_theme()
            # Re-dibujar con datos actuales si existen
            if hasattr(self, 'last_predictions') and self.last_predictions is not None:
                try:
                    niveles = self.last_predictions['nivel_trafico'].tolist()
                    bajos = niveles.count('Bajo')
                    medios = niveles.count('Medio')
                    altos = niveles.count('Alto')
                    self._update_pie_chart(bajos, medios, altos)
                except Exception:
                    self._update_pie_chart(0, 0, 0)
            else:
                self._update_pie_chart(0, 0, 0)
    
    def _parse_coordinate(self, value):
        """Extrae coordenadas WGS84 con máxima precisión."""
        if pd.isna(value):
            return None
        try:
            str_val = str(value).strip()
            is_negative = str_val.startswith('-')
            str_clean = str_val.lstrip('-').replace('.', '')
            
            if str_clean.startswith('4'):
                # Latitud (40.xxx...)
                if len(str_clean) >= 2:
                    coord = float(str_clean[0:2] + '.' + str_clean[2:])
                else:
                    coord = float(str_clean)
            elif str_clean.startswith('3'):
                # Longitud (3.xxx...)
                if len(str_clean) >= 1:
                    coord = float(str_clean[0:1] + '.' + str_clean[1:])
                else:
                    coord = float(str_clean)
            else:
                if len(str_clean) >= 2:
                    coord = float(str_clean[0:2] + '.' + str_clean[2:])
                else:
                    coord = float(str_clean)
            
            if is_negative:
                coord = -coord
            
            return coord
        except Exception:
            return None
    
    def _apply_pie_theme(self):
        """Aplica los colores del tema actual al gráfico pie."""
        if not MATPLOTLIB_AVAILABLE or not hasattr(self, 'pie_fig'):
            return
        
        try:
            import sv_ttk
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
        except:
            self.pie_text_color = "black"
    
    def _update_pie_chart(self, bajos: int, medios: int, altos: int):
        """Actualiza el gráfico pie con los datos de tráfico."""
        if MATPLOTLIB_AVAILABLE and hasattr(self, "pie_ax"):
            self.pie_ax.clear()
            
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
    
    def _show_map(self):
        """Muestra un mapa con las predicciones."""
        if not hasattr(self, 'last_zone_coords') or not self.last_zone_coords:
            messagebox.showwarning("Mapa", "No hay predicciones para mostrar. Ejecuta una predicción primero.")
            return
        
        if not FOLIUM_AVAILABLE:
            messagebox.showerror("Error", "Instala folium para ver el mapa: pip install folium")
            return
        
        # Crear diálogo de carga
        loading_dialog = LoadingDialog(self.tab.master.master, title="Mapa", message="Generando mapa...\nEsto puede tardar un momento")
        
        # Iniciar generación de mapa en hilo separado
        thread = Thread(target=self._map_worker, args=(loading_dialog,), daemon=True)
        thread.start()

    def _map_worker(self, loading_dialog):
        """Función que se ejecuta en un hilo separado para generar el mapa."""
        try:
            madrid_center = [40.4168, -3.7038]
            m = folium.Map(location=madrid_center, zoom_start=11, tiles="OpenStreetMap")
            
            color_map = {"Bajo": "blue", "Medio": "orange", "Alto": "red"}
            
            if hasattr(self, 'last_predictions') and self.last_predictions is not None:
                for idx, row in self.last_predictions.iterrows():
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
            
            map_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapa_trafico_user.html")
            m.save(map_file)
            
            # Cerrar diálogo y abrir el mapa
            self.tab.after(0, lambda: loading_dialog.close())
            webbrowser.open(f"file://{map_file}")
            
        except Exception as e:
            self.tab.after(0, lambda: loading_dialog.close())
            self.tab.after(0, lambda: messagebox.showerror("Error", f"No se pudo generar el mapa: {e}"))
    
    def _save_results(self):
        """Exporta resultados a CSV."""
        if not hasattr(self, "last_predictions") or self.last_predictions is None:
            messagebox.showwarning("Atención", "No hay predicciones para guardar. Ejecuta una predicción primero.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.last_predictions.to_csv(filename, index=False, sep=";")
                self.entry_guardar.delete(0, "end")
                self.entry_guardar.insert(0, filename)
                messagebox.showinfo("Éxito", f"Resultados exportados a:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar:\n{e}")
