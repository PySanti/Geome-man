import pygame
from pygame.locals import *
import ideas
import math
import os
from random import randint

class BulletExplosionAnimation:
    """
        Clase creada para el mantenimiento de las explosiones de las balas al colisionar. 
        Este tipo de objeto se almacena en una lista declarada en el archivo "main" llamada "BULLETS_EXPLOSIONS" cuando las balas colisionan. 
        Esto se detecta al actualizar la posicion de las balas en el metodo "update" de la clase "Bullet".
        "WAKE_LIST" permite que a traves de la funcion "updateBulletExplosionAnimation" se actualizen los efectos por cada iteracion
    """
    def __init__(self, position):
        self.position = position
        self.current_frame = 0
        self.current_animation = 0
    def update(self, frames_per_img):
        """
            Actualiza los valores de las animaciones del efecto
        """
        if self.current_frame == frames_per_img:
            self.current_frame = 0
            self.current_animation += 1

        else:
            self.current_frame += 1
    def render(self, surface, animation_list,scroll):
        """
            Renderiza la imagen actual de la animacion en "surface"
        """
        surface.blit(animation_list[self.current_animation], [self.position[0], self.position[1]])
class Wake:
    """
        Clase creada para el mantenimiento de las estelas provocadas por el personaje al saltar. 
        Este tipo de objeto se crea cuando el usuario salta con un "player.jump_count == 0" y "player.in_floor == True" en la funcion "eventHandling"
        Y se almacena en una lista declarada en el archivo "main", llamada "WAKE_LIST", para que de este modo, a traves de la funcion "updateWakes", las estelas 
        concurrentes se actualizen.

    """
    def __init__(self, max_frames, position, animations):
        self.animations = animations
        self.position = position
        self.max_frames =  max_frames
        self.current_frame = 0
        self.current_sprite = 0
    def update(self):
        """
            Actualiza la informacion relacionada con la animacion de la estela
        """
        if self.current_frame  == self.max_frames:
            self.current_frame = 0
            self.current_sprite += 1
        else:
            self.current_frame += 1
    def render(self, surface, scroll):
        """
            Renderiza la imagen actual de la animacion en "surface"
        """
        surface.blit(self.animations[self.current_sprite], [self.position[0] - scroll[0], self.position[1] - scroll[1]])
