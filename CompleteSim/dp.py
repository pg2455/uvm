from Classes import *

# constants
GAMMA = 0

# actions
nothing = Action(0.33, 0.33, 0.33, 0.01, 0.1, -0.01, 'nothing')
videoAd = Action(0.3, 0, 0.7, 0.4, 0, -0.1, 'videoAd')

actions = [nothing, videoAd]

#Grid
nrows = 3
ncols = 3
grid = Grid(nrows, ncols, actions)

# Value Iteration
epsilon = 0.1
delta = 0
firstIteration = True
counter = 0
while delta > epsilon or firstIteration:
    print "iteration#", counter
    tmpDelta = delta
    if counter == 0:
        firstIteration = False
    for state in sorted(grid.states.keys()):
        if state == -1000:
            continue
        tmpV = grid.ValueMatrix[state]
        max_value = 0
        for action in grid.states[state].policy:
            # evaluation of action in state
            value = 0
            for next_state in grid.states[state].next:
                next_state_objID = grid.states[state].next[next_state].id
                value += action.transition[next_state] * ( action.reward[next_state] + GAMMA * grid.ValueMatrix[next_state_objID] )

            if value > max_value :
                max_value = value

        grid.ValueMatrix[state] = max_value
        delta = max(delta, abs(tmpV - max_value))

    if abs(tmpDelta - delta) < 0.00001 :
        break

    counter += 1

print delta


# deterministic policy
policy = grid.states.copy()
policy.pop(-1000)
for state in sorted(grid.states.keys()):

    max_value = -10000
    for action in grid.states[state].policy:
        # evaluation of action in state
        value = 0
        for next_state in grid.states[state].next:
            next_state_objID = grid.states[state].next[next_state].id
            value += action.transition[next_state] * ( action.reward[next_state] + GAMMA * grid.ValueMatrix[next_state_objID] )

        if value > max_value :
            max_value = value
            policy[state] = action.name
