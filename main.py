import pygame
import os
from pygame.display import update
from pygame.locals import *
from material import engine
pygame.init()
pygame.mixer.init()

#   todo :
#       recordar usar el arma como punto 0 del plano para usar la tecnica del marco para los disparos
#        repasar codigo
#        implementar sonido "sin balas"
#        implementar colisiones de balas
#        implementar objetos de ambiente 
#        implementar outlines 
#        implementar rotacion de la mira al disparar
#        implementar admision de armas melee a la clase weapon, que usar el metodo shot no siginifique necesariamente disparar
#        Mejorar sprite de personaje y de balas
#        Efecto de salto
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

#   others
WINDOW_SIZE         =   [1000, 700]
WINDOW              =   pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
PIV_SURFACE_SIZE    =   [800, 400]
PIV_SURFACE         =   pygame.Surface(PIV_SURFACE_SIZE)
COLOR               =   ( 0, 100, 150)
CLOCK               =   pygame.time.Clock()
EXIT                =   False
ASSETS_PATH         =   "material"
SPEED               =   5
GRAVITY             =   1
MAX_GRAVITY         =   10
JUMP_FORCE          =   -8
SHOT_SMOOTH         =  10
FRAMES_PER_IMAGE    =   7
SOUNDS_PATH         =   ASSETS_PATH + "/efects/"
BACKGROUND_MUSIC    =   pygame.mixer.music.load(SOUNDS_PATH + "background.wav")
JUMP_SOUND          =   pygame.mixer.Sound(ASSETS_PATH + "/efects/jump/jump.wav")
STEPS_SOUND         =   pygame.mixer.Sound(ASSETS_PATH + "/efects/steps/steps.wav")
PLAYER              =   engine.Player( ASSETS_PATH +  "/animations", FRAMES_PER_IMAGE, STEPS_SOUND, SPEED, JUMP_SOUND)
MIRA_SMOOTH         =   5
MIRA_SIZE           =    [30,30]
MIRA                =   engine.Mira(engine.getImageReady(pygame.image.load("material/mira/shot_mira.png"), MIRA_SIZE, None, True))
LAST_MOUSE_POS      =   None
CELL_LIST           =   []
GAME_MAP            =   engine.loadMap( ASSETS_PATH + "/map.txt")
TILE_SIZE           =   [16, 16]
SCROLL              =   [0,0]
SCROLL_SMOOTH       =   20
SHOT_LIMIT          = 100
BULLETS_FRAME       =   500

PLAYER.weaponList.append(engine.Weapon(ASSETS_PATH + "/armas/ametralladora_1.png", ASSETS_PATH + "/efects/shots/shot.wav", 1, [60, 20], True, 1000, 5, [PLAYER.width//1.5, PLAYER.height//1.5], 0, engine.getImageReady(pygame.image.load(ASSETS_PATH + "/armas/bullet2.png"), [20, 3], None, True), False))
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
    PIV_SURFACE.fill(COLOR)

    #   ````````        update
    weapon = PLAYER.weaponList[PLAYER.currentWeapon]
    MIRA.updateState(MIRA_SMOOTH)
    PLAYER.updateState(MIRA, SCROLL, SHOT_SMOOTH, GRAVITY, MAX_GRAVITY, CELL_LIST, BULLETS_FRAME)
    weapon.updateCurrentRotationAngle(MIRA, SCROLL, PLAYER)
    weapon.updateBulletsPosition(PIV_SURFACE_SIZE)
    engine.updateScroll(SCROLL,  PLAYER, PIV_SURFACE_SIZE, SCROLL_SMOOTH)

    #   ````````        render


    engine.printMap(TILE_SIZE, CELL_LIST, TILES, PIV_SURFACE, GAME_MAP, SCROLL)
    PLAYER.render(PIV_SURFACE, SCROLL)
    MIRA.render(PIV_SURFACE)
    weapon.render( PIV_SURFACE,  weapon.operativeSprite, SCROLL, PLAYER)
    weapon.renderBullets(PIV_SURFACE)
    if weapon.pepe != None:
        pygame.draw.circle(PIV_SURFACE, (255,0, 0), weapon.pepe, 20)
        print(weapon.pepe)
    engine.triangleProve(PIV_SURFACE, BULLETS_FRAME, SCROLL, PLAYER, PLAYER.weaponList[PLAYER.currentWeapon], MIRA)
    WINDOW.blit(pygame.transform.scale(PIV_SURFACE, [WINDOW.get_width(), WINDOW.get_height()]), (0,0))

    # recordar que tenemos que retornar tanto EXIT como LAST_MOUSE_POS por que al sustituir su valor, se crea una variable nueva, por lo tanto la referencia no es la misma
    EXIT, LAST_MOUSE_POS = engine.eventHandling(pygame.event.get(), PLAYER, MIRA, EXIT, JUMP_FORCE,  LAST_MOUSE_POS)
    CLOCK.tick(60)
    pygame.display.update()
pygame.quit()
