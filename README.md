# ChatBot de Soporte Técnico Nivel 1

**TUP – Organización Empresarial – Trabajo Práctico Integrador**
Alumno: Christian Damian Ruiz | UTN | Comisión 10

---

## Descripción

Chatbot de consola que automatiza el proceso de **soporte técnico nivel 1**
siguiendo el flujo modelado en BPMN 2.0. Implementa una Máquina de Estados,
persistencia en JSON y base de conocimiento en CSV.

## Requisitos

- Python 3.10 o superior
- Sin dependencias externas (usa solo la biblioteca estándar)

## Estructura del proyecto

```
tpi_soporte/
│
├── chatbot.py              # Código principal – Máquina de estados
├── base_conocimiento.csv   # Base de datos simulada (10 soluciones)
├── tickets.json            # Registro de tickets (generado en ejecución)
└── README.md               # Este archivo
```

## Ejecución

```bash
cd tpi_soporte
python chatbot.py
```

## Flujo del proceso

```
INICIO
  └─► BIENVENIDA
        └─► NOMBRE (validación: letras, mín. 2 chars)
              └─► CATEGORÍA (red/impresora/sistema/acceso/correo)
                    └─► SÍNTOMA (texto libre, mín. 3 chars)
                          ├─► [Encontrado en KB] → SOLUCIÓN
                          │       ├─► Usuario confirma: sí → CONFIRMAR → CERRADO
                          │       └─► Usuario dice: no  → reintento (máx. 2)
                          │                              └─► ESCALADO (Nivel 2)
                          └─► [No encontrado en KB] → ESCALADO (Nivel 2)
```

## Categorías y síntomas disponibles

| Categoría   | Síntomas clave                            |
|-------------|-------------------------------------------|
| red         | sin_internet, lento                       |
| impresora   | no_imprime, papel_atascado                |
| sistema     | lento, pantalla_azul                      |
| acceso      | contrasena_olvidada, sin_permisos         |
| correo      | no_llegan, no_envia                       |

## Gestión de errores (camino infeliz)

| Entrada inválida          | Respuesta del bot                        |
|---------------------------|------------------------------------------|
| Nombre con números        | Solicita reingreso                       |
| Nombre < 2 caracteres     | Solicita reingreso                       |
| Categoría no listada      | Muestra opciones y solicita reingreso    |
| Síntoma < 3 caracteres    | Solicita más detalle                     |
| Confirmación ≠ s/n        | Solicita s o n                           |
| 2 intentos fallidos       | Escala automáticamente a Nivel 2         |

## Persistencia

Los tickets se guardan en `tickets.json` con el siguiente esquema:

```json
{
  "id": "TKT-0001",
  "usuario": "Juan Pérez",
  "categoria": "red",
  "sintoma": "sin_internet",
  "estado": "cerrado",
  "prioridad": "Alta",
  "fecha": "2026-06-17T10:30:00"
}
```

## Herramienta de IA utilizada

Se utilizó **Claude (Anthropic)** para:
- Diseño del diagrama BPMN 2.0
- Generación del código base de la Máquina de Estados
- Redacción del informe en formato UTN

Los prompts y respuestas se documentan en el informe PDF adjunto.
