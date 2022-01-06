from ideas import AnimationController
import pygame
import os
from pygame.locals import *
from material import engine
pygame.init()
pygame.mixer.init()


#   others, ordenado alfabeticamente
ASSETS_PATH                             =   "material"

WINDOW_SIZE                             =   [1000, 700]
WINDOW                                  =   pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)

WAKE_SIZE                               =   [40,20]
WAKE_ANIMATIONS                         =   engine.loadWakeAnimations( ASSETS_PATH + "/estela", WAKE_SIZE)
WAKE_LIST                               =   []



SPEED                                   =   5
SOUNDS_PATH                             =   ASSETS_PATH + "/efects/"
STEPS_SOUND                             =   pygame.mixer.Sound(ASSETS_PATH + "/efects/steps/steps.wav")
SCROLL                                  =   [0,0]
SCROLL_SMOOTH                           =   20



JUMP_SOUND                              =   pygame.mixer.Sound(ASSETS_PATH + "/efects/jump/jump.wav")
JUMP_FORCE                              =   -8


PIV_SURFACE_SIZE                        =   [800, 400]
PLAYER_ANIMATIONS_FRAMES_PER_IMAGE      =   7
PIV_SURFACE                             =   pygame.Surface(PIV_SURFACE_SIZE)
PLAYER_SIZE                             =   [80,90]
PLAYER_ANIMATION_FPS                    =   4
PLAYER                                  =   engine.Player( 
    steps_sound         = STEPS_SOUND, 
    player_speed        = SPEED,
    jump_sound          = JUMP_SOUND, 
    animation_manager   = AnimationController(engine.animationDict(PLAYER_SIZE, None, "material/animations/", True),PLAYER_ANIMATION_FPS, "stand_1",False ), 
    size                = PLAYER_SIZE,
    cadencia_de_arma    = 5,
    no_amoo_sound_path  = "material/efects/shots/no amoo.wav",
    alcance             = 100,
    attack_sound_path   = "material/efects/shots/shot.wav")


BACKGROUND_COLOR                        =   ( 0, 100, 150)
BACKGROUND_MUSIC                        =   pygame.mixer.music.load(SOUNDS_PATH + "background.wav")
BULLETS_SIZE                            =   [20, 3]
BULLET_SPRITE                           =   engine.getImageReady("material/armas/bullet.png", BULLETS_SIZE, None, True)
BULLETS_LIST                            =   []
BULLETS_SPEED                           =  20
CELL_LIST                               =   []
CLOCK                                   =   pygame.time.Clock()

BULLETS_EXPLOSIONS                      =   []
BULLETS_EXPLOSION_ANIMATION_SIZE        =    [20,20]
BULLETS_ANIMATION_FPS                   =   3
BULLETS_EXPLOSION_ANIMATION             =   engine.loadExplosionAnimation(ASSETS_PATH + "/explosion/animations/", BULLETS_EXPLOSION_ANIMATION_SIZE)
EXIT                                    =   False

GAME_MAP                                =   engine.loadMap( ASSETS_PATH + "/map.txt")
GRAVITY                                 =   1

MAX_GRAVITY                             =   10


TILE_SIZE                               =   [32, 32]

JUMP_SOUND.set_volume(0.4)
STEPS_SOUND.set_volume(0.3)
pygame.mixer.music.set_volume(0.03)
pygame.mixer.music.play(-1)
pygame.mouse.set_visible(False)

TILES               = {}

for i in range(1,10):
    path_name = ASSETS_PATH + f"/tiles/tiles/{i}.png"
    print(path_name)
    TILES[i] = engine.getImageReady(path_name, TILE_SIZE, None, False)



while not EXIT:
    PIV_SURFACE.fill(BACKGROUND_COLOR)

    #   ````````        update
    PLAYER.updateShotsInfo(SCROLL, BULLETS_LIST, BULLET_SPRITE, BULLETS_SPEED, BULLETS_SIZE)
    engine.updateBullets(BULLETS_LIST, CELL_LIST, PIV_SURFACE_SIZE, BULLETS_EXPLOSIONS, SCROLL)
    engine.updateBulletExplosionAnimation(BULLETS_EXPLOSIONS, len(BULLETS_EXPLOSION_ANIMATION), BULLETS_ANIMATION_FPS)
    engine.updateWakes(WAKE_LIST, SCROLL)
    PLAYER.updateState(GRAVITY, MAX_GRAVITY, CELL_LIST)
    engine.updateScroll(SCROLL,  PLAYER, PIV_SURFACE_SIZE, SCROLL_SMOOTH)

    #   ````````        render
    engine.renderBullets(BULLETS_LIST, PIV_SURFACE)
    engine.renderWakes(WAKE_LIST, PIV_SURFACE, SCROLL)
    engine.printMap(TILE_SIZE, CELL_LIST, TILES, PIV_SURFACE, GAME_MAP, SCROLL)
    PLAYER.render(PIV_SURFACE, SCROLL)
    engine.renderBulletExplosionAnimation(BULLETS_EXPLOSIONS, PIV_SURFACE, BULLETS_EXPLOSION_ANIMATION, SCROLL)
    WINDOW.blit(pygame.transform.scale(PIV_SURFACE, [WINDOW.get_width(), WINDOW.get_height()]), (0,0))
    #   ````````        event handling
    # recordar que tenemos que retornar tanto EXIT como LAST_MOUSE_POS por que al sustituir su valor, se crea una variable nueva, por lo tanto la referencia no es la misma
    EXIT = engine.eventHandling(pygame.event.get(), PLAYER,EXIT, JUMP_FORCE, WAKE_LIST, WAKE_ANIMATIONS, WAKE_SIZE)
    CLOCK.tick(60)
    pygame.display.update()

pygame.quit()
