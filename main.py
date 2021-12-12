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
PLAYER                                  =   engine.Player( ASSETS_PATH +  "/animations", PLAYER_ANIMATIONS_FRAMES_PER_IMAGE, STEPS_SOUND, SPEED, JUMP_SOUND)


BACKGROUND_COLOR                        =   ( 0, 100, 150)
BACKGROUND_MUSIC                        =   pygame.mixer.music.load(SOUNDS_PATH + "background.wav")
BULLETS_SIZE                            =   [20, 3]
BULLETS_ANIMATION_FPS                   =   3
BULLET_SPRITE                           =   engine.getImageReady("material/armas/bullet.png", BULLETS_SIZE, None, True)
BULLETS_LIST                            =   []
BULLETS_SPEED                           =  20
CELL_LIST                               =   []
CLOCK                                   =   pygame.time.Clock()

BULLETS_EXPLOSIONS                      =   []
BULLETS_EXPLOSION_ANIMATION_SIZE        =    [20,20]
BULLETS_EXPLOSION_ANIMATION             =   engine.loadExplosionAnimation(ASSETS_PATH + "/explosion/animations/", BULLETS_EXPLOSION_ANIMATION_SIZE)
EXIT                                    =   False

GAME_MAP                                =   engine.loadMap( ASSETS_PATH + "/map.txt")
GRAVITY                                 =   1

MAX_GRAVITY                             =   10


TILE_SIZE                               =   [16, 16]

JUMP_SOUND.set_volume(0.4)
STEPS_SOUND.set_volume(0.3)
pygame.mixer.music.set_volume(0.03)
pygame.mixer.music.play(-1)
pygame.mouse.set_visible(False)

TILES               = {
    1 : engine.getImageReady(ASSETS_PATH + "/tiles/grass.png", TILE_SIZE, None, False),
    2 : engine.getImageReady(ASSETS_PATH + "/tiles/dirt.png", TILE_SIZE, None, False),
    3 : engine.getImageReady(ASSETS_PATH + "/tiles/plant.png", TILE_SIZE, (255,255,255), True),}

PLAYER.addWeapon(engine.Weapon(None, 200, 7, 100, pygame.mixer.Sound("material/efects/shots/shot.wav"), False, pygame.mixer.Sound("material/efects/shots/no amoo.wav")))

while not EXIT:
    PIV_SURFACE.fill(BACKGROUND_COLOR)

    #   ````````        update
    currentWeapon = PLAYER.weapon_list[PLAYER.current_weapon]
    currentWeapon.updateShotsInfo(PLAYER, SCROLL, BULLETS_LIST, BULLET_SPRITE, BULLETS_SPEED, BULLETS_SIZE)
    engine.updateBullets(BULLETS_LIST, CELL_LIST, PIV_SURFACE_SIZE, BULLETS_EXPLOSIONS, SCROLL)
    engine.updateBulletExplosionAnimation(BULLETS_EXPLOSIONS, len(BULLETS_EXPLOSION_ANIMATION), BULLETS_ANIMATION_FPS)
    engine.updateWakes(WAKE_LIST, SCROLL)
    PLAYER.updateState(GRAVITY, MAX_GRAVITY, CELL_LIST)
    engine.updateScroll(SCROLL,  PLAYER, PIV_SURFACE_SIZE, SCROLL_SMOOTH)

    #   ````````        render
    print(f"Cantidad de municion {currentWeapon.amoo}")
    print(f"Cantidad de balas {len(BULLETS_LIST)}")

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
