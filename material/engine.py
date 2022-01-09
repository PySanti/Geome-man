import pygame
from pygame.locals import *
import os
from random import randint


class Player:
    """
        Clase creada para la administracion del personaje y datos del arma
    """
    def __init__(self, steps_sound, player_speed, jump_sound, animation_manager, size, cadencia_de_arma, attack_sound_path):
        self.width                  =   size[0]
        self.height                 =   size[1]
        self.rect                   =   pygame.Rect([1000,350, self.width, self.height])
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
        self.animation_manager      =   animation_manager
        self.amoo                   =   1000
        self.cadencia               =   cadencia_de_arma
        self.attack_sound           =   pygame.mixer.Sound(attack_sound_path)
        self.look_back_couter       =   0
        self.look_back_max_counter  =   None
        self.last_direction         =   None
    def updateSounds(self):
        """
            Actualiza los sonidos que esten corriendo en el momento
        """
        if (self.moving()) and (self.in_floor) and (not self.walking_sound_runing):
            self.walking_sound_runing = True
            self.steps_sound.play(-1)
        elif ((not self.moving()) or (not self.in_floor)) and (self.walking_sound_runing):
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
        self.animation_manager.updateAnimation()
        self.updateSounds()
        self.updateLastDirection()
    def generateAttackSound(self, volume, fadeout):
        """
            Reproduce el sonido de ataque
        """
        self.attack_sound.set_volume(volume)
        self.attack_sound.play().fadeout(fadeout)
    def attack(self, scroll, bullets_list, bullets_speed, bullets_size, particles, particles_per_shot):
        """
            Administra las acciones necesarias al disparar
        """
        if self.amoo > 0:
            bulletInitialPos    = getScrolledPosition(scroll, [self.rect.right + 10 if self.attacking["right"] else self.rect.left - 10, self.rect.bottom - self.height//2])
            new_bullet          = Bullet(bulletInitialPos,  [bullets_speed if self.attacking["right"] else -bullets_speed, 0], bullets_size)
            bullets_list.append(new_bullet)
            self.amoo -= 1
            self.generateAttackSound(volume=0.1, fadeout=700)


            particles_color         =  [100,100,100 ]
            particles_move          =  [randint(-1,1),-1] 
            particles_move_change   =   [0, 0.1] 
            particles_color_change =  [0,0,0]
            particles_size_change  =  0.05
            particles_size          =   3
            move_range              =  10

            for i in range(1, particles_per_shot+1):
                particle_pos = [self.rect.x + self.width,self.rect.y + (self.height//2) ] if self.attacking["right"] else [self.rect.x ,self.rect.y + (self.height//2) ] 
                particle_pos[0] += randint(-move_range,move_range)
                particle_pos[1] += randint(-move_range,move_range)
                new_particle     = Particle(
                    particle_pos.copy(), 
                    particles_size,
                    particles_color.copy(), 
                    particles_move.copy(), 
                    particles_size_change, 
                    particles_move_change, 
                    particles_color_change,
                    False  )
                particles.append(new_particle)
    def moving(self):
        """
            Retorna True en caso de que el personaje se este moviendo
        """
        return (self.moving_left or self.moving_right)
    def animationCheck(self):
        """
            Cambia las animaciones en caso de que sea necesario cambiarlas teniendo en cuenta el estado del personaje
        """
        animation_manager = self.animation_manager
        if ("stand" in animation_manager.current_animation_name) and (not "attack" in animation_manager.current_animation_name):
            if (animation_manager.current_animation_index == (len(animation_manager.current_animation_list) -1 )) :
                if (animation_manager.current_animation_name == "stand_1") :
                    random_ = randint(1,50)
                    if  random_ in [2, 3]:
                        animation_manager.changeAnimation("stand_2" if random_ == 2 else "stand_3")
                        if random_ == 3:
                            self.look_back_couter += 1
                            self.look_back_max_counter = randint(1,5)
                elif self.look_back_couter > 0:
                    animation_manager.changeAnimation("stand_3")
                    self.look_back_couter += 1
                    if self.look_back_couter > self.look_back_max_counter:
                        self.look_back_couter = 0

                else:
                    animation_manager.changeAnimation("stand_1" )
        if (self.moving()) and (self.in_floor) and (animation_manager.current_animation_name not in ["run", "attacking_running_right", "attacking_running_left"]):
            animation_manager.changeAnimation("run")
        elif ((not self.moving()) and (not (self.attacking["right"] or self.attacking["left"])) and ("stand" not in animation_manager.current_animation_name )) and (self.in_floor):
            animation_manager.changeAnimation("stand_1")
        if (not self.in_floor) and ("attack" not in animation_manager.current_animation_name):
            if self.y_momentum < 0:
                if animation_manager.current_animation_name != "jump_momentum_negativo":
                    animation_manager.changeAnimation("jump_momentum_negativo")
                elif (animation_manager.current_animation_index == (len(animation_manager.current_animation_list) - 1)):
                    animation_manager.current_animation_frame = 0
            else:
                if animation_manager.current_animation_name != "jump_momentum_positivo":
                    animation_manager.changeAnimation("jump_momentum_positivo")
                elif (animation_manager.current_animation_index == (len(animation_manager.current_animation_list) - 1)):
                    animation_manager.current_animation_frame = 0
        if (((self.attacking["right"] or self.attacking["left"]) and (self.amoo > 0)) and ("stand" in animation_manager.current_animation_name)) or (animation_manager.current_animation_name == "attacking_stand"):
            if animation_manager.current_animation_name != "attacking_stand":
                animation_manager.changeAnimation("attacking_stand")
            elif animation_manager.current_animation_index == 3 and (self.attacking["right"] or self.attacking["left"]):
                animation_manager.changeAnimation("attacking_stand")
            elif ( animation_manager.current_animation_name == "attacking_stand") and (not (self.attacking["right"] or self.attacking["left"])):
                animation_manager.changeAnimation("stand_1")

        if ((self.attacking["right"] or self.attacking["left"]) and (self.amoo > 0)) and (animation_manager.current_animation_name == "run") or (animation_manager.current_animation_name in ["attacking_running_right","attacking_running_left"]):
            new_animation = None
            if (animation_manager.current_animation_index == (len(animation_manager.current_animation_list) - 1 )) and (not (self.attacking["right"] or self.attacking["left"])) :
                animation_manager.changeAnimation("run")
            else:
                if ((self.attacking["right"] and self.moving_right) or (self.attacking["left"] and self.moving_left)):
                    new_animation = "attacking_running_right"
                elif (self.attacking["right"] and self.moving_left) or (self.attacking["left"] and self.moving_right):
                    new_animation = "attacking_running_left"
                if (new_animation != animation_manager.current_animation_name) and (new_animation != None):
                    animation_manager.changeAnimation(new_animation)
        if  ((self.attacking["right"] or self.attacking["left"]) and (self.amoo > 0)) and (not self.in_floor) :
            new_animation = None
            if (animation_manager.current_animation_index == (len(animation_manager.current_animation_list) - 1 )) and (not (self.attacking["right"] or self.attacking["left"])) :
                animation_manager.changeAnimation("jump_momentum_positivo" if self.y_momentum > 0 else "jump_momentum_negativo")
            else:
                if (self.attacking["right"] or self.attacking["left"])  and (animation_manager.current_animation_name != "attacking_jumping"):
                    animation_manager.changeAnimation("attacking_jumping")
    def updateShotsInfo(self, scroll, bullets_list, bullets_speed, bullets_size, particles_list, particles_per_shot):
        """
            Actualiza los datos para disparar, y dispara en caso de que las condiciones esten dadas
        """
        if (self.attacking["right"] or self.attacking["left"]) and (self.current_shot_iter == self.cadencia):
            self.attack(scroll, bullets_list, bullets_speed, bullets_size, particles_list, particles_per_shot)
            self.current_shot_iter = 0

        elif not (self.attacking["right"] or self.attacking["left"]):
            self.current_shot_iter = self.cadencia

        elif self.current_shot_iter != self.cadencia:
            self.current_shot_iter += 1
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
    def generateJumpSound(self, fadeout):
        """
            Reproduce el efecto de salto
        """
        self.jump_sound.play().fadeout(fadeout)
    def jump(self, jump_force):
        """
            Actualiza el momentum del personaje para que "salte" siempre y cuando las condiciones de salto esten dadas
        """
        if self.jump_count <= 1:
            if self.jump_count == 0 and self.in_floor:
                self.y_momentum = jump_force
                self.jump_count += 1
                self.in_floor = False
                self.generateJumpSound(500)

            elif self.jump_count == 1:
                self.y_momentum = jump_force*2
                self.jump_count += 1
    def render(self, surface, scroll):
        """
            Renderiza al personaje
        """
        current_index  =   self.animation_manager.current_animation_index
        current_sprite = self.animation_manager.current_animation_list[current_index]
        if self.last_direction == "left":
            current_sprite = pygame.transform.flip(current_sprite, True, False)
        surface.blit(current_sprite, [ self.rect.x - scroll[0], self.rect.y - scroll[1]])
    def updateLastDirection(self):
        """
            Actualiza el atributo "last_direction" dependiendo de las condiciones
        """
        if (self.moving_left and self.attacking["left"]) or (self.attacking["left"] and self.moving_right) or (self.moving_left and (not self.attacking["right"])) or (self.attacking["left"] and (not self.moving_right)):
            self.last_direction = "left"
        elif (self.moving_right and self.attacking["right"]) or (self.attacking["right"] and self.moving_left) or (self.moving_right and (not self.attacking["left"])) or (self.attacking["right"] and (not self.moving_left)):
            self.last_direction = "right"
class Bullet:
    """
        Clase creada para el mantenimiento de las posiciones de las balas
    """
    def __init__(self, initial_pos,  move, size):
        self.position   = initial_pos
        self.move       = move
        self.size       = size
    def updatePosition(self):
        """
        Actualiza la posicion de la bala self usando el atributo move
        """
        self.position[0] += self.move[0]
        self.position[1] += self.move[1]
    def render(self, surface):
        """
            Renderiza la imagen de la bala en "surface"
        """
        pygame.draw.rect(surface,  (100,100,100), [self.position[0], self.position[1], self.size[0], self.size[1]])
class Particle:
    """
        Clase creada para el mantenimiento de las particulas
    """
    def __init__(self, position, size, color, move, size_change, move_change, color_change, is_colider) -> None:
        self.size           = size
        self.color          = color
        self.move_count     = move
        self.size_change    = size_change
        self.move_change    = move_change
        self.color_change   = color_change
        self.rect           = pygame.Rect([position[0], position[1], size, size])
        self.is_colider     = is_colider
    def update(self, cell_list):
        """
            Mueve la bala y corrige colisiones en caso de haberlas, actualiza el tamanyo de la particula, actualiza el atributo move_count 
            el cual define la cantidad de pixeles que la particula se mueve por iteracion. Ademas, actualiza el color 
        """
        self.move(cell_list)
        self.updateSize()
        self.updateMoveCount()
        self.updateColor()
    def updateMoveCount(self):
        """
            Actualiza la cantidad de movimiento que se le aplica a la particula por iteracion
        """
        self.move_count[0] += self.move_change[0]
        self.move_count[1] += self.move_change[1]
    def updateSize(self):
        """
            Actualiza el tamanyo de la particula
        """
        self.size -= self.size_change
    def updateColor(self):
        """
            Actualiza el color de la particula
        """
        self.color[0] += self.color_change[0]
        self.color[1] += self.color_change[1]
        self.color[2] += self.color_change[2]
        if len([i for i in self.color if (i < 0 or i > 255)]) > 0:
            for color in self.color:
                if (color < 0) :
                    self.color[self.color.index(color)] = 0
                elif (color > 255):
                    self.color[self.color.index(color)] = 255
    def move(self, cell_list):
        """
            Aplica movimiento sobre la particula y corrige las potenciales colisiones en caso de que la particula lo amerite
        """
        self.rect.x += self.move_count[0]
        if self.is_colider:
            for cell in colisionTest(self.rect, cell_list):
                if self.move_count[0] > 0:
                    self.rect.right = cell.left
                else:
                    self.rect.left = cell.right

        self.rect.y += self.move_count[1]
        if self.is_colider:
            for cell in colisionTest(self.rect, cell_list):
                if self.move_count[1] > 0:
                    self.rect.bottom = cell.top
                else:
                    self.rect.top = cell.bottom
    def render(self, surface, scroll):
        """
            Renderiza la particula
        """
        pygame.draw.circle(surface, self.color, [self.rect.x - scroll[0], self.rect.y  - scroll[1]], self.size)
class BackgroundRect:
    """
        Clase creada para la administracion de rectangulos de fondo
    """
    def __init__(self, color, rect, scroll_proportion) -> None:
        self.color = color
        self.rect = rect
        self.scroll_proportion = scroll_proportion
    def render(self, surface, scroll):
        rect_pos = [self.rect.x - (scroll[0] * self.scroll_proportion), self.rect.y - (scroll[1] * self.scroll_proportion)]
        pygame.draw.rect(surface, self.color, [rect_pos[0], rect_pos[1], self.rect.width, self.rect.height])



def generateBackgroundRects(levels, columnas, capas, initial_pos, space_diff, rect_size, rect_color):
    """
        Funcion diseniada para crear los rectangulos del fondo. Rectorna la lista de rectangulos y la posicion media de toda la decoracion
    """
    initial_x, initial_y = initial_pos
    rects = [[] for i in range(columnas+1)]
    for a in range(1,levels+1):
        for i in range(0, columnas):
            color           =   rect_color.copy()
            scroll_propor       = 0.1
            for a in range(1, capas+1):
                color[1]            += ((155)//capas)
                initial_pos[0] += space_diff 
                scroll_propor       +=  0.1
                curr_rect           = pygame.Rect([initial_pos[0],initial_pos[1],rect_size[0], rect_size[1]])
                rect                = BackgroundRect([value for key,value in color.items() ],curr_rect, scroll_propor)
                rects[i].append(rect)
        initial_pos[0] = initial_x 
        initial_pos[1] += 200
    middle =initial_pos[0]  + 600
    return rects, middle
def updateBullets(bullets_list, cell_list, surface_size, scroll, particles):
    """
        Actualiza la posicion de las balas, y elimina aquellas que ya no sean renderizables, que esten colisionando con algo o 
        cuyo alcance haya terminado. Ademas genera las particulas pertinentes en caso de que la bala colisione y siga siendo visible
    """
    copy_list = bullets_list.copy()
    for bullet in copy_list:
        if  (surface_size[0] < bullet.position[0]) or (bullet.position[0] < 0):
            bullets_list.remove(bullet)
        else:
            last_bullet_pos = [bullet.position[0] + scroll[0], bullet.position[1] + scroll[1]]
            bullet.updatePosition()
            colisions = colisionTest(pygame.Rect([bullet.position[0] + scroll[0], bullet.position[1] + scroll[1], bullet.size[0], bullet.size[1]]), cell_list)
            if len(colisions) > 0:
                bullets_list.remove(bullet)
                colied_tile = colisions[0]
                for i in range(1,10):
                    particle_initial_pos    =  [colied_tile.right if last_bullet_pos[0] > colied_tile.right else colied_tile.left, last_bullet_pos[1]]
                    particle_size           = 3
                    particle_color          = [100,100,100].copy()
                    particle_move           =   [randint(-2,2),randint(-1,1)].copy() 
                    particle_size_change    =   0.1
                    particle_move_change    = [0,0.1]
                    particle_color_change   = [0,0,0]
                    new_particle            = Particle(
                        particle_initial_pos,
                        particle_size, 
                        particle_color, 
                        particle_move, 
                        particle_size_change, 
                        particle_move_change, 
                        particle_color_change, 
                        False)
                    particles.append(new_particle)
            else:
                for i in range(1,3):
                    particle_initial_pos    = [bullet.position[0] + scroll[0], bullet.position[1] + scroll[1]].copy()
                    particle_size           = 3
                    particle_color          = [100,100,100].copy()
                    particle_move           =   [0,1].copy() if i == 1 else [0,-1]
                    particle_size_change    =   0.1
                    particle_move_change    = [0,0]
                    particle_color_change   = [0,0,0]
                    new_particle            = Particle(
                        particle_initial_pos,
                        particle_size, 
                        particle_color, 
                        particle_move, 
                        particle_size_change, 
                        particle_move_change, 
                        particle_color_change, 
                        False)
                    particles.append(new_particle)
def renderBullets(bullets_list, surface):
    for bullet in bullets_list:
        bullet.render(surface)
def eventHandling(eventList, player,EXIT, jump_force, particles):
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
                if (player.jump_count == 0) and (player.in_floor):
                    for i in range(1,randint(3,8)):
                        particle_pos            = [player.rect.x + (player.width//2), player.rect.bottom-5].copy()
                        particle_size           = 5
                        particle_color          = [100,100,100].copy()
                        particle_move           = [randint(-5,5), -3].copy()
                        particle_size_change    = 0.1
                        if particle_move[0] < 0:
                            particle_move_change = [0.1, 0.3]
                        elif particle_move[0] == 0:
                            particle_move_change = [0, 0.3]
                        else:
                            particle_move_change = [-0.1, 0.3]
                        particle_color_change = [0,0,0]
                        new_particle = Particle(particle_pos, particle_size, particle_color, particle_move, particle_size_change, particle_move_change, particle_color_change,True)
                        particles.append(new_particle)
                player.jump(jump_force)
    return EXIT
def animationDict(size, colorkey, animationSetPath, has_alpha):
    """
        Retorna el diccionario de animaciones obtenido del animationSetPath, las animaciones deben seguir el formato: animationType -> animationDirection -> Animations
    """
    animations = {}
    try:
        for animationType in os.listdir(animationSetPath):
            animations[animationType]   = []
            animationSet                = os.listdir(f"{animationSetPath}/{animationType}/animation")
            index                       = 0
            counter                     = 1
            while (counter != len(animationSet) + 1)  :
                if str(counter) in animationSet[index]:
                    sprite_path = f"{animationSetPath}/{animationType}/animation/{animationSet[index]}"
                    sprite      = getImageReady(sprite_path,size, colorkey, has_alpha )
                    animations[animationType].append(sprite)
                    index       = 0
                    counter     += 1
                else:
                    index += 1
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
                    current_line.append(char)
            map_.append(current_line)
    return map_
def printMap(tile_size, cells, color_change, surface, map_, scroll, space_char, player_pos):
    """
        Imprime el mapa, correspondiente a map_, ademas agrega las celdas a la lista "cells" en caso de que no esten ya ahi.
    """
    curr_x = 0
    curr_y = 0
    no_cells_loaded = len(cells) == 0
    player_pos = getScrolledPosition(scroll, player_pos)
    for line in map_:
        for char in line:
            if char != space_char:
                char        = int(char)
                tile        = pygame.Rect([curr_x - scroll[0], curr_y - scroll[1], tile_size[0], tile_size[1]]) 
                if watchable(tile, surface, player_pos, 1):
                    pygame.draw.rect(surface, (char * color_change,50,50), tile)
                if no_cells_loaded:
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
def renderBackgroundRects(player_rect, middle_decoration, background_rects, surface, scroll):
    """
        Renderiza los rectangulos de fondo. Recordar que los rectangulos estan almacenados en una lista, 
        y organizados en listas (dentro de la primera lista) que representan las 
        columnas de arriba a abajo. Esto es necesario para casos en los que 
        el personaje este por detras de cierto punto en donde las capas empiezan a 
        solaparse por el orden de renderizado. Si se almacenan en columas, 
        unicamente basta con saber cuando el personaje se encuentre en aquel punto y renderizar las columnas en sentido contrario
    """
    if (player_rect.x) >= middle_decoration:
        for columna in background_rects:
            for capa in columna:
                capa.render(surface, scroll)
    else:
        len_ = len(background_rects)
        for i in range(0,len_):
            for  capa in background_rects[len_ - i -1 ]:
                capa.render(surface, scroll)
def renderParticles(particle_list, surface, scroll):
    """
        Renderiza las particulas vigentes
    """
    for particle in particle_list:
        particle.render(surface, scroll)
def updateParticles(particle_list, cell_list):
    """
        Actualiza el estado de todas las particulas vigentes
    """
    for particle in particle_list.copy():
        particle.update(cell_list)
        if particle.size < 1:
            particle_list.remove(particle)
def watchable(rect, surface, player_pos, surface_peace):
    """
        Funcion creada para determinar si algun rectangulo es visible por el personaje
    """
    surface_size = [surface.get_width(), surface.get_height()]
    return ((rect.right > (player_pos[0] - (surface_size[0]//surface_peace))) and (rect.left < (player_pos[0] + (surface_size[0]//surface_peace))) and (rect.top < (player_pos[1] + (surface_size[1]//surface_peace))) and (rect.bottom > (player_pos[1] - (surface_size[1]//surface_peace))))