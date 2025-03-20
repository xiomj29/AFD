# Simulador de Autómatas Finitos Deterministas (AFD)

Este código consiste en una aplicación gráfica para crear, simular y analizar Autómatas Finitos Deterministas (AFD)

## Características principales

- Crear y editar autómatas finitos deterministas de forma visual
- Definir estados iniciales y de aceptación
- Establecer transiciones entre estados
- Validar cadenas de texto contra el autómata
- Visualizar simulaciones paso a paso
- Guardar y cargar autómatas en formatos propios (.afd) y formato JFLAP (.jff)
- Herramientas para análisis de subcadenas, prefijos y sufijos
- Generación de cerraduras de Kleene y positivas

## Requisitos

- Python 3.6 o superior
- Tkinter (incluido en la mayoría de instalaciones de Python)

## Instalación

1. Clona o descarga el repositorio:
   ```bash
   git clone https://github.com/xiomj29/AFD.git
   cd AFD
   ```

2. Asegúrate de tener los requisitos instalados:
   ```bash
   # En sistemas basados en Debian/Ubuntu
   sudo apt-get install python3-tk
   
   # En macOS con Homebrew
   brew install python-tk
   
   # En Windows, Tkinter generalmente viene incluido con Python
   ```

3. Ejecuta la aplicación:
   ```bash
   python3 practica2.py
   ```

## Guía de uso

La aplicación está dividida en tres pestañas principales: Definición de AFD, Simulación y Herramientas.

### Definición de AFD

En esta pestaña puedes crear y editar tu autómata:

1. **Añadir estados**:
   - Introduce un nombre para el estado en el campo "Nombre del estado"
   - Marca "Estado inicial" si es el estado inicial del autómata
   - Marca "Estado de aceptación" si es un estado final
   - Haz clic en "Agregar Estado"

2. **Definir transiciones**:
   - Selecciona el estado origen desde el menú desplegable
   - Introduce el símbolo que activará la transición (puede ser un carácter vacío para transiciones lambda)
   - Selecciona el estado destino desde el menú desplegable
   - Haz clic en "Agregar Transición"

3. **Gestionar el autómata**:
   - "Cargar Autómata": Abre un archivo .afd o .jff existente
   - "Guardar Autómata": Guarda el autómata actual en formato .afd
   - "Reiniciar Autómata": Elimina todos los estados y transiciones para comenzar de nuevo

### Simulación

En esta pestaña puedes validar cadenas y observar su procesamiento paso a paso:

1. **Validar una cadena**:
   - Introduce la cadena en el campo "Cadena a validar"
   - Haz clic en "Validar"
   - El resultado se mostrará como "ACEPTADA" (verde) o "RECHAZADA" (rojo)

2. **Simulación paso a paso**:
   - Una vez validada una cadena, usa los botones "Paso anterior" y "Siguiente paso" para ver cómo el autómata procesa la cadena
   - "Reiniciar simulación" vuelve al primer paso
   - La visualización muestra el estado actual y resalta la posición en la cadena que se está procesando

### Herramientas

Esta pestaña ofrece funcionalidades adicionales para el análisis de lenguajes formales:

1. **Subcadenas, Prefijos y Sufijos**:
   - Introduce una cadena en el campo correspondiente
   - Haz clic en "Calcular"
   - La aplicación mostrará todas las subcadenas, prefijos y sufijos posibles

2. **Cerradura de Kleene y Positiva**:
   - Introduce los símbolos del alfabeto (ej: "ab" para un alfabeto de dos símbolos 'a' y 'b')
   - Establece la longitud máxima para limitar la generación
   - Haz clic en "Calcular"
   - La aplicación mostrará:
     - Cerradura de Kleene (Σ*): Incluye todas las cadenas posibles, incluyendo la cadena vacía
     - Cerradura Positiva (Σ+): Incluye todas las cadenas excepto la cadena vacía

## Formatos de archivo

### Formato .afd (Nativo)

El formato nativo .afd es un archivo JSON con la siguiente estructura:

```json
{
  "alphabet": ["a", "b", ...],
  "states": ["q0", "q1", ...],
  "initial_state": "q0",
  "final_states": ["q1", ...],
  "transitions": {
    "q0,a": "q1",
    "q1,b": "q0",
    ...
  }
}
```

### Formato .jff (JFLAP)

La aplicación también soporta archivos en formato JFLAP (.jff), que utiliza XML para representar los autómatas.

## Ejemplos de uso

### Creación de un autómata que acepte cadenas terminadas en 'a'

1. Añade dos estados: "q0" (inicial) y "q1" (final)
2. Añade las siguientes transiciones:
   - De q0 a q0 con símbolo 'b'
   - De q0 a q1 con símbolo 'a'
   - De q1 a q0 con símbolo 'b'
   - De q1 a q1 con símbolo 'a'
3. Prueba con cadenas como "a", "ba", "abba", etc.

### Análisis de lenguajes

1. En la pestaña "Herramientas", ingresa "abc" en el campo de subcadenas
2. Haz clic en "Calcular" para ver todas las subcadenas, prefijos y sufijos
3. Para ver las posibles combinaciones de un alfabeto {a,b}, usa la función de Cerradura de Kleene

## Consejos y solución de problemas

- Si una transición ya existe para un estado y símbolo, no se puede añadir otra (AFD significa Determinista)
- Para representar transiciones con cadena vacía (epsilon/lambda), deja el campo de símbolo vacío
- Verifica que hayas definido correctamente los estados inicial y de aceptación
- Si cargas un archivo .jff que contiene un autómata no determinista, puede que no se comporte como se espera

