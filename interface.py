# -*- coding: utf-8 -*-
import pygame
from pygame.locals import * #(QUIT, KEYDOWN, K_ESCAPE, K_r)

import Box2D  # The main library
# Box2D.b2 maps Box2D.b2Vec2 to vec2 (and so on)
from Box2D.b2 import * # (world, edgeShape, polygonShape, circleShape, staticBody, dynamicBody)

import numpy as np
import pickle
import sys
import random 
import matplotlib.pyplot as plt
# --- constants ---
# Box2D deals with meters, but we want to display pixels,
# so define a conversion factor:
PPM = 15.0  # pixels per meter
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 480

# --- pygame setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Perceived Bounciness')
clock = pygame.time.Clock()

# --- pybox2d world setup ---
# Create the world
world = world(gravity=(0, -20), doSleep=True)

# Create a static body to hold the ground shape
x1 = 0.0
vertice1 = (x1, 4)
vertice2 = (x1, 0)

x2 = np.random.uniform(12, 20)
vertice3 = (x2, 0)
vertice4 = (x2, np.random.uniform(2.4, 3.6))
# vertice4 = (np.random.uniform(5, 60), np.random.uniform(0.5, 3))

x3 = np.random.uniform(25, 35)
vertice5 = (x3, 0)
vertice6 = (x3, np.random.uniform(1.4, 3.2))
vertice7 = ((x2+x3)/2.0, np.random.uniform(2.7, 3.9))

x4 = np.random.uniform(40, 50)
vertice8 = (x4, 0)
vertice9 = (x4, np.random.uniform(0.7, 2.1))
vertice10 = ((x3+x4)/2.0, np.random.uniform(1.6, 2.9))

x5 = 60.0
vertice11 = (x5, 0)
vertice12 = ((x4+x5)/2.0, np.random.uniform(0.3, 1.6))

ground_body1 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice1, vertice2, vertice3, vertice4]))
ground_body2 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice4, vertice3, vertice5, vertice6, vertice7]))
ground_body3 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice6, vertice5, vertice8, vertice9, vertice10]))
ground_body4 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice9, vertice8, vertice11, vertice12]))


# Create a couple dynamic bodies
org_position_circle = (5, 10)
# body = world.CreateDynamicBody(position=org_position_circle)
org_restitution_circle = 1.0
org_radius_circle = 0.7
org_density_circle = 1
# circle = body.CreateCircleFixture(radius=org_radius_circle, density=org_density_circle, restitution=org_restitution_circle)

# body = world.CreateDynamicBody(position=(10, 10), angle=0)
# box = body.CreatePolygonFixture(box=(1, 1), density=20, restitution=1.0)

colors = {
    staticBody: (50, 145, 100, 255),
    dynamicBody: (100, 100, 100, 255),
}

# Let's play with extending the shape classes to draw for us.
def my_draw_polygon(polygon, body, fixture):
    vertices = [(body.transform * v) * PPM for v in polygon.vertices]
    vertices = [(v[0], SCREEN_HEIGHT - v[1]) for v in vertices]
    pygame.draw.polygon(screen, colors[body.type], vertices)
polygonShape.draw = my_draw_polygon

def my_draw_circle(circle, body, fixture):
    position = body.transform * circle.pos * PPM
    position = (position[0], SCREEN_HEIGHT - position[1])
    pygame.draw.circle(screen, colors[body.type], [int(
        x) for x in position], int(circle.radius * PPM))
    # Note: Python 3.x will enforce that pygame get the integers it requests,
    #       and it will not convert from float.
circleShape.draw = my_draw_circle

# --- main game loop ---
# iter_cnt = 0
num_trials = 1
running = True
time_left = 0
# stop_criteria = 0.0000001
eps = 0.6
# R = 1.0
R0 = 0.8
seq_A_played = False
seq_B_played = False
return_enable = False
user_input = -1

current_seq = 'C'

eps_cnt = 1
eps_step_size = 0.6
eps_rep = 6
eps_stop_crt = 0.01

all_eps_lst = [eps]
user_input_lst = []
physical_lst = []
step_size_lst = []

text_box_color = (0,0,0,0)

init_v_x = np.random.uniform(0,5)
init_v_y = -np.random.uniform(0,10)

# Mode = 0 --> display physical motion
# Mode = 1 --> display modified motion
mode = [0,1]
random.shuffle(mode)
mode_idx = 0
if mode[0] == 0:
    physical_lst.append(0)
else:
    physical_lst.append(1)

# initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
myfont = pygame.font.SysFont("arial", 23)

def display_eps():
    global myfont
    global screen
    global eps
    global eps_step_size

    # -- Text Output --
    # label_change = myfont.render("Press r to change eps.", 1, (255,255,255))
    # screen.blit(label_change, (200, 5))
    label_eps = myfont.render("Eps: "+str(eps)+ "     Step Size: "+ str(eps_step_size) , 1, (255,255,255))
    screen.blit(label_eps, (25, 50))


