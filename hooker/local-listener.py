from flask import Flask, jsonify, request
from pythonosc.udp_client import SimpleUDPClient

app = Flask(__name__)

counter = 0


# Blast with Tens Unit
def tens_send():
    return


# OSC Send
def osc_send():
    global counter
    ip = "127.0.0.1"
    port = 8001

    # client = SimpleUDPClient(ip, port)  # Create client

    # client.send_message("/eos/key/go_0", "")  # Send float message

    counter += 1

    # print("OSC ping")
    print(counter)
    print()
    return


@app.route("/")
def hello_world():
    global counter
    return "<h1 style='font-size: 100'>Total Hits: " + str(counter) + "<h1>"


@app.route("/webhook", methods=["POST"])
def webhook_receiver():
    data = request.json  # Get the JSON data from the incoming request
    # Process the data and perform actions based on the event
    print("Received webhook data:", data)
    osc_send()
    return jsonify({"message": "Webhook received successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
