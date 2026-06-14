from pushbullet import Pushbullet
API_KEY = 'o.LHnHc0sjJmU2qIlznldn3vMdwsLyKR4O'

pb = Pushbullet(API_KEY)

def notify(title, body, logger):
    print('calling notify')
    logger.info('sending notification to pushbullet')
    push = pb.push_note(title, body)
    return push