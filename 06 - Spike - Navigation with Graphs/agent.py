class Agent(object):
    def __init__(self, id, speedType="FAST", agentType="HUNTER"):
        
        self.id = id
        
        self.name = "{}_{}".format(speedType, agentType)
        
        self.speed = speedType
        
        self.type = agentType
        
        self.traversalCost = TRAVERSAL_COSTS[speedType]
        
        self.colors = AGENT_COLORS[self.name]
        
        self.startBox = None
        
        self.currentBox = None
        
        self.targetBox = None
        
# Define the traversal costs for each tile types with each agent types with
TRAVERSAL_COSTS = {
    "FAST": {
        "CLEAR": 1,
        "MUD": 2,
        "WATER": 5,
        "FOREST": 10,
        "ICE": 15,
        "WALL": float("inf")
    },
    "SLOW": {
        "CLEAR": 2,
        "MUD": 4,
        "WATER": 10,
        "FOREST": 20,
        "ICE": 30,
        "WALL": float("inf")
    },
}

AGENT_COLORS = {
    "FAST_PREY": {
        "Start": "DARK_BLUE",
        "Path": "LIGHT_GREEN"
    },
    "SLOW_PREY": {
        "Start": "LIGHT_BLUE",
        "Path": "LIGHT_GREEN"
    },
    "FAST_HUNTER": {
        "Start": "LIGHT_RED",
        "Path": "RED"
    },
    "SLOW_HUNTER": {
        "Start": "DARK_RED",
        "Path": "RED"
    },
}