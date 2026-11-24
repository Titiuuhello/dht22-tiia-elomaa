# Tiia Elomaa
# 24.11.2026
# DHT22-anturin harjoitus

# Tuodaan kaikki ohjelmassa tarvittavat kirjastot
from machine import Pin
import dht
import time
import network
from umqtt.simple import MQTTClient
from wifi_config import SSID, PASSWORD

# Yhdistetään Pico WiFi-verkkoon
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Yhdistetään verkkoon...")

while not wlan.isconnected():
    time.sleep(1)

ip = wlan.ifconfig()[0]
print("IP-osoite:", ip)
print("WiFi-yhteys muodostettu")

# Yhdistetään MQTT-brokeriin
client = MQTTClient(
    b"dht22-tiia-elomaa",
    "iot.research.hamk.fi",
    keepalive=60
)

client.connect()
print("MQTT-yhteys muodostettu")

# Määritellään MQTT-aiheet
topic_lampo = b"HAMK/Fo/DHT22/amk1021358/lampotila"
topic_kosteus = b"HAMK/Fo/DHT22/amk1021358/kosteus"

# Määritellään DHT22-anturi
anturi = dht.DHT22(Pin(21))

# Asetetaan edellisten mittaustulosten alkuarvot
vanha_lampo = None
vanha_kosteus = None

# Mitataan lämpötila ja kosteus jatkuvasti
while True:
    anturi.measure()

    lampotila = round(anturi.temperature(), 1)
    kosteus = round(anturi.humidity(), 1)

    print("Lämpötila:", lampotila, "°C")
    print("Kosteus:", kosteus, "%")

    # Tarkistetaan, onko lämpötila muuttunut
    if lampotila != vanha_lampo:
        client.publish(topic_lampo, str(lampotila).encode())
        print("Lämpötila muuttunut - viesti lähetetty")
    else:
        print("Lämpötila ennallaan - ei lähetetty")

    # Tarkistetaan, onko kosteus muuttunut
    if kosteus != vanha_kosteus:
        client.publish(topic_kosteus, str(kosteus).encode())
        print("Kosteus muuttunut - viesti lähetetty")
    else:
        print("Kosteus ennallaan - ei lähetetty")

    # Tallennetaan mittaustulokset seuraavaa vertailua varten
    vanha_lampo = lampotila
    vanha_kosteus = kosteus

    print("------------")

    # Pidetään MQTT-yhteys aktiivisena
    client.ping()
    client.check_msg()

    # Odotetaan 10 sekuntia ennen seuraavaa mittausta
    time.sleep(10)