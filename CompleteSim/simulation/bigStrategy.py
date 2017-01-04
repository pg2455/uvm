import numpy

# segment class
class segmentData(object):
    def __init__(self, ncells, ACTIONS):
        self.transitionProbs = {x+1:{action:{'obs':3,'down':1,'right':1,'dead':1 } for action in ACTIONS} for x in ncells }
        self.ACTIONS = ACTIONS

    def recordTransition(self, state, actions, reaction):
        for action in actions:
            self.transitionProbs[state][action]['obs'] += 1
            self.transitionProbs[state][action][reaction] += 1

    def defineActionConstraints(self, **kwargs):
    #showVideo_threshold, MAX_SURVEY_COUNT, showSurvey_probability, softPaywall_TIME_THRESHOLD, showSoft_probability, SD_HARD_PAYWALL ):
        # video
        self.showVideo_threshold = 0.6 # show video in first session with this probability

        #survey
        self.MAX_SURVEY_COUNT = 2
        self.showSurvey_probability = 0.5

        # soft paywall
        self.softPaywall_TIME_THRESHOLD = 50 # amount of time spent after which soft paywall will start appearing
        self.showSoft_probability = 0.7

        # hard paywall
        self.SD_HARD_PAYWALL = 10 # only if hard paywall is on



# user class
class userData(object):

    def __init__(self, number, arrival_frquency, nmonths):
        self.id = number
        self.sd = {'total':0}
        for i in range(nmonths):
            self.sd['month'+str(i+1)] = 0

        # mean of gamma is 10 visits in 3 month
        self.arrival_frequency = arrival_frequency
        number_of_arrivals = numpy.random.poisson(arrival_frequency)
        self.time_of_arrivals = sorted(numpy.random.uniform(low = 0, high = nmonths * 30 * 24, size = number_of_arrivals))

        self.firstTime = self.time_of_arrivals[0]
        self.segment = 'non-subscriber'

    def changeSegment(self):
        self.segment = 'subscriber'

# simulation
class onlineBehavior(object):

    def __init__(self,segments = None):
        self.nmonths = 3 # traffic to be simulated for 3 months
        self.N = 10000 # number of users to be simulated
        self.TIME_GAP = 10 # binning of atsop

        self.nrows = 180
        self.ncols = 40
        self.deadState = -1000
        self.ncells = range(self.nrows * self.ncols) + [deadState]

        # mean of gamma is 10 visits in 3 month
        self.gamma_scale = 10
        self.gamma_shape = 2

        self.users = {}
        self.segments = {}

        # define factors
        self.defineFrictionFactors()
        self.defineUsers(10,2)
        if segments:
            self.defineSegments(segments)

    def defineFrictionFactors(self):
        self.friction_disp = 0.01 # per time_gap. it keeps on accumulating
        self.videoAd = 0.1 # once in 24 hours and only in sd =1 or 2
        self.surveys = 0.05 # show it max twice but with 50 % chance
        self.friction_soft = 0.15 # after 5 (50 second) states show with 70% probability

    def defineUsers(self, gamma_scale, gamma_shape):
        arrival_frequency = numpy.random.gamma(self.gamm_shape, self.gamma_scale)
        for i in range(self.N):
            self.users[i] = userData(i, arrival_frequency, startingSegment, self.nmonths)

    def defineSegments(self,segments):
        for (segment, (actions, params)) in segments.iteritems():
            self.segments[segment] = segmentData(self.ncells, actions)
            self.segments[segment].defineActionConstraints(params)

    def simulateUser(self, user_id):
        user = self.users[user_id]
        segment = self.segments[user.segment]

        start = user.time_of_arrivals[0]

        for t in user.time_of_arrivals:
            # dont show a video ad if the user returns in 24 hours
            if t == start or t - start >= 24:
                showVideo = True


            time_budget = numpy.random.random_integers(self.nrows) # *TIME_GAP number of seconds
            self.simulateSession(time_budget, user, segment,showVideo)

            start = t

    def simulateSession(self, time_budget, user, segment, showVideo):
        friction, sd = 0, 1
        survey_count, old_survey_sd = 0, 0
        state = 1

        for time_bucket in range(time_budget):
            action = []
            Pright = self.recommendationClick()
            friction += self.friction_disp
            action.append('nothing')
            if showVideo:
                friction += self.getVideoFriction(sd)
                action.append('video')
            if segment == 'non-subscriber':
                pass




    def getVideoFriction(self, sd):
        if sd == 1:
            if numpy.random.uniform() > showVideo_threshold:
                showVideo == False
                action.append('video')
        if sd == 2:
            friction += friction_videoAd
            showVideo = False
            action.append('video')


    def recommendationClick(self):
        return numpy.random.beta(2,2)





class simulate(object):

    def __init__(self, segments):
        self.onlineEnvironment = onlineBehavior()
        self.

non_subscriber_parameters = {
    'showVideo_threshold': 0.6,
    'MAX_SURVEY_COUNT': 2
    'showSurvey_probability': 0.5,
    'softPaywall_TIME_THRESHOLD': 50,
    'showSoft_probability':0.7,
    'SD_HARD_PAYWALL': 10
}

subscriber_parameters = {
    'showVideo_threshold': 0,
    'MAX_SURVEY_COUNT': 2
    'showSurvey_probability': 0.4,
    'softPaywall_TIME_THRESHOLD': 10000,
    'showSoft_probability':0,
    'SD_HARD_PAYWALL': 100000
}

segments = {
    "non-subscriber" : (['nothing', 'video', 'survey', 'soft_paywall', 'hard_paywall'], non_subscriper_parameters),
    'subscriber' : (['nothing', 'survey'], subscriber_parameters)
}

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
