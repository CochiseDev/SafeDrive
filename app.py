import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sv_ttk

try:
    import darkdetect
except ImportError:
    darkdetect = None

class SafeDriveApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SafeDrive")
        self.geometry("1100x650")
        self.minsize(950, 600)

        self.header_bg = "#1d4ed8" 

        self._create_style()
        self._create_layout()

    # ------------------ ESTILOS ------------------ #
    def _create_style(self):
        # Detectar tema del sistema (si darkdetect está instalado)
        system_theme = "light"
        if darkdetect is not None:
            try:
                detected = darkdetect.theme().lower()
                if detected in ("dark", "light"):
                    system_theme = detected
            except Exception:
                pass

        # Aplicar Sun Valley con el tema detectado
        sv_ttk.set_theme(system_theme)

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
        self.notebook.add(self.pred_tab, text="Predicción")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._build_train_tab()
        self._build_pred_tab()

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
        self._update_theme_button_icon()

    # ------------------ PESTAÑA ENTRENAMIENTO ------------------ #
    def _build_train_tab(self):
        tab = self.train_tab
        tab.columnconfigure(1, weight=1)
        tab.columnconfigure(2, weight=0)

        # Fuentes A y B
        lbl_a = ttk.Label(tab, text="Fuente de datos A:")
        lbl_a.grid(row=0, column=0, sticky="e", padx=(15, 5), pady=(15, 5))

        self.entry_fuente_a = ttk.Entry(tab)
        self.entry_fuente_a.grid(row=0, column=1, sticky="ew", pady=(15, 5))

        btn_fuente_a = ttk.Button(
            tab, text="Seleccionar",
            command=lambda: self._select_file(self.entry_fuente_a)
        )
        btn_fuente_a.grid(row=0, column=2, padx=(10, 15), pady=(15, 5))

        lbl_b = ttk.Label(tab, text="Fuente de datos B:")
        lbl_b.grid(row=1, column=0, sticky="e", padx=(15, 5), pady=5)

        self.entry_fuente_b = ttk.Entry(tab)
        self.entry_fuente_b.grid(row=1, column=1, sticky="ew", pady=5)

        btn_fuente_b = ttk.Button(
            tab, text="Seleccionar",
            command=lambda: self._select_file(self.entry_fuente_b)
        )
        btn_fuente_b.grid(row=1, column=2, padx=(10, 15), pady=5)

        # Selector de algoritmo
        lbl_alg = ttk.Label(tab, text="Seleccionar algoritmo:")
        lbl_alg.grid(row=2, column=0, sticky="e", padx=(15, 5), pady=(15, 5))

        self.combo_algoritmo = ttk.Combobox(
            tab, state="readonly",
            values=[
                "Árbol de decisión",
                "Random Forest",
                "Gradient Boosted Trees",
                "k-NN",
                "GLM (Modelo Lineal Generalizado)",
                "Deep Learning"
            ]
        )
        self.combo_algoritmo.current(0)
        self.combo_algoritmo.grid(row=2, column=1, sticky="w", pady=(15, 5))

        self.combo_algoritmo.bind("<<ComboboxSelected>>", self._on_combo_select)

        # Botón Ejecutar
        btn_ejecutar = ttk.Button(
            tab, text="Ejecutar", style="Accent.TButton",
            command=self._fake_train
        )
        btn_ejecutar.grid(row=2, column=2, padx=(10, 15), pady=(15, 5), sticky="e")

        # Vista previa de resultados
        preview_card = ttk.Labelframe(
            tab, text="VISTA PREVIA", style="Card.TLabelframe"
        )
        preview_card.grid(row=3, column=0, columnspan=3,
                          padx=15, pady=(15, 5), sticky="nsew")
        tab.rowconfigure(3, weight=0)

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
        resultado_card.grid(row=4, column=0, columnspan=3,
                            padx=15, pady=(10, 5), sticky="nsew")
        tab.rowconfigure(4, weight=1)
        resultado_card.columnconfigure(0, weight=3)
        resultado_card.columnconfigure(1, weight=1)

        self.lbl_resultado = ttk.Label(
            resultado_card,
            text="Error medio: -\nRMSE: -\nMAE: -\nR²: -",
            anchor="nw",
            justify="left"
        )
        self.lbl_resultado.grid(row=0, column=0, sticky="nsew",
                                padx=(5, 10), pady=5)


        canvas = tk.Canvas(
            resultado_card, width=180, height=120,
            bg="#fef2f2", highlightthickness=0
        )
        canvas.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=5)

        canvas.create_rectangle(20, 80, 40, 100, outline="", fill="#fecaca")
        canvas.create_rectangle(50, 60, 70, 100, outline="", fill="#fed7aa")
        canvas.create_rectangle(80, 40, 100, 100, outline="", fill="#bfdbfe")
        canvas.create_oval(110, 20, 170, 80, outline="#fb7185", width=2)
        canvas.create_arc(110, 20, 170, 80, start=0, extent=220,
                          outline="", fill="#fda4af")

        # Guardar modelo
        lbl_guardar = ttk.Label(tab, text="Guardar modelo:")
        lbl_guardar.grid(row=5, column=0, sticky="e",
                         padx=(15, 5), pady=(10, 15))

        self.entry_modelo_path = ttk.Entry(tab)
        self.entry_modelo_path.grid(row=5, column=1, sticky="ew", pady=(10, 15))

        btn_guardar_modelo = ttk.Button(
            tab, text="Guardar", style="Accent.TButton",
            command=self._save_model
        )
        btn_guardar_modelo.grid(row=5, column=2, padx=(10, 15), pady=(10, 15))

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
            command=lambda: self._select_file(self.entry_ejemplares)
        )
        btn_ejemplares.grid(row=0, column=2, padx=(10, 15), pady=(15, 5))

        lbl_modelo = ttk.Label(tab, text="Modelo a aplicar:")
        lbl_modelo.grid(row=1, column=0, sticky="e", padx=(15, 5), pady=5)

        self.entry_modelo_pred = ttk.Entry(tab)
        self.entry_modelo_pred.grid(row=1, column=1, sticky="ew", pady=5)

        btn_modelo = ttk.Button(
            tab, text="Seleccionar",
            command=lambda: self._select_file(self.entry_modelo_pred)
        )
        btn_modelo.grid(row=1, column=2, padx=(10, 15), pady=5)

        # Tabla y resumen
        center_frame = ttk.Frame(tab)
        center_frame.grid(row=2, column=0, columnspan=3,
                          padx=15, pady=(10, 5), sticky="nsew")
        tab.rowconfigure(2, weight=1)
        center_frame.columnconfigure(0, weight=3)
        center_frame.columnconfigure(1, weight=1)

        # Tabla de resultados
        table_frame = ttk.Frame(center_frame, style="Card.TFrame")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        center_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("ejemplar", "incidencia", "pred")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.tree.heading("ejemplar", text="Ejemplar")
        self.tree.heading("incidencia", text="Incidencia")
        self.tree.heading("pred", text="Pred.")

        self.tree.column("ejemplar", width=120, anchor="center")
        self.tree.column("incidencia", width=90, anchor="center")
        self.tree.column("pred", width=80, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        table_frame.rowconfigure(0, weight=1)

        # Relleno de ejemplo
        sample_rows = [
            ("Posición 1", "Sí", "55%"),
            ("Posición 2", "No", "27%"),
            ("Posición 3", "No", "47%"),
            ("Posición 4", "Sí", "75%"),
            ("Posición 5", "Sí", "62%"),
            ("Posición 6", "No", "33%"),
        ]
        for row in sample_rows:
            self.tree.insert("", "end", values=row)

        # Resumen
        resumen_card = ttk.Labelframe(
            center_frame, text="RESUMEN", style="Card.TLabelframe"
        )
        resumen_card.grid(row=0, column=1, sticky="nsew")

        self.lbl_total = ttk.Label(resumen_card, text="Total casos: 6")
        self.lbl_total.grid(row=0, column=0, sticky="w", pady=(2, 0), padx=5)

        self.lbl_vender = ttk.Label(resumen_card, text="Recom. vender: 3")
        self.lbl_vender.grid(row=1, column=0, sticky="w", pady=2, padx=5)

        self.lbl_comprar = ttk.Label(resumen_card, text="Recom. comprar: 2")
        self.lbl_comprar.grid(row=2, column=0, sticky="w", pady=2, padx=5)

        ttk.Separator(resumen_card, orient="horizontal").grid(
            row=3, column=0, sticky="ew", padx=5, pady=(6, 4)
        )

        self.lbl_tiempo_pred = ttk.Label(resumen_card, text="Tiempo: -")
        self.lbl_tiempo_pred.grid(row=4, column=0, sticky="w", pady=2, padx=5)

        pie_canvas = tk.Canvas(
            resumen_card, width=120, height=90,
            bg="#fefce8", highlightthickness=0
        )
        pie_canvas.grid(row=5, column=0, pady=(8, 5))
        pie_canvas.create_oval(10, 10, 80, 80, fill="#93c5fd", outline="")
        pie_canvas.create_arc(10, 10, 80, 80, start=30, extent=110,
                              fill="#f97373", outline="")

        # Fila 3: Mapa
        bottom_map = ttk.Frame(tab)
        bottom_map.grid(row=3, column=0, columnspan=3,
                        padx=15, pady=(10, 5), sticky="ew")
        for i in range(3):
            bottom_map.columnconfigure(i, weight=1)

        btn_mapa = ttk.Button(
            bottom_map, text="Mapa", style="Accent.TButton",
            command=self._show_map
        )
        btn_mapa.grid(row=0, column=1, pady=(0, 0))

        # Fila 4: Guardar resultados
        lbl_guardar_res = ttk.Label(tab, text="Guardar resultados:")
        lbl_guardar_res.grid(row=4, column=0, sticky="e",
                             padx=(15, 5), pady=(5, 15))

        self.entry_guardar_res = ttk.Entry(tab)
        self.entry_guardar_res.grid(row=4, column=1, sticky="ew", pady=(5, 15))

        btn_guardar_res = ttk.Button(
            tab, text="Guardar", style="Accent.TButton",
            command=self._save_results
        )
        btn_guardar_res.grid(row=4, column=2, padx=(10, 15), pady=(5, 15))

    # ------------------ FUNCIONES AUXILIARES ------------------ #
    def _select_file(self, target_entry):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Todos los archivos", "*.*")]
        )
        if filename:
            target_entry.delete(0, "end")
            target_entry.insert(0, filename)

    def _fake_train(self):
        import datetime
        now = datetime.datetime.now()

        self.lbl_fecha.config(text=f"Fecha: {now:%d/%m/%Y}")
        self.lbl_ejemplares.config(text="Ejemplares: 1.646")
        self.lbl_tiempo.config(text="Tiempo de entrenamiento: 00:01:27")
        self.lbl_alg_seleccionado.config(
            text=f"Algoritmo seleccionado: {self.combo_algoritmo.get()}"
        )

        texto = (
            "Error medio: 181.10\n"
            "RMSE: 335.23\n"
            "MAE: 181.10\n"
            "R²: 0.854\n\n"
            "Modelo entrenado correctamente."
        )
        self.lbl_resultado.config(text=texto)


        messagebox.showinfo("Entrenamiento",
                            "Entrenamiento completado (ejemplo).")

    def _save_model(self):
        filename = filedialog.asksaveasfilename(
            title="Guardar modelo",
            defaultextension=".mdl",
            filetypes=[("Modelo SafeDrive", "*.mdl"), ("Todos", "*.*")]
        )
        if filename:
            self.entry_modelo_path.delete(0, "end")
            self.entry_modelo_path.insert(0, filename)
            messagebox.showinfo("Guardar modelo",
                                f"Modelo guardado en:\n{filename}")

    def _save_results(self):
        filename = filedialog.asksaveasfilename(
            title="Guardar resultados",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")]
        )
        if filename:
            self.entry_guardar_res.delete(0, "end")
            self.entry_guardar_res.insert(0, filename)
            messagebox.showinfo("Guardar resultados",
                                f"Resultados guardados en:\n{filename}")

    def _show_map(self):
        messagebox.showinfo(
            "Mapa",
            "Aquí se mostraría el mapa de posiciones.\n"
            "(Por ahora es solo un placeholder.)"
        )


if __name__ == "__main__":
    app = SafeDriveApp()
    app.mainloop()
