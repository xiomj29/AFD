import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import json
import os

class State:
    """
    Clase que representa un estado en un autómata finito determinista (AFD).
    
    Atributos:
        name (str): Nombre o identificador del estado.
        is_initial (bool): Indica si es un estado inicial.
        is_final (bool): Indica si es un estado final o de aceptación.
    """
    def __init__(self, name, is_initial=False, is_final=False):
        self.name = name
        self.is_initial = is_initial
        self.is_final = is_final
    
    def __str__(self):
        """Representación en cadena del estado."""
        return self.name
    
    def __repr__(self):
        """Representación oficial del estado para depuración."""
        return self.name

class AFD:
    """
    Clase que implementa un Autómata Finito Determinista (AFD).
    
    Un AFD es una máquina de estados que acepta o rechaza cadenas de entrada
    según un conjunto de reglas definidas.
    
    Atributos:
        states (list): Lista de objetos State que representan los estados del autómata.
        alphabet (set): Conjunto de símbolos que conforman el alfabeto del autómata.
        initial_state (State): Estado inicial del autómata.
        final_states (list): Lista de estados finales o de aceptación.
        transitions (dict): Diccionario de transiciones donde la clave es una tupla (estado, símbolo)
                          y el valor es el estado destino.
    """
    def __init__(self):
        """Inicializa un AFD vacío."""
        self.states = []
        self.alphabet = set()
        self.initial_state = None
        self.final_states = []
        self.transitions = {}  # {(state, symbol): next_state}
    
    def add_state(self, state, is_initial=False, is_final=False):
        """
        Añade un nuevo estado al autómata.
        
        Args:
            state (str): Nombre del estado a añadir.
            is_initial (bool): Indica si el estado es inicial.
            is_final (bool): Indica si el estado es final.
            
        Returns:
            State: El objeto State creado.
        """
        new_state = State(state, is_initial, is_final)
        self.states.append(new_state)
        if is_initial:
            self.initial_state = new_state
        if is_final:
            self.final_states.append(new_state)
        return new_state
    
    def add_transition(self, from_state, symbol, to_state):
        """
        Añade una transición al autómata.
        
        Args:
            from_state (State): Estado de origen.
            symbol (str): Símbolo que activa la transición.
            to_state (State): Estado de destino.
        """
        if symbol not in self.alphabet and symbol != '':
            self.alphabet.add(symbol)
        
        self.transitions[(from_state, symbol)] = to_state
    
    def get_state_by_name(self, name):
        """
        Busca un estado por su nombre.
        
        Args:
            name (str): Nombre del estado a buscar.
            
        Returns:
            State: El estado encontrado o None si no existe.
        """
        for state in self.states:
            if state.name == name:
                return state
        return None
    
    def validate_string(self, input_string):
        """
        Valida si una cadena es aceptada por el autómata.
        
        Recorre la cadena de entrada símbolo por símbolo, siguiendo las transiciones
        definidas en el autómata. La cadena es aceptada si el estado final
        después de procesar toda la cadena es un estado de aceptación.
        
        Args:
            input_string (str): Cadena a validar.
            
        Returns:
            tuple: (bool, list) Donde bool indica si la cadena es aceptada y list
                  contiene los pasos de la validación para visualización.
        """
        if not self.initial_state:
            return False, []
        
        current_state = self.initial_state
        steps = [(current_state, 0, input_string)]  # [(state, position, remaining)]
        
        for i, symbol in enumerate(input_string):
            if (current_state, symbol) not in self.transitions:
                return False, steps + [(None, i+1, input_string[i+1:])]
            
            current_state = self.transitions[(current_state, symbol)]
            steps.append((current_state, i+1, input_string[i+1:]))
        
        return current_state in self.final_states, steps
    
    def to_afd_format(self):
        """
        Convierte el AFD a un formato de diccionario para serialización.
        
        Returns:
            dict: Diccionario con la representación del AFD.
        """
        data = {
            "alphabet": list(self.alphabet),
            "states": [state.name for state in self.states],
            "initial_state": self.initial_state.name if self.initial_state else "",
            "final_states": [state.name for state in self.final_states],
            "transitions": {
                f"{from_state.name},{symbol}": to_state.name 
                for (from_state, symbol), to_state in self.transitions.items()
            }
        }
        return data
    
    @classmethod
    def from_afd_format(cls, data):
        """
        Crea un AFD a partir de un diccionario con el formato específico.
        
        Args:
            data (dict): Diccionario con la representación del AFD.
            
        Returns:
            AFD: Objeto AFD creado.
        """
        afd = cls()
        
        # Add states
        for state_name in data["states"]:
            is_initial = state_name == data["initial_state"]
            is_final = state_name in data["final_states"]
            afd.add_state(state_name, is_initial, is_final)
        
        # Add transitions
        for transition_key, to_state_name in data["transitions"].items():
            from_state_name, symbol = transition_key.split(",")
            from_state = afd.get_state_by_name(from_state_name)
            to_state = afd.get_state_by_name(to_state_name)
            
            if from_state and to_state:
                afd.add_transition(from_state, symbol, to_state)
        
        return afd
    
    @classmethod
    def from_jff_format(cls, jff_content):
        """
        Crea un AFD a partir de un archivo en formato JFF (JFLAP).
        
        JFLAP es una herramienta para crear y simular autómatas,
        y utiliza un formato XML con extensión .jff para guardar
        los autómatas.
        
        Args:
            jff_content (str): Contenido del archivo JFF en formato XML.
            
        Returns:
            AFD: Objeto AFD creado.
        """
        afd = cls()
        root = ET.fromstring(jff_content)
        
        # Get states
        state_elements = root.findall(".//state")
        id_to_name = {}
        id_to_state = {}
        
        for state_elem in state_elements:
            state_id = state_elem.get("id")
            state_name = state_elem.get("name", state_id)
            id_to_name[state_id] = state_name
            
            is_initial = state_elem.find("initial") is not None
            is_final = state_elem.find("final") is not None
            
            state = afd.add_state(state_name, is_initial, is_final)
            id_to_state[state_id] = state
        
        # Get transitions
        transition_elements = root.findall(".//transition")
        for trans_elem in transition_elements:
            from_id = trans_elem.find("from").text
            to_id = trans_elem.find("to").text
            read_elem = trans_elem.find("read")
            
            symbol = read_elem.text if read_elem is not None and read_elem.text else ""
            
            from_state = id_to_state[from_id]
            to_state = id_to_state[to_id]
            
            afd.add_transition(from_state, symbol, to_state)
        
        return afd

