"""
ChatBot de Soporte Técnico Nivel 1
===================================
TUP – Organización Empresarial – Trabajo Práctico Integrador
Alumno: Christian Damian Ruiz | Comisión 10 | UTN
Diplomatura universitaria en Python UTN 
Dimplomatura Full Stack UTN
Diplomatura analista de datos en python
Implementa una Máquina de Estados para guiar al usuario
a través del proceso de soporte técnico nivel 1.
Base de conocimiento: base_conocimiento.csv
"""

import csv
import os
import json
import datetime

# ─────────────────────────────────────────────
#  CONFIGURACIÓN
# ─────────────────────────────────────────────
BASE_CONOCIMIENTO = "base_conocimiento.csv"
REGISTRO_TICKETS  = "tickets.json"

CATEGORIAS_VALIDAS = ["red", "impresora", "sistema", "acceso", "correo"]

# ─────────────────────────────────────────────
#  ESTADOS DE LA MÁQUINA
# ─────────────────────────────────────────────
ESTADO_BIENVENIDA   = "BIENVENIDA"
ESTADO_NOMBRE       = "NOMBRE"
ESTADO_CATEGORIA    = "CATEGORIA"
ESTADO_SINTOMA      = "SINTOMA"
ESTADO_SOLUCION     = "SOLUCION"
ESTADO_CONFIRMAR    = "CONFIRMAR"
ESTADO_ESCALADO     = "ESCALADO"
ESTADO_CERRADO      = "CERRADO"

# ─────────────────────────────────────────────
#  BASE DE CONOCIMIENTO
# ─────────────────────────────────────────────
def cargar_base_conocimiento():
    """Carga el CSV de soluciones en una lista de diccionarios."""
    ruta = os.path.join(os.path.dirname(__file__), BASE_CONOCIMIENTO)
    if not os.path.exists(ruta):
        print(f"[ERROR] No se encontró '{BASE_CONOCIMIENTO}'. "
              "Ejecute el bot desde la carpeta del proyecto.")
        return []
    with open(ruta, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def buscar_solucion(base, categoria, sintoma):
    """
    Busca en la base de conocimiento por categoría y sintoma_clave.
    Retorna el registro si lo encuentra, None si no.
    """
    for fila in base:
        if (fila["categoria"].lower() == categoria.lower() and
                fila["sintoma_clave"].lower() in sintoma.lower()):
            return fila
    return None

# ─────────────────────────────────────────────
#  REGISTRO DE TICKETS (persistencia JSON)
# ─────────────────────────────────────────────
def cargar_tickets():
    ruta = os.path.join(os.path.dirname(__file__), REGISTRO_TICKETS)
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    return []


def guardar_ticket(tickets, ticket):
    tickets.append(ticket)
    ruta = os.path.join(os.path.dirname(__file__), REGISTRO_TICKETS)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)


def nuevo_id_ticket(tickets):
    return f"TKT-{len(tickets) + 1:04d}"

# ─────────────────────────────────────────────
#  VALIDACIONES (camino infeliz)
# ─────────────────────────────────────────────
def validar_nombre(texto):
    """Nombre: solo letras y espacios, mínimo 2 caracteres."""
    limpio = texto.strip()
    if len(limpio) < 2:
        return None, "El nombre debe tener al menos 2 caracteres."
    if not all(c.isalpha() or c.isspace() for c in limpio):
        return None, "El nombre solo puede contener letras y espacios."
    return limpio.title(), None


def validar_categoria(texto):
    """Valida que la categoría ingresada sea una de las permitidas."""
    limpio = texto.strip().lower()
    if limpio not in CATEGORIAS_VALIDAS:
        return None, (
            f"Categoría no reconocida. Opciones: "
            f"{', '.join(CATEGORIAS_VALIDAS)}."
        )
    return limpio, None


def validar_confirmacion(texto):
    """Acepta s/si/sí/n/no como respuesta binaria."""
    limpio = texto.strip().lower()
    if limpio in ("s", "si", "sí"):
        return True, None
    if limpio in ("n", "no"):
        return False, None
    return None, "Responda 's' para sí o 'n' para no."

