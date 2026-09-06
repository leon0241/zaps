from flask import Flask, jsonify, request
from pythonosc.udp_client import SimpleUDPClient

app = Flask(__name__)


# Blast with Tens Unit
def tens_send():
    return


# OSC Send
def osc_send():
    ip = "127.0.0.1"
    port = 8001

    client = SimpleUDPClient(ip, port)  # Create client

    client.send_message("/eos/key/go_0", "")  # Send float message

    print("OSC ping")
    return


@app.route("/webhook", methods=["POST"])
def webhook_receiver():
    data = request.json  # Get the JSON data from the incoming request
    # Process the data and perform actions based on the event
    print("Received webhook data:", data)
    osc_send()
    return jsonify({"message": "Webhook received successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