def display_mode():
    global myfont
    global screen
    global mode
    global mode_idx
    # -- Text Output --
    label_mode = myfont.render("Mode: "+str(mode[mode_idx]), 1, (0,255,255))
    screen.blit(label_mode, (20, 30))

def display_seq():
    global myfont
    global screen
    global current_seq
    # -- Text Output --
    label_mode = myfont.render("Playing Animation "+current_seq, 1, (120,230,120))
    screen.blit(label_mode, (SCREEN_WIDTH/2 - 80, 60))

def display_welcome():
    global myfont
    global screen

    title_font = pygame.font.SysFont("arial", 50)
    welcome = myfont.render("Welcome to the Bouncie Study", 1, (255,255,255))
    screen.blit(welcome, (SCREEN_WIDTH/2 - 120, 18))

    label_ins1 = myfont.render("In each trial, you'll be shown 2 animation of a bouncy ball", 1, (255,255,255))
    screen.blit(label_ins1, (SCREEN_WIDTH/2 - 210, 58))

    label_ins2 = myfont.render("You'll be asked to choose the more physical animation after them playing", 1, (255,255,255))
    screen.blit(label_ins2, (SCREEN_WIDTH/2 - 260, 78))

    label_ins3 = myfont.render("Play/replay animation: Press key A for animation A | key B for animation B", 1, (255,255,255))
    screen.blit(label_ins3, (SCREEN_WIDTH/2 - 260, 98))

    label_ins4 = title_font.render("Have Fun!", 0, (255,255,255))
    screen.blit(label_ins4, (SCREEN_WIDTH/2 - 90, 128))

def display_instruction():
    global myfont
    global screen
    # -- Text Output --
    label_ins2 = myfont.render("Play/replay animation: Press key A for animation A | key B for animation B", 1, (200,200,200))
    screen.blit(label_ins2, (SCREEN_WIDTH/2 - 260, 38))

def display_choice():
    global myfont
    global screen
    global user_input
    # -- Text Output --
    label_ins2 = myfont.render("Please choose between 1 and 2. ", 1, (255,255,255))
    screen.blit(label_ins2, (SCREEN_WIDTH/2 - 200, 66))
    label_ins3 = myfont.render("1 - Animation A looks more physical.", 1, (255,255,255))
    screen.blit(label_ins3, (SCREEN_WIDTH/2 - 175, 90))
    label_ins4 = myfont.render("2 - Animation B looks more physical.", 1, (255,255,255))
    screen.blit(label_ins4, (SCREEN_WIDTH/2 - 175, 110))
    if user_input < 0:
        label_user = myfont.render("Your answer: ", 1, (255,255,255))
    else:
        label_user = myfont.render("Your answer: "+str(user_input+1) + "  Hit enter when you're ready", 1, (255,255,255))
    screen.blit(label_user, (SCREEN_WIDTH/2 - 175, 140))


def throw_ball_A():
    global time_left
    global org_position_circle
    global org_radius_circle
    global org_density_circle
    global org_restitution_circle
    global seq_A_played
    global current_seq
    global mode_idx
    global init_v_x
    global init_v_y

    if time_left == 0: # and (not seq_A_played):
        # world.DestroyBody(world.bodies[3])
        # world.DestroyBody(world.bodies[2])
        # world.DestroyBody(world.bodies[1])
        # world.DestroyBody(world.bodies[0])
        # # Create a static body to hold the ground shape
        # x1 = 0.0
        # vertice1 = (x1, 4)
        # vertice2 = (x1, 0)
        
        # x2 = np.random.uniform(12, 20)
        # vertice3 = (x2, 0)
        # vertice4 = (x2, np.random.uniform(2.4, 3.6))
        # # vertice4 = (np.random.uniform(5, 60), np.random.uniform(0.5, 3))
        
        # x3 = np.random.uniform(25, 35)
        # vertice5 = (x3, 0)
        # vertice6 = (x3, np.random.uniform(1.4, 3.2))
        # vertice7 = ((x2+x3)/2.0, np.random.uniform(2.7, 3.9))
        
        # x4 = np.random.uniform(40, 50)
        # vertice8 = (x4, 0)
        # vertice9 = (x4, np.random.uniform(0.7, 2.1))
        # vertice10 = ((x3+x4)/2.0, np.random.uniform(1.6, 2.9))
        
        # x5 = 60.0
        # vertice11 = (x5, 0)
        # vertice12 = ((x4+x5)/2.0, np.random.uniform(0.3, 1.6))
        
        # ground_body1 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice1, vertice2, vertice3, vertice4]))
        # ground_body2 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice4, vertice3, vertice5, vertice6, vertice7]))
        # ground_body3 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice6, vertice5, vertice8, vertice9, vertice10]))
        # ground_body4 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice9, vertice8, vertice11, vertice12]))

        mode_idx = 0
        time_left = 600
        body = world.CreateDynamicBody(position=org_position_circle)
        body.linearVelocity = (init_v_x, init_v_y)
        circle = body.CreateCircleFixture(radius=org_radius_circle, density=org_density_circle, restitution=org_restitution_circle)
        seq_A_played = True
        current_seq = 'A'


