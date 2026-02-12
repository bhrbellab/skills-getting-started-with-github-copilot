from flask import Flask, jsonify, request
import os

static_dir = os.path.join(os.path.dirname(__file__), "src", "static")
app = Flask(__name__, static_folder=static_dir, static_url_path="")

# In-memory activities store
ACTIVITIES = {
    "Chess Club": {
        "description": "Weekly chess practice and friendly matches.",
        "schedule": "Wednesdays 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["alice@mergington.edu"]
    },
    "Robotics Team": {
        "description": "Build and program robots for competitions.",
        "schedule": "Tuesdays 4:00 PM - 6:00 PM",
        "max_participants": 12,
        "participants": []
    },
    "Art Club": {
        "description": "Open studio and group projects.",
        "schedule": "Fridays 2:30 PM - 4:00 PM",
        "max_participants": 15,
        "participants": ["bob@mergington.edu", "carol@mergington.edu"]
    }
}

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/activities", methods=["GET"])
def list_activities():
    return jsonify(ACTIVITIES)

@app.route("/activities/<path:activity>/signup", methods=["POST"])
def signup(activity):
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"detail": "Email is required"}), 400

    # activity path param is URL-decoded by Flask
    if activity not in ACTIVITIES:
        return jsonify({"detail": "Activity not found"}), 404

    act = ACTIVITIES[activity]
    participants = act.setdefault("participants", [])

    if email in participants:
        return jsonify({"detail": "Already signed up"}), 409

    if len(participants) >= act.get("max_participants", 0):
        return jsonify({"detail": "Activity is full"}), 409

    participants.append(email)
    return jsonify({"message": f"{email} signed up for {activity}"}), 200

@app.route("/activities/<path:activity>/participants/<path:email>", methods=["DELETE"])
def remove_participant(activity, email):
    if activity not in ACTIVITIES:
        return jsonify({"detail": "Activity not found"}), 404

    act = ACTIVITIES[activity]
    participants = act.get("participants", [])

    if email not in participants:
        return jsonify({"detail": "Participant not found"}), 404

    participants.remove(email)
    return jsonify({"message": f"Removed {email} from {activity}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
