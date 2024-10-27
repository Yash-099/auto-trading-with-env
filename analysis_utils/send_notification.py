from pushbullet import Pushbullet
API_KEY = 'o.LHnHc0sjJmU2qIlznldn3vMdwsLyKR4O'

pb = Pushbullet(API_KEY)

def notify(title, body):
    print('sending notification to pushbullet')
    push = pb.push_note(title, body)
    return push