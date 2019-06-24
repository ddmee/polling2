import mock

class Stop(StopIteration):
    def __init__(self, state=None):
        self.state = state

class SuccessStop(Stop):
    pass

class TimeoutError(Stop):
    pass

class MaxCountStop(Stop):
    pass

event_4 = mock.Mock(side_effect=[3,3,4])
# Write a poll func that calls x() 5 times unless it first returns 4

def poll(**state):
    if state['count'] > 5:
        raise MaxCountStop(state=state)
    else:
        # call the x function again
        state['rv'] = state['x']()
        if state['rv'] == 4:
            raise SuccessStop(state=state)
        else:
            state['count'] += 1
            return poll(**state)


def counter(state):
    if state['count'] > 5:
        raise MaxCountStop(state=state)
    else:
        # Call to next thing.
        state['count'] += 1
        return state


def check_x(state):
    # call the x function again
    state['rv'] = state['x']()
    if state['rv'] == 4:
        raise SuccessStop(state=state)
    else:
        return state

# Catching the rv value and stuff like that

try:
    poll(count=0, x=event_4)
except SuccessStop as exc_info:
    result = exc_info.state['rv']
print "Primiviate poll function returned: ", result


event_4 = mock.Mock(side_effect=[3,3,4])
state = {'count':0, 'x':event_4}
while True:
    try:
        state = counter(check_x(state=state))
    except SuccessStop as exc_info:
        result = exc_info.state['rv']
        break
print "Primitive polling chain returned: ", result
