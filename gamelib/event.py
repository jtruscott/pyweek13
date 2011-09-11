import logging
log = logging.getLogger('event')

listeners = {}
def on(event):
    def wrapper(fn):
        log.debug("registered %s.%s on '%s'", fn.__module__, fn.__name__, event)
        listeners.setdefault(event, [])
        listeners[event].append(fn)
        return fn
    return wrapper

def fire(event, *args, **kwargs):
    if event not in listeners:
        log.warn("firing '%s', which has no listeners!", event)
        return
    log.debug("firing '%s'", event)    
    for f in listeners[event]:
        f(*args, **kwargs)
