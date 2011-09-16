import random
from room import create_room

import logging
log = logging.getLogger('layouts')
class Layout:
    curr_x = None
    curr_y = None
    curr_room = None
    def __init__(self, map_data):
        self.rooms = []
        self.parse_map(map_data)


    def parse_map(self, map_data):
        #just figure out what's going on, don't instantiate
        map = []
        y = 0
        for row_data in map_data:
            row = []
            x = 0
            for desc in row_data:
                if desc is None:
                    row.append((None, None))
                    continue

                key,_,prop = desc.partition(',')
                if prop == 'start':
                    self.start_x = self.curr_x = x
                    self.start_y = self.curr_y = y
                filenames = groups[key]

                row.append((filenames, prop))
                x += 1
            map.append(row)
            y += 1

        self.map = map

    def setup(self):
        #actually load the layout's rooms
        y = 0
        for row in self.map:
            room_row = []
            x = 0
            for col in row:
                filenames, prop = col
                if filenames is None:
                    room = None
                else:
                    room = create_room(random.choice(filenames), prop=prop)
                room_row.append(room)
                x += 1
            self.rooms.append(room_row)
            y += 1

        self.curr_room = self.rooms[self.start_y][self.start_x]

    def change_room(self, x, y):
        log.debug("change_room: (%r, %r)", x, y)
        log.debug("curr: (%r, %r)", self.curr_x, self.curr_y)
        old_room = self.curr_room
        self.curr_x += x
        self.curr_y += y
        new_room = self.rooms[self.curr_y][self.curr_x]

        new_px = old_room.player_x
        new_py = old_room.player_y
        if x != 0:
            log.debug('flipping x: %r - %r', old_room.buf.width,old_room.player_x)
            new_px = old_room.buf.width - old_room.player_x
        else:
            log.debug('flipping y: %r - %r', old_room.buf.height,old_room.player_y)
            new_py = old_room.buf.height - old_room.player_y
        
        new_room.move_player(new_px, new_py)
        self.curr_room = new_room


groups = {
    #mapping of map "names" to one or more files in data/ which count
    
    #general tiles
    'e': None,
    'w': None,
    'n': None,

    'ws': None,
    
    'wse': None,
    'nse': None,

    #special tiles
    'beach': ['beach.ans'],
    'ruins': ['ruins.ans'],
}

start_layout = Layout([
    ['beach,start', 'ruins']
])

#random dungeon layouts
dungeon_layouts = [
    Layout([
        ['e,start',  'wse',  'w'],
        [None,       'nse',  'ws'],
        [None,       'n,boss','n,key'],
    ]),

    Layout([
    ]),
]


def random_layout():
    layout = random.choice(dungeon_layouts)
    layout.setup()
    return layout
