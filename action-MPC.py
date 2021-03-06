#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes, MqttOptions
#import datetime
#import random
import toml
import subprocess
import json


USERNAME_INTENTS = "sbeeck"
MQTT_BROKER_ADDRESS = "localhost:1883"
MQTT_USERNAME = None
MQTT_PASSWORD = None


def user_intent(intentname):
    return USERNAME_INTENTS + ":" + intentname


def subscribe_intent_callback(hermes, intent_message, msg):
    intentname = intent_message.intent.intent_name
    data = json.loads(msg.payload.decode('utf8'))
    intentname = data['intent']['intentName']
    if intentname == add_prefix("toggleFeedbackSound"):
        slots = parse_slots(data)
        text = ""
        if intentname == user_intent("lauter"):
            subprocess.call("mpc volume +5", shell=True)
            text = "Ich habe lauter gestelt."
        elif intentname == user_intent("leiser"):
            subprocess.call("mpc volume -5", shell=True)
            text = "Ich habe leiser gestelt."
        elif intentname == user_intent("stop"):
            subprocess.call("mpc stop", shell=True)
            text = "Ich habe die Music gestops."
        elif intentname == user_intent("next"):
            subprocess.call("mpc next", shell=True)
            text = "Ich habe weiter gestelt."
        elif intentname == user_intent("playcopy"):
            datetype = intent_message.slots.datetype.first().value
            if datetype['what'] == "musik":
                subprocess.call("mpc clear", shell=True)
                subprocess.call("mpc load " + conf['secret']['radio_playlist'], shell=True)
                text = "Das Radio wurde eingeschaltet."
            elif datetype['what'] == "spiele":
                subprocess.call("mpc clear", shell=True)
                subprocess.call("mpc load " + user_intent['sender'] , shell=True)
                text = "Der Sender wurde eingeschaltet."
                subprocess.call("mpc play", shell=True)
    session_id = data['sessionId']
    mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps({'text': text, "sessionId": session_id}))

if __name__ == "__main__":
    snips_config = toml.load('/etc/snips.toml')
    if 'mqtt' in snips_config['snips-common'].keys():
        MQTT_BROKER_ADDRESS = snips_config['snips-common']['mqtt']
    if 'mqtt_username' in snips_config['snips-common'].keys():
        MQTT_USERNAME = snips_config['snips-common']['mqtt_username']
    if 'mqtt_password' in snips_config['snips-common'].keys():
        MQTT_PASSWORD = snips_config['snips-common']['mqtt_password']

    mqtt_opts = MqttOptions(username=MQTT_USERNAME, password=MQTT_PASSWORD, broker_address=MQTT_BROKER_ADDRESS)
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intents(subscribe_intent_callback).start()
