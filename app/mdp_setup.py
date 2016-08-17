MAX_ATSOP_ROWS = 3
MAX_SD_COLS = 3 # Refresh after this number of pageviews
ATSOP_GAP = 10 # don't look beyond ATSOP_GAP * MAX_ATSOP_ROWS (for example : everything beyond 30sec ATSOP will be considered success)

ALPHA = 0.5 # correction factor
GAMMA = 0.5 # discount factor

ACTIONS = ['nothing', 'video'] # add actions here to extend the algorithm to other actions
REACTION_REWARD = {
    'nothing': {
            "down":0.5,
            "dead":0.5,
            "right":0.5
        },
    'video': {
            "down":0.5,
            "dead":0.5,
            "right":0.5
        }
    }
