non_subscriber_parameters = {
    'showVideo_threshold': 0.6,
    'MAX_SURVEY_COUNT': 2
    'showSurvey_probability': 0.5,
    'softPaywall_TIME_THRESHOLD': 50,
    'showSoft_probability':0.7,
    'SD_HARD_PAYWALL': 10,
        'friction': {
            "display":0.01,# per time_gap. it keeps on accumulating
            "videoAd": 0.1, # once in 24 hours and only in sd =1 or 2
            "soft_paywall": 0.15,# after 5 (50 second) states show with 70% probability
            "surveys":0.05, # show it max twice but with 50 % chance
            "hard_paywall":1.0
        }
}

subscriber_parameters = {
    'showVideo_threshold': 0,
    'MAX_SURVEY_COUNT': 2
    'showSurvey_probability': 0.4,
    'softPaywall_TIME_THRESHOLD': 10000,
    'showSoft_probability':0,
    'SD_HARD_PAYWALL': 100000,
    'friction': {
        "display":0.01,# per time_gap. it keeps on accumulating
    }
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

#user class
class User(object):

    def __init__(self, number, arrival_frequency, nmonths):
        self.id = number
        for i in range(nmonths):
            self.sd['month'+str(i+1)] = 0

        # mean of gamma is 10 visits in 3 month
        self.arrival_frequency = arrival_frequency
        number_of_arrivals = numpy.random.poisson(arrival_frequency)
        self.time_of_arrivals = sorted(numpy.random.uniform(low = 0, high = nmonths * 30 * 24, size = number_of_arrivals))

        self.firstTime = self.time_of_arrivals[0]
        self.showVideo = True
        self.showSurvey = True
        self.showSoftPaywall = True
        self.showHardPaywall = True


    def setSegment(self, segment):
        self.segment = segment
        if segment.name == 'subscriber':
            self.showSurvey = False
            self.showSoftPaywall = False
            self.showHardPaywall = False

    def simulateSession(self, time_budget, arrival_time):
        currentMonth = 'month' + str(arrival_time // (30*24)  + 1)
        friction, sd = 0, 1
        survey_count, old_survey_sd = 0, 0
        state = 1
        segment = user.segment

        for time_bucket in range(time_budget):
            action = []

            Pright = self.recommendationClick()

            friction += segment.friction_disp
            action.append('recommendation')


            if self.showVideo and 'video' in segment.ACTIONS:
                if sd == 1:
                    if numpy.random.uniform() > segment.showVideo_threshold:
                        friction += segment.friction['video']
                        action.append('video')
                if sd == 2:
                    friction += segment.videoAd

            # show survey
            if self.showSurvey and 'survey' in segment.ACTIONS:
                if self.surveyCount <= segment.MAX_SURVEY_COUNT and numpy.random.uniform() < segment.showSurvey_probability:
                    friction += segment.friction['surveys']
                    self.surveyCount += 1
                    action.append('survey')

            # show a soft paywall
            if self.showSoftPaywall and 'soft_paywall' in segment.ACTIONS:
                if self.sd[currentMonth] > segment.action_params['softSD']:
                    friction += segment.friction['soft_paywall']
                    action.append('soft_paywall')

            # show a hard paywall
            if self.showHardPaywall and 'hard_paywall' in segment.ACTIONS:
                if self.sd[currentMonth] > segment.SD_HARD_PAYWALL:
                    friction += segment.friction['hard_paywall']
                    action.append('hard_paywall')








    def recommendationClick(self):
        return numpy.random.beta(2,2)




# segment class
class Segment(object):
    def __init__(self, ncells, ACTIONS, **params, name):
        self.transitionProbs = {x+1:{action:{'obs':3,'down':1,'right':1,'dead':1 } for action in ACTIONS} for x in ncells }
        self.ACTIONS = ACTIONS
        self.action_params = params
        self.friction = friction_params
        self.defineActionConstraints(params)
        self.name = name

    def recordTransition(self, state, actions, reaction):
        for action in actions:
            self.transitionProbs[state][action]['obs'] += 1
            self.transitionProbs[state][action][reaction] += 1

    def defineActionConstraints(self, kwargs):
    #showVideo_threshold, MAX_SURVEY_COUNT, showSurvey_probability, softPaywall_TIME_THRESHOLD, showSoft_probability, SD_HARD_PAYWALL ):
        # video
        self.showVideo_threshold = kwargs['showVideo_threshold'] # show video in first session with this probability

        #survey
        self.MAX_SURVEY_COUNT = kwargs['MAX_SURVEY_COUNT']
        self.showSurvey_probability = kwargs['showSurvey_probability']

        # soft paywall
        self.softPaywall_TIME_THRESHOLD = kwargs['softPaywall_TIME_THRESHOLD'] # amount of time spent after which soft paywall will start appearing
        self.showSoft_probability = kwargs['showSoft_probability']

        # hard paywall
        self.SD_HARD_PAYWALL = kwargs['SD_HARD_PAYWALL'] # only if hard paywall is on

    def defineFrictionFactors(self):
        self.friction_disp = 0.01 # per time_gap. it keeps on accumulating
        self.friction_videoAd = 0.1 # once in 24 hours and only in sd =1 or 2
        self.friction_surveys = 0.05 # show it max twice but with 50 % chance
        self.friction_soft = 0.15 # after 5 (50 second) states show with 70% probability
        self.friction_hard = 1


class Publisher(object):
    def __init__(self, nrows, ncols, nmonths, N):
        self.nmonths = nmonths # traffic to be simulated for 3 months
        self.N = N # number of users to be simulated
        self.TIME_GAP = 10 # binning of atsop

        self.nrows = nrows
        self.ncols = ncols
        self.deadState = -1000
        self.ncells = range(self.nrows * self.ncols) + [deadState]

        # mean of gamma is 10 visits in 3 months
        self.gamma_shape = 10
        self.gamma_scale = 2

        self.users = {}
        self.segments = {}

        # define factors
        self.defineFrictionFactors()
        self.defineSegments()
        self.defineUsers()

    def defineSegments(self):
        self.segments = {
            "non-subscriber" : Segment( self.ncells,['recommendation', 'video', 'survey', 'soft_paywall', 'hard_paywall'], **non_subscriper_parameters, 'non-subscriber'),
            'subscriber' : Segment(self.ncells ,['recommendation', 'survey'], **subscriber_parameters, 'subscriber')
        }

    def defineUsers(self):
        arrival_frequency = numpy.random.gamma(self.gamma_shape, self.gamma_scale)
        for i in range(self.N):
            self.users[i] = User(i, arrival_frequency, self.nmonths)
            self.users[i].setSegment(self.segments['non-subscriber'])


def onlineBehavior(object):

    def __init__(self):
        self.Publisher = Publisher(nrows = 10, ncols = 10, nmonths = 3, N = 10000)


    def simulateUser(self):
        for i,user in self.Publisher.users.iteritems():

            start = user.firstTime
            user.showVideo =  True
            for arrival_time in user.time_of_arrivals:
                # dont show a video ad if the user returns in 24 hours
                if arrival_time - start >= 24 and user.showVideo = False:
                    user.showVideo = True

                time_budget = numpy.random.random_integers(self.nrows) # *TIME_GAP number of seconds

                user.simulateSession(time_budget, arrival_time)
                start = arrival_time






def g(**kwargs):
    print kwargs