# ─────────────────────────────────────────────
#  CLASE CHATBOT
# ─────────────────────────────────────────────
class ChatBotSoporte:
    """
    Máquina de estados que modela el flujo BPMN del proceso
    de soporte técnico nivel 1.

    Estados:
        BIENVENIDA → NOMBRE → CATEGORIA → SINTOMA →
        SOLUCION → CONFIRMAR → CERRADO | ESCALADO
    """

    def __init__(self):
        self.base = cargar_base_conocimiento()
        self.tickets = cargar_tickets()
        self._reset()

    def _reset(self):
        """Reinicia el contexto de la sesión actual."""
        self.estado     = ESTADO_BIENVENIDA
        self.nombre     = None
        self.categoria  = None
        self.sintoma    = None
        self.solucion   = None
        self.ticket_id  = None
        self.intentos   = 0          # intentos de resolución en el mismo ticket
        self.MAX_INTENTOS = 2

    # ── Dispatcher ───────────────────────────
    def procesar(self, entrada):
        """
        Recibe la entrada del usuario y delega al método
        correspondiente según el estado actual.
        """
        if self.estado == ESTADO_BIENVENIDA:
            return self._estado_bienvenida()
        if self.estado == ESTADO_NOMBRE:
            return self._estado_nombre(entrada)
        if self.estado == ESTADO_CATEGORIA:
            return self._estado_categoria(entrada)
        if self.estado == ESTADO_SINTOMA:
            return self._estado_sintoma(entrada)
        if self.estado == ESTADO_SOLUCION:
            return self._estado_solucion(entrada)
        if self.estado == ESTADO_CONFIRMAR:
            return self._estado_confirmar(entrada)
        if self.estado in (ESTADO_CERRADO, ESTADO_ESCALADO):
            # Si el bot ya terminó, ofrece reiniciar
            self._reset()
            return self._estado_bienvenida()
        return "Estado desconocido. Escriba cualquier mensaje para reiniciar."

    # ── Estados ──────────────────────────────
    def _estado_bienvenida(self):
        self.estado = ESTADO_NOMBRE
        return (
            "╔══════════════════════════════════════╗\n"
            "║   SOPORTE TÉCNICO NIVEL 1 – UTN TUP  ║\n"
            "╚══════════════════════════════════════╝\n\n"
            "Bienvenido al sistema de soporte técnico automatizado.\n"
            "Podré ayudarle con problemas de: red, impresora, sistema, "
            "acceso o correo.\n\n"
            "Para comenzar, ¿cuál es su nombre completo?"
        )

    def _estado_nombre(self, entrada):
        nombre, error = validar_nombre(entrada)
        if error:
            return f"⚠  {error}\n¿Cuál es su nombre completo?"
        self.nombre = nombre
        self.estado = ESTADO_CATEGORIA
        return (
            f"Gracias, {self.nombre}.\n\n"
            "¿En qué categoría se encuentra su problema?\n"
            "  1. red\n  2. impresora\n  3. sistema\n"
            "  4. acceso\n  5. correo\n\n"
            "Escriba la categoría (ej: red):"
        )

    def _estado_categoria(self, entrada):
        # Acepta tanto el número como el nombre
        mapeo = {"1": "red", "2": "impresora", "3": "sistema",
                 "4": "acceso", "5": "correo"}
        entrada = mapeo.get(entrada.strip(), entrada)

        categoria, error = validar_categoria(entrada)
        if error:
            return (
                f"⚠  {error}\n\n"
                "Categorías disponibles: red, impresora, sistema, "
                "acceso, correo.\nIntente nuevamente:"
            )
        self.categoria = categoria
        self.estado = ESTADO_SINTOMA

        guia = {
            "red":       "Describa el síntoma (ej: sin_internet, lento):",
            "impresora": "Describa el síntoma (ej: no_imprime, papel_atascado):",
            "sistema":   "Describa el síntoma (ej: lento, pantalla_azul):",
            "acceso":    "Describa el síntoma (ej: contrasena_olvidada, sin_permisos):",
            "correo":    "Describa el síntoma (ej: no_llegan, no_envia):",
        }
        return (
            f"Categoría registrada: {self.categoria.upper()}\n\n"
            + guia.get(self.categoria, "Describa el síntoma con detalle:")
        )

    def _estado_sintoma(self, entrada):
        sintoma = entrada.strip()
        if len(sintoma) < 3:
            return "⚠  Por favor describa el síntoma con más detalle:"

        self.sintoma = sintoma

        # Generar y registrar ticket
        self.ticket_id = nuevo_id_ticket(self.tickets)
        ticket = {
            "id":        self.ticket_id,
            "usuario":   self.nombre,
            "categoria": self.categoria,
            "sintoma":   self.sintoma,
            "estado":    "abierto",
            "prioridad": "pendiente",
            "fecha":     datetime.datetime.now().isoformat(timespec="seconds"),
        }
        guardar_ticket(self.tickets, ticket)

        # Buscar en base de conocimiento
        resultado = buscar_solucion(self.base, self.categoria, self.sintoma)

        if resultado:
            self.solucion = resultado["solucion"]
            prioridad     = resultado["prioridad"]
            self.estado   = ESTADO_SOLUCION

            # Actualizar prioridad en el ticket guardado
            self.tickets[-1]["prioridad"] = prioridad

            pasos = "\n".join(
                f"  {linea}" for linea in self.solucion.split(". ")
                if linea.strip()
            )
            return (
                f"Ticket registrado: {self.ticket_id} | "
                f"Prioridad: {prioridad.upper()}\n\n"
                "Se encontró una solución en la base de conocimiento:\n\n"
                f"{pasos}\n\n"
                "Por favor siga los pasos indicados.\n"
                "¿Logró resolver el problema? (s/n)"
            )
        else:
            # No hay solución en KB → escalar directamente
            self.estado = ESTADO_ESCALADO
            self.tickets[-1]["estado"]    = "escalado"
            self.tickets[-1]["prioridad"] = "Alta"
            self._guardar_tickets_actualizados()
            return (
                f"Ticket registrado: {self.ticket_id} | Prioridad: ALTA\n\n"
                "⚠  El problema no se encontró en nuestra base de conocimiento.\n"
                "Su ticket ha sido escalado a un técnico especialista de Nivel 2.\n\n"
                "Recibirá una respuesta en un plazo máximo de 4 horas hábiles.\n"
                "Conserve su número de ticket: {self.ticket_id}\n\n"
                "Escriba cualquier mensaje para iniciar una nueva consulta."
            ).replace("{self.ticket_id}", self.ticket_id)

    def _estado_solucion(self, entrada):
        """El usuario confirma si la solución funcionó."""
        ok, error = validar_confirmacion(entrada)
        if error:
            return f"⚠  {error}"
        if ok:
            self.estado = ESTADO_CONFIRMAR
            return (
                "¡Excelente! Nos alegra que su problema se haya resuelto.\n\n"
                "¿Desea cerrar el ticket oficial? (s/n)"
            )
        else:
            self.intentos += 1
            if self.intentos >= self.MAX_INTENTOS:
                # Escalar después de N intentos fallidos
                self.estado = ESTADO_ESCALADO
                self.tickets[-1]["estado"] = "escalado"
                self._guardar_tickets_actualizados()
                return (
                    f"Se alcanzó el límite de intentos ({self.MAX_INTENTOS}).\n"
                    "Su ticket ha sido escalado a Nivel 2.\n\n"
                    f"Ticket: {self.ticket_id}\n"
                    "Un técnico especialista lo contactará próximamente.\n\n"
                    "Escriba cualquier mensaje para iniciar una nueva consulta."
                )
            return (
                "Entendido. Volvamos a intentarlo.\n\n"
                "¿Puede describir con más detalle qué paso falló o qué "
                "ocurrió al seguir los pasos?\n(Describa el síntoma nuevamente)"
            )

    def _estado_confirmar(self, entrada):
        ok, error = validar_confirmacion(entrada)
        if error:
            return f"⚠  {error}"
        if ok:
            self.tickets[-1]["estado"] = "cerrado"
            self._guardar_tickets_actualizados()
            self.estado = ESTADO_CERRADO
            return (
                f"✔  Ticket {self.ticket_id} cerrado correctamente.\n"
                "Gracias por utilizar el sistema de soporte técnico.\n\n"
                "Escriba cualquier mensaje para iniciar una nueva consulta."
            )
        else:
            self.estado = ESTADO_ESCALADO
            self.tickets[-1]["estado"] = "escalado"
            self._guardar_tickets_actualizados()
            return (
                "De acuerdo. Su ticket permanece abierto y ha sido escalado "
                "a Nivel 2 para revisión adicional.\n\n"
                f"Ticket: {self.ticket_id}\n\n"
                "Escriba cualquier mensaje para iniciar una nueva consulta."
            )

    def _guardar_tickets_actualizados(self):
        ruta = os.path.join(os.path.dirname(__file__), REGISTRO_TICKETS)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.tickets, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────
#  LOOP PRINCIPAL
# ─────────────────────────────────────────────
def main():
    bot = ChatBotSoporte()
    print(bot.procesar(""))          # Arranca en BIENVENIDA (entrada vacía)
    while True:
        try:
            entrada = input("\nUsted: ").strip()
            if not entrada:
                print("[Bot]: Por favor ingrese un mensaje.")
                continue
            respuesta = bot.procesar(entrada)
            print(f"\n[Bot]: {respuesta}")
            if bot.estado in (ESTADO_CERRADO, ESTADO_ESCALADO):
                print("\n" + "─" * 44)
        except KeyboardInterrupt:
            print("\n\nSesión finalizada por el usuario.")
            break


if __name__ == "__main__":
    main()
