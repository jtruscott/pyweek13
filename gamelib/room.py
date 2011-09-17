import event, state, screen, term, message
import ansiparse
import os

import logging
log = logging.getLogger('room')

class Tile:
    passable = True
    door = False
    warp = False
    is_pickup = False
    picked_up = False
    monster = False

    def __init__(self, fg, bg, char, prop=None):
        if char == '\xdb':
            #F4 in tundra
            #full block, used as walls
            self.passable = False

        if char == '\xCE':
            #F2 in Set 5 in tundra,
            #double crosspiece. indicates a door.
            self.door = True
        if char == '\xE8':
            #F5 in Set 5 in tundra
            #portally thing. indicates warp to next level.
            self.warp = True
        
        if char == '\xfa':
            #F10 in Set 6 in tundra
            #centered period, used as a health pickup
            self.is_pickup = True
            self.pickup_type = "health"
        if char == 'K':
            #K for Key!
            #Hidden if 'key' is not the room's property
            if prop != 'key':
                char = ' '
            else:
                self.is_pickup = True
                self.pickup_type = 'key'
        if char == 'E':
            #E for Enemy!
            #New: Color determines relative difficulty level
            #Others = Totally Random
            self.monster = True
            if fg == term.LIGHTGREEN:
                #Lightgreen = Super Easy (1 non-human part, two limbs)
                self.monster_properties = 'super_easy'
            elif fg == term.GREEN:
                #Green = Easy (2 non-human parts, two limbs)
                self.monster_properties = 'easy'
            elif fg == term.LIGHTRED:
                self.monster_properties = 'jesus_christ'
            else:
                self.monster_properties = 'random'



        self.fg = fg
        self.bg = bg
        self.char = char

    def clear(self):
        self.passable = True
        self.char = ' '
        self.picked_up = True


class Room:
    start_x = 1
    start_y = 1

    player_x = -1
    player_y = -1
    player_color = term.WHITE
    explore_messages = []
    def __init__(self, name, buf, prop=None):
        self.name = name
        self.buf = buf
        self.prop = prop

        self.height = len(buf.data)
        self.width = len(buf.data[0])
        self.parse_tiles() 
        

    def parse_tiles(self):
        self.tiles = []
        y = 0
        for data_row in self.buf.data:
            row = []
            x = 0
            for fg, bg, char in data_row:
                if char == '$':
                    char = ' '
                    self.start_x = x
                    self.start_y = y
                    self.player_color = fg
                row.append(Tile(fg, bg, char, self.prop))
                x += 1
            self.tiles.append(row)
            y += 1

    def try_move(self, x=0, y=0):
        px = self.player_x + x
        py = self.player_y + y
        if px < 0 or py < 0 or px >= self.width or py >= self.height:
            message.error("You cannot exit the map.", flip=True)
            return False
        
        tile = self.tiles[py][px]
        if tile.door:
            message.add("<YELLOW>You enter the next room.", flip=True)
            return ("changeroom", (x, y))

        elif tile.warp:
            message.add("<YELLOW>You descend into the darkness.", flip=True)
            return ("changelevel", (None,))

        elif tile.monster:
            message.add("<LIGHTRED>You attack the monster!", flip=True)
            state.mode = 'battle'
            event.fire('battle.start', tile.monster_properties)
            state.after_battle_tile = tile
            state.after_battle_pos = (px, py)
            raise state.StateChanged()

        elif tile.passable:
            if tile.is_pickup and not tile.picked_up:
                #they found a thing!
                if tile.pickup_type == "health":
                    message.add("<GREEN>You found a <LIGHTGREEN>Stone Of Health</>!", flip=True)
                    state.player.bonus_hp += 1
                tile.clear()

            self.move_player(px, py)
            return True
        else:
            message.error("Something is in the way.", flip=True)
        return False

    def move_player(self, px, py):
        #fixup the buffer
        log.debug("moving player to %r,%r", px, py)
        tile = self.tiles[self.player_y][self.player_x]
        data = self.buf.data[self.player_y][self.player_x]
        data[0] = tile.fg
        data[2] = tile.char

        self.player_x = px
        self.player_y = py
        
        data = self.buf.data[self.player_y][self.player_x]
        data[0] = self.player_color
        data[2] = term.Room.player
        self.buf.dirty = True

    def draw(self, viewport):
        self.buf.draw(
            xoff=viewport.x + 1,
            yoff=viewport.y + 1
        )


def create_room(name, prop):
    log.debug("Creating room: %r", name)
    filename = os.path.join('data','maps',name)
    f = open(filename)
    buf = ansiparse.read_to_buffer(f, width=state.config.viewport_width-2, max_height=state.config.viewport_height-2, crop=True)
    
    room = Room(name, buf, prop)
    room.move_player(room.start_x,room.start_y)
    #add some fluff
    if name == "beach.ans":
        room.explore_messages = [
        "<LIGHTBLUE>You are surrounded by water, with no other islands anywhere on the horizon.",
        "<YELLOW>There is a faded trail leading off to the east."
        ]
    if name == "ruins.ans":
        room.explore_messages = [
        "<YELLOW>The trail leads to a massive shrine of unknown origin.",
        "<WHITE>In the center of the shrine is a chasm with stairs leading down.",
        ]
    if name == "e-1.ans":
        room.explore_messages = [
        "<WHITE>The room sparkles with impossibly beautiful gems.",
        ]
    if name == "wse-1.ans":
        room.explore_messages = [
        "<LIGHTGREEN>This room is terrifyingly unnatural.",
        "<LIGHTMAGENTA>Your sanity begs you to leave quickly.",
        ]
    if name == 'w-1.ans':
        room.explore_messages = [
        "<LIGHTGREY>This appears to be the remains of an ancient prison",
        ]
    if name == 'nse-1.ans':
        room.explore_messages = [
        "<LIGHTGREY>Flooding has taken over much of this cavern.",
        ]
    #prop messages
    if prop == 'key':
        room.explore_messages.append(
        "<YELLOW>There is a key in this room!"
        )
    return room
