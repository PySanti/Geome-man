from typing import final
import pygame
from pygame.locals import *
import os
from random import choice, randint


class Player:
    """
        Clase creada para la administracion del personaje y datos del arma
    """
    def __init__(self, steps_sound, player_speed, jump_sound, animation_manager, size, cadencia_de_arma, attack_sound_path):
        self.width                  =   size[0]
        self.height                 =   size[1]
        self.rect                   =   pygame.Rect([1000,350, self.width, self.height])
        self.y_momentum             =   0
        self.x_momentum             =   0
        self.moving_right           =   False
        self.moving_left            =   False
        self.in_floor               =   False
        self.jump_count             =   0
        self.shot_sound_runing      =   False
        self.attacking              =   {"left" : False, "right" : False}
        self.speed                  =   player_speed
        self.jump_sound             =   jump_sound
        self.animation_manager      =   animation_manager
        self.amoo                   =   1000
        self.cadencia               =   cadencia_de_arma
        self.attack_sound           =   pygame.mixer.Sound(attack_sound_path)
        self.look_back_couter       =   0
        self.look_back_max_counter  =   None
        self.last_direction         =   "right"
        self.live                   =   100
        self.max_live               = self.live
        self.horizontal_move_counter  =   [0,0]
        self.current_horizontal_move_index = 0
        self.dashTimer              =   0
        self.dashIterationLimit     = 20
        self.score                  = 0
        self.energy_bar_particle_generation_timer = 0
    def updateDashTimer(self, dashTimerLimit):
        self.dashTimer += 1
        if self.dashTimer >= dashTimerLimit:
            self.dashTimer = dashTimerLimit
    def startendHorizontalMoveCounter(self, dashTimerLimit, particles, dash_force):
        """
            Funcion principal en la administraacion del dash_counter

            Cuando se mueve hacia la derecha se llama a checkStatus() quien modifica el valor player.current_horizontal_move_index y en caso 
            de que el player.current_horizontal_move_index sea diferente de la direccion a la que se esta moviendo (0 == izquierda, 1 == derecha), checkDashStatus() 
            resetea el conteo del horizontal_move_counter[] y lo mismo para el caso contrario. Por otro lado, startendHorizontalMoveCounter() comienza el conteo en caso de 
            que el indice sea diferente de 0.

            Por otro lado, updateDashCounter aumenta el valor del contador para la direccion actual en caso de que el valor del contador sea diferente 0. Despues, cuando se 
            pulse por segunda vez el boton de la direccion actual, se comprueba si el contador esta en un rango de 0 a 15 iteraciones y si el dashTimer es igual a limite 
        """
        if self.horizontal_move_counter[self.current_horizontal_move_index] == 0:
            self.horizontal_move_counter[self.current_horizontal_move_index] = 1
        else:
            if (0 <= self.horizontal_move_counter[self.current_horizontal_move_index] <= self.dashIterationLimit) and (self.dashTimer == dashTimerLimit):
                self.activateDash(particles, dash_force)
                self.dashTimer = 0
            self.horizontal_move_counter[self.current_horizontal_move_index] = 0
    def activateDash(self, particles, dash_force):
        dash_direction = "right" if self.current_horizontal_move_index == 1 else "left"
        self.x_momentum += dash_force if dash_direction == "right" else -dash_force

        initial_particle_pos = [self.rect.centerx, self.rect.centery]
        initial_size = 5
        for i in range(10):
            particles.append(Particle(initial_particle_pos, initial_size, [255,255,255], [randint(-5, -1), randint(-20,20)/5], 0.1, [0,0], [0,0,0], False))
            initial_particle_pos[0] -= 10 if dash_direction == "right" else -10
    def checkDashStatus(self, move_direction, dashTimerLimit, particles, dash_force):
        # 0 ==  izquierda, 1 ==  derecha
        if move_direction == "right":
            if self.current_horizontal_move_index == 0:
                self.horizontal_move_counter[0] = 0
            self.current_horizontal_move_index = 1
            self.startendHorizontalMoveCounter(dashTimerLimit, particles, dash_force)
        elif move_direction == "left":
            if self.current_horizontal_move_index == 1:
                self.horizontal_move_counter[1] = 0
            self.current_horizontal_move_index = 0
            self.startendHorizontalMoveCounter(dashTimerLimit, particles, dash_force)
        else:
            print("Error ... ")
    def updateDashCounter(self):
        if self.horizontal_move_counter[self.current_horizontal_move_index] > 0:
            self.horizontal_move_counter[self.current_horizontal_move_index] += 1
            if  self.horizontal_move_counter[self.current_horizontal_move_index] >= self.dashIterationLimit:
                self.horizontal_move_counter[self.current_horizontal_move_index] = 0
    def updateState(self, gravity, max_gravity, cell_list, x_momentum_decrease):
        """
            Actualiza la posicion del personaje llamando al metodo move, actualiza el momentum (para ello hace uso de los parametros "gravity" y "max_gravity" ).
            Ademas, actualiza las animaciones a traves del metodo animationCheck y updateAnimation, los sonidos a traves del metodo updateSounds.

        """
        player_movement = [0, 0]
        if self.moving_right:
            player_movement[0] += self.speed
        elif self.moving_left:
            player_movement[0] -= self.speed

        if self.x_momentum < 0:
            self.x_momentum += x_momentum_decrease 
        elif self.x_momentum > 0:
            self.x_momentum += -x_momentum_decrease
        if abs(self.x_momentum) <= x_momentum_decrease:
            self.x_momentum = 0
        player_movement[0] += self.x_momentum


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
        self.updateLastDirection()
    def generateAttackSound(self, volume, fadeout):
        """
            Reproduce el sonido de ataque
        """
        try:
            self.attack_sound.set_volume(volume)
            self.attack_sound.play().fadeout(fadeout)
        except AttributeError:
            pass
    def attack(self, scroll, bullets_list, bullets_speed, bullets_size, particles, particles_per_shot, player_particle_shot_color):
        """
            Administra las acciones necesarias al disparar
        """
        if self.amoo > 0:
            bulletInitialPos    = getScrolledPosition(scroll, [self.rect.right + 10 if self.attacking["right"] else self.rect.left - 10, self.rect.bottom - self.height//2])
            new_bullet          = Bullet(bulletInitialPos,  [bullets_speed if self.attacking["right"] else -bullets_speed, 0], bullets_size, "player", None, (255,50,0))
            bullets_list.append(new_bullet)
            self.amoo -= 1
            self.generateAttackSound(volume=0.1, fadeout=2000)


            particles_color         =  player_particle_shot_color
            particles_move          =  [0,-1] 
            particles_move_change   =   [0, 0.1] 
            particles_color_change =  [0,5,0]
            particles_size_change  =  0.05
            particles_size          =   3
            move_range              =  10

            for i in range(1, particles_per_shot+1):
                particle_pos = [self.rect.x + self.width,self.rect.y + (self.height//2) ] if self.attacking["right"] else [self.rect.x ,self.rect.y + (self.height//2) ] 
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

            particles_color         =  player_particle_shot_color
            particles_color_change =  [0,10,0]
            particles_size_change  =  0.1
            particles_size          =   3
            move_range              =  10
            for i in range(1, randint(5,10)):
                particle_pos =  [self.rect.centerx - randint(-5,5), self.rect.centery - randint(-5,5)]
                particles_move          =  [randint(-1,1),randint(-1,1)] 
                particles_move_change   =   [0, randint(-1,1)/10] 
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
        if ("stand" in animation_manager.current_animation_name) and (not "attack" in animation_manager.current_animation_name) or (not (self.moving()) and (not (self.attacking["right"] or self.attacking["left"]))):
            if (animation_manager.current_animation_index == (len(animation_manager.current_animation_list) -1 )) :
                if (animation_manager.current_animation_name == "stand_1") :
                    random_ = randint(1,10)
                    if  random_ in range(5,11):
                        animation_manager.changeAnimation("stand_3" if random_ == 5 else "stand_2")
                        if random_ == 5:
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
        if (abs(self.y_momentum) > 3) and ("attack" not in animation_manager.current_animation_name):
            if self.y_momentum < 0:
                if animation_manager.current_animation_name != "jump_momentum_negativo":
                    animation_manager.changeAnimation("jump_momentum_negativo")
                elif (animation_manager.current_animation_index == ((len(animation_manager.current_animation_list)) - 2)):
                    animation_manager.current_animation_frame = 0
            else:
                if animation_manager.current_animation_name != "jump_momentum_positivo":
                    animation_manager.changeAnimation("jump_momentum_positivo")
                elif (animation_manager.current_animation_index == (len(animation_manager.current_animation_list) - 2)):
                    animation_manager.current_animation_frame = 0
        if ((self.attacking["right"] or self.attacking["left"]) and (self.amoo > 0)) and (not (self.moving())):
            if animation_manager.current_animation_name != "attacking_stand":
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
                if (self.attacking["right"] and self.moving_left) or (self.attacking["left"] and self.moving_right):
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
    def updateShotsInfo(self, scroll, bullets_list, bullets_speed, bullets_size, particles_list, particles_per_shot, player_particle_shot_color):
        """
            Actualiza los datos para disparar, y dispara en caso de que las condiciones esten dadas
        """
        if (self.attacking["right"] or self.attacking["left"]) and (self.current_shot_iter == self.cadencia):
            self.attack(scroll, bullets_list, bullets_speed, bullets_size, particles_list, particles_per_shot, player_particle_shot_color)
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
    def render(self, surface, scroll, dashTimerLimit):
        """
            Renderiza al personaje
        """
        current_index  =   self.animation_manager.current_animation_index
        current_sprite = self.animation_manager.current_animation_list[current_index]
        if self.last_direction == "left":
            current_sprite = pygame.transform.flip(current_sprite, True, False)
        surface.blit(current_sprite, [ self.rect.x - scroll[0], self.rect.y - scroll[1]])

        live_bar_piece = 3
        self.renderLiveBar(surface, scroll, live_bar_piece)
        energy_bar_piece = (dashTimerLimit/self.max_live)*live_bar_piece
        self.renderEnergyBar(surface, scroll, self.dashTimer/energy_bar_piece)
    def updateLastDirection(self):
        """
            Actualiza el atributo "last_direction" dependiendo de las condiciones
        """
        if (self.moving_left and self.attacking["left"]) or (self.attacking["left"] and self.moving_right) or (self.moving_left and (not self.attacking["right"])) or (self.attacking["left"] and (not self.moving_right)):
            self.last_direction = "left"
        if (self.moving_right and self.attacking["right"]) or (self.attacking["right"] and self.moving_left) or (self.moving_right and (not self.attacking["left"])) or (self.attacking["right"] and (not self.moving_left)):
            self.last_direction = "right"
    def renderLiveBar(self, surface, scroll, live_bar_piece):
        live_color = generateLiveColor(self.max_live, self.live)
        if self.last_direction == "right":
            pygame.draw.rect(surface, live_color, [self.rect.x + 15   - scroll[0], self.rect.y - 3 - scroll[1], self.live/live_bar_piece, 3])
        else:
            pygame.draw.rect(surface, live_color, [self.rect.x + 15   - scroll[0], self.rect.y - 3 - scroll[1], self.live/live_bar_piece, 3])
    def renderEnergyBar(self, surface, scroll, energy_bar_len):
        bar_color = [255,255,255]
        if self.last_direction == "right":
            pygame.draw.rect(surface, bar_color, [self.rect.x + 15   - scroll[0], self.rect.y - 7 - scroll[1], energy_bar_len, 3])
        else:
            pygame.draw.rect(surface, bar_color, [self.rect.x + 15   - scroll[0], self.rect.y - 7 - scroll[1], energy_bar_len, 3])
class Bullet:
    """
        Clase creada para el mantenimiento de las posiciones de las balas
    """
    def __init__(self, initial_pos,  move, size, owner, time_live, color):
        self.position   = initial_pos
        self.move       = move
        self.size       = size
        self.owner      =   owner
        self.move_change=   [0,0]
        self.time_live  =   time_live
        self.current_iter = 0
        self.color      =   color
    def updatePosition(self):
        """
        Actualiza la posicion de la bala self usando el atributo move
        """
        self.position[0] += self.move[0]
        self.position[1] += self.move[1]
        if self.time_live != None: # recordar que a las balas del player se les asigna un tiempo de vida None ya que estas no tienen tiempo de vida :|
            self.current_iter += 1
    def render(self, surface):
        """
            Renderiza la imagen de la bala en "surface"
        """ 
        pygame.draw.circle(surface,  self.color, self.position, self.size[0] if self.owner == "enemy" else self.size[1])
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
class Enemy:
    def __init__(self, position, attack_timing, size, color, live):
        self.width          = size[0]
        self.height         = size[1]
        self.rect           = pygame.Rect([position[0], position[1], self.width, self.height])
        self.attack_timing  = attack_timing
        self.max_attack_timing = attack_timing
        self.color          = color
        self.in_floor       =   False
        self.y_momentum     = 0
        self.live           =   live
        self.max_live       =   self.live
    def update(self, gravity, max_gravity, cell_list, player, bullet_list, bullet_size, scroll,  bullet_alcance, bullet_lowest_speed, bullet_smooth):
        """
            Actualiza la altura y el momentum en y del enemigo. Ademas, ataca en caso de que las condiciones esten dadas
        """
        enemy_movement = [0,0]
        self.y_momentum += gravity
        if self.y_momentum > max_gravity:
            self.y_momentum = max_gravity
        enemy_movement[1] += self.y_momentum
        colisions = self.move(enemy_movement, cell_list)
        if colisions["bottom"]:
            self.in_floor = True
            self.y_momentum = 0
        else:
            self.in_floor = False
        if self.attack_timing == 0:
            self.attack_timing = self.max_attack_timing
            self.attack(player, bullet_list, bullet_size, scroll, bullet_alcance, bullet_lowest_speed, bullet_smooth)
        else:
            self.attack_timing -= 1
    def attack(self, player, bullet_list, bullet_size, scroll, bullet_alcance, bullet_lowest_speed, bullet_smooth):
        """
            Dispara al personaje
        """
        # referencia de los catetos : personaje
        initial_pos     = [self.rect.x - scroll[0] + (self.width//2), self.rect.y - scroll[1] + (self.height//2)]
        bullet_speed = bulletEnemySpeed(getScrolledPosition(scroll, [player.rect.x, player.rect.y]), initial_pos, bullet_smooth)
        if (len([i for i in bullet_speed if (abs(i)) <= bullet_lowest_speed]) <= 1):
            new_bullet = Bullet(initial_pos, bullet_speed,bullet_size, "enemy",bullet_alcance, (100,100,100))
            bullet_list.append(new_bullet)
    def move(self, enemy_movement, cell_list) -> dict:
        """
            Mueve al enemigo usando el enemy_movement recibido por parametro, retorna un diccionario que simboliza las direcciones en las cuales
            ha habido una colision, ademas de arreglar dichas colisiones
        """
        colisions = {
            "right" : False,
            "left"  : False,
            "top"  : False,
            "bottom"  : False,
        }
        self.rect.x += enemy_movement[0]
        for cell in colisionTest(self.rect, cell_list):
            if enemy_movement[0] > 0:
                self.rect.right = cell.left
                colisions["right"] = True
            elif enemy_movement[0] < 0:
                self.rect.left = cell.right
                colisions["left"] = True
        # movemos el personaje en y, buscamos colisiones y corregimos
        self.rect.y += enemy_movement[1]
        for cell in colisionTest(self.rect, cell_list):
            if enemy_movement[1] > 0:
                self.rect.bottom = cell.top
                colisions["bottom"] = True
            elif enemy_movement[1] < 0:
                self.rect.top = cell.bottom
                colisions["top"] = True
        return colisions
    def render(self, surface, scroll):
        """
            Renderiza al personaje
        """
        pygame.draw.rect(surface, self.color, [self.rect.x - scroll[0], self.rect.y - scroll[1], self.width, self.height])
        self.renderLiveBar(surface, scroll)
    def renderLiveBar(self, surface, scroll):
        live_color = generateLiveColor(self.max_live, self.live)
        pygame.draw.rect(surface, live_color, [self.rect.x - ((self.live-self.width)//2) - scroll[0], self.rect.y - 5 - scroll[1], self.live, 3])



def generateBackgroundRects():
    """
        Funcion diseniada para crear los rectangulos del fondo. Rectorna la lista de rectangulos y la posicion media de toda la decoracion
    """
    initial_color       =   {1:30,2:30,3:30}
    initial_position    =   [-100,500]
    size                =   [5000,200]
    capas               =   500
    capas_spacediff     =   15  
    rects               =   []
    scroll_proportion   =   0.3
    final_color = [i[1] for i in initial_color.items()]
    for i in range(1,capas+1):
        new_rect = BackgroundRect([a for i,a in initial_color.items()], pygame.Rect(initial_position[0], initial_position[1], size[0], size[1] ),scroll_proportion)
        initial_position[0] -= capas_spacediff
        initial_position[1] -= capas_spacediff 
        initial_color[1] += 3
        initial_color[1] = 255 if initial_color[1] >=255 else initial_color[1]
#        scroll_proportion += (0.9/capas)
        rects.append(new_rect)

    initial_position  = [200,0]
    space_diff  =   [50,50]
    size        = [100,100]
    scroll_proportion  = 0.1
    initial_color       =   {1:30,2:30,3:30}
    for a in range(10):
        for i in range(10):
            new_rect = BackgroundRect([i[1] for i in initial_color.items()], pygame.Rect([initial_position[0],initial_position[1],size[0],size[1]]),scroll_proportion)
            rects.append(new_rect)
            scroll_proportion += 0.1
            initial_color[1] += 20 if a%2 == 0 else -20
            initial_position[0] += space_diff[0]
            initial_position[1] += space_diff[1]
        space_diff  =   [50,50]
        size        = [100,100]
        scroll_proportion  = 0.1
        initial_color       =   {1:30,2:30,3:30}
    return rects, final_color
def updateBullets(bullets_list, cell_list, surface_size, scroll, particles, enemy_list, bullet_power, player, bullet_move_change, player_particle_shot_color):
    """
        Actualiza la posicion de las balas, y elimina aquellas que ya no sean renderizables, que esten colisionando con algo o 
        cuyo alcance haya terminado. Ademas genera las particulas pertinentes en caso de que la bala colisione y siga siendo visible
    """
    copy_list = bullets_list.copy()
    for bullet in copy_list:
        if  ((surface_size[0] < bullet.position[0]) or (bullet.position[0] < 0)) and (bullet.owner == "player"):
            bullets_list.remove(bullet)
        else:
            last_bullet_pos = [bullet.position[0] + scroll[0], bullet.position[1] + scroll[1]]
            bullet.updatePosition()
            bullet_real_rect = pygame.Rect([bullet.position[0] + scroll[0], bullet.position[1] + scroll[1], bullet.size[0], bullet.size[1]])
            if bullet.owner == "player":
                checkPlayerBullet(bullet_real_rect, cell_list, bullets_list, bullet, last_bullet_pos, particles, bullet_power, enemy_list, scroll, player_particle_shot_color, player)
            elif bullet.owner == "enemy":
                updateEnemyBulletsMoveChange(bullet, bullet_move_change)
                checkEnemyBullets(bullet, scroll, particles, player, bullets_list, bullet_real_rect)
def renderBullets(bullets_list, surface):
    for bullet in bullets_list:
        bullet.render(surface)
def eventHandling(eventList, player,EXIT, jump_force, particles, dashTimerLimit, dash_force):
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
                if event.type == KEYDOWN:
                    # 0 ==  izquierda, 1 ==  derecha
                    player.checkDashStatus("right", dashTimerLimit, particles, dash_force)
                player.moving_right = (event.type == KEYDOWN)
            if event.key == K_a:
                if event.type == KEYDOWN:
                    player.checkDashStatus("left", dashTimerLimit, particles, dash_force)
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
def renderBackgroundRects(background_rects, surface, scroll):
    """
        Renderiza los rectangulos de fondo. 
    """
    for capa in background_rects:
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
def renderEnemys(enemy_list, scroll, surface):
    for enemy in enemy_list:
        enemy.render(surface, scroll)
def updateEnemys(enemy_list, gravity, max_gravity, cell_list, player, bullet_list, generation_timing, bullet_size, scroll, bullet_alcance, bullet_lowest_speed, enemy_shooting_timing_range, live_enemy_range, bullet_smooth):
    for enemy in enemy_list.copy():
        enemy.update(gravity, max_gravity, cell_list, player, bullet_list, bullet_size, scroll, bullet_alcance, bullet_lowest_speed, bullet_smooth)


    if (randint(1,generation_timing) == 1) and (len(enemy_list)  == 0) and (len(cell_list) > 0):
        size                = [randint(30,40),randint(50,70)]
        initial_position    = [choice(cell_list).x, 0]
        attack_timing       = randint(enemy_shooting_timing_range[0], enemy_shooting_timing_range[1])
        color               = (100,100,100)
        live                =   randint(live_enemy_range[0], live_enemy_range[1]) if player.score == 0 else player.score/5
        enemy_list.append(Enemy(initial_position, attack_timing , size, color, live))
def bulletEnemySpeed(player_pos, enemy_pos, bullet_smooth):
    """
        Retorna el punto de conexion del triangulo limite proporcional  creado por la mira, y el arma. Necesario para establecer una velocidad fija y 
        absoluta de las balas independiente de la posicion de la mira
    """
    bullet_speed = [(player_pos[0] - enemy_pos[0])/bullet_smooth, (player_pos[1] + randint(-50,50) - enemy_pos[1])/bullet_smooth]
    return bullet_speed
def makePlayerShotCellColision(cell_colisions, last_bullet_pos, particles, particle_colision_color):
    colied_tile = cell_colisions[0]
    for i in range(1,10):
        particle_initial_pos    =  [colied_tile.right if last_bullet_pos[0] > colied_tile.right else colied_tile.left, last_bullet_pos[1]]
        new_particle            = Particle(position= particle_initial_pos,size=3,color = particle_colision_color.copy(), move=[randint(-2,2), randint(-1,1)].copy(), size_change=0.1, move_change=[0,0.1], color_change=[0,1,0], is_colider=False)
        particles.append(new_particle)
def checkPlayerBullet(bullet_real_rect, cell_list, bullets_list, bullet, last_bullet_pos, particles, bullet_power, enemy_list, scroll, player_particle_shot_color, player):
    cell_colisions = colisionTest(bullet_real_rect, cell_list)
    if len(cell_colisions) > 0:
        bullets_list.remove(bullet)
        makePlayerShotCellColision(cell_colisions, last_bullet_pos, particles, player_particle_shot_color)
    else:
        if not (checkPlayerShotEnemyColision(enemy_list, bullet_real_rect, bullets_list, bullet_power, last_bullet_pos, particles, bullet, player)):
            bullet.position[1] += randint(-5,5)
            for i in range(1,4):
                particle_initial_pos    = [bullet.position[0] + scroll[0], bullet.position[1] + scroll[1]].copy()
                particle_move = [0,0]
                particle_move[0] = 2 if bullet.move[0] < 0 else -2
                particle_move[1] = randint(-1,0)
                new_particle            = Particle(particle_initial_pos,size=2, color=player_particle_shot_color.copy(), move=particle_move.copy(), size_change=0.05, move_change=[0,0.1], color_change=[0,1,0], is_colider=True)
                particles.append(new_particle)
def checkPlayerShotEnemyColision(enemy_list, bullet_rect, bullets_list, bullet_power, last_bullet_pos, particles, bullet, player):
    enemy_rect_list = [enemy.rect for enemy in enemy_list]
    enemys_colisions = colisionTest(bullet_rect, enemy_rect_list)
    if len(enemys_colisions) > 0:
        bullets_list.remove(bullet)
        colied_enemy_rect = enemys_colisions[0]
        colied_enemy = enemy_list[enemy_rect_list.index(colied_enemy_rect)]
        colied_enemy.live-= bullet_power
        if colied_enemy.live > 0:
            for i in range(1,10):
                particle_initial_pos    =  [colied_enemy_rect.right if last_bullet_pos[0] > colied_enemy_rect.right else colied_enemy_rect.left, last_bullet_pos[1]]
                new_particle            = Particle(position= particle_initial_pos,size=3,color = [100,100,100].copy(), move=[randint(-2,2), randint(-1,1)].copy(), size_change=0.1, move_change=[0,0.1], color_change=[0,0,0], is_colider=False)
                particles.append(new_particle)
        else:
            enemy_list.remove(colied_enemy)
            player.score += 100
            for i in range(1,10):
                particle_initial_pos    = [colied_enemy.rect.x + colied_enemy.width//2 , colied_enemy.rect.y + colied_enemy.height//2 ].copy()
                particle_move           =   [bullet.move[0]//6 + randint(-3,3), bullet.move[1]//6 + randint(-3,3)]
                new_particle            = Particle(
                    particle_initial_pos,
                    size=3,
                    color=[100,100,100].copy(), 
                    move=particle_move.copy(), size_change=0.05, move_change=[0,0.1], color_change=[0,0,0], is_colider=True)
                particles.append(new_particle)
        return True
    else:
        return False
def checkEnemyBullets(bullet, scroll, particles, player, bullets_list, bullet_real_rect):
    def generateExplosion(particles_count, particles_initial_size):
        for i in range(1,particles_count+1):
            particle_initial_pos    = [bullet.position[0] + scroll[0], bullet.position[1] + scroll[1]].copy()
            particle_move           =   [randint(-5,5), randint(-5,3)]
            new_particle            = Particle(
                particle_initial_pos,
                size=particles_initial_size, 
                color=[100,100,100].copy(), 
                move=particle_move.copy(), size_change=0.05, move_change=[0,0.1], color_change=[0,0,0], is_colider=False)
            particles.append(new_particle)
    if bullet.current_iter >= bullet.time_live:
        generateExplosion(particles_count=30,particles_initial_size=4)
        bullets_list.remove(bullet)
    else:
        if player.rect.colliderect(bullet_real_rect):
            generateExplosion(particles_count=30, particles_initial_size=4)
            bullets_list.remove(bullet)
        else:
            generateExplosion(particles_count=1, particles_initial_size=2)
    
    if  (bullet.current_iter >= bullet.time_live) or (player.rect.colliderect(bullet_real_rect)):
        space = [0,0]
        real_bullet_pos = [bullet.position[0] + scroll[0],bullet.position[1] + scroll[1]]
        space[0] = ((real_bullet_pos[0] + bullet.size[0]/2) - (player.rect.x + player.width/2))
        space[1] = ((real_bullet_pos[1] + bullet.size[0]/2) - (player.rect.y + player.height/2))*2
        limit = 100
        explosion_force = []
        for i in space:
            explosion_force.append((-abs(i) + limit)/5 if abs(i) <= limit else 0)
        explosion_force[0] = -explosion_force[0] if space[0] > 0  else explosion_force[0]
        explosion_force[1] = -explosion_force[1] if space[1] > 0  else explosion_force[1]
        player.x_momentum += explosion_force[0]
        player.y_momentum += explosion_force[1]
        player.live -= abs(explosion_force[0])
def updateEnemyBulletsMoveChange(bullet, bullet_move_change):
    bullet.move[0] += bullet.move_change[0]
    bullet.move[1] += bullet.move_change[1]
    bullet.move_change[0] = bullet_move_change if randint(1,2) ==  1 else -bullet_move_change
def generateLiveColor(max_live, current_live):
    live_color = None
    if  max_live/2 < current_live:
        live_color = (0,255,0)
    elif max_live/2 > current_live > max_live/3:
        live_color = (255, 100,0)
    else:
        live_color = (255,0,0)
    return live_color
def generateEnergyChargeParticles(player, particles, dash_timer_limit, energybar_particle_generation_timer, energybar_particle_generation_timer_LIMIT ):
    move_speed  =   5
    if (player.dashTimer == dash_timer_limit):
        if player.energy_bar_particle_generation_timer == energybar_particle_generation_timer_LIMIT:
            player.energy_bar_particle_generation_timer = 0
            particles.append(Particle([player.rect.centerx , player.rect.centery], 3, [200,200,200],[randint(-move_speed,move_speed)/5, randint(-move_speed, move_speed)/10], 0.02,[randint(-2,2)/50,randint(-2,2)/50], [1,1,1], False  ))
        else:
            player.energy_bar_particle_generation_timer += 1