class Player:
    """
        Clase creada para la administracion del personaje
    """
    def __init__(self, animation_path, frames_per_image, steps_sound, player_speed, jump_sound):
        self.width                  =   60
        self.height                 =   40
        animationSet                =   animationDict([self.width, self.height], (255, 255, 255), animation_path, False)
        self.animation_manager      =   ideas.AnimationController(animationSet, frames_per_image, "idle/right", True)
        self.rect                   =   pygame.Rect([200,-10, self.width, self.height])
        self.y_momentum             =   0
        self.moving_right           =   False
        self.moving_left            =   False
        self.in_floor               =   False
        self.jump_count             =   0
        self.walking_sound_runing   =   False
        self.shot_sound_runing      =   False
        self.attacking              =   {"left" : False, "right" : False}
        self.steps_sound            =   steps_sound
        self.speed                  =   player_speed
        self.jump_sound             =   jump_sound
        # weapon
        self.weapon_list            =   []
        self.current_weapon         =   0
    def updateSounds(self):
        """
            Actualiza los sonidos que esten corriendo en el momento
        """
        if self.moving() and self.in_floor and (not self.walking_sound_runing):
            self.walking_sound_runing = True
            self.steps_sound.play(-1)
        elif ((not self.moving()) or (not self.in_floor)) and self.walking_sound_runing:
            self.steps_sound.fadeout(100)
            self.walking_sound_runing = False
    def updateState(self, gravity, max_gravity, cell_list):
        """
            Actualiza la posicion del personaje llamando al metodo move, actualiza el momentum (para ello hace uso de los parametros "gravity" y "max_gravity" ).
            Ademas, actualiza las animaciones a traves del metodo animationCheck y updateAnimation, los sonidos a traves del metodo updateSounds.

        """

        player_movement = [0, 0]
        if self.moving_right:
            player_movement[0] += self.speed
        elif self.moving_left:
            player_movement[0] -= self.speed
        self.y_momentum += gravity
        if self.y_momentum > max_gravity:
            self.y_momentum = max_gravity
        player_movement[1] += self.y_momentum

        colisions = self.move(player_movement, cell_list) # aplicacion de movimiento y correccion de colisiones

        if colisions["bottom"]:
            self.y_momentum  = 0
            self.in_floor = True
            self.jump_count = 0
        else :
            if colisions["top"]:
                self.y_momentum = max_gravity//10
            self.in_floor = False




        # actualizacion de sonidos y animaciones
        self.animationCheck()
        self.updateSounds()
        self.animation_manager.updateAnimation()
    def moving(self):
        """
            Retorna True en caso de que el personaje se este moviendo
        """
        return (self.moving_left or self.moving_right)
    def animationCheck(self):
        """
            Cambia las animaciones en caso de que sea necesario cambiarlas teniendo en cuenta el estado del personaje
        """
        if (self.moving()) and (self.in_floor):
            if self.moving_right and (self.animation_manager.current_animation_name != "run/right"):
                self.animation_manager.changeAnimation("run/right")
            elif self.moving_left and (self.animation_manager.current_animation_name != "run/left"):
                self.animation_manager.changeAnimation("run/left")

        elif (not self.in_floor) and (self.moving()):
            if (self.moving_right) and (self.animation_manager.current_animation_name != "idle/right"):
                self.animation_manager.changeAnimation("idle/right")
            elif (self.moving_left) and (self.animation_manager.current_animation_name != "idle/left"):
                self.animation_manager.changeAnimation("idle/left")

        elif ((not (self.moving_right or self.moving_left)) or (not self.in_floor)) and (not "idle" in self.animation_manager.current_animation_name):
            if "left" in self.animation_manager.current_animation_name:
                self.animation_manager.changeAnimation("idle/left")
            elif "right" in self.animation_manager.current_animation_name:
                self.animation_manager.changeAnimation("idle/right")
    def move(self, player_movement, cell_list) -> dict:
        """
            Mueve el personaje usando el player_movement recibido por parametro, retorna un diccionario que simboliza las direcciones en las cuales
            ha habido una colision, ademas de arreglar dichas colisiones
        """
        colisions = {
            "right" : False,
            "left"  : False,
            "top"  : False,
            "bottom"  : False,
        }
        # movemos el personaje en x, buscamos colisiones y corregimos
        self.rect.x += player_movement[0]
        for cell in colisionTest(self.rect, cell_list):
            if player_movement[0] > 0:
                self.rect.right = cell.left
                colisions["right"] = True
            elif player_movement[0] < 0:
                self.rect.left = cell.right
                colisions["left"] = True


        # movemos el personaje en y, buscamos colisiones y corregimos
        self.rect.y += player_movement[1]
        for cell in colisionTest(self.rect, cell_list):
            if player_movement[1] > 0:
                self.rect.bottom = cell.top
                colisions["bottom"] = True
            elif player_movement[1] < 0:
                self.rect.top = cell.bottom
                colisions["top"] = True

        return colisions
    def jump(self, jump_force):
        """
            Actualiza el momentum del personaje para que "salte" siempre y cuando las condiciones de salto esten dadas
        """
        if self.jump_count <= 1:
            if self.jump_count == 0 and self.in_floor:
                self.y_momentum = jump_force
                self.jump_count += 1
                self.in_floor = False
                self.jump_sound.play().fadeout(500)
            elif self.jump_count == 1:
                self.y_momentum = jump_force*2
                self.jump_count += 1

    def render(self, surface, scroll):
        """
            Renderiza al personaje
        """
        surface.blit(self.animation_manager.current_animation_list[self.animation_manager.current_animation_index], [ self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.width, self.rect.height])
    def addWeapon(self, weapon):
        self.weapon_list.append(weapon)

