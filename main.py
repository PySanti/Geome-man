from random import randint
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
WINDOW                                  =   pygame.display.set_mode(WINDOW_SIZE)


SPEED                                   =   5
STEPS_SOUND                             =   pygame.mixer.Sound(ASSETS_PATH + "/efects/steps/steps.wav")
SCROLL                                  =   [0,0]
SCROLL_SMOOTH                           =   20



JUMP_SOUND                              =   pygame.mixer.Sound(ASSETS_PATH + "/efects/jump/jump.wav")
JUMP_FORCE                              =   -15


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
    cadencia_de_arma        = 20,
    attack_sound_path  = "material/efects/shots/shot_set/2.wav")
PARTICLES_PER_SHOT                      =   3

BACKGROUND_COLOR                        =   ( 50, 50, 50)
BACKGROUND_MUSIC                        =   pygame.mixer.music.load(ASSETS_PATH + "/efects/background/theme.wav")
BULLETS_SIZE                            =   [10, 3]
BULLETS_LIST                            =   []
BULLETS_SPEED                           =   20
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
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)
pygame.mouse.set_visible(False)





#   recordar que la lista de rectangulos de fondo contiene "microlistas" que almacenan las capas de las columnas
#           proporcion de scroll, color, rect
BACKGROUND_RECTS        =   engine.generateBackgroundRects()
PARTICLES                                   =   []
ENEMY_LIST                                  =   []
ENEMY_GENERATION_TIMING                     =   10
BULLET_FORCE                                =   20
BULLET_ALCANCE                              =   100 # recordar que el alcance se define como la cantidad de iteraciones que dura la vida de la bala
ENEMY_BULLET_LOWEST_SPEED                   =   2
ENEMY_SHOOTING_TIMING_RANGE                 =   [100,200]
ENEMY_BULLET_SMOOTH                         =   100
LIVE_ENEMY_RANGE                            =   [20,30]
PLAYER_X_MOMENTUM_DECREASE                  =   2
ENEMY_BULLETS_MOVE_CHANGE                   =   0.5
PARTICLE_PLAYER_SHOT_COLOR                  =   [255,0,0]
DASH_TIMER_LIMIT                            =   1000
MAX_SURFACE_SIZE    =   [1600,800]
PEND_ZOOM_MOVE  =   [0,0]



while not EXIT:
    PIV_SURFACE.fill(BACKGROUND_COLOR)

    if PLAYER.live <= 0:
        break

    #   ````````        update
    PLAYER.updateDashCounter()
    PLAYER.updateDashTimer(DASH_TIMER_LIMIT)
    PLAYER.updateShotsInfo(SCROLL, BULLETS_LIST, BULLETS_SPEED, BULLETS_SIZE, PARTICLES, PARTICLES_PER_SHOT, PARTICLE_PLAYER_SHOT_COLOR)
    PLAYER.updateState(GRAVITY, MAX_GRAVITY, CELL_LIST, PLAYER_X_MOMENTUM_DECREASE)
    engine.updateScroll(SCROLL,  PLAYER, PIV_SURFACE_SIZE, SCROLL_SMOOTH)
    engine.updateParticles(PARTICLES, CELL_LIST)
    engine.updateEnemys(ENEMY_LIST, GRAVITY, MAX_GRAVITY, CELL_LIST, PLAYER, BULLETS_LIST, ENEMY_GENERATION_TIMING, BULLETS_SIZE, SCROLL, BULLET_ALCANCE, ENEMY_BULLET_LOWEST_SPEED, ENEMY_SHOOTING_TIMING_RANGE, LIVE_ENEMY_RANGE, ENEMY_BULLET_SMOOTH)
    engine.updateBullets(BULLETS_LIST, CELL_LIST, PIV_SURFACE_SIZE, SCROLL, PARTICLES, ENEMY_LIST, BULLET_FORCE, PLAYER, ENEMY_BULLETS_MOVE_CHANGE, PARTICLE_PLAYER_SHOT_COLOR)


    #   ````````        render
    engine.renderBackgroundRects(BACKGROUND_RECTS, PIV_SURFACE, SCROLL)
    PLAYER.render(PIV_SURFACE, SCROLL)
    engine.printMap(TILE_SIZE, CELL_LIST, CELL_COLOR_CHANGE, PIV_SURFACE, GAME_MAP, SCROLL, SPACE_CHAR, [PLAYER.rect.x, PLAYER.rect.y])
    engine.renderParticles(PARTICLES, PIV_SURFACE, SCROLL)
    engine.renderBullets(BULLETS_LIST, PIV_SURFACE)
    engine.renderEnemys(ENEMY_LIST, SCROLL, PIV_SURFACE)
    WINDOW.blit(pygame.transform.scale(PIV_SURFACE, [WINDOW.get_width(), WINDOW.get_height()]), (0,0))


    #   ````````        event handling
    # recordar que tenemos que retornar tanto EXIT como LAST_MOUSE_POS por que al sustituir su valor, se crea una variable nueva, por lo tanto la referencia no es la misma
    EXIT = engine.eventHandling(pygame.event.get(), PLAYER,EXIT, JUMP_FORCE, PARTICLES, DASH_TIMER_LIMIT)
    CLOCK.tick(60)
    pygame.display.update()

pygame.quit()
