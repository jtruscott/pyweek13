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
    M.scroll_offset = 0
    M.text_height = M.message_zone.height - 2
    M.text_width = M.message_zone.width - 2

    zone_title = screen.Text(
                                "[ Messages ]",
                                fg=term.LIGHTBLUE,
    )
    zone_title.x = (M.message_zone.width - len(zone_title.message)) / 2
    M.message_zone.children.append(zone_title)

    add_message("This is an incredibly long line" + "abcdefg " * 12)

@event.on('battle.tick')
def tmp():
    add_message("oh my god!")

@event.on('battle.draw')
@event.on('explore.draw')
def draw_message_log():
    M.message_zone.dirty = True
    M.message_zone.draw()
    M.pointer.draw()

    message_slice = M.messages[M.scroll_offset:M.scroll_offset + M.text_height - 1]
    '''
    the -1 in that slice fixes an issue where text wasn't scrolling all the way down; there's an arguement to be made
    that this is not the place where the math error is occurring, but it's not an error in scroll_offset, because the top scroll area
    is fine. (Try it out - add a -1 to the first scroll_offset there. the text output shits itself.)
    So unless there's other issues with text_height that point to a math error there, this is where the fix goes.
    '''
    y = 1
    for i in range(len(message_slice)):
        msg = message_slice[i]
        if y + msg.height >= M.text_height:
            #gonna run offscreen
            break

        msg.x = 1 + M.message_zone.x
        msg.y = y
        msg.dirty = True
        msg.draw()

        y += msg.height

@event.on('scroll')
def scroll_message(rel=0, home=False, end=False):
    if state.mode not in ('battle', 'explore'):
        return
    if home:
        off = 0
    elif end:
        off = len(M.messages)
    else:
        off = M.scroll_offset

    M.scroll_offset = calc_offset(off + rel)
    log.debug("new scroll offset: %r", M.scroll_offset)

    M.pointer.y = min(1+M.text_height, max(1, int(float(M.scroll_offset) * (M.text_height) / (len(M.messages) or 1))))

    M.message_zone.dirty = M.pointer.dirty = True
    draw_message_log()
    event.fire('flip')

def calc_offset(off):
    off = max(0, off) #dont go negative
    off = min(off, len(M.messages)) #and always leave a message around
    return off


def add_message(message, flip=False):
    log.debug("adding message: %r", message)
    rt = screen.RichText(message, x=1, wrap_to=M.text_width)
    M.messages.append(rt)
    M.scroll_offset = calc_offset(len(M.messages) - M.text_height)
    if flip:
        draw_message_log()
        event.fire('flip')

add = add_message
def error(message, **kwargs):
    add_message("<RED>%s</>" % message, **kwargs)

def newline(**kwargs):
    add_message("", **kwargs)
