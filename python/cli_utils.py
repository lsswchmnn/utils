import os
import time
import threading
import sys
#=========================================================================
# Klasse für Ladescreen (Spinner)

class Spinner:
    def __init__(self, symbols="|/—\\", delay=0.15):
        self.symbols    = symbols
        self.delay      = delay
        self.running    = False
        self.thread     = None

    def start(self, message="Loading"):
        self.running = True
        self.thread = threading.Thread(target=self._spin, args=(message,), daemon=True)
        self.thread.start()

    def _spin(self, message):
        idx = 0
        while self.running:
            sys.stdout.write(f"\r{message} {self.symbols[idx % len(self.symbols)]}")
            sys.stdout.flush()
            idx += 1
            time.sleep(self.delay)
        sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")  # Clear line

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

#=========================================================================
# CLI-Utilities

def show_error(title: str="Error", text: str="An unknown error occurred."):
    print(f"\n ⚠️ {title}: {text}\n")

# Standardisierte Fehlermeldung mit Überschrift, Fehlertyp, Fehlertext und Aufforderung zum Weitermachen
def cli_blocking_message(heading: str, error_type: str, 
                         msg_error: str, msg_continue: str="Press enter to continue"):
    print_heading(heading)
    show_error(f"{error_type}", f"{msg_error}")
    enter_continue(f"{msg_continue}", seperation=True)

# Trennlinien im Terminal für saubere CLI-Abschnitte
def print_separation(length: int=50, linebreak: bool=True):
    if linebreak:
        print(f"\n{length*'='}")
    else:
        print(f"{length*'='}")

# Dünne Trennlinie
def print_thin_separation(length: int=50, linebreak: bool=True):
    if linebreak:
        print(f"\n{length*'-'}")
    else:
        print(f"{length*'-'}")

# Überschrift
def print_heading(title: str="HEADING", length: int=50, clear: bool=True, linebreak: bool=True):
    if clear:
        clear_cli()
    print_separation(length, linebreak=False)
    print(title)
    print_separation(length, linebreak=False)
    if linebreak:
        print()

# Mit Enter fortfahren
def enter_continue(msg: str="Press Enter to continue...", seperation: bool=True, linebreak: bool=True):
    if seperation:
        print_thin_separation()
    if linebreak:
        input(f"\n{msg}")
    else:
        input(f"{msg}")

# Leert das CLI komplett
def clear_cli():
    os.system('cls' if os.name == 'nt' else 'clear')
    sys.stdout.write("\r\033[2K")
    sys.stdout.flush()
    sys.stdout.write("\n")
    sys.stdout.flush()

# Fortschritts-Iterator mit tqdm; funktioniert bei for-Schleifen
def printProgressBar(iteration, 
                     total, 
                     prefix = '', 
                     suffix = '', 
                     decimals = 1, 
                     length = 100, 
                     fill = '█',
                     printEnd = "\r"):
    '''
    Ein Iterator, der über einen iterierbaren Prozess läuft,
    dabei eine Fortschrittsleiste anzeigt und optional eine Callback-Funktion
    auf jedes Element anwenden kann.

    Parameter:
    - iterable: Ein iterierbares Objekt (z.B. range, Liste, Generator).
    - desc: Beschreibung, die links von der Leiste angezeigt wird.
    - unit: Einheit für die Leiste (standard: "it" für Iterationen).
    - total: Gesamtzahl der Schritte (falls tqdm sie nicht automatisch bestimmen kann).
    - callback: Optionale Funktion, die auf jedes Element angewendet wird.

    Rückgabe:
    - Liste mit Ergebnissen der Callback-Verarbeitung (falls callback gesetzt),
    sonst eine Liste der Elemente selbst.
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    '''

    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    
    sys.stdout.write(
        f"\r{prefix} |{bar}| {percent}% {suffix}"
    )
    sys.stdout.flush()

    if iteration == total:
        sys.stdout.write("\n")
        sys.stdout.flush()

def finishProgressBar():
    sys.stdout.write("\r\033[2K\n")
    sys.stdout.flush()

#=========================================================================
# Input-Utilities

