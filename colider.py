import random
import os

############################################################################
class Particle:
    def __init__(self,x,y,vx,vy,r):
        self.x = x 
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = r

    def step(self,delta,frontier):
        x_temp = self.x + self.vx*delta
        y_temp = self.y + self.vy*delta
        left,right,bottom,top,condition = frontier.check_collision(x_temp,y_temp)
        if condition:
            if left: 
                self.x = abs(x_temp)
                self.vx *= -1

            if right:
                delta_x = x_temp - frontier.xf
                self.x = frontier.xf - delta_x
                self.vx *= -1

            if bottom: 
                self.y = abs(y_temp)
                self.vy *= -1

            if top:
                delta_y = y_temp - frontier.yf
                self.y = frontier.yf - delta_y
                self.vy *= -1
     
        else:
          self.x = x_temp
          self.y = y_temp



    def position(self):
        return self.x,self.y
############################################################################

class Frontier:
    def __init__(self,lenght,width):
        self.xi = 0
        self.xf = lenght
        self.yi = 0
        self.yf = width


    def check_collision(self, x, y):
        collide_left   = (x <= self.xi)
        collide_right  = (x >= self.xf)
        collide_bottom = (y <= self.yi)
        collide_top    = (y >= self.yf)
        collide_any = collide_left or collide_right or collide_bottom or collide_top

        return collide_left, collide_right, collide_bottom, collide_top, collide_any

############################################################################
def init_sim(quantity,cx=1,cy=1,vel_col=1):
    particles = []
    frontier = Frontier(cx,cy)
    colx = 1
    coly = 1
    for q in range(quantity):
        x = random.random()
        y = random.random()
        if random.random() > 0.5:
            colx = -1
        if random.random() > 0.5:
            coly = -1
        vx = (random.random()*vel_col) * colx
        vy = (random.random()*vel_col) * coly 
        particle_a = Particle(x,y,vx,vy)
        particles.append(particle_a)
    return particles,frontier


def temporal_step(delta,particle_index,particles,frontier):
    particles[particle_index].step(delta,frontier)
    x_now,y_now = particles[particle_index].position()
    return x_now,y_now 

def save_output(passo,id,x,y,quantity):
    with open('colider_output.txt','w+') as f:
        f.write(f'quantity;{quantity}\n')
        for a in range(len(x)):
            f.write(str(passo[a])+";"+str(id[a])+";"+str(x[a])+";"+str(y[a])+'\n')
#-------------------------------------------------------------------------------------------------------------------------------

def main():


    quantity = None  
    delta = None
    steps = None

    x = []
    y = []
    id = []
    passo = [] 
    with open("colider.cfg", 'r') as f:
        for line in f:
            line = line.strip() 
            if not line or line.startswith("#"):
                continue
            var, value = line.split("=")
            var = var.strip().lower()
            value = value.strip()
            if var == "particles_quantity":
                quantity = int(value)
            elif var == "delta":
                delta = float(value)
            elif var == "steps":
                steps = int(value)
            elif var == "box_width":
                width = float(value)
            elif var == "box_lenght":
                lenght = float(value)
            elif var == "velocity_coeficient":
                vel_col = float(value)
        if delta is None or steps is None or quantity is None:
            return print("Core config not present, exit script")

    print('Starting Simulation with:')
    print(f'{quantity} Particles')
    print(f'{delta} Delta t')
    print(f'{steps} steps')

    particles,frontier = init_sim(quantity,lenght,width,vel_col)
    for step in range(steps):
       for p in range(quantity):
        x_now,y_now = temporal_step(delta,p,particles,frontier)
        x.append(x_now)
        y.append(y_now)
        id.append(p)
        passo.append(step)
    save_output(passo,id,x,y,quantity)

main()
