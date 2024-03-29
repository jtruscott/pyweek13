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
            log.debug('moving x: old=%r',old_room.player_x)
            if old_room.player_x < old_room.width/2:
                #they were on the left, put them on the right
                #note that we use -3 because there's a weirdness in map width
                new_px = new_room.width - 3
            else:
                new_px = 2
        else:
            log.debug('moving y: old=%r',old_room.player_y)
            if old_room.player_y < old_room.height/2:
                #they were on the top, put them on the bottom
                new_py = new_room.height - 2
            else:
                new_py = 2
        
        new_room.move_player(new_px, new_py)
        self.curr_room = new_room


groups = {
    #mapping of map "names" to one or more files in data/ which count
    
    #general tiles
    'e': ['e-1.ans'],
    'w': ['w-1.ans'],
    'n': ['n-1.ans'],

    'ws': None,
    'ns': ['ns-1.ans'],
    
    'wse': ['wse-1.ans'],
    'nse': ['nse-1.ans'],

    #special tiles
    'beach': ['beach.ans'],
    'ruins': ['ruins.ans'],
    'victory': ['victory.ans']
}

def start_layout():
    return Layout([
        ['beach,start', 'ruins']
    ])

#random dungeon layouts
dungeon_layouts = [
    Layout([
        ['e,start',  'wse',  'w,key'],
        [None,       'ns',  None],
        [None,       'n,boss',None],
    ]),

    Layout([['victory,start']]),
]


def random_layout():
    layout = dungeon_layouts.pop(0)
    layout.setup()
    return layout