class Bullet:
    """
        Clase creada para el mantenimiento de las posiciones de las balas
    """
    def __init__(self, initial_pos, sprite, move, size, alcance):
        self.position   = initial_pos
        self.move       = move
        self.sprite     = sprite
        self.size       = size
        self.alcance    = alcance
        self.distanciaRecorrida = 0
    def updatePosition(self):
        """
        Actualiza la posicion de la bala self usando el atributo move, ademas actualiza la distancia recorrida por la bala
        """
        self.position[0] += self.move[0]
        self.position[1] += self.move[1]
        self.distanciaRecorrida += abs(self.move[0])
    def render(self, surface):
        """
            Renderiza la imagen de la bala en "surface"
        """
        surface.blit(self.sprite, self.position)

class Weapon:
    def __init__(self, sprites_path, alcance, cadencia, initial_amoo, attack_sound, is_melee, no_amoo_sound):
        self.sprite_path        = sprites_path
        self.alcance            = alcance
        self.cadencia           = cadencia
        self.amoo               = initial_amoo
        self.attack_sound       = attack_sound
        self.is_melee           = is_melee
        self.current_shot_iter  = cadencia
        self.no_amoo_sound      =   no_amoo_sound
    def attack(self, player, scroll, bullets_list, bullet_sprite, bullets_speed, bullets_size):
        if self.amoo > 0:
            if (player.attacking["right"]):
                bulletInitialPos    = getScrolledPosition(scroll, [player.rect.right + 10, player.rect.bottom - player.height//2])
                new_bullet          = Bullet(bulletInitialPos, bullet_sprite, [bullets_speed, 0], bullets_size, self.alcance)
                bullets_list.append(new_bullet)

            elif (player.attacking["left"]):
                bulletInitialPos    = getScrolledPosition(scroll, [player.rect.left - 10, player.rect.bottom - player.height//2])
                bullet_sprite       = pygame.transform.flip(bullet_sprite, True, False)
                new_bullet          = Bullet(bulletInitialPos, bullet_sprite, [-bullets_speed, 0], bullets_size, self.alcance)
                bullets_list.append(new_bullet)
            self.amoo -= 1
            self.attack_sound.set_volume(0.5)
            self.attack_sound.play().fadeout(500)

        else:
            self.no_amoo_sound.set_volume(0.5)
            self.no_amoo_sound.play().fadeout(500)
    def updateShotsInfo(self, player, scroll, bullets_list, bullet_sprite, bullets_speed, bullets_size):
        if (not self.is_melee) and (player.attacking["right"] or player.attacking["left"]) and (self.current_shot_iter == self.cadencia):
            self.attack(player, scroll, bullets_list, bullet_sprite, bullets_speed, bullets_size)
            self.current_shot_iter = 0

        elif not (player.attacking["right"] or player.attacking["left"]):
            self.current_shot_iter = self.cadencia

        elif self.current_shot_iter != self.cadencia:
            self.current_shot_iter += 1



def updateBullets(bullets_list, cell_list, surface_size, bullets_explosion_list, scroll):
    """
        Actualiza la posicion de las balas, y elimina aquellas que ya no sean renderizables, que esten colisionando con algo o 
        cuyo alcance haya terminado
    """
    copy_list = bullets_list.copy()
    for bullet in copy_list:
        if  (surface_size[0] < bullet.position[0]) or (bullet.position[0] < 0):
            bullets_list.remove(bullet)
        else:
            bullet.updatePosition()
            colisions = colisionTest(pygame.Rect([bullet.position[0] + scroll[0], bullet.position[1] + scroll[1], bullet.size[0], bullet.size[1]]), cell_list)
            if len(colisions) > 0:
                print("colision de bala")
                bullets_list.remove(bullet)
                colied_tile = colisions[0]
                colision_position = [colied_tile.x + colied_tile.width//2, colied_tile.y + colied_tile.height//2]
                bullets_explosion_list.append(BulletExplosionAnimation(colision_position))

            elif bullet.distanciaRecorrida > bullet.alcance:
                print("distancia final alcanzada")
                bullets_list.remove(bullet)
                bullets_explosion_list.append(BulletExplosionAnimation(bullet.position))



def renderBullets(bullets_list, surface):
    for bullet in bullets_list:
        bullet.render(surface)

def updateBulletExplosionAnimation(BulletExplosionList, animationListLen, frames_per_img):
    """
        Actualiza la informacion de las animaciones de las explosiones de las balas de la lista "BulletExplosionList"
        ademas elimina aquellas animaciones que se hayan terminado
    """
    BulletExplosionList2 = BulletExplosionList
    for explosion in BulletExplosionList2:
        explosion.update(frames_per_img)
        if explosion.current_animation > animationListLen-1:
            BulletExplosionList.remove(explosion)
def renderBulletExplosionAnimation(BulletExplosionAnimationList, surface, animation_list, scroll):
    """
        Recorre la lista de los objetos BulletExplosionAnimation, y renderiza la imagen correspondiente
    """
    for explosion in BulletExplosionAnimationList:
        explosion.render(surface, animation_list, scroll)
def loadExplosionAnimation(path, animation_size):
    """
        Carga la lista de imagenes necesarias para la animacion de las explosiones de las balas y la retorna
    """
    animation_list = []
    current_img = 0
    current_target = 1
    folder = os.listdir(path)
    while current_target != len(folder):
        if str(current_target) in folder[current_img]:
            ready_img = getImageReady(path + folder[current_img], animation_size, None, True)
            animation_list.append(ready_img)
            current_target += 1
            current_img = 0 
        else:
            current_img += 1
    
    return animation_list

def eventHandling(eventList, player,EXIT, jump_force, wake_list, wake_animations, wake_size):
    """
        Funcion creada para la recepcion de todos los eventos en el programa, encargada de llamar a las funciones necesarias relativas al evento en particular

        Retorna "LAST_MOUSE_POS" y el valor de EXIT ya que son objetos inmutables, su modificacion en esta funcion implicaria la creacion de una nueva variable, 
        imperceptible para el modulo "main"
    """
    for event in eventList:
        if event.type == QUIT:
            EXIT = True
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            EXIT = True
        if event.type == KEYDOWN  or event.type == KEYUP:
            if event.key == K_d:
                player.moving_right = (event.type == KEYDOWN)
            if event.key == K_a:
                player.moving_left = (event.type == KEYDOWN)

            if event.key == K_SEMICOLON:
                player.attacking["right"] = (event.type == KEYDOWN)
            if event.key == K_k:
                player.attacking["left"] = (event.type == KEYDOWN)
            if event.key == K_w and event.type == KEYDOWN:
                if player.jump_count == 0 and player.in_floor:
                    animation_direction = player.animation_manager.current_animation_name.split("/")[1]
                    wake_list.append(Wake(3, [player.rect.x, player.rect.y + player.height - wake_size[1]], wake_animations["right" if animation_direction == "left" else "left"]))
                player.jump(jump_force)
    return EXIT
def animationDict(size, colorkey, animationSetPath, has_alpha):
    """
        Retorna el diccionario de animaciones obtenido del animationSetPath, las animaciones deben seguir el formato: animationType -> animationDirection -> Animations
    """
    animations = {}
    try:
        for animationType in os.listdir(animationSetPath):
            animations[animationType] ={}
            for animationDirection in os.listdir(animationSetPath + f"/{animationType}/"):
                animations[animationType][animationDirection] = []
                animationSet = os.listdir(animationSetPath + f"/{animationType}/{animationDirection}")
                index = 0
                counter = 1
                loops    = 0 
                while counter != (len(animationSet) + 1)  :
                    if str(counter) in animationSet[index]:
                        sprite = pygame.image.load(animationSetPath + f"/{animationType}/{animationDirection}/{animationSet[index]}")
                        if not has_alpha:
                            sprite.convert()
                        else:
                            sprite.convert_alpha()
                        sprite = pygame.transform.scale(sprite, size)
                        if colorkey != None:
                            sprite.set_colorkey(colorkey)
                        animations[animationType][animationDirection].append(sprite)
                        counter += 1
                        index = 0
                    index += 1
                    if index == len(animationSet):
                        index = 0
                        loops += 1
                        if loops > 3:
                            print(f"Error, animacion numero > {counter} < de tipo > {animationType} < no encontrada")
                            exit(-1)
    except IndexError:
            print(f"Error, animacion numero > {counter} < de tipo > {animationType} < no encontrada")
            exit(-1)
    else:
        return animations
def getScrolledPosition(scroll, position ):
    """
        Retorna "position" con "scroll" aplicado
    """
    position[0] -= scroll[0]
    position[1] -= scroll[1]
    return position
def colisionTest(rect, cells):
    """
        Retorna la lista de "cells" con las cuales esta colisionando "rect"
    """
    colisions = []
    for cell in cells:
        if rect.colliderect(cell):
            colisions.append(cell)
    return colisions
def loadMap(path) -> list:
    """
        Recibe la ruta del archivo del mapa y retorna la lista correspondiente  al mapa 
    """
    map_ = []
    with open(path, "r") as file_:
        for line in file_:
            current_line = []
            for char in line:
                if char != "\n":
                    current_line.append(int(char))
            map_.append(current_line)
    return map_
def printMap(tile_size, cells, tiles, surface, map_, scroll):
    """
        Imprime el mapa, correspondiente a map_, ademas agrega las celdas a la lista "cells" en caso de que no esten ya ahi.
    """
    curr_x = 0
    curr_y = 0
    no_cells_loaded = len(cells) == 0
    for line in map_:
        for char in line:
            if char >= 1:
                surface.blit(tiles[char], [curr_x - scroll[0], curr_y - scroll[1]])
                if no_cells_loaded:
                    if char != 3:
                        cells.append(pygame.Rect([curr_x, curr_y, tile_size[0], tile_size[1]]))
            curr_x += tile_size[0]
        curr_y += tile_size[1]
        curr_x = 0
def getImageReady(path, size, colorkey, has_alpha_pixels):
    """
        Modifica la imagen img  con los atributos pasados por parametro
    """
    img = pygame.transform.scale(pygame.image.load(path), size)
    if (colorkey != None) and (type(colorkey) in [tuple, list]) and (len(colorkey) == 3) and (max(colorkey) <= 255):
        img.set_colorkey(colorkey)
    convertFunction = img.convert_alpha if has_alpha_pixels else img.convert
    convertFunction()
    return img
def updateScroll(scroll, player, surface_size, scroll_smooth):
    """
        Actualiza el scroll de manera relativa a la posicion del personaje
    """
    scroll[0] += (player.rect.x - scroll[0] - surface_size[0]//2)//scroll_smooth
    scroll[1] += (player.rect.y - scroll[1] - surface_size[1]//2)//scroll_smooth
def loadWakeAnimations(path, size ):
    """
        Funcion creada para cargar las imagenes necesarias para la animacion de la estela al saltar
    """
    animations = {}
    for direction in os.listdir(path):
        animations[direction] = []
        current_target = 1
        currIndex = 0
        animationList = os.listdir(f"{path}/{direction}")
        while current_target != len(animationList):
            if str(current_target) in animationList[currIndex]:
                animations[direction].append(getImageReady(f"{path}/{direction}/{animationList[currIndex]}", size, None, True))
                current_target += 1
                currIndex = 0
            else:
                currIndex += 1
    
    return animations
def renderWakes(wake_list, surface, scroll):
    """
        Funcion creada para renderizar las imagenes de los objetos "Wake"
    """
    for wake in wake_list:
        wake.render(surface, scroll)
def updateWakes(wake_list, scroll):
    """
        Funcion creada para actualizar la informacion de la animacion de los objetos wakes
    """
    wakeList2 = wake_list.copy()
    for wake in wakeList2:
        wake.update()
        if wake.current_sprite == len(wake.animations):
            wake_list.remove(wake)
