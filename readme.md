# Open-source Tetris Game 
## Key Features 
- Can Increase Speed
- Supports scoreboard 
- Play background music on your own
- Network play-can play with your friends!

## Install
### Client
#### Prequisites
1. Necessary
    - Python3 (Tested on 3.5)
    - Cython
2. Optional (Background Music)
    - [SDL2](https://www.libsdl.org/download-2.0.php)
    - [Ogg Vorbis](http://www.vorbis.com)
    - [SDL Mixer](https://www.libsdl.org/projects/SDL_mixer/)
#### Main installation
1. Clone repository

    `git clone https://github.com/thy2134/OSDTetris.git && cd OSDTetris`
2. Install dependencies with 

    `pip install pygame tinydb requests` (Windows / Linux)

    `pip3 install pygame tinydb requests` (macOS)
3. Start python script

    `python tetris.py` (Windows / Linux)
    `python3 tetris.py` (macOS)

#### Play Background Music
1. Install sdl2 library
2. Install oggvorbis library
3. Install sdl_mixer library
4. Put your music file(ogg format) inside the `files` folder, rename it to `bg_music.ogg`, and start game!

## Keys
- Left/Right: Move block left/right
- Down: Drop block 
- Up: Rotate block
- P: Pause game
- S: Speed up
- H: Hold block
- M: Start/Stop BGM
- D: **COMMIT SUICIDE**
- Return/Enter: Drop block instantly

## Online Scoreboard
You can connect to server and compete with your friends.

To connect to server, insert the address of server to the end of the execution command, like

`python3 tetris.py foobar.com`
.

When you're connected online, you can publish your score onto the server with your name!

Note that, your plays while connected online will not be saved offline.

