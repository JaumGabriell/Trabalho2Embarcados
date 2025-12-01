import paho.mqtt.client as mqtt
import json
import time

class MQTTClient:
    """Cliente MQTT para monitoramento"""
    
    def __init__(self, broker="localhost", port=1883):
        self.broker = broker
        self.port = port
        # Compatível com paho-mqtt 1.6.1
        self.client = mqtt.Client()
        self.connected = False
        
        self.topics = {
            'alert': 'datacenter/fuzzy/alert',
            'control': 'datacenter/fuzzy/control',
            'temp': 'datacenter/fuzzy/temp'
        }
        
        # Configura callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback quando conecta"""
        if rc == 0:
            self.connected = True
            print(f"🟢 MQTT conectado ao broker {self.broker}:{self.port}")
        else:
            self.connected = False
            print(f"❌ Falha na conexão MQTT. Código: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback quando desconecta"""
        self.connected = False
        if rc != 0:
            print(f"⚠️ MQTT desconectado inesperadamente. Código: {rc}")
    
    def connect(self):
        """Conecta ao broker MQTT"""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            time.sleep(0.5)  # Aguarda conexão estabelecer
            return self.connected
        except Exception as e:
            print(f"❌ Erro ao conectar MQTT: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Desconecta do broker"""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
    
    def publish_alert(self, alert_data):
        """Publica alerta"""
        if self.connected and self.client.is_connected():
            try:
                payload = json.dumps(alert_data)
                result = self.client.publish(self.topics['alert'], payload, qos=1)
                return result.rc == mqtt.MQTT_ERR_SUCCESS
            except Exception as e:
                print(f"⚠️ Erro ao publicar alerta: {e}")
                return False
        return False
    
    def publish_control_data(self, data):
        """Publica dados de controle"""
        if self.connected and self.client.is_connected():
            try:
                payload = json.dumps(data)
                self.client.publish(self.topics['control'], payload, qos=1)
                self.client.publish(self.topics['temp'], str(data.get('erro', 0)), qos=1)
                return True
            except Exception as e:
                print(f"⚠️ Erro ao publicar dados de controle: {e}")
                self.connected = False
                return False
        return False
    
    def is_connected(self):
        """Verifica se está conectado"""
        # Verifica tanto a flag quanto o estado real do cliente
        return self.connected and self.client.is_connected()
