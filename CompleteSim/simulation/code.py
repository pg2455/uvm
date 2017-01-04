import numpy
# sessions are generated for 3 months
nmonths = 3
N = 10000 # number of users
TIME_GAP = 10 # seconds // states
softPaywall_TIME_THRESHOLD = 50 # seconds

# Friction factor in any state
friction_disp = 0.01 # per TIME_GAP
friction_videoAd = 0.1 # once in 24 hours and only in sd =1 or 2
friction_surveys = 0.05 # show it max twice but with 50 % chance
friction_soft = 0.15 # after 5 (50 second) states show with 70% probability

# show video in first session with this probability
showVideo_threshold = 0.6
MAX_SURVEY_COUNT = 2
showSurvey_probability = 0.5
showSoft_probability = 0.7

#HARD PAYWALL  session depth
SD_HARD_PAYWALL = 10

# user class
class userData(object):
    def __init__(self, number):
        self.id = number
        self.sd = {'total':0}
        for i in range(nmonths):
            self.sd['month'+str(i+1)] = 0

        # mean of gamma is 10 visits in 3 month
        self.arrival_frequency = numpy.random.gamma(shape = 10, scale = 2)

## grid properties
nrows = 360
ncols = 30
deadState = -1000
ncells = range(nrows *  ncols) + [deadState]
ACTIONS = ['nothing', 'video', 'survey', 'soft_paywall']


def recordTransition(segment,state, actions, reaction):
    for action in actions:
        segment.transitionProbs[state][action]['obs'] +=  1
        segment.transitionProbs[state][action][reaction] += 1


def selectRandom(probs):
    if len(probs) == 1:
        return probs[0][0]
    # action probs - list of tuples; (object, prob)
    total_prob = sum(item[1] for item in probs)
    chosen = random.uniform(0, total_prob)
    cumulative = 0
    for action,probability in probs:
        cumulative += probability
        if cumulative > chosen:
            return action

# segment class
class segmentData(object):
    def __init__(self):
        self.transitionProbs = {x+1:{action:{'obs':3,'down':1,'right':1,'dead':1 } for action in ACTIONS} for x in ncells }

users = {x: userData(x) for x in range(N)}
segments = {x:segmentData() for x in ['segment1', 'segment2']}
segment = segments['segment1']
# sessions by each user
for i in range(N):
    user = users[i]
    lmda = user.arrival_frequency
    number_of_arrivals = numpy.random.poisson(lmda)
    if not number_of_arrivals:
        continue
    time_of_arrivals = sorted(numpy.random.uniform(low = 0, high = nmonths * 30 * 24, size = number_of_arrivals))

    user.time_of_arrivals = time_of_arrivals
    firstTime = start = time_of_arrivals[0]

    user.sd['total'] += 1
    user.sd['month1'] += 1

    for t in time_of_arrivals:
        month = int(math.ceil((t - firstTime + 0.00001) / (30 * 24)))
        sd_key = 'month' + str(month)

        # dont show a video ad if the user returns in 24 hours
        if t == start or t - start >= 24:
            showVideo = True

        # decide the user's time budget for this session(a min to an hour)
        # number of vertical jumps in terms of states. Every state is a 10 second gap
        # max states = 1hour * 60 mins * 60secs / 10 = 360 states
        # time budget can be decided based on uniform distribution over 360 states
        time_budget = numpy.random.random_integers(360)
        friction = 0 # start afresh
        # session_depth starts at 1
        sd = 1
        survey_count = 0
        old_survey_sd = 0
        state = 1
        for the_state in range(time_budget):

            action = []
            Pright = numpy.random.beta(2,2) # click on recommendation

            # display ad
            friction += friction_disp
            action.append('nothing')

            #video ad
            if showVideo:
                if sd == 1:
                    if numpy.random.uniform() > showVideo_threshold:
                        friction += friction_videoAd
                        showVideo == False
                        action.append('video')
                if sd == 2:
                    friction += friction_videoAd
                    showVideo = False
                    action.append('video')

            #survey
            if old_survey_sd != sd and survey_count <= MAX_SURVEY_COUNT:
                if numpy.random.uniform() < showSurvey_probability:
                    old_survey_sd = sd
                    survey_count += 1
                    friction += friction_surveys
                    action.append('survey')

            # soft paywall
            if TIME_GAP*(the_state+1) > softPaywall_TIME_THRESHOLD:
                if numpy.random.uniform() < showSoft_probability:
                    friction += friction_soft
                    action.append('soft_paywall')


            Pdead = numpy.random.beta(1,friction)

            Pdown = 1 - Pdead - Pright

            reaction = selectRandom([('right', Pright), ('down', Pdown), ('dead', Pdead)])

            if reaction == 'dead':
                recordTransition(segment, state, action, reaction)
                state = deadState
                break
            elif reaction == 'right':
                recordTransition(segment, state, action, reaction)
                user.sd['total'] += 1
                user.sd[sd_key] += 1
                sd += 1
                state += nrows
            else:
                recordTransition(segment, state, action, reaction)
                state += 1


        start = t


def getAverageSD(users):
    total = 0
    for u in users.values():
        total += u.sd['total']
    return total / (3.0 * len(users.keys()))
