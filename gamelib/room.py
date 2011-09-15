import event, state, screen, term, message
import ansiparse
import os

import logging
log = logging.getLogger('room')

class Tile:
    passable = True
    door = False
    def __init__(self, fg, bg, char):
        if char == '\xdb':
            #F4 in tundra
            #full block, used as walls
            self.passable = False
        if char == '\xb2':
            #F3 in tundra
            #sparkly block, usually used with reverse color
            self.door = True
        self.fg = fg
        self.bg = bg
        self.char = char

class Room:
    def __init__(self, player_x, player_y, name, buf):
        self.player_x = player_x
        self.player_y = player_y
        self.name = name
        self.buf = buf

        self.height = len(buf.data)
        self.width = len(buf.data[0])
        self.parse_tiles()
        self.move_player(player_x,player_y)

    def parse_tiles(self):
        self.tiles = []
        for data_row in self.buf.data:
            row = []
            for fg, bg, char in data_row:
                row.append(Tile(fg, bg, char))
            self.tiles.append(row)

    def try_move(self, x=0, y=0):
        px = self.player_x + x
        py = self.player_y + y
        if px < 0 or py < 0 or px >= self.width or py >= self.height:
            message.error("nope.jpg", flip=True)
            return False
        
        tile = self.tiles[py][px]
        if tile.door:
            message.add("<YELLOW>That's a door!", flip=True)
        elif tile.char == 'F':
            message.add("<LIGHTRED>HOLY TOLEDO! ITS A MONSTER!", flip=True)
            state.mode = 'battle'
            event.fire('battle.start')
            raise state.StateChanged()

        elif tile.passable:
            self.move_player(px, py)
            return True
        else:
            message.error("impassible", flip=True)
        return False

    def move_player(self, px, py):
        #fixup the buffer
        log.debug("moving player to %r,%r", px, py)
        tile = self.tiles[self.player_y][self.player_x]
        data = self.buf.data[self.player_y][self.player_x]
        data[0] = tile.fg
        data[1] = tile.bg
        data[2] = tile.char

        self.player_x = px
        self.player_y = py
        
        data = self.buf.data[self.player_y][self.player_x]
        data[0] = term.LIGHTGREEN
        data[1] = term.BLACK
        data[2] = term.Room.player
        self.buf.dirty = True

    def draw(self, viewport):
        self.buf.draw(
            xoff=viewport.x + 1,
            yoff=viewport.y + 1
        )


def create_room(name):
    log.debug("Creating room: %r", name)
    filename = os.path.join('data','maps',name)
    f = open(filename)
    buf = ansiparse.read_to_buffer(f, width=state.config.viewport_width-2, max_height=state.config.viewport_height-2)
    return Room(10, 10, name, buf)