# Um Integer abzufragen
def input_int(min_value: int=0, max_value: int=10000, default: int=100, 
        forbidden: list = [], msg: str="value", loop: bool = True,
        error: bool=True) -> int | None:
    
    if forbidden is None:
        forbidden = []

    while True:
        raw = input(f"{msg} (min: {min_value}, max: {max_value}): ").strip()

        # Input leer?
        if raw == '':
            if error:
                raise ValueError("Input is empty.")
            return default

        # Ist Input ein integer?
        try:
            value = int(raw)
        except ValueError:
            if not loop:
                if error:
                    raise ValueError(f"'{raw}' is not a valid Integer.")
                return default
            else:
                if error:
                    raise ValueError(f"'{raw}' is not a valid Integer.")
                continue

        # Ist der Wert erlaubt?
        if value in forbidden:
            if not loop:
                if error:
                    raise ValueError(f"'{raw}' is not allowed.")
                return default
            else:
                if error:
                    raise ValueError(f"'{raw}' is not allowed.")
                continue

        # Wert klein genug?
        if value > max_value:
            if not loop:
                if error:
                    raise ValueError(f"{value} is to big, maximal value is {max_value}.")
                return max_value
            else:
                if error:
                    raise ValueError(f"{value} is to big, maximal value is {max_value}.")
                continue

        # Wert groß genug?
        elif value < min_value:
            if not loop:
                if error:
                    raise ValueError(f"{value} is to small, minimal value is {min_value}.")
                return min_value
            else:
                if error:
                    raise ValueError(f"{value} is to small, minimal value is {min_value}.")
                continue

        return value

# Um Float abzufragen
def input_float(min_value: float=0, max_value: float=10000, default: float=100, 
                forbidden: list = [], msg: str="value", loop: bool=True,
                error: bool=True) -> float:
    if forbidden is None:
        forbidden = []

    while True:

        raw = input(f"{msg} (min: {min_value}, max: {max_value}): ").strip()

        # Input leer?
        if raw == '':
            if error:
                show_error("InputError", "Input is empty. Returning Default")
            return default

        # "," durch "." ersetzen
        raw = raw.replace(',', '.')
        
        # Ist Input ein float?
        try:
            value = float(raw)
        except ValueError:
            if not loop:
                if error:
                    show_error("Input Error", f"'{raw}' is not a valid Float. Returning Default")
                return default
            else:
                if error:
                    show_error("Input Error", f"'{raw}' is not a valid Float.")
                continue

        # Ist der Wert erlaubt?
        if value in forbidden:
            if not loop:
                if error:
                    show_error("InputError", f"'{raw} is not allowed. Returning Default")
                return default
            else:
                if error:
                    show_error("InputError", f"'{raw} is not allowed.")
                continue

        # Wert klein genug?
        if value > max_value:
            if not loop:
                if error:
                    show_error("Input Error", f"{value} is to big, maximal value is {max_value}. Returning {max_value}")
                return max_value
            else:
                if error:
                    show_error("Input Error", f"{value} is to big, maximal value is {max_value}.")
                continue

        # Wert groß genug?
        elif value < min_value:
            if not loop:
                if error:
                    show_error("Input Error", f"{value} is to small, minimal value is {min_value}. Retruning {min_value}")
                return min_value
            else:
                if error:
                    show_error("Input Error", f"{value} is to small, minimal value is {min_value}. Retruning {min_value}")
                continue

        return value

# Um Strings abzufragen
def input_str(msg: str="value") -> str:
    value = input(f"{msg}: ").strip()
    if value == '':
        return None    
    return value

# Ja/Nein Abfrage
def input_confirm(msg: str="Are you sure?", default_true: bool=True) -> bool:
    print()
    print_thin_separation(linebreak=False)
    print()
    choice = input(f"{msg} (y/n): ").strip().lower()

    if not default_true:
        if choice == '':
            choice = False
        if choice == "y" or choice == True or choice == "yes":
            return True
        else:
            return False
        
    elif default_true:
        if choice == '':
            choice = True
        if choice == "n" or choice == False or choice == "no":
            return False
        else:
            return True