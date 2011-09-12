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

    zone_title = screen.Text(
                                "[ Messages ]",
                                fg=term.LIGHTBLUE,
    )
    zone_title.x = (M.message_zone.width - len(zone_title.message)) / 2
    M.message_zone.children.append(zone_title)

@event.on('battle.tick')
def tmp():
    add_message("oh my god!")

@event.on('battle.draw')
@event.on('explore.draw')
def draw_message_log():
    M.message_zone.draw()
    M.pointer.draw()

    message_slice = M.messages[M.scroll_offset:M.scroll_offset + M.text_height]
    for i in range(len(message_slice)):
        msg = message_slice[i]
        msg.x = 1 + M.message_zone.x
        msg.y = 1 + i
        msg.dirty = True
        msg.draw()

@event.on('scroll')
def scroll_message(rel=0, home=False, end=False):
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

def calc_offset(off):
    off = max(0, off) #dont go negative
    off = min(off, len(M.messages)) #and always leave a message around
    return off


def add_message(message):
    log.debug("adding message: %r", message)
    rt = screen.RichText(message)
    M.messages.append(rt)
