import random
import json
import os
import time

# === FUNCIONES LÓGICAS ===
def nor(a, b): return int(not (a or b))
def nand(a, b): return int(not (a and b))
def xnor(a, b): return int(a == b)
def zero(a, b): return 0

# === SONIDO (SOX) MEJORADO ===
def generar_tono(frecuencia=440, duracion=0.1, forma="square", volumen=0.5):
    cmd = f"play -n synth {duracion} {forma} {frecuencia} vol {volumen} > /dev/null 2>&1"
    os.system(cmd)

# === CLASES ===
class Trigrama:
    def __init__(self, nombre, bits, tipo, logica):
        self.nombre = nombre
        self.bits = bits
        self.tipo = tipo
        self.logica = logica

    def operar(self, entrada):
        return [self.logica(a, b) for a, b in zip(self.bits, entrada)]

    def to_dict(self):
        return {"nombre": self.nombre, "bits": self.bits, "tipo": self.tipo}

class Hexagrama:
    def __init__(self, sup, inf):
        self.sup = sup
        self.inf = inf
        self.bits = sup.bits + inf.bits

    def operar(self, entrada):
        return self.sup.operar(entrada[:3]) + self.inf.operar(entrada[3:])

    def to_dict(self):
        return {"sup": self.sup.to_dict(), "inf": self.inf.to_dict()}

# === BAGUA ===
BAGUA = [
    Trigrama("☰", [1,1,1], "yang", lambda a, b: a or b),
    Trigrama("☱", [1,1,0], "yang", nor),
    Trigrama("☲", [1,0,1], "yang", lambda a, b: a ^ b),
    Trigrama("☳", [1,0,0], "yang", lambda a, b: a & b),
    Trigrama("☴", [0,1,1], "yin",  nand),
    Trigrama("☵", [0,1,0], "yin",  xnor),
    Trigrama("☶", [0,0,1], "yin",  lambda a, b: int(not a)),
    Trigrama("☷", [0,0,0], "yin",  zero)
]

# === RED ===
def crear_red():
    return [[Hexagrama(random.choice(BAGUA), random.choice(BAGUA)) for _ in range(8)] for _ in range(8)]

def obtener_vecinos(x, y, matriz):
    vecinos = []
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(matriz) and 0 <= nx < len(matriz[0]):
            vecinos.append(matriz[ny][nx])
    return vecinos

def promediar_bits(salidas):
    if not salidas:
        return [0,0,0]
    suma = [sum(bits[i] for bits in salidas) for i in range(3)]
    return [1 if s >= len(salidas)/2 else 0 for s in suma]

# === CONSTRUCCIÓN DE CARA ===
def construir_cara(mutaciones, estado):
    ojos_izq_peq = list("·°o")
    ojos_izq_grd = list("O0ø")
    ojos_izq_loco = list("^*xXó")

    ojos_der_peq = list("·°o")
    ojos_der_grd = list("O0ø")
    ojos_der_loco = list("^*xXò")

    bocas_cierre = list("_-·")
    bocas_abre = list("oO~")
    bocas_raras = list("×*–")

    num_mut = len(mutaciones)
    total_bits = sum(sum(celda) for fila in estado for celda in fila)
    total_celdas = len(estado) * len(estado[0]) * 6
    energia = total_bits / total_celdas

    if energia < 0.2:
        ojo_izq = random.choice(ojos_izq_peq)
        ojo_der = random.choice(ojos_der_peq)
    elif energia < 0.6:
        ojo_izq = random.choice(ojos_izq_grd)
        ojo_der = random.choice(ojos_der_grd)
    else:
        ojo_izq = random.choice(ojos_izq_loco)
        ojo_der = random.choice(ojos_der_loco)

    if num_mut < 4:
        boca = random.choice(bocas_cierre)
    elif num_mut < 10:
        boca = random.choice(bocas_abre)
    else:
        boca = random.choice(bocas_raras)

    return f"_/°({ojo_izq}{boca}{ojo_der})"