def throw_ball_B():
    global time_left
    global org_position_circle
    global org_radius_circle
    global org_density_circle
    global org_restitution_circle
    global seq_B_played
    global current_seq
    global mode_idx
    global init_v_x
    global init_v_y

    if time_left == 0: # and (not seq_B_played):
        # world.DestroyBody(world.bodies[3])
        # world.DestroyBody(world.bodies[2])
        # world.DestroyBody(world.bodies[1])
        # world.DestroyBody(world.bodies[0])
        # # Create a static body to hold the ground shape
        # x1 = 0.0
        # vertice1 = (x1, 4)
        # vertice2 = (x1, 0)
        
        # x2 = np.random.uniform(12, 20)
        # vertice3 = (x2, 0)
        # vertice4 = (x2, np.random.uniform(2.4, 3.6))
        # # vertice4 = (np.random.uniform(5, 60), np.random.uniform(0.5, 3))
        
        # x3 = np.random.uniform(25, 35)
        # vertice5 = (x3, 0)
        # vertice6 = (x3, np.random.uniform(1.4, 3.2))
        # vertice7 = ((x2+x3)/2.0, np.random.uniform(2.7, 3.9))
        
        # x4 = np.random.uniform(40, 50)
        # vertice8 = (x4, 0)
        # vertice9 = (x4, np.random.uniform(0.7, 2.1))
        # vertice10 = ((x3+x4)/2.0, np.random.uniform(1.6, 2.9))
        
        # x5 = 60.0
        # vertice11 = (x5, 0)
        # vertice12 = ((x4+x5)/2.0, np.random.uniform(0.3, 1.6))
        
        # ground_body1 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice1, vertice2, vertice3, vertice4]))
        # ground_body2 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice4, vertice3, vertice5, vertice6, vertice7]))
        # ground_body3 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice6, vertice5, vertice8, vertice9, vertice10]))
        # ground_body4 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice9, vertice8, vertice11, vertice12]))

        mode_idx = 1
        time_left = 600
        body = world.CreateDynamicBody(position=org_position_circle)
        body.linearVelocity = (init_v_x, init_v_y)
        circle = body.CreateCircleFixture(radius=org_radius_circle, density=org_density_circle, restitution=org_restitution_circle)
        seq_B_played = True  
        current_seq = 'B'    


def countdown():
    global time_left
    if time_left == 0 and len(world.bodies) > 4:
        world.DestroyBody(world.bodies[4])
    if time_left > 0:
        time_left -= 1

def calculate_next_eps():
    global user_input_lst
    global physical_lst
    global eps_rep
    global eps_step_size
    global eps

    err_cnt = 0

    assert len(user_input_lst) == len(physical_lst)
    for i in range(1, eps_rep+1):
        if physical_lst[-i] != user_input_lst[-i]:
            err_cnt += 1

    err_rate = 1.0*err_cnt/eps_rep
    eps_step_size /= 2

    if err_rate > 0.4:
        eps += eps_step_size
    else:
        eps -= eps_step_size

    all_eps_lst.append(eps)

