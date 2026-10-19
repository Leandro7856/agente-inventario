import json
import os
import unicodedata

class MotorInferencia:
    def __init__(self, ruta_reglas, ruta_inventario):
        with open(ruta_reglas, 'r', encoding='utf-8') as f:
            self.reglas = json.load(f)
        with open(ruta_inventario, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            self.inventario = datos.get("productos", [])

    def _normalizar(self, valor):
        """Quita acentos, pasa a minúsculas y limpia espacios."""
        valor = str(valor).strip().lower()
        valor = unicodedata.normalize('NFKD', valor)
        valor = ''.join(c for c in valor if not unicodedata.combining(c))
        return valor

    def buscar_productos(self, texto):
        """Búsqueda inteligente: 'leche' encuentra todos los productos con 'leche' en el nombre."""
        texto_norm = self._normalizar(texto)
        coincidencias = []
        
        for prod in self.inventario:
            nombre_norm = self._normalizar(prod["nombre"])
            codigo_norm = self._normalizar(prod["codigo"])
            
            # Coincide si el texto está contenido en el nombre o código
            if texto_norm in nombre_norm or texto_norm in codigo_norm:
                coincidencias.append(prod)
        
        return coincidencias

    def evaluar_situacion(self, hechos):
        """Evalúa hechos y devuelve TODAS las reglas aplicables."""
        reglas_aplicadas = []
        hechos_norm = {k: self._normalizar(v) for k, v in hechos.items()}
        
        for nombre, detalles in self.reglas.items():
            condiciones = detalles["si"]
            if all(hechos_norm.get(k) == self._normalizar(v) for k, v in condiciones.items()):
                reglas_aplicadas.append({
                    "regla": nombre,
                    "decision": detalles["entonces"],
                    "explicacion": detalles["explicacion"],
                    "prioridad": detalles.get("prioridad", "media")
                })
        return reglas_aplicadas

    def generar_reporte(self):
        """Aplica las reglas a todo el inventario."""
        reporte = []
        for prod in self.inventario:
            reglas_aplicadas = self.evaluar_situacion(prod)
            if reglas_aplicadas:
                reporte.append({
                    "producto": prod["nombre"],
                    "codigo": prod["codigo"],
                    "reglas": reglas_aplicadas
                })
        return reporte