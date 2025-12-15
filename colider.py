import random
############################################################################
class Particle:
    def __init__(self,x,y,vx,vy):
        self.x = x 
        self.y = y
        self.vx = vx
        self.vy = vy

    def step(self,delta,frontier):
        x_temp = self.x + self.vx*delta
        y_temp = self.y + self.vy*delta
        left,right,bottom,top,condition = frontier.check_collision(x_temp,y_temp)
        if condition:
            if left: 
                self.x = abs(x_temp)
                self.vx *= -1
                print("ping left")
            if right:
                delta_x = x_temp - frontier.xf
                self.x = frontier.xf - delta_x
                self.vx *= -1
                print("ping right")
            if bottom: 
                self.y = abs(y_temp)
                self.vy *= -1
                print("ping bot")
            if top:
                delta_y = y_temp - frontier.yf
                self.y = frontier.yf - delta_y
                self.vy *= -1
                print("ping top")
            
        else:
          self.x = x_temp
          self.y = y_temp



    def position(self):
        print(self.x,self.y)
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




def init_sim(quantity,cx,cy):
    particles = []
    frontier = Frontier(cx,cy)
    for q in range(quantity):
        x = random.random()
        y = random.random()
        vx = (random.random()/10) - 0.05
        vy = (random.random()/10) - 0.05
        particle_a = Particle(x,y,vx,vy)
        particles.append(particle_a)
    return particles,frontier


def temporal_step(delta,particle_index,particles,frontier):
    particles[particle_index].step(delta,frontier)
    #particles[particle_index].position()
#-------------------------------------------------------------------------------------------------------------------------------
    
quantity = 2  
delta = 1
steps = 3000
particles,frontier = init_sim(quantity,1,1)


for step in range(steps):
    temporal_step(delta,0,particles,frontier)

