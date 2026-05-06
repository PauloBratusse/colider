import random
import math

############################################################################
# ========================= MATH UTILS =====================================
############################################################################

def dot(u, v):
    return sum(u[i]*v[i] for i in range(3))

def cross(u, v):
    return [
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    ]

def sub(a, b):
    return [a[i] - b[i] for i in range(3)]

def normalize(v):
    mag = math.sqrt(sum(x*x for x in v))
    if mag == 0:
        return [0,0,0]
    return [x/mag for x in v]

def reflect(v, n):
    d = dot(v, n)
    return [v[i] - 2*d*n[i] for i in range(3)]

############################################################################
# ========================= GEOMETRY =======================================
############################################################################

def intersect_segment_triangle(P0, P1, A, B, C):
    EPS = 1e-8
    
    dir = sub(P1, P0)
    edge1 = sub(B, A)
    edge2 = sub(C, A)
    
    h = cross(dir, edge2)
    a = dot(edge1, h)

    if -EPS < a < EPS:
        return False

    f = 1.0 / a
    s = sub(P0, A)
    u = f * dot(s, h)

    if u < 0.0 or u > 1.0:
        return False

    q = cross(s, edge1)
    v = f * dot(dir, q)

    if v < 0.0 or u + v > 1.0:
        return False

    t = f * dot(edge2, q)

    return 0.0 <= t <= 1.0

############################################################################
# ========================= MESH ===========================================
############################################################################

class Mesh:
    def __init__(self, triangles):
        self.triangles = triangles

def check_collision_mesh(P0, P1, mesh):
    for (A, B, C) in mesh.triangles:
        if intersect_segment_triangle(P0, P1, A, B, C):
            return True, (A, B, C)
    return False, None

############################################################################
# ========================= PARTICLE =======================================
############################################################################

class Particle:
    def __init__(self,x,y,z,vx,vy,vz,r=0.0):
        self.x = x 
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.radius = r

    def step(self, delta, mesh):
        x_temp = self.x + self.vx * delta
        y_temp = self.y + self.vy * delta
        z_temp = self.z + self.vz * delta

        P0 = [self.x, self.y, self.z]
        P1 = [x_temp, y_temp, z_temp]

        collided, tri = check_collision_mesh(P0, P1, mesh)

        if collided:
            A, B, C = tri

            edge1 = sub(B, A)
            edge2 = sub(C, A)

            normal = cross(edge1, edge2)
            normal = normalize(normal)

            v = [self.vx, self.vy, self.vz]
            v_ref = reflect(v, normal)

            self.vx, self.vy, self.vz = v_ref

            # mantém posição (simples)
        else:
            self.x = x_temp
            self.y = y_temp
            self.z = z_temp
        
    def position(self):
        return self.x,self.y,self.z

############################################################################
# ========================= INIT ===========================================
############################################################################

def init_sim(quantity, vel_col=1):
    particles = []
    for q in range(quantity):
        x = random.random()
        y = random.random()
        z = random.random()

        vx = (random.random()*vel_col) * random.choice([-1,1])
        vy = (random.random()*vel_col) * random.choice([-1,1])
        vz = (random.random()*vel_col) * random.choice([-1,1])

        particles.append(Particle(x,y,z,vx,vy,vz))

    return particles

############################################################################
# ========================= SAMPLE MESH ====================================
############################################################################

def create_box_mesh(xf, yf, zf):
    A = [0,0,0]
    B = [xf,0,0]
    C = [xf,yf,0]
    D = [0,yf,0]

    E = [0,0,zf]
    F = [xf,0,zf]
    G = [xf,yf,zf]
    H = [0,yf,zf]

    triangles = [
        (A,B,C),(A,C,D),
        (E,F,G),(E,G,H),
        (A,B,F),(A,F,E),
        (B,C,G),(B,G,F),
        (C,D,H),(C,H,G),
        (D,A,E),(D,E,H)
    ]

    return Mesh(triangles)

############################################################################
# ========================= SIMULATION =====================================
############################################################################

def temporal_step(delta, particle_index, particles, mesh):
    particles[particle_index].step(delta, mesh)
    return particles[particle_index].position()

def save_output(passo,id,x,y,z,quantity):
    with open('colider_output.txt','w+') as f:
        f.write(f'quantity;{quantity}\n')
        for a in range(len(x)):
            f.write(str(passo[a])+";"+str(id[a])+";"+str(x[a])+";"+str(y[a])+";"+str(z[a])+'\n')

############################################################################
# ========================= MAIN ===========================================
############################################################################

def main():

    quantity = 50
    delta = 0.01
    steps = 500
    vel_col = 1.0

    # caixa como exemplo (mas pode trocar por qualquer mesh)
    mesh = create_box_mesh(1,1,1)

    particles = init_sim(quantity, vel_col)

    x = []
    y = []
    z = []
    id = []
    passo = []

    print("Running simulation...")

    for step in range(steps):
        for p in range(quantity):
            x_now,y_now,z_now = temporal_step(delta,p,particles,mesh)
            x.append(x_now)
            y.append(y_now)
            z.append(z_now)
            id.append(p)
            passo.append(step)

    save_output(passo,id,x,y,z,quantity)

    print("Simulation finished!")

############################################################################

if __name__ == "__main__":
    main()

