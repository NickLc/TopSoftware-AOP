# ---------------------------
# Importacion de los módulos
# ---------------------------

import pygame
from pygame.locals import *
from pygame import mixer
from functools import wraps
import os
import sys
import random

screen = 0
explosion_screen_time = 0
coord = (0,0)
# -----------
# Constantes
# -----------

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 690
BRICK_WIDTH = 40
BRICK_HEIGHT = 20

IMG_DIR = "imagenes"

# ------------------------------
# Clases y Funciones utilizadas
# ------------------------------


def load_image(nombre, dir_imagen, alpha=False):
    # Encontramos la ruta completa de la imagen
    ruta = os.path.join(dir_imagen, nombre)
    try:
        image = pygame.image.load(ruta)
    except:
        print("Error, no se puede cargar la imagen: " + ruta)
        sys.exit(1)
    # Comprobar si la imagen tiene "canal alpha" (como los png)
    if alpha is True:
        image = image.convert_alpha()
    else:
        image = image.convert()
    return image


# -----------------------------------------------
# Creamos los sprites (clases) de los objetos del juego:


class Pelota(pygame.sprite.Sprite):
    "La bola y su comportamiento en la pantalla"

    def __init__(self, weight, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image("bola.png", IMG_DIR, alpha=True)
        self.image = pygame.transform.scale(self.image, (weight, height))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.centery = SCREEN_HEIGHT / 2
        self.speed = [7, 7]

    def update(self):
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed[0] = -self.speed[0]
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.speed[1] = -self.speed[1]
        self.rect.move_ip((self.speed[0], self.speed[1]))

    def colision(self, objetivo):
        if self.rect.colliderect(objetivo.rect):
            self.speed[1] = -self.speed[1]


class Paleta(pygame.sprite.Sprite):
    "Define el comportamiento de las paletas de ambos jugadores"

    def __init__(self, weight, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image("paleta.png", IMG_DIR, alpha=True)
        self.image = pygame.transform.scale(self.image, (weight, height))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.centery = SCREEN_HEIGHT - SCREEN_HEIGHT / 10
        self.speed = 5

    def humano(self):
        # Controlar que la paleta no salga de la pantalla
        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        elif self.rect.left <= 0:
            self.rect.left = 0


class Ladrillo(pygame.sprite.Sprite):
    "La bola y su comportamiento en la pantalla"

    def __init__(self, material, posx, posy):
        pygame.sprite.Sprite.__init__(self)
        self.material = material
        self.image = load_image(f"{material}.jpg", IMG_DIR, alpha=True)
        self.image = pygame.transform.scale(self.image, (BRICK_WIDTH, BRICK_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.centerx = posx
        self.rect.centery = posy
        self.eliminado = False
        self.sound_effect = mixer.Sound(f'sound_effect/{material}.wav')
        self.image_effect = load_image(f"{material}_break.jpg", IMG_DIR, alpha=True)
        self.image_effect = pygame.transform.scale(self.image_effect, (BRICK_WIDTH*2, BRICK_HEIGHT*4))

    def colision(self, objetivo):
        if self.rect.colliderect(objetivo.rect):
            self.eliminado = True


# ------------------------------
# Aplicando aspectos al sonido
# ------------------------------


def display_sonido(orig_func):
    @wraps(orig_func)
    def wrapper(*args, **kwargs):
        global explosion_screen_time
        args[1].sound_effect.play()
        #screen.blit(args[1].image_effect, args[1].rect)         
        explosion_screen_time = 5 
        orig_func(*args, **kwargs)

    return wrapper


@display_sonido
def ladrillodestruction(ladrillos, lad):
    lad.eliminado=True


def colision_ladrillos(bola, ladrillos):
    global coord
    for lad in ladrillos:
        if lad.eliminado == False:
            bola.colision(lad)  # La bola cambia de direccion
            if lad.rect.colliderect(bola):            
                ladrillodestruction(ladrillos, lad)  # Se elimina el ladrillo
                print(lad.material)
                coord = lad.rect

    return ladrillos


def create_matrix_position_ladrillos():

    matrix = []
    pos_init = [40, 40]

    for fil in range(9):
        for col in range(9):
            pos = [
                pos_init[0] + col * BRICK_WIDTH,
                pos_init[1] + fil * BRICK_HEIGHT
            ]
            matrix.append(pos)

    return matrix


def create_ladrillos(material, matrix, cant):
    pos = []
    for p in range(cant):
        index = random.randint(0, len(matrix) - 1)
        pos.append(matrix[index])
        matrix.remove(matrix[index])

    ladrillos = [Ladrillo(material, p[0], p[1]) for p in pos]
    return ladrillos


# ------------------------------
# Funcion principal del juego
# ------------------------------


def main():    
    pygame.init()
    # creamos la ventana y le indicamos un titulo:  
    global screen    
    global explosion_screen_time
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Break Brick")

    # cargamos los objetos
    fondo = load_image("fondo.jpg", IMG_DIR, alpha=False)
    fondo = pygame.transform.scale(fondo, (SCREEN_WIDTH, SCREEN_HEIGHT))

    #Poner la musica del juego
    mixer.music.load('sound_effect/music.mp3')
    mixer.music.play(-1)

    matrix = create_matrix_position_ladrillos()
    ladrillos = create_ladrillos('ladrillo', matrix, 20)
    ladrillos += create_ladrillos('vidrio', matrix, 10)
    ladrillos += create_ladrillos('metal', matrix, 10)

    bola = Pelota(30, 30)
    jugador1 = Paleta(60, 15)

    clock = pygame.time.Clock()
    pygame.key.set_repeat(1, 25)  # Activa repeticion de teclas
    
    # el bucle principal del juego
    while True:
        clock.tick(60)

        # Actualizamos los obejos en pantalla
        jugador1.humano()
        bola.update()
        # Comprobamos si colisionan los objetos
        bola.colision(jugador1)


        # Posibles entradas del teclado y mouse
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

            elif event.type == pygame.KEYDOWN:
                if event.key == K_LEFT:
                    jugador1.rect.centerx -= jugador1.speed
                elif event.key == K_RIGHT:
                    jugador1.rect.centerx += jugador1.speed
                elif event.key == K_SPACE:  #salir juego
                    sys.exit(0)

        #actualizamos la pantalla
        screen.blit(fondo, (0, 0))
        screen.blit(bola.image, bola.rect)
        screen.blit(jugador1.image, jugador1.rect)

        if len(ladrillos) != 0:
            ladrillos = colision_ladrillos(bola, ladrillos)
            for lad in ladrillos: 
                if lad.eliminado == False:               
                    screen.blit(lad.image, lad.rect)    

        if explosion_screen_time > 0 :
            explosion_screen_time+=-1
            #cambias el ladrillo por su efecto      
            #Agregar aqui el bucle
            screen.blit(lad.image_effect, coord) 
            #clock.tick(7)
            print(explosion_screen_time)


        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()

        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed[0] = -self.speed[0]
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.speed[1] = -self.speed[1]
        self.rect.move_ip((self.speed[0], self.speed[1]))

    def colision(self, objetivo):
        if self.rect.colliderect(objetivo.rect):
            self.speed[1] = -self.speed[1]


class Paleta(pygame.sprite.Sprite):
    "Define el comportamiento de las paletas de ambos jugadores"

    def __init__(self, weight, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image("paleta.png", IMG_DIR, alpha=True)
        self.image = pygame.transform.scale(self.image, (weight, height))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.centery = SCREEN_HEIGHT - SCREEN_HEIGHT / 10
        self.speed = 5

    def humano(self):
        # Controlar que la paleta no salga de la pantalla
        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        elif self.rect.left <= 0:
            self.rect.left = 0


class Ladrillo(pygame.sprite.Sprite):
    "La bola y su comportamiento en la pantalla"

    def __init__(self, material, posx, posy):
        pygame.sprite.Sprite.__init__(self)
        self.material = material
        self.image = load_image(f"{material}.jpg", IMG_DIR, alpha=True)
        self.image = pygame.transform.scale(self.image, (BRICK_WIDTH, BRICK_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.centerx = posx
        self.rect.centery = posy
        self.eliminado = False
        self.sound_effect = mixer.Sound(f'sound_effect/{material}.wav')
        self.image_effect = load_image(f"{material}_break.jpg", IMG_DIR, alpha=True)
        self.image_effect = pygame.transform.scale(self.image_effect, (BRICK_WIDTH*2, BRICK_HEIGHT*4))

    def colision(self, objetivo):
        if self.rect.colliderect(objetivo.rect):
            self.eliminado = True


# ------------------------------
# Aplicando aspectos al sonido
# ------------------------------


def display_sonido(orig_func):
    @wraps(orig_func)
    def wrapper(*args, **kwargs):
        args.sound_effect.play()

    return


@display_sonido
def colliderect(*args, **kwargs):
    return super(self).colliderect(*args, **kwargs)


def colision_ladrillos(bola, ladrillos):
    for lad in ladrillos:
        bola.colision(lad)  # La bola cambia de direccion
        if lad.rect.colliderect(bola):
            ladrillos.remove(lad)  # Se elimina el ladrillo
            print(lad.material)

    return ladrillos


def create_matrix_position_ladrillos():

    matrix = []
    pos_init = [40, 40]

    for fil in range(9):
        for col in range(9):
            pos = [
                pos_init[0] + col * BRICK_WIDTH,
                pos_init[1] + fil * BRICK_HEIGHT
            ]
            matrix.append(pos)

    return matrix


def create_ladrillos(material, matrix, cant):
    pos = []
    for p in range(cant):
        index = random.randint(0, len(matrix) - 1)
        pos.append(matrix[index])
        matrix.remove(matrix[index])

    ladrillos = [Ladrillo(material, p[0], p[1]) for p in pos]
    return ladrillos


# ------------------------------
# Funcion principal del juego
# ------------------------------


def main():
    pygame.init()
    # creamos la ventana y le indicamos un titulo:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Break Brick")

    # cargamos los objetos
    fondo = load_image("fondo.jpg", IMG_DIR, alpha=False)
    fondo = pygame.transform.scale(fondo, (SCREEN_WIDTH, SCREEN_HEIGHT))

    #Poner la musica del juego
    mixer.music.load('sound_effect/music.mp3')
    mixer.music.play(-1)

    matrix = create_matrix_position_ladrillos()
    ladrillos = create_ladrillos('ladrillo', matrix, 20)
    ladrillos += create_ladrillos('vidrio', matrix, 10)
    ladrillos += create_ladrillos('metal', matrix, 10)

    bola = Pelota(30, 30)
    jugador1 = Paleta(60, 15)

    clock = pygame.time.Clock()
    pygame.key.set_repeat(1, 25)  # Activa repeticion de teclas

    # el bucle principal del juego
    while True:
        clock.tick(60)

        # Actualizamos los obejos en pantalla
        jugador1.humano()
        bola.update()
        # Comprobamos si colisionan los objetos
        bola.colision(jugador1)


        # Posibles entradas del teclado y mouse
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

            elif event.type == pygame.KEYDOWN:
                if event.key == K_LEFT:
                    jugador1.rect.centerx -= jugador1.speed
                elif event.key == K_RIGHT:
                    jugador1.rect.centerx += jugador1.speed
                elif event.key == K_SPACE:  #salir juego
                    sys.exit(0)

        #actualizamos la pantalla
        screen.blit(fondo, (0, 0))
        screen.blit(bola.image, bola.rect)
        screen.blit(jugador1.image, jugador1.rect)

        if len(ladrillos) != 0:
            #ladrillos = colision_ladrillos(bola, ladrillos)
            for lad in ladrillos:
                bola.colision(lad)  # La bola cambia de direccion
                #mostrar los ladrillos
                screen.blit(lad.image, lad.rect) 
                
                if lad.rect.colliderect(bola):
                    lad.sound_effect.play()
                    #cambias el ladrillo por su efecto      
                    #Agregar aqui el bucle
                    screen.blit(lad.image_effect, lad.rect) 
                    clock.tick(7)
                    lad.eliminado = True
                
                # Eliminar al ladrillo que colisiono
                if lad.eliminado:
                    ladrillos.remove(lad)


        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
