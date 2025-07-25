# These are the necessary import declarations
from opentelemetry import trace
from opentelemetry import metrics

from random import randint
from flask import Flask, request
import logging

# Acquire a tracer
tracer = trace.get_tracer("diceroller.tracer")
# Acquire a meter.
meter = metrics.get_meter("diceroller.meter")

# Now create a counter instrument to make measurements with
roll_counter = meter.create_counter(
    "dice.rolls",
    description="The number of rolls by roll value",
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/rolldice")
def roll_dice():
    # This creates a new span that's the child of the current one
    with tracer.start_as_current_span("roll") as roll_span:
        player = request.args.get('player', default=None, type=str)
        result = str(roll())
        roll_span.set_attribute("roll.value", result)
        # This adds 1 to the counter for the given roll value
        roll_counter.add(1, {"roll.value": result})
        if player:
            logger.warning("%s is rolling the dice: %s", player, result)
        else:
            logger.warning("Anonymous player is rolling the dice: %s", result)
        return result


@app.route("/")
def index():
    return {
        "message": "Welcome to the Rolldice App!",
        "endpoints": {
            "/rolldice": "Roll a dice (add ?player=name for personalized rolls)",
            "/health": "Health check endpoint"
        }
    }


@app.route("/health")
def health():
    return {"status": "healthy", "service": "rolldice-app"}


def roll():
    return randint(1, 6)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
