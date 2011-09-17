import screen, event, state, term

import logging
log = logging.getLogger('message')

class M:
    message_zone = None
    pointer = None

    messages = []
    scroll_offset = 0

@event.on('setup')
def setup_message_ui():

    conf = state.config
    M.message_zone = screen.make_box(conf.width - conf.viewport_width, conf.viewport_height,
                                border_fg=term.BLUE,
                                boxtype=term.BoxMessage,
                                draw_left=False,
    )
    M.pointer = screen.Buffer(1,1,
                                x=M.message_zone.width-1, y=1,
                                data=[[[term.LIGHTBLUE, term.BLACK, term.BoxMessage.cur]]]
    )
    M.messages = []
    
    #the math is actually easier in reverse...
    M.last_message_idx = 0
    
    M.text_height = M.message_zone.height - 2
    M.text_width = M.message_zone.width - 2

    zone_title = screen.Text(
                                "[ Messages ]",
                                fg=term.LIGHTBLUE,
    )
    zone_title.x = (M.message_zone.width - len(zone_title.message)) / 2
    M.message_zone.children.append(zone_title)

@event.on('battle.draw')
@event.on('explore.draw')
@event.on('defeat.draw')
def draw_message_log():
    M.message_zone.dirty = True
    M.message_zone.draw()
    M.pointer.draw()

    #log.debug("last idx: %r len: %r", M.last_message_idx, len(M.messages))
    slice_start = M.last_message_idx
    slice_y = M.text_height
    #count backwards from the current
    for i in range(M.last_message_idx, 0, -1):
        slice_y -= M.messages[i].height
        if slice_y <= 1:
            #that's it, we found the top
            break
        #log.debug("slice_y %r slice_start %r", slice_y, slice_start)
        slice_start -= 1

    y = 1
    log.debug('message log slice: %r to %r', slice_start,M.last_message_idx)
    for i in range(slice_start,M.last_message_idx+1): #+1 because range is exclusive
        msg = M.messages[i]
        #log.debug("i: %r y: %r msg: %r", i, y, msg.message)
        msg.x = 1 + M.message_zone.x
        msg.y = y
        msg.dirty = True
        msg.draw()

        y += msg.height

@event.on('scroll')
def scroll_message(rel=0, home=False, end=False):
    if state.mode not in ('battle', 'explore', 'defeat'):
        return
    if home:
        off = 0
    elif end:
        off = len(M.messages)
    else:
        off = M.last_message_idx

    M.last_message_idx = calc_offset(off + rel)
    log.debug("new scroll offset: %r", M.last_message_idx)

    M.pointer.y = min(1+M.text_height, max(1, int(float(M.last_message_idx) * (M.text_height) / (len(M.messages) or 1))))

    M.message_zone.dirty = M.pointer.dirty = True
    draw_message_log()
    event.fire('flip')

def calc_offset(off):
    off = max(0, off) #dont go negative
    off = min(off, len(M.messages)-1) #and always leave a message around
    return off


def add_message(message, flip=False):
    log.debug("adding message: %r", message)
    rt = screen.RichText(message, x=0, wrap_to=M.text_width)
    M.messages.append(rt)
    M.last_message_idx = calc_offset(len(M.messages))
    if flip:
        draw_message_log()
        event.fire('flip')

add = add_message
def error(message, **kwargs):
    add_message("<RED>%s</>" % message, **kwargs)

def newline(**kwargs):
    add_message("", **kwargs)
