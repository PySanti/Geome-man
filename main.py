from ideas import AnimationController
import pygame
from pygame.locals import *
from material import engine
pygame.init()
pygame.mixer.init()


#   others, ordenado alfabeticamente
ASSETS_PATH                             =   "material"
SPACE_CHAR                              =   "_"

WINDOW_SIZE                             =   [1000, 700]
WINDOW                                  =   pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)


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
PLAYER_SIZE                             =   [80,70]
PLAYER_ANIMATION_FPS                    =   4
PLAYER                                  =   engine.Player( 
    steps_sound             = STEPS_SOUND, 
    player_speed            = SPEED,
    jump_sound              = JUMP_SOUND, 
    animation_manager       = AnimationController(engine.animationDict(PLAYER_SIZE, None, "material/animations/", True),PLAYER_ANIMATION_FPS, "stand_1",False ), 
    size                    = PLAYER_SIZE,
    cadencia_de_arma        = 10,
    attack_sound_path  = "material/efects/shots/cero.wav")
PARTICLES_PER_SHOT      =   3

BACKGROUND_COLOR                        =   ( 100, 100, 100)
BACKGROUND_MUSIC                        =   pygame.mixer.music.load(ASSETS_PATH + "/efects/background/background.wav")
BULLETS_SIZE                            =   [20, 3]
BULLET_SPRITE                           =   engine.getImageReady("material/armas/bullet.png", BULLETS_SIZE, None, True)
BULLETS_LIST                            =   []
BULLETS_SPEED                           =  30
CELL_LIST                               =   []
CLOCK                                   =   pygame.time.Clock()

EXIT                                    =   False
CELL_COLOR_CHANGE                       =   50

GAME_MAP                                =   engine.loadMap( ASSETS_PATH + "/map.txt")
GRAVITY                                 =   1

MAX_GRAVITY                             =   10


TILE_SIZE                               =   [30, 20]

JUMP_SOUND.set_volume(0.1)
STEPS_SOUND.set_volume(0.1)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
pygame.mouse.set_visible(False)





#   recordar que la lista de rectangulos de fondo contiene "microlistas" de la forma
#           proporcion de scroll, color, rect
BACKGROUND_RECTS, MIDDLE_RECT_DECORATION        =   engine.generateBackgroundRects(
    levels=3,
    columnas=12,
    capas= 7, 
    initial_pos=[0,0], 
    space_diff= 30,
    rect_size=[100,150], 
    rect_color={1: 100, 2:100,3:100})
PARTICLES                                       =   []





while not EXIT:
    PIV_SURFACE.fill(BACKGROUND_COLOR)

    #   ````````        update
    PLAYER.updateShotsInfo(SCROLL, BULLETS_LIST, BULLETS_SPEED, BULLETS_SIZE, PARTICLES, PARTICLES_PER_SHOT)
    engine.updateBullets(BULLETS_LIST, CELL_LIST, PIV_SURFACE_SIZE, SCROLL, PARTICLES)
    PLAYER.updateState(GRAVITY, MAX_GRAVITY, CELL_LIST)
    engine.updateScroll(SCROLL,  PLAYER, PIV_SURFACE_SIZE, SCROLL_SMOOTH)
    engine.updateParticles(PARTICLES, CELL_LIST)

    #   ````````        render
    engine.renderBackgroundRects(PLAYER.rect, MIDDLE_RECT_DECORATION, BACKGROUND_RECTS, PIV_SURFACE, SCROLL)
    PLAYER.render(PIV_SURFACE, SCROLL)
    engine.printMap(TILE_SIZE, CELL_LIST, CELL_COLOR_CHANGE, PIV_SURFACE, GAME_MAP, SCROLL, SPACE_CHAR, [PLAYER.rect.x, PLAYER.rect.y])
    engine.renderParticles(PARTICLES, PIV_SURFACE, SCROLL)
    engine.renderBullets(BULLETS_LIST, PIV_SURFACE)


    WINDOW.blit(pygame.transform.scale(PIV_SURFACE, [WINDOW.get_width(), WINDOW.get_height()]), (0,0))


    #   ````````        event handling
    # recordar que tenemos que retornar tanto EXIT como LAST_MOUSE_POS por que al sustituir su valor, se crea una variable nueva, por lo tanto la referencia no es la misma
    EXIT = engine.eventHandling(pygame.event.get(), PLAYER,EXIT, JUMP_FORCE, PARTICLES)
    CLOCK.tick(60)
    pygame.display.update()

pygame.quit()
