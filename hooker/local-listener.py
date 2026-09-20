from tokenize import String
from typing import Any

from flask import Flask, jsonify, request
from pythonosc.udp_client import SimpleUDPClient

from rpi.webhook_relay import RelayController, load_config, parse_args
from utils.payload import Payload

app = Flask(__name__)

counter = 0


# Blast with Tens Unit
def tens_send():
    return


@app.route("/")
def hello_world():
    global counter
    return "<h1 style='font-size: 100'>Total Hits: " + str(counter) + "<h1>"


args = parse_args()
controller = RelayController(load_config(args.config), dry_run=True)


@app.route("/webhook", methods=["POST"])
def webhook_receiver():
    global counter
    # print(request.data)
    # this could be NoneType but not gonna bother with the typecasting :P
    data: dict[str, Any] = request.json

    payload: Payload = Payload()
    payload.unpack_json(data)

    _ = controller.pulse(payload.get_player(), payload.get_damage())

    # Process the data and perform actions based on the event
    print("Received webhook data:", payload.get_damage())

    osc_send(payload)
    counter += 1

    return jsonify({"message": "Webhook received successfully"}), 200


# OSC Send
def osc_send(payload: Payload) -> None:
    global counter
    ip = "127.0.0.1"
    port = 8000

    client = SimpleUDPClient(ip, port)  # Create client

    # cheeky add a tens to fire Sub 11 if death else 1 for example
    print(payload.death)
    death_cue: str = "1" if payload.death else ""

    # Case match ping for users
    match payload.player:
        # Louis
        case "AulrenT":
            client.send_message("/eos/sub/" + death_cue + "1/fire", "")
        # Aaron
        case "cado47":
            client.send_message("/eos/sub/" + death_cue + "2/fire", "")
        # Miki
        case "JustImagine436":
            client.send_message("/eos/sub/" + death_cue + "3/fire", "")
        # L
        case "whatever L is":
            client.send_message("/eos/sub/" + death_cue + "4/fire", "")
        # Leon
        case "leon024":
            client.send_message("/eos/sub/" + death_cue + "5/fire", "")
        # Luke
        case "rankquasar64914":
            client.send_message("/eos/sub/" + death_cue + "6/fire", "")
        case _:
            pass

    print("OSC ping")
    print(counter)
    print()
    return


if __name__ == "__main__":
    app.run(debug=True)
