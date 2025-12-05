import random

templates = [
    "The key to {success} is {perseverance} and {curiosity}.",
    "{Name} once said, '{Wisdom}.'",
    "Learning never exhausts the {mind}, it only {grows}."
]

fillings = {
    "success": ["success", "happiness", "innovation"],
    "perseverance": ["perseverance", "hard work", "dedication"],
    "curiosity": ["curiosity", "passion", "integrity"],
    "Name": ["Einstein", "Sidekick", "A great leader"],
    "Wisdom": [
        "Knowledge speaks, but wisdom listens",
        "Adapt, improvise, and overcome",
        "Be yourself; everyone else is already taken"
    ],
    "mind": ["mind", "spirit", "potential"],
    "grows": ["grows", "unfolds", "expands"]
}

template = random.choice(templates)
sentence = template.format(
    success=random.choice(fillings["success"]),
    perseverance=random.choice(fillings["perseverance"]),
    curiosity=random.choice(fillings["curiosity"]),
    Name=random.choice(fillings["Name"]),
    Wisdom=random.choice(fillings["Wisdom"]),
    mind=random.choice(fillings["mind"]),
    grows=random.choice(fillings["grows"])
)
print(sentence)