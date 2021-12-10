import pygame
import os
from pygame.locals import *
from material import engine
pygame.init()
pygame.mixer.init()


#   todo :
#        aumentar realismo de sonido de disparo, implementar cambios de precision relativos a la cadencia del arma, impolementar colatazos
#        implementar colisiones de balas
#        implementar objetos de ambiente 
#        implementar outlines 
#        implementar admision de armas melee a la clase weapon, que usar el metodo shot no siginifique necesariamente disparar
#        Mejorar sprite de personaje y de balas
#        Particulas al disparar
#        Colisiones reales (y adision de sprites)
#        Revisar otros proyectos y hacerlos portables a Windows (probar)
#        Retroceso de arma
#        Documentar
#        Arreglar imagen de las celdas (poner imagenes mas de tipo rambo)
#        Poner balas y particulas al disparar
#        Poner enemigos
#        Poner score
#        Poner menu de configuracion
#        Poner objetos de fondo
#        Poner icono
#        Modificacion de mira en menu

#   others, ordenado alfabeticamente
ASSETS_PATH                             =   "material"

WINDOW_SIZE                             =   [1000, 700]
WINDOW                                  =   pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
WAKE_SIZE                               =   [40,20]
WAKE_ANIMATIONS                         =   engine.loadWakeAnimations( ASSETS_PATH + "/estela", WAKE_SIZE)
WAKE_LIST                               =   []



SPEED                                   =   5
SHOT_SMOOTH                             =  10
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
BULLETS_FRAME                           =   500
BULLETS_SIZE                            =   [20, 3]
BULLETS_ANIMATION_FPS                   = 3

CELL_LIST                               =   []
CLOCK                                   =   pygame.time.Clock()

BULLETS_EXPLOSIONS                      =   []
BULLETS_EXPLOSION_ANIMATION_SIZE        =    [20,20]
BULLETS_EXPLOSION_ANIMATION             =   engine.loadExplosionAnimation(ASSETS_PATH + "/explosion/animations/", BULLETS_EXPLOSION_ANIMATION_SIZE)
EXIT                                    =   False

GAME_MAP                                =   engine.loadMap( ASSETS_PATH + "/map.txt")
GRAVITY                                 =   1
LAST_MOUSE_POS                          =   None

MIRA_SMOOTH                             =   5
MIRA_SIZE                               =    [30,30]
MIRA                                    =   engine.Mira(engine.getImageReady(pygame.image.load(ASSETS_PATH + "/mira/shot_mira.png"), MIRA_SIZE, None, True))
MAX_GRAVITY                             =   10


TILE_SIZE                               =   [16, 16]

PLAYER.weaponList.append(engine.Weapon(
        sprite_path = ASSETS_PATH + "/armas/ametralladora_1.png", 
        sound_effect_path = ASSETS_PATH + "/efects/shots/shot.wav", 
        volume = 1, 
        size = [60, 20], 
        has_alpha_pixels = True, 
        amoo = 1000, 
        shots_per_iter = 5, 
        relative_pos = [PLAYER.width//1.5, PLAYER.height//1.5], 
        id_ = 0, 
        bullet_img = engine.getImageReady(pygame.image.load(ASSETS_PATH + "/armas/bullet2.png"), BULLETS_SIZE, None, True), 
        no_amoo_sound_path = ASSETS_PATH + "/efects/shots/no amoo.wav",
        is_melee = False))

JUMP_SOUND.set_volume(0.4)
STEPS_SOUND.set_volume(0.3)
pygame.mixer.music.set_volume(0.03)
pygame.mixer.music.play(-1)
pygame.mouse.set_visible(False)

TILES               = {
    1 : engine.getImageReady(pygame.image.load(ASSETS_PATH + "/tiles/grass.png"), TILE_SIZE, None, False),
    2 : engine.getImageReady(pygame.image.load(ASSETS_PATH + "/tiles/dirt.png"), TILE_SIZE, None, False),
    3 : engine.getImageReady(pygame.image.load(ASSETS_PATH + "/tiles/plant.png"), TILE_SIZE, (255,255,255), True),}


while not EXIT:
    PIV_SURFACE.fill(BACKGROUND_COLOR)

    #   ````````        update

    engine.updateBulletExplosionAnimation(BULLETS_EXPLOSIONS, len(BULLETS_EXPLOSION_ANIMATION), BULLETS_ANIMATION_FPS)
    weapon = PLAYER.weaponList[PLAYER.currentWeapon]
    engine.updateWakes(WAKE_LIST, SCROLL)
    MIRA.updateState(MIRA_SMOOTH)
    PLAYER.updateState(MIRA, SCROLL, SHOT_SMOOTH, GRAVITY, MAX_GRAVITY, CELL_LIST, BULLETS_FRAME, BULLETS_SIZE)
    weapon.updateCurrentRotationAngle(MIRA, SCROLL, PLAYER)
    weapon.updateBulletsPosition(PIV_SURFACE_SIZE, CELL_LIST, SCROLL, BULLETS_EXPLOSIONS)
    engine.updateScroll(SCROLL,  PLAYER, PIV_SURFACE_SIZE, SCROLL_SMOOTH)
    print(SCROLL)

    #   ````````        render
    engine.renderWakes(WAKE_LIST, PIV_SURFACE, SCROLL)
    engine.printMap(TILE_SIZE, CELL_LIST, TILES, PIV_SURFACE, GAME_MAP, SCROLL)
    PLAYER.render(PIV_SURFACE, SCROLL)
    MIRA.render(PIV_SURFACE)
    weapon.render( PIV_SURFACE,  weapon.operativeSprite, SCROLL, PLAYER)
    weapon.renderBullets(PIV_SURFACE)
    #engine.triangleProve(PIV_SURFACE, BULLETS_FRAME, SCROLL, PLAYER, weapon, MIRA)
    engine.renderBulletExplosionAnimation(BULLETS_EXPLOSIONS, PIV_SURFACE, BULLETS_EXPLOSION_ANIMATION, SCROLL)
    WINDOW.blit(pygame.transform.scale(PIV_SURFACE, [WINDOW.get_width(), WINDOW.get_height()]), (0,0))

    #   ````````        event handling
    # recordar que tenemos que retornar tanto EXIT como LAST_MOUSE_POS por que al sustituir su valor, se crea una variable nueva, por lo tanto la referencia no es la misma
    EXIT, LAST_MOUSE_POS = engine.eventHandling(pygame.event.get(), PLAYER, MIRA, EXIT, JUMP_FORCE,  LAST_MOUSE_POS, WAKE_LIST, WAKE_ANIMATIONS, WAKE_SIZE)
    CLOCK.tick(60)
    pygame.display.update()

pygame.quit()