# === VISUALIZACIÓN ===
def mostrar_estado(estado, mutaciones):
    altura = len(estado)
    ancho = len(estado[0])
    centro_y = altura // 2
    centro_x = ancho // 2

    piel = list("¹1")
    marco = list("o⁰0O")

    cara = construir_cara(mutaciones, estado)
    cuerpo = ""
    for y, fila in enumerate(estado):
        for x, celda in enumerate(fila):
            mutado = (y, x) in mutaciones
            valor = sum(celda)

            if abs(x - centro_x) <= 2 and abs(y - centro_y) <= 2:
                char = random.choice(piel)
            elif valor == 0:
                char = " "
            elif valor <= 2:
                char = random.choice(marco)
            elif valor <= 4:
                char = random.choice(piel)
            else:
                char = random.choice(marco + piel)
            cuerpo += char
        cuerpo += "\n"

    mitad = cuerpo.strip().split("\n")
    cara_coloreada = f"\033[37m{cara.center(ancho)}\033[0m"
    cuerpo_coloreado = [f"\033[92m{line}\033[0m" for line in mitad]
    cuerpo_coloreado.insert(centro_y, cara_coloreada)
    return "\n".join(cuerpo_coloreado)

# === CICLO CON SONIDO MEJORADO ===
def ciclo(red, estado, tasa=0.05):
    nuevo_estado = []
    mutaciones = set()
    for y, fila in enumerate(red):
        nueva_fila = []
        for x, hexagrama in enumerate(fila):
            vecinos = obtener_vecinos(x, y, estado)
            entrada = estado[y][x][:3] + promediar_bits([s[3:] for s in vecinos])
            if random.random() < tasa:
                if random.random() < 0.5:
                    hexagrama.sup = random.choice(BAGUA)
                else:
                    hexagrama.inf = random.choice(BAGUA)
                hexagrama.bits = hexagrama.sup.bits + hexagrama.inf.bits
                mutaciones.add((y,x))
                frecuencia = 220 + sum(hexagrama.bits) * 60
                forma = random.choice(["sine", "square", "sawtooth", "pluck"])
                generar_tono(frecuencia, duracion=0.1, forma=forma)
            salida = hexagrama.operar(entrada)
            nueva_fila.append(salida)
        nuevo_estado.append(nueva_fila)
    return nuevo_estado, mutaciones

# === GUARDADO Y CARGA ===
def guardar(nombre, red, estado, ciclo_num):
    with open(nombre, "w") as f:
        json.dump({
            "red": [[h.to_dict() for h in fila] for fila in red],
            "estado": estado,
            "ciclo": ciclo_num
        }, f)

def cargar(nombre):
    with open(nombre, "r") as f:
        data = json.load(f)

    def trigrama(d):
        log = next(t.logica for t in BAGUA if t.nombre == d["nombre"])
        return Trigrama(d["nombre"], d["bits"], d["tipo"], log)

    red = [[Hexagrama(trigrama(h["sup"]), trigrama(h["inf"])) for h in fila] for fila in data["red"]]
    estado = data["estado"]
    ciclo_num = data.get("ciclo", 0)
    return red, estado, ciclo_num

# === EJECUCIÓN PRINCIPAL ===
if __name__ == "__main__":
    archivo = "universo.json"
    if os.path.exists(archivo):
        red, estado, ciclo_num = cargar(archivo)
    else:
        red = crear_red()
        estado = [[h.operar([1,0,1,0,1,0]) for h in fila] for fila in red]
        ciclo_num = 0

    try:
        while True:
            os.system("clear")
            print(f"\n Cx {ciclo_num}\n")
            estado, mutaciones = ciclo(red, estado)
            print(mostrar_estado(estado, mutaciones))
            guardar(archivo, red, estado, ciclo_num)
            time.sleep(0.3)
            ciclo_num += 1
    except KeyboardInterrupt:
        print("\n El bitcho se duerme...\n")
