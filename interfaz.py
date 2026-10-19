import customtkinter as ctk
from tkinter import messagebox
from motor import MotorInferencia

class AppInventario(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(" Agente Inteligente de Inventario - Walmart")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.motor = MotorInferencia('conocimiento/reglas.json', 'conocimiento/inventario.json')
        self.historial_evaluaciones = []
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="MENÚ", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        ctk.CTkButton(self.sidebar, text="🔍 Consultar Producto", command=self.mostrar_consulta).pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="️ Evaluar Situación", command=self.mostrar_evaluacion).pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="📊 Generar Reporte", command=self.mostrar_reporte).pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="📋 Ver Historial", command=self.mostrar_historial).pack(pady=10, padx=10)
        
        self.contenido = ctk.CTkFrame(self, corner_radius=10)
        self.contenido.grid(row=0, column=1, rowspan=2, padx=20, pady=20, sticky="nsew")
        
        self.pantalla_inicio()
    
    def limpiar_contenido(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()
    
    def pantalla_inicio(self):
        self.limpiar_contenido()
        ctk.CTkLabel(self.contenido, text="Bienvenido al Agente de Inventario", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=50)
        ctk.CTkLabel(self.contenido, text="Selecciona una opción del menú lateral", font=ctk.CTkFont(size=16)).pack()
    
    # ========== CONSULTA ==========
    def mostrar_consulta(self):
        self.limpiar_contenido()
        
        ctk.CTkLabel(self.contenido, text=" Consultar Producto", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkLabel(self.contenido, text="Escribe el nombre o código (ej: 'leche', 'P001')").pack()
        
        self.entry_busqueda = ctk.CTkEntry(self.contenido, width=400, placeholder_text="Buscar producto...")
        self.entry_busqueda.pack(pady=10)
        self.entry_busqueda.bind("<Return>", lambda e: self.ejecutar_busqueda())
        
        ctk.CTkButton(self.contenido, text="Buscar", command=self.ejecutar_busqueda).pack(pady=10)
        
        self.resultado_frame = ctk.CTkScrollableFrame(self.contenido, width=700, height=350)
        self.resultado_frame.pack(pady=20, fill="both", expand=True)
        
        ctk.CTkLabel(self.resultado_frame, text="Los resultados aparecerán aquí", text_color="gray").pack(pady=20)
    
    def ejecutar_busqueda(self):
        texto = self.entry_busqueda.get()
        if not texto:
            messagebox.showwarning("Atención", "Escribe algo para buscar")
            return
        
        if len(texto) < 2:
            messagebox.showwarning("Atención", "Escribe al menos 2 caracteres")
            return
        
        for widget in self.resultado_frame.winfo_children():
            widget.destroy()
        
        coincidencias = self.motor.buscar_productos(texto)
        
        if not coincidencias:
            ctk.CTkLabel(self.resultado_frame, text=f"❌ No se encontró '{texto}'", text_color="red", font=ctk.CTkFont(size=14)).pack(pady=20)
            return
        
        if len(coincidencias) > 1:
            ctk.CTkLabel(self.resultado_frame, text=f"🔎 Se encontraron {len(coincidencias)} productos:", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=10)
        
        for prod in coincidencias:
            prod_frame = ctk.CTkFrame(self.resultado_frame)
            prod_frame.pack(pady=5, padx=10, fill="x")
            
            ctk.CTkLabel(prod_frame, text=f"📦 {prod['nombre']} ({prod['codigo']})", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            
            info = ""
            for k, v in prod.items():
                if k not in ["nombre", "codigo"]:
                    info += f"• {k}: {v}\n"
            ctk.CTkLabel(prod_frame, text=info, justify="left").pack(anchor="w", padx=10)
            
            reglas = self.motor.evaluar_situacion(prod)
            if reglas:
                ctk.CTkLabel(prod_frame, text="⚠️ Alertas:", text_color="orange", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
                for r in reglas:
                    ctk.CTkLabel(prod_frame, text=f"  → {r['decision']} [{r['prioridad']}]", justify="left").pack(anchor="w", padx=20)
            else:
                ctk.CTkLabel(prod_frame, text="✅ Sin alertas", text_color="green").pack(anchor="w", padx=10, pady=5)
    
    # ========== EVALUACIÓN ==========
    def mostrar_evaluacion(self):
        self.limpiar_contenido()
        
        ctk.CTkLabel(self.contenido, text="⚙️ Evaluar Situación Manual", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        scroll_frame = ctk.CTkScrollableFrame(self.contenido, width=700, height=500)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        formulario = ctk.CTkFrame(scroll_frame)
        formulario.pack(pady=10, fill="x", padx=10)
        
        ctk.CTkLabel(formulario, text="Ingresa los datos de la situación:", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=10)
        
        self.vars = {}
        campos = [
            ("nivel_stock", "Nivel de stock (alto/medio/bajo/critico)"),
            ("demanda", "Demanda (alta/media/baja/estacional_alta/estacional_baja)"),
            ("tiempo_entrega", "Tiempo de entrega (rapido/lento) - opcional"),
            ("estado_caducidad", "Caducidad (normal/proximo_a_vencer) - opcional"),
            ("tipo", "Tipo (perecedero/no_perecedero) - opcional"),
            ("margen_ganancia", "Margen (alto/medio/bajo) - opcional"),
            ("proveedor", "Proveedor (unico/multiple) - opcional")
        ]
        
        for i, (campo, placeholder) in enumerate(campos):
            frame_fila = ctk.CTkFrame(formulario)
            frame_fila.pack(pady=5, fill="x", padx=10)
            
            ctk.CTkLabel(frame_fila, text=campo.replace("_", " ").title() + ":", width=150, anchor="w").pack(side="left", padx=10)
            entry = ctk.CTkEntry(frame_fila, width=400, placeholder_text=placeholder)
            entry.pack(side="left", padx=10)
            self.vars[campo] = entry
        
        botones_frame = ctk.CTkFrame(scroll_frame)
        botones_frame.pack(pady=20, fill="x", padx=10)
        
        ctk.CTkButton(botones_frame, text="✅ Evaluar", command=self.ejecutar_evaluacion, fg_color="green").pack(side="left", padx=10, expand=True)
        ctk.CTkButton(botones_frame, text="🗑️ Limpiar Campos", command=self.limpiar_campos, fg_color="orange").pack(side="left", padx=10, expand=True)
        ctk.CTkButton(botones_frame, text="➕ Nueva Evaluación", command=self.nueva_evaluacion, fg_color="blue").pack(side="left", padx=10, expand=True)
        
        self.resultado_eval = ctk.CTkFrame(scroll_frame)
        self.resultado_eval.pack(pady=10, fill="both", expand=True, padx=10)
        
        ctk.CTkLabel(self.resultado_eval, text=" Los resultados aparecerán aquí", text_color="gray", font=ctk.CTkFont(size=12)).pack(pady=20)
    
    def limpiar_campos(self):
        for campo, entry in self.vars.items():
            entry.delete(0, "end")
        
        for widget in self.resultado_eval.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(self.resultado_eval, text="📝 Campos limpios. Listo para nueva evaluación.", text_color="gray").pack(pady=20)
    
    def nueva_evaluacion(self):
        self.limpiar_campos()
        messagebox.showinfo("Nueva Evaluación", "Campos limpiados. Puedes ingresar una nueva situación.")
    
    def ejecutar_evaluacion(self):
        hechos = {}
        for campo, entry in self.vars.items():
            valor = entry.get().strip()
            if valor:
                hechos[campo] = valor
        
        for widget in self.resultado_eval.winfo_children():
            widget.destroy()
        
        if not hechos:
            ctk.CTkLabel(self.resultado_eval, text="⚠️ Completa al menos nivel_stock y demanda", text_color="red").pack(pady=20)
            return
        
        reglas = self.motor.evaluar_situacion(hechos)
        
        self.historial_evaluaciones.append({
            "hechos": hechos,
            "reglas": reglas,
            "timestamp": len(self.historial_evaluaciones) + 1
        })
        
        if reglas:
            ctk.CTkLabel(self.resultado_eval, text=f"✅ Se aplicaron {len(reglas)} regla(s):", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=10)
            
            for r in reglas:
                frame = ctk.CTkFrame(self.resultado_eval)
                frame.pack(pady=5, padx=10, fill="x")
                
                prioridad_color = {"urgente": "red", "alta": "orange", "media": "yellow", "baja": "green"}.get(r['prioridad'], "white")
                
                ctk.CTkLabel(frame, text=f"[{r['regla'].upper()}] {r['decision']}", 
                           font=ctk.CTkFont(weight="bold"), text_color=prioridad_color).pack(anchor="w", padx=10, pady=5)
                ctk.CTkLabel(frame, text=f"💡 {r['explicacion']}", justify="left").pack(anchor="w", padx=20, pady=(0,5))
        else:
            ctk.CTkLabel(self.resultado_eval, text="✅ No se aplicaron reglas. Estado estable.", text_color="green", font=ctk.CTkFont(size=14)).pack(pady=20)
    
    # ========== HISTORIAL ==========
    def mostrar_historial(self):
        self.limpiar_contenido()
        
        ctk.CTkLabel(self.contenido, text="📋 Historial de Evaluaciones", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        scroll_frame = ctk.CTkScrollableFrame(self.contenido)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        if not self.historial_evaluaciones:
            ctk.CTkLabel(scroll_frame, text="No hay evaluaciones en el historial", font=ctk.CTkFont(size=14)).pack(pady=50)
            return
        
        ctk.CTkLabel(scroll_frame, text=f"Total de evaluaciones realizadas: {len(self.historial_evaluaciones)}", 
                    font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        for eval_item in reversed(self.historial_evaluaciones):
            eval_frame = ctk.CTkFrame(scroll_frame)
            eval_frame.pack(pady=10, fill="x")
            
            ctk.CTkLabel(eval_frame, text=f"📊 Evaluación #{eval_item['timestamp']}", 
                        font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", padx=10, pady=5)
            
            hechos_text = ", ".join([f"{k}: {v}" for k, v in eval_item['hechos'].items()])
            ctk.CTkLabel(eval_frame, text=f"📝 Datos: {hechos_text}", justify="left").pack(anchor="w", padx=20, pady=5)
            
            if eval_item['reglas']:
                ctk.CTkLabel(eval_frame, text=f"✅ {len(eval_item['reglas'])} regla(s) aplicadas:", 
                            text_color="green").pack(anchor="w", padx=20, pady=5)
                for r in eval_item['reglas']:
                    ctk.CTkLabel(eval_frame, text=f"  → {r['decision']}", justify="left").pack(anchor="w", padx=30)
            else:
                ctk.CTkLabel(eval_frame, text="✅ Sin reglas aplicadas", text_color="gray").pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkButton(self.contenido, text="🗑️ Limpiar Historial", 
                     command=self.limpiar_historial, fg_color="red").pack(pady=10)
    
    def limpiar_historial(self):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de borrar todo el historial?"):
            self.historial_evaluaciones.clear()
            self.mostrar_historial()
    
    # ========== REPORTE ==========
    def mostrar_reporte(self):
        self.limpiar_contenido()
        
        ctk.CTkLabel(self.contenido, text="📊 Reporte Completo", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        scroll_frame = ctk.CTkScrollableFrame(self.contenido)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        reporte = self.motor.generar_reporte()
        
        if not reporte:
            ctk.CTkLabel(scroll_frame, text="✅ No hay alertas en el inventario").pack(pady=20)
            return
        
        for res in reporte:
            prod_frame = ctk.CTkFrame(scroll_frame)
            prod_frame.pack(pady=10, fill="x")
            
            ctk.CTkLabel(prod_frame, text=f"📦 {res['producto']} ({res['codigo']})", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
            
            for r in res['reglas']:
                color = {"urgente": "red", "alta": "orange", "media": "yellow", "baja": "green"}.get(r['prioridad'], "white")
                ctk.CTkLabel(prod_frame, text=f"  🔸 [{r['prioridad'].upper()}] {r['decision']}", text_color=color, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
                ctk.CTkLabel(prod_frame, text=f"      {r['explicacion']}", justify="left").pack(anchor="w", padx=30, pady=(0,5))

if __name__ == "__main__":
    app = AppInventario()
    app.mainloop()