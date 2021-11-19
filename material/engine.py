import pygame
from pygame.locals import *
import ideas
import math
import os
from random import randint


class Player:
    def __init__(self, animation_path, frames_per_image, steps_sound, player_speed, jump_sound):
        self.width                  =   30
        self.height                 =   40
        animationSet                =   animationDict([self.width, self.height], (255, 255, 255), animation_path, False)
        self.animation_manager      =   ideas.AnimationController(animationSet, frames_per_image, "idle/right", True)
        self.rect                   =   pygame.Rect([0, 0, self.width, self.height])
        self.y_momentum             =   0
        self.moving_right           =   False
        self.moving_left            =   False
        self.in_floor               =   False
        self.jump_count             =   0
        self.walking_sound_runing   =   False
        self.shot_sound_runing      =   False
        self.attacking              =   False
        self.weaponList             =   []
        self.currentWeapon          =   0
        self.steps_sound            =   steps_sound
        self.speed                  =   player_speed
        self.jump_sound             =   jump_sound
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
    def updateState(self, mira, scroll, shot_smooth, gravity, max_gravity, cell_list, bullets_frame):
        """
            Actualiza la posicion del personaje llamando al metodo move, actualiza el momentum (para ello hace uso de los parametros "gravity" y "max_gravity" ), llama al metodo animationCheck(), updateSounds() y updateAnimation() del animationManager
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
        colisions = self.move(player_movement, cell_list)
        if colisions["bottom"]:
            self.y_momentum  = 0
            self.in_floor = True
            self.jump_count = 0
        else :
            if colisions["top"]:
                self.y_momentum = max_gravity//10
            self.in_floor = False
        currentWeapon = self.weaponList[self.currentWeapon]
        if self.attacking: 
            if currentWeapon.current_shot_iter == currentWeapon.shots_per_iter:
                currentWeapon.shot(mira, self, scroll, shot_smooth, bullets_frame)
                currentWeapon.current_shot_iter = 0
            else:
                currentWeapon.current_shot_iter += 1
        
        else:
            currentWeapon.current_shot_iter = currentWeapon.shots_per_iter
        self.animationCheck()
        self.updateSounds()
        self.animation_manager.updateAnimation()
    def moving(self) -> bool:
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
            else:
                print("Error, no hay direccion en la animacion, metodo 'animationCheck' de la clase Player")
                exit(-1)
    def move(self, player_movement, cell_list) -> dict:
        """
            Mueve el personaje usando el player_movement recibido por parametro, retorna un diccionario que simboliza las direcciones en las cules ha habido una colision,
            ademas de arreglar dichas colisiones
        """
        colisions = {
            "right" : False,
            "left"  : False,
            "top"  : False,
            "bottom"  : False,
        }
        self.rect.x += player_movement[0]
        for cell in colisionTest(self.rect, cell_list):
            if player_movement[0] > 0:
                self.rect.right = cell.left
                colisions["right"] = True
            elif player_movement[0] < 0:
                self.rect.left = cell.right
                colisions["left"] = True
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
        if self.jump_count <= 1:
            if self.jump_count == 0 and self.in_floor:
                self.y_momentum = jump_force
                self.jump_count += 1
                self.in_floor = False
                self.jump_sound.play().fadeout(500)
            elif self.jump_count == 1:
                self.jump_count += 1
                self.y_momentum = jump_force*2
    def render(self, surface, scroll):
        surface.blit(self.animation_manager.current_animation_list[self.animation_manager.current_animation_index], [ self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.width, self.rect.height])
class Mira:
    """
        Clase disenada para el mantenimiento de la mira
        Nota: recordar que para que la mira pueda moverse con "smooth" el movimiento relativo del mouse no puede aplicarse directamente, sino que tiene que agregarse           a un "recipiente" (pend_move) del cual se vaya agarrando movimiento poco a poco, tomando siempre una cantidad especifica (pend_move[x]//MIRA_SMOOTH])
    """
    def __init__(self, sprite):
        self.position           =   [0, 0]
        self.pend_move          =   [0, 0]
        self.initialized        =   False
        self.sprite             =   sprite
    def move(self, move):
        """
            Actualiza el movimiento pendiente de la mira
        """
        self.pend_move[0] += move[0]
        self.pend_move[1] += move[1]
    def updateState(self, smooth):
        """
            Actualiza la posicion de la mira con el movimiento pendiente
        """
        self.position[0]  += (self.pend_move[0]//smooth)
        self.position[1]  += (self.pend_move[1]//smooth)
        self.pend_move[0] -= (self.pend_move[0]//smooth)
        self.pend_move[1] -= (self.pend_move[1]//smooth)
    def render(self, surface):
        surface.blit(self.sprite, self.position)
class Weapon:
    """
        Clase creada para el uso y mantenimiento del arma del personaje
        Nota: recordar que la idea a futuro es que el usuario pueda usar varias armas, es por eso que se solicitan tantos datos. Ademas recordar que el "arma actual" la lleva el personaje, no puede ser una variable global.
    """
    def __init__(self, sprite_path, sound_effect_path, volume, size, has_alpha_pixels, amoo, shots_per_iter, relative_pos, id_, bullet_img, is_melee):
        self.size               = size
        self.sprite             = pygame.transform.scale(pygame.image.load(sprite_path), size)
        self.amoo               = amoo
        self.shots_per_iter     = shots_per_iter
        self.current_shot_iter  = 0
        self.relative_pos       =  relative_pos
        self.id                 = id_
        self.pend_bullets       =   []
        self.sound_effect       = pygame.mixer.Sound(sound_effect_path)
        self.sound_effect.set_volume(volume)
        self.currentOrientation = "right"
        self.bullet_img         =   bullet_img
        self.flipping_dict      = { "right" : True, "left" : False }
        self.operativeSprite    = None
        self.pepe               = None
        self.is_melee           = is_melee
        convertFunction = self.sprite.convert_alpha if has_alpha_pixels else self.sprite.convert
        convertFunction()
    def updateCurrentRotationAngle(self, mira, scroll, player):
        """
            Actualiza el angulo de rotacion del arma y hace mantenimiento al diccionario de flipping, necesario para la orientacion del arma(esto ultimo llamando a la funcion updateFippingDict)
        """
        current_pos = getScrolledPosition(scroll, weaponPosition(player, self.relative_pos))
        catetoOpuesto   = current_pos[1]   - mira.position[1] - mira.sprite.get_height()//2
        catetoAdyacente = mira.position[0] - current_pos[0] - mira.sprite.get_width()//2
        if catetoAdyacente != 0:
            self.currentAngle = math.atan(catetoOpuesto/catetoAdyacente)*50
            rotated_sprite =  pygame.transform.rotate(self.sprite,  self.currentAngle)
        else:
            self.currentAngle = 75
            rotated_sprite =  pygame.transform.rotate(self.sprite,  75)
        self.updateFlippingDict(player, scroll, mira)
        self.operativeSprite = rotated_sprite
    def updateFlippingDict(self, player, scroll, mira):
        """
            Actualiza el FippingDict, diccionario necesario para el mantenimiento de la orientacion del arma 
        """
        orientationLimit = player.rect.x - scroll[0] + (player.width//1.5)
        if (mira.position[0] > orientationLimit) and self.currentOrientation != "right":
            self.currentOrientation = "right"
        elif (mira.position[0] < orientationLimit) and self.currentOrientation != "left":
            self.currentOrientation = "left"
        if not self.flipping_dict[self.currentOrientation]:
            self.flipping_dict["left" if self.currentOrientation == "right" else "right"] = False
            self.flipping_dict[self.currentOrientation] = True
            self.sprite = pygame.transform.flip(self.sprite, True, False)
    def render(self, surface, sprite,  scroll, player):
        current_pos = getScrolledPosition(scroll, weaponPosition(player, self.relative_pos))
        surface.blit(sprite, [current_pos[0] - (sprite.get_width()//2), current_pos[1] - (sprite.get_height()//2)])
    def shot(self, mira, player, scroll, shot_smooth, bullets_frame):
        """
            Crea un objeto Bullet y lo agrega a la weaponList del arma en caso de que la misma tenga balas, ademas ejecuta el soundEffect del arma
        """
        if self.amoo > 0:
            weaponPos = getScrolledPosition(scroll, weaponPosition(player, self.relative_pos))
            catetoOpuesto =  mira.position[1] - weaponPos[1] + mira.sprite.get_height()//2
            catetoAdyacente =  mira.position[0] - weaponPos[0] + mira.sprite.get_width()//2

            # desviaciones
            #limit = 20
            #catetoOpuesto += randint(1,limit)
            #catetoAdyacente += randint(1,limit)





            move = [catetoAdyacente//shot_smooth, catetoOpuesto//shot_smooth]
            self.pend_bullets.append(Bullet(weaponPos, move, self.currentAngle))
            self.amoo -= 1
            self.sound_effect.play().fadeout(500)
        elif self.amoo == 0:
            # dar play a sonido "sin balas"
            pass
    def updateBulletsPosition(self,  surface_size):
        """
            Recorre la lista de balas del arma "self", elimina las balas cuya posicion no sea "renderizable", actualiza la posicion de aquellas que si lo sean 
        """
        piv_bullet_list = self.pend_bullets
        # eliminamos las balas que esten por fuera de los limites y aquellas que no, actualizamos su posicion
        for bullet in self.pend_bullets:
            if ( ((bullet.position[0] + bullet.move[0]) > surface_size[0]) or  ((bullet.position[0] + bullet.move[0]) < 0)) or ((bullet.position[1] < 0) or ((bullet.position[1] + bullet.move[1]) > surface_size[1]) ):
                piv_bullet_list.remove(bullet)
            else:
                bullet.updatePosition()
    def renderBullets(self, surface):
        """
            Recorre la lista de pend_bullets y las renderiza uno a uno
        """
        for bullet in self.pend_bullets:
            bullet.render(surface, self.bullet_img)
class Bullet:
    def __init__(self, initial_pos, move, angle):
        self.position = initial_pos
        self.move = move
        self.angle = angle
    def updatePosition(self):
        """
        Actualiza la posicion de la bala self usando el atributo move
        """
        self.position[0] += self.move[0]
        self.position[1] += self.move[1]
    def render(self, surface, bullet_img):
        img = bullet_img.copy()
        img = pygame.transform.rotate(img, self.angle)
        surface.blit(img, self.position)

def proportionalLimitTriangle(miraRealPos, weaponPos, bullets_frame):
    windowLimits = [0,0]
    miraPosition = miraRealPos.copy()
    miraPosition2 = miraPosition.copy()
    if miraPosition[1] < weaponPos[1]:
        windowLimits[1] = -bullets_frame
    else:
        windowLimits[1] = bullets_frame
    if miraPosition[0] < weaponPos[0]:
        windowLimits[0] = -bullets_frame
    else:
        windowLimits[0] = bullets_frame
    relativeWeaponPos = [(weaponPos[0] - miraPosition[0]),(weaponPos[1] - miraPosition[1])]
    relativeWeaponPos2 = relativeWeaponPos.copy()
    spaceDiff = [(abs(windowLimits[0]) - abs( relativeWeaponPos[0])),(abs(windowLimits[1]) - abs( relativeWeaponPos[1]))]
    if spaceDiff[0] < spaceDiff[1]:
        print("x")
        relativeWeaponPos[0] = windowLimits[0]
        proportion = (relativeWeaponPos[0]/relativeWeaponPos2[0])
        relativeWeaponPos[1] *= (proportion)
    else:
        print("y")
        relativeWeaponPos[1] = windowLimits[1]
        proportion = (relativeWeaponPos[1]/relativeWeaponPos2[1])
        relativeWeaponPos[0] *= (proportion)
    print(f"Space diff {spaceDiff}")
    print(f"Window limits   {windowLimits}")
    print(f"New position   {relativeWeaponPos}")
    print(f"Proportion {proportion}")
    print(f"Relative weapon pos {relativeWeaponPos}")
    del miraPosition2
    return relativeWeaponPos
    
def eventHandling(eventList, player, mira, EXIT, jump_force, last_mouse_pos):
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
        if (event.type == MOUSEBUTTONDOWN) or (event.type == MOUSEBUTTONUP):
            if (event.button == 3) and (event.type == MOUSEBUTTONDOWN):
                player.jump(jump_force)
            elif (event.button == 1):
                player.attacking = (event.type == MOUSEBUTTONDOWN)
        if event.type == MOUSEMOTION:
            if not mira.initialized :
                mira.position = list(event.pos)
                mira.initialized = True
            else:
                if  last_mouse_pos != None:
                    mira.move([ event.pos[0] - last_mouse_pos[0] ,  event.pos[1] - last_mouse_pos[1]])
                    last_mouse_pos = None
                else:
                    mira.move(event.rel)
        if event.type == WINDOWLEAVE:
            hipoteticalMouseMoIndex = eventList.index(event) - 2
            if eventList[hipoteticalMouseMoIndex].type == MOUSEMOTION:
                last_mouse_pos = eventList[hipoteticalMouseMoIndex].pos
            else:
                last_mouse_pos = None
    return EXIT, last_mouse_pos
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
def weaponPosition(player, rel_pos):
    """
    Retorna la posicion del arma teniendo en cuenta la posicion del "player" y "rel_pos"
    """
    return [player.rect.x + rel_pos[0], player.rect.y  + rel_pos[1]]
def triangleProve(PIV_SURFACE, BULLETS_FRAME, SCROLL, PLAYER, WEAPON, MIRA):
    weaponPos = getScrolledPosition(SCROLL,weaponPosition(PLAYER, WEAPON.relative_pos))
    miraPosition = [MIRA.position[0] + MIRA.sprite.get_width()//2, MIRA.position[1] + MIRA.sprite.get_height()//2]
    midPos = [miraPosition[0], weaponPos[1]]
    pygame.draw.line(PIV_SURFACE, (0, 255, 0), weaponPos, midPos, 2)
    pygame.draw.line(PIV_SURFACE, (0, 255, 0), midPos, miraPosition, 2)
    pygame.draw.line(PIV_SURFACE, (0, 255, 0), miraPosition, weaponPos, 2) 

    miraPosition2 = proportionalLimitTriangle(miraPosition, weaponPos, BULLETS_FRAME)
    midPos = [miraPosition2[0], weaponPos[1]]

    pygame.draw.line(PIV_SURFACE, (255,   0, 0), weaponPos, midPos, 2)
    pygame.draw.line(PIV_SURFACE, (255,   0, 0), midPos, miraPosition2, 2)
    pygame.draw.line(PIV_SURFACE, (255,   0, 0), miraPosition2, weaponPos, 2) 
def getImageReady(img, size, colorkey, has_alpha_pixels):
    """
        Modifica la imagen img  con los atributos pasados por parametro
    """
    img = pygame.transform.scale(img, size)
    if (colorkey != None) and (type(colorkey) in [tuple, list]) and (len(colorkey) == 3) and (max(colorkey) <= 255):
        img.set_colorkey(colorkey)
    convertFunction = img.convert_alpha if has_alpha_pixels else img.convert
    convertFunction()
    return img
def updateScroll(scroll, player, surface_size, scroll_smooth):
    scroll[0] += (player.rect.x - scroll[0] - surface_size[0]//2)//scroll_smooth
    scroll[1] += (player.rect.y - scroll[1] - surface_size[1]//2)//scroll_smooth