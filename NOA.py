# -------------------PROYECTO NOA DE TITANTECH--------------------------------------------------

# ------------------- IMPORTACIÓN DE LIBRERÍAS -------------------
from machine import Pin, time_pulse_us, PWM # Controla pines digitales, mide pulsos y genera señales PWM
import machine, network, urequests, time # Control del hardware, conexión Wi-Fi, peticiones HTTP y manejo de tiempo


# ------------------- DATOS DE CONFIGURACIÓN -------------------
ssid = "ESTUDIANTES"   # Nombre de la red Wi-Fi
password = "mblock25"  # Contraseña de la red Wi-Fi
# Datos del dispositivo en Ubidots
device_id = "sen" # ID del dispositivo en Ubidots 
token = "BBUS-YDtSMfO6Ae5AHEUKhl8kzAgbzZI4WY" # Token de autenticación de Ubidots


# ------------------- CONFIGURACIÓN DE PINES -------------------
trig = Pin(26, Pin.OUT)   # Pin 26 configurado como salida: envía el pulso ultrasónico (TRIG)
echo = Pin(27, Pin.IN)    # Pin 27 configurado como entrada: recibe el eco del pulso (ECHO)
buzzer = PWM(Pin(25))     # Pin 25 configurado como salida PWM para controlar el buzzer (alarma sonora)


# ------------------- FUNCIÓN PARA CONECTAR AL WI-FI -------------------
def connect_wifi():
    global ssid, password
    station = network.WLAN(network.STA_IF)  # Activa el Wi-Fi del ESP32
    station.active(False)                   # Reinicia el Wi-Fi
    time.sleep(1)
    if not station.isconnected():           # Si no está conectado aún
        print('Conectando a la red Wi-Fi...')
        station.active(True)
        station.connect(ssid, password)     # Conecta a la red
        while not station.isconnected():    # Espera hasta que se conecte
            print('Conectando...')
            time.sleep(2)
    print('Conectado:', station.ifconfig()) # Muestra la IP del dispositivo



# ------------------- FUNCIÓN PARA ENVIAR DATOS A UBIDOTS -------------------
def send_data(distancia):
    global device_id, token
    url = "https://industrial.api.ubidots.com/api/v1.6/devices/" + device_id
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"} # Encabezados de autenticación y tipo de dato
    data = {"sen": distancia}               # Envia la distancia medida
    response = urequests.post(url=url, headers=headers, json=data)  # Envía los datos a Ubidots por método POST
    print(response.text)                    # Muestra la respuesta del servidor
    response.close()

# ------------------- FUNCIÓN PARA MEDIR DISTANCIA -------------------
def medir_distancia():
    # Manda las ondas para detectar la distancia
    trig.value(0) # Apaga el TRIG
    time.sleep_us(2) # Espera 2 microsegundos
    trig.value(1) # Enciende el TRIG para generar el pulso ultrasónico
    time.sleep_us(10) # Mantiene el pulso durante 10 microsegundos
    trig.value(0) # Lo apaga nuevamente
      
    duracion = time_pulse_us(echo, 1, 100000)       # Mide cuánto tiempo el pin ECHO está en alto (eco del sonido)
    distancia = (duracion / 2) * 0.0343             # Convierte el tiempo en distancia (cm) usando la velocidad del sonido
    return distancia                                # Devuelve la distancia medida
    
# ------------------- FUNCIÓN PARA HACER SONAR EL BUZZER -------------------
def sonar_buzzer(freq, duracion_ms):
    buzzer.freq(freq)                   # Frecuencia del sonido (Hz)
    buzzer.duty(512)                    # Intensidad del sonido
    time.sleep(duracion_ms / 1000)      # Duración del sonido (en segundos)


# ------------------- PROGRAMA PRINCIPAL -------------------
# Inicia la conexión Wi-Fi
connect_wifi()

# Ciclo principal: mide, alerta y envía datos
while True:
    d = medir_distancia()               # Mide la distancia actual
    if d <= 150:                        # Si está a menos de 150 cm...
        sonar_buzzer(1000, 500)         # ... suena el buzzer
    else:
        buzzer.duty(0)                  # Apaga el buzzer si no hay objeto cerca
    print("Distancia:", d, "cm")        # Muestra la distancia medida
    send_data(d)                        # Envía la distancia a Ubidots
    time.sleep(0.5)                     # Espera 0.5 segundos antes de repetir el proceso