while running:
    screen.fill((0, 0, 0, 0))

    img = pygame.image.load('blue_sky.png')
    img = pygame.transform.scale(img, (SCREEN_WIDTH,SCREEN_HEIGHT))

    screen.blit(img, (0,0))

    text_box = pygame.Surface((SCREEN_WIDTH - 20,160))
    text_box.set_alpha(180)
    text_box.fill((0,0,0))
    screen.blit(text_box,(10,10))

    countdown()
    # display_eps()
    if not seq_A_played and not seq_B_played:
        if num_trials == 1:
            display_welcome()
        else:
            display_instruction()

    if seq_A_played and seq_B_played and time_left == 0:
        display_instruction()
        display_choice()
    elif seq_A_played or seq_B_played:
        if time_left > 0:
            # display_mode()
            display_seq()
        else:
            display_instruction()

    # Check the event queue
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            # The user closed the window or pressed escape
            running = False
        if event.type == KEYDOWN and event.key == K_a:
            print('a')
            throw_ball_A()
        if event.type == KEYDOWN and event.key == K_b:
            print('b')
            throw_ball_B()
        if seq_A_played and seq_B_played and time_left == 0 and event.type == KEYDOWN and event.key == K_1:
            user_input = 0
            return_enable = True
        if seq_A_played and seq_B_played and time_left == 0 and event.type == KEYDOWN and event.key == K_2:
            user_input = 1
            return_enable = True
        if seq_A_played and seq_B_played and time_left == 0 and return_enable and event.type == KEYDOWN and event.key == K_RETURN:
            user_input_lst.append(user_input)

            if eps_cnt >= eps_rep:
                calculate_next_eps()
                if eps_step_size < eps_stop_crt:
                    running = False
                eps_cnt = 1
            else:
                eps_cnt += 1

            print(eps_cnt)

            num_trials = num_trials + 1

            assert len(world.bodies) == 4

            world.DestroyBody(world.bodies[3])
            world.DestroyBody(world.bodies[2])
            world.DestroyBody(world.bodies[1])
            world.DestroyBody(world.bodies[0])
            # Create a static body to hold the ground shape
            x1 = 0.0
            vertice1 = (x1, 4)
            vertice2 = (x1, 0)
            
            x2 = np.random.uniform(12, 20)
            vertice3 = (x2, 0)
            vertice4 = (x2, np.random.uniform(2.4, 3.6))
            # vertice4 = (np.random.uniform(5, 60), np.random.uniform(0.5, 3))
            
            x3 = np.random.uniform(25, 35)
            vertice5 = (x3, 0)
            vertice6 = (x3, np.random.uniform(1.4, 3.2))
            vertice7 = ((x2+x3)/2.0, np.random.uniform(2.7, 3.9))
            
            x4 = np.random.uniform(40, 50)
            vertice8 = (x4, 0)
            vertice9 = (x4, np.random.uniform(0.7, 2.1))
            vertice10 = ((x3+x4)/2.0, np.random.uniform(1.6, 2.9))
            
            x5 = 60.0
            vertice11 = (x5, 0)
            vertice12 = ((x4+x5)/2.0, np.random.uniform(0.3, 1.6))
            
            ground_body1 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice1, vertice2, vertice3, vertice4]))
            ground_body2 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice4, vertice3, vertice5, vertice6, vertice7]))
            ground_body3 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice6, vertice5, vertice8, vertice9, vertice10]))
            ground_body4 = world.CreateStaticBody(position=(0, 0), shapes=polygonShape(vertices=[vertice9, vertice8, vertice11, vertice12]))

            seq_A_played = False
            seq_B_played = False
            return_enable = False
            user_input = -1

            init_v_x = np.random.uniform(0,5)
            init_v_y = -np.random.uniform(0,10)

            mode = [0,1]
            random.shuffle(mode)
            mode_idx = 0
            if mode[0] == 0:
                physical_lst.append(0)
            else:
                physical_lst.append(1)


    if time_left > 0:
        if mode[mode_idx] == 0:
            world.bodies[4].fixtures[0].restitution = R0
        else:
            world.bodies[4].fixtures[0].restitution = np.random.uniform(1-eps, 1+eps)*R0


    # iter_cnt = iter_cnt + 1
    # Draw the world
    for body in world.bodies:
        for fixture in body.fixtures:
            fixture.shape.draw(body, fixture)

    # render trail number
    label = myfont.render("Trial: "+str(num_trials), 1, (255,255,255))
    screen.blit(label, (20, 18))

    # if time_left > 0 and (seq_A_played or seq_B_played):
        # print(world.bodies[1].fixtures[0].restitution)

    # Make Box2D simulate the physics of our world for one step.
    world.Step(TIME_STEP, 10, 10)

    # Flip the screen and try to keep at the target FPS
    pygame.display.flip()
    clock.tick(TARGET_FPS)
    # print(iter_cnt)
    # print(plausible)
    # print(delta_R)
    # print(time_left)
    print(eps_step_size)
pygame.quit()

# Visualization code
def save_all_eps_lst():
    global all_eps_lst

    saving_dict = {'all_eps_lst': all_eps_lst}

    if len(sys.argv) > 1:
        saving_dir = sys.argv[1]
    else:
        saving_dir = 'result.pkl'

    with open(saving_dir, 'wb') as handle:
        pickle.dump(saving_dict, handle)

def visualize_all_eps_lst():
    global all_eps_lst

    num_eps_lst = [x for x in range(1,len(all_eps_lst)+1)]
    threshold_list = [all_eps_lst[-1]]*len(all_eps_lst)

    plt.plot(num_eps_lst, all_eps_lst, 'b-', num_eps_lst, threshold_list, 'y-')
    plt.axis([0, len(all_eps_lst)+1, 0, 0.6])
    plt.xlabel('Experiment Number')
    plt.ylabel('Eps')
    plt.show()

save_all_eps_lst()
visualize_all_eps_lst()

print(physical_lst)
print(user_input_lst)
print('Experiment Finished!')
print(all_eps_lst)