class AFDSimulator(tk.Tk):
    """
    Simulador de Autómatas Finitos Deterministas con interfaz gráfica.
    Permite definir, guardar, cargar y simular AFDs, además de proporcionar
    herramientas para análisis de lenguajes formales.
    """
    def __init__(self):
        """
        Inicializa la aplicación del simulador, configura la ventana principal
        y crea un AFD vacío para comenzar a trabajar.
        """
        super().__init__()
        self.title("Simulador de Autómatas Finitos Deterministas")
        self.geometry("1000x700")
        
        self.current_afd = AFD()  # Instancia de AFD actual
        self.simulation_steps = []  # Almacena los pasos de la simulación
        self.current_step = 0  # Índice del paso actual en la simulación
        
        self.setup_ui()  # Configura la interfaz de usuario
    
    def setup_ui(self):
        """
        Configura la interfaz de usuario principal, creando un sistema de pestañas
        para organizar las diferentes funcionalidades.
        """
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.definition_tab = ttk.Frame(self.notebook)
        self.simulation_tab = ttk.Frame(self.notebook)
        self.tools_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.definition_tab, text="Definición de AFD")
        self.notebook.add(self.simulation_tab, text="Simulación")
        self.notebook.add(self.tools_tab, text="Herramientas")
        
        # Setup each tab
        self.setup_definition_tab()
        self.setup_simulation_tab()
        self.setup_tools_tab()
    
    def setup_definition_tab(self):
        """
        Configura la pestaña de definición del AFD, donde el usuario puede
        añadir estados, definir transiciones y gestionar el autómata.
        """
        # State definition frame
        state_frame = ttk.LabelFrame(self.definition_tab, text="Definición de Estados")
        state_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # State name
        ttk.Label(state_frame, text="Nombre del estado:").grid(row=0, column=0, padx=5, pady=5)
        self.state_name_var = tk.StringVar()  # Variable para almacenar el nombre del estado
        ttk.Entry(state_frame, textvariable=self.state_name_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        # State type checkboxes
        self.is_initial_var = tk.BooleanVar()  # Variable para indicar si es estado inicial
        ttk.Checkbutton(state_frame, text="Estado inicial", variable=self.is_initial_var).grid(row=0, column=2, padx=5, pady=5)
        
        self.is_final_var = tk.BooleanVar()  # Variable para indicar si es estado de aceptación
        ttk.Checkbutton(state_frame, text="Estado de aceptación", variable=self.is_final_var).grid(row=0, column=3, padx=5, pady=5)
        
        # Add state button
        ttk.Button(state_frame, text="Agregar Estado", command=self.add_state).grid(row=0, column=4, padx=5, pady=5)
        
        # Transition definition frame
        transition_frame = ttk.LabelFrame(self.definition_tab, text="Definición de Transiciones")
        transition_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # From state
        ttk.Label(transition_frame, text="Estado origen:").grid(row=0, column=0, padx=5, pady=5)
        self.from_state_var = tk.StringVar()  # Estado de origen para la transición
        self.from_state_combobox = ttk.Combobox(transition_frame, textvariable=self.from_state_var, state="readonly", width=15)
        self.from_state_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        # Symbol
        ttk.Label(transition_frame, text="Símbolo:").grid(row=0, column=2, padx=5, pady=5)
        self.symbol_var = tk.StringVar()  # Símbolo de la transición
        ttk.Entry(transition_frame, textvariable=self.symbol_var, width=5).grid(row=0, column=3, padx=5, pady=5)
        
        # To state
        ttk.Label(transition_frame, text="Estado destino:").grid(row=0, column=4, padx=5, pady=5)
        self.to_state_var = tk.StringVar()  # Estado destino para la transición
        self.to_state_combobox = ttk.Combobox(transition_frame, textvariable=self.to_state_var, state="readonly", width=15)
        self.to_state_combobox.grid(row=0, column=5, padx=5, pady=5)
        
        # Add transition button
        ttk.Button(transition_frame, text="Agregar Transición", command=self.add_transition).grid(row=0, column=6, padx=5, pady=5)
        
        # Transitions table frame
        table_frame = ttk.LabelFrame(self.definition_tab, text="Tabla de Transiciones")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for transitions
        self.transitions_tree = ttk.Treeview(table_frame)  # Tabla para visualizar las transiciones
        self.transitions_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars for treeview
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.transitions_tree.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.transitions_tree.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.transitions_tree.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.definition_tab)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="Cargar Autómata", command=self.load_afd).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(buttons_frame, text="Guardar Autómata", command=self.save_afd).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(buttons_frame, text="Reiniciar Autómata", command=self.reset_afd).pack(side=tk.LEFT, padx=5, pady=5)
    
    def setup_simulation_tab(self):
        """
        Configura la pestaña de simulación, donde el usuario puede
        validar cadenas y ver la ejecución paso a paso.
        """
        # Input frame
        input_frame = ttk.Frame(self.simulation_tab)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="Cadena a validar:").pack(side=tk.LEFT, padx=5, pady=5)
        self.input_string_var = tk.StringVar()  # Cadena a validar en el autómata
        ttk.Entry(input_frame, textvariable=self.input_string_var, width=30).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(input_frame, text="Validar", command=self.validate_string).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Result frame
        result_frame = ttk.Frame(self.simulation_tab)
        result_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.validation_result_var = tk.StringVar()  # Resultado de la validación
        self.validation_result_label = ttk.Label(result_frame, textvariable=self.validation_result_var, font=("Arial", 12))
        self.validation_result_label.pack(padx=5, pady=5)
        
        # Simulation frame
        sim_frame = ttk.LabelFrame(self.simulation_tab, text="Simulación paso a paso")
        sim_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Current position label
        self.current_position_var = tk.StringVar()  # Posición actual en la simulación
        ttk.Label(sim_frame, textvariable=self.current_position_var, font=("Arial", 10)).pack(padx=5, pady=5, anchor=tk.W)
        
        # Simulation steps text
        self.simulation_text = scrolledtext.ScrolledText(sim_frame, width=80, height=15)  # Área para mostrar los pasos de simulación
        self.simulation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Simulation control buttons
        control_frame = ttk.Frame(sim_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Paso anterior", command=self.prev_step).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Siguiente paso", command=self.next_step).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Reiniciar simulación", command=self.reset_simulation).pack(side=tk.LEFT, padx=5, pady=5)
    
    def setup_tools_tab(self):
        """
        Configura la pestaña de herramientas, con utilidades para analizar
        subcadenas, prefijos, sufijos y cerraduras de alfabetos.
        """
        # Substrings frame
        substrings_frame = ttk.LabelFrame(self.tools_tab, text="Subcadenas, Prefijos y Sufijos")
        substrings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        input_frame = ttk.Frame(substrings_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Cadena para analizar:").pack(side=tk.LEFT, padx=5, pady=5)
        self.substring_input_var = tk.StringVar()  # Cadena a analizar para subcadenas
        ttk.Entry(input_frame, textvariable=self.substring_input_var, width=30).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(input_frame, text="Calcular", command=self.calculate_substrings).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Results text
        results_frame = ttk.Frame(substrings_frame)
        results_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.substrings_text = scrolledtext.ScrolledText(results_frame, width=80, height=10)  # Área para mostrar resultados de subcadenas
        self.substrings_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Kleene closure frame
        kleene_frame = ttk.LabelFrame(self.tools_tab, text="Cerradura de Kleene y Positiva")
        kleene_frame.pack(fill=tk.X, padx=10, pady=5)
        
        kleene_input_frame = ttk.Frame(kleene_frame)
        kleene_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(kleene_input_frame, text="Alfabeto (ej: ab):").pack(side=tk.LEFT, padx=5, pady=5)
        self.kleene_alphabet_var = tk.StringVar()  # Alfabeto para calcular cerradura
        ttk.Entry(kleene_input_frame, textvariable=self.kleene_alphabet_var, width=15).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(kleene_input_frame, text="Longitud máxima:").pack(side=tk.LEFT, padx=5, pady=5)
        self.kleene_length_var = tk.StringVar(value="3")  # Longitud máxima para cerradura
        ttk.Entry(kleene_input_frame, textvariable=self.kleene_length_var, width=5).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(kleene_input_frame, text="Calcular", command=self.calculate_kleene).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Results text
        kleene_results_frame = ttk.Frame(kleene_frame)
        kleene_results_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.kleene_text = scrolledtext.ScrolledText(kleene_results_frame, width=80, height=10)  # Área para mostrar resultados de cerradura
        self.kleene_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
   # Event handlers
    def add_state(self):
        """
        Maneja la adición de un nuevo estado al autómata.
        Valida que el nombre no esté vacío y que no exista ya un estado con el mismo nombre.
        """
        state_name = self.state_name_var.get().strip()
        is_initial = self.is_initial_var.get()
        is_final = self.is_final_var.get()
        
        if not state_name:
            messagebox.showerror("Error", "El nombre del estado no puede estar vacío")
            return
        
        if self.current_afd.get_state_by_name(state_name):
            messagebox.showerror("Error", f"El estado {state_name} ya existe")
            return
        
        self.current_afd.add_state(state_name, is_initial, is_final)
        self.state_name_var.set("")
        self.is_initial_var.set(False)
        self.is_final_var.set(False)
        
        self.update_state_dropdowns()
        self.update_transitions_table()
    
    def add_transition(self):
        """
        Maneja la adición de una nueva transición entre estados.
        Valida que se hayan seleccionado estados origen y destino, y que
        el símbolo sea válido. Además verifica que no exista ya una transición
        con el mismo estado de origen y símbolo.
        """
        from_state_name = self.from_state_var.get()
        symbol = self.symbol_var.get().strip()
        to_state_name = self.to_state_var.get()
        
        if not from_state_name or not to_state_name:
            messagebox.showerror("Error", "Debe seleccionar los estados origen y destino")
            return
        
        if not symbol and symbol != '':  # Allow empty string for lambda transitions
            messagebox.showerror("Error", "Debe ingresar un símbolo")
            return
        
        from_state = self.current_afd.get_state_by_name(from_state_name)
        to_state = self.current_afd.get_state_by_name(to_state_name)
        
        if (from_state, symbol) in self.current_afd.transitions:
            messagebox.showerror("Error", f"Ya existe una transición desde {from_state_name} con el símbolo {symbol}")
            return
        
        self.current_afd.add_transition(from_state, symbol, to_state)
        self.symbol_var.set("")
        
        self.update_transitions_table()
    
    def validate_string(self):
        """
        Valida si una cadena es aceptada por el autómata actual.
        Guarda los pasos de la simulación para poder visualizarlos después.
        Actualiza el resultado visual según si la cadena es aceptada o rechazada.
        """
        input_string = self.input_string_var.get()
        
        if input_string is None:
            return
        
        is_accepted, steps = self.current_afd.validate_string(input_string)
        self.simulation_steps = steps
        self.current_step = 0
        
        if is_accepted:
            self.validation_result_var.set(f"La cadena '{input_string}' es ACEPTADA por el autómata")
            self.validation_result_label.configure(foreground="green")
        else:
            self.validation_result_var.set(f"La cadena '{input_string}' es RECHAZADA por el autómata")
            self.validation_result_label.configure(foreground="red")
        
        self.update_simulation_view()
    
    def next_step(self):
        """
        Avanza al siguiente paso en la simulación del autómata,
        si hay más pasos disponibles.
        """
        if self.simulation_steps and self.current_step < len(self.simulation_steps) - 1:
            self.current_step += 1
            self.update_simulation_view()
    
    def prev_step(self):
        """
        Retrocede al paso anterior en la simulación del autómata,
        si es posible (si no estamos en el primer paso).
        """
        if self.simulation_steps and self.current_step > 0:
            self.current_step -= 1
            self.update_simulation_view()
    
    def reset_simulation(self):
        """
        Reinicia la simulación al paso inicial (paso 0).
        """
        self.current_step = 0
        self.update_simulation_view()
    
    def load_afd(self):
        """
        Carga un autómata desde un archivo.
        Soporta formatos .afd (formato propio) y .jff (formato JFLAP).
        Actualiza la interfaz después de la carga.
        """
        file_types = [("AFD Files", "*.afd"), ("JFLAP Files", "*.jff"), ("All Files", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.afd'):
                with open(file_path, 'r') as f:
                    afd_data = json.load(f)
                self.current_afd = AFD.from_afd_format(afd_data)
            
            elif file_path.endswith('.jff'):
                with open(file_path, 'r') as f:
                    jff_content = f.read()
                self.current_afd = AFD.from_jff_format(jff_content)
            
            self.update_state_dropdowns()
            self.update_transitions_table()
            
            messagebox.showinfo("Éxito", f"Autómata cargado desde {file_path}")
        
        except Exception as ex:
            messagebox.showerror("Error", f"Error al cargar el archivo: {str(ex)}")
    
    def save_afd(self):
        """
        Guarda el autómata actual en un archivo con formato .afd (formato propio).
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".afd",
            filetypes=[("AFD Files", "*.afd"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            afd_data = self.current_afd.to_afd_format()
            with open(file_path, 'w') as f:
                json.dump(afd_data, f, indent=2)
            
            messagebox.showinfo("Éxito", f"AFD guardado en {file_path}")
        
        except Exception as ex:
            messagebox.showerror("Error", f"Error al guardar: {str(ex)}")
    
    def reset_afd(self):
        """
        Reinicia el autómata actual, creando uno nuevo vacío.
        Limpia la interfaz de usuario y reinicia los resultados de simulación.
        """
        self.current_afd = AFD()
        self.simulation_steps = []
        self.current_step = 0
        
        self.update_state_dropdowns()
        self.update_transitions_table()
        
        self.validation_result_var.set("")
        self.simulation_text.delete(1.0, tk.END)
        self.current_position_var.set("")
    
    def calculate_substrings(self):
        """
        Calcula y muestra todas las subcadenas, prefijos y sufijos
        de una cadena de entrada dada.
        """
        input_string = self.substring_input_var.get()
        if not input_string:
            return
        
        # Generate all possible substrings
        substrings = []
        for i in range(len(input_string)):
            for j in range(i + 1, len(input_string) + 1):
                substrings.append(input_string[i:j])
        
        # Generate all possible prefixes
        prefixes = [input_string[:i] for i in range(len(input_string) + 1)]
        
        # Generate all possible suffixes
        suffixes = [input_string[i:] for i in range(len(input_string) + 1)]
        
        # Display results
        self.substrings_text.delete(1.0, tk.END)
        self.substrings_text.insert(tk.END, f"Subcadenas ({len(substrings)}):\n")
        self.substrings_text.insert(tk.END, ", ".join(substrings) + "\n\n")
        
        self.substrings_text.insert(tk.END, f"Prefijos ({len(prefixes)}):\n")
        self.substrings_text.insert(tk.END, ", ".join(prefixes) + "\n\n")
        
        self.substrings_text.insert(tk.END, f"Sufijos ({len(suffixes)}):\n")
        self.substrings_text.insert(tk.END, ", ".join(suffixes))
    
    def calculate_kleene(self):
        """
        Calcula y muestra la cerradura de Kleene (Σ*) y la cerradura positiva (Σ+)
        de un alfabeto dado, hasta una longitud máxima especificada.
        """
        alphabet_input = self.kleene_alphabet_var.get()
        max_length_str = self.kleene_length_var.get()
        
        try:
            max_length = int(max_length_str)
        except ValueError:
            messagebox.showerror("Error", "La longitud máxima debe ser un número entero")
            return
        
        # Parse alphabet
        alphabet = []
        for char in alphabet_input:
            if char not in alphabet and not char.isspace():
                alphabet.append(char)
        
        if not alphabet:
            messagebox.showerror("Error", "El alfabeto no puede estar vacío")
            return
        
        # Generate Kleene star (including empty string)
        kleene_star = [""]
        for length in range(1, max_length + 1):
            self.generate_strings(alphabet, "", length, kleene_star)
        
        # Generate Kleene plus (excluding empty string)
        kleene_plus = [s for s in kleene_star if s]
        
        # Display results
        self.kleene_text.delete(1.0, tk.END)
        self.kleene_text.insert(tk.END, f"Cerradura de Kleene (Σ*) - {len(kleene_star)} cadenas:\n")
        self.kleene_text.insert(tk.END, ", ".join(kleene_star) + "\n\n")
        
        self.kleene_text.insert(tk.END, f"Cerradura Positiva (Σ+) - {len(kleene_plus)} cadenas:\n")
        self.kleene_text.insert(tk.END, ", ".join(kleene_plus))
    
    # Helper methods
    def update_state_dropdowns(self):
        """
        Actualiza los menús desplegables de estados con los nombres
        de los estados actuales del autómata.
        """
        state_names = [state.name for state in self.current_afd.states]
        self.from_state_combobox['values'] = state_names
        self.to_state_combobox['values'] = state_names
    
    def update_transitions_table(self):
        """
        Actualiza la tabla de transiciones para reflejar el estado actual del autómata.
        Muestra todos los estados y sus transiciones para cada símbolo del alfabeto.
        """
        # Clear current table
        for item in self.transitions_tree.get_children():
            self.transitions_tree.delete(item)
        
        # Set up columns
        self.transitions_tree['columns'] = ['state'] + sorted(list(self.current_afd.alphabet))
        self.transitions_tree.column('#0', width=0, stretch=tk.NO)
        self.transitions_tree.column('state', anchor=tk.W, width=150)
        
        self.transitions_tree.heading('#0', text='', anchor=tk.CENTER)
        self.transitions_tree.heading('state', text='Estado', anchor=tk.CENTER)
        
        for symbol in sorted(self.current_afd.alphabet):
            self.transitions_tree.column(symbol, anchor=tk.CENTER, width=80)
            self.transitions_tree.heading(symbol, text=symbol, anchor=tk.CENTER)
        
        # Add rows for each state
        for state in self.current_afd.states:
            state_label = f"{state.name}{' (I)' if state.is_initial else ''}{' (F)' if state in self.current_afd.final_states else ''}"
            
            row_values = {'state': state_label}
            for symbol in sorted(self.current_afd.alphabet):
                next_state = self.current_afd.transitions.get((state, symbol), None)
                row_values[symbol] = next_state.name if next_state else "-"
            
            self.transitions_tree.insert('', tk.END, values=[row_values.get(col, '') for col in ['state'] + sorted(list(self.current_afd.alphabet))])
    
    def update_simulation_view(self):
        """
        Actualiza la vista de simulación en la interfaz para mostrar el estado 
        actual de la simulación del autómata.
        Muestra los pasos ejecutados hasta el paso actual y resalta la posición
        actual en la cadena de entrada.
        """
        self.simulation_text.delete(1.0, tk.END)
        
        if not self.simulation_steps:
            return
            
        for i, (state, pos, remaining) in enumerate(self.simulation_steps):
            if i > self.current_step:
                break
                
            if i == self.current_step:
                state_text = f"→ Estado: {state.name if state else 'Error'}"
            else:
                state_text = f"Estado: {state.name if state else 'Error'}"
                
            self.simulation_text.insert(tk.END, f"Paso {i}: {state_text}\n")
        
        if self.simulation_steps and self.current_step < len(self.simulation_steps):
            current_state, pos, remaining = self.simulation_steps[self.current_step]
            input_string = self.input_string_var.get()
            
            if input_string:
                highlighted_string = ""
                for i, char in enumerate(input_string):
                    if i < pos:
                        highlighted_string += char
                    elif i == pos and self.current_step < len(self.simulation_steps) - 1:
                        highlighted_string += f"[{char}]"
                    else:
                        highlighted_string += char
                
                self.current_position_var.set(f"Posición actual: {highlighted_string}")
    
    def generate_strings(self, alphabet, current, length, result):
        """
        Función recursiva que genera todas las cadenas posibles de una longitud
        determinada utilizando los símbolos del alfabeto proporcionado.
    
         Args:
        alphabet: Lista de símbolos del alfabeto
        current: Cadena actual en construcción
        length: Longitud restante por generar
        result: Lista donde se almacenan las cadenas generadas
        """
        if length == 0:
            result.append(current)
            return
        
        for symbol in alphabet:
            self.generate_strings(alphabet, current + symbol, length - 1, result)

if __name__ == "__main__":
    """
    Punto de entrada principal del programa.
    Crea una instancia del simulador de AFD y la ejecuta.
    """
    app = AFDSimulator()
    app.mainloop()