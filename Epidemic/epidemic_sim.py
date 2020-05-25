from pygame.locals import *
import math
import random
from QuadTree import *

#--------------- ADJUSTABLE PARAMETERS -------------------
npeople = 999                   # More than 1000 may make text formatting weird
infection_radius = 20           # Must be smaller than the quads in the quadtree
probability = .2
duration = 1000
mortality = .02
strictness = 0.1
test_percent = .7
strictness_funct = True         # If true, starting strictness is given by strictness, must be nonzero
response = .1                    # Only needs to be specified for strictness funct
#--------------- ADJUSTABLE PARAMETERS -------------------


class Person:
    def __init__(self, x, y, vx, vy, infected, ID):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.infected = infected
        self.neighbors = []
        self.recovered = False
        self.dead = False
        self.quarantined = False
        self.progression = duration  # This can be turned into picking from a gaussian dist
        self.ID = ID
        self.confirmed = False
        self.tested = False
        self.destination = [0, 0]
        self.in_quarantine = False

    def update_pos(self):
        if self.in_quarantine:
            return

        if self.confirmed:
            if abs(self.destination[0] - self.x) < 15 and abs(self.destination[1] - self.y) < 15:
                self.in_quarantine = True
                return
            if abs(self.destination[1] - self.y) < 15:
                self.vx = self.destination[0] - self.x
                self.vx = self.vx/(math.sqrt(self.vx**2 + self.vy**2))
                self.x = self.x + self.vx*15
                return

            self.vx = self.destination[0] - self.x
            self.vy = self.destination[1] - self.y
            self.vx = self.vx/(math.sqrt(self.vx**2 + self.vy**2))
            self.vy = self.vy/(math.sqrt(self.vx**2 + self.vy**2))
            self.x = self.x + self.vx*15
            self.y = self.y + self.vy*15
            return

        if self.x > screen_size[0] or self.x < 0:
            self.vx = -self.vx
        if self.y > screen_size[1] or self.y < 0:
            self.vy = -self.vy
        self.x = self.x + self.vx*.4
        self.y = self.y + self.vy*.4

    def update_vel(self):
        dvx = (random.random()-.5)/2
        dvy = (random.random()-.5)/2
        self.vx = self.vx + dvx
        self.vy = self.vy + dvy
        self.vx = self.vx/(math.sqrt(self.vx**2 + self.vy**2))
        self.vy = self.vy/(math.sqrt(self.vx**2 + self.vy**2))

    def draw_person(self):
        color = (0, 255, 255)
        if self.infected:
            color = (255, 0, 0)
        if self.recovered:
            color = (125, 125, 125)
        if self.dead:
            return
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 2)

    def update_neighbors(self, obj, quad):
        self.neighbors = []
        quadcount = quad.find_quad(obj, quad.treelocs)
        for person in quad.quads[quadcount]:
            distance = math.sqrt((self.x-person.x)**2+(self.y-person.y)**2)
            if distance < infection_radius:
                self.neighbors.append(person)

    def update_health(self):
        if len(self.neighbors) == 0:
            return

        probability = spread_probability * len(self.neighbors)

        if random.random() < probability:
            self.infected = True
            infected.append(person)

    def __eq__(self, other):
        return self.ID == other.ID

    def progress_sickness(self, infected):
        self.progression -= 1
        if self.progression < duration*strictness and self.tested == False and self.progression > 10:
            self.tested = True
            if random.random() < test_percent:
                self.confirmed = True
                self.destination = [screen_size[0]+ 107 + random.random()*215, 395 + random.random()*187]

        if self.progression <= 0:
            if random.random() < mortality:
                self.dead = True
            self.recovered = True
            self.infected = False
            for person in infected:
                if person.ID == self.ID:
                    infected.remove(person)


def sim_analysis(people, data):
    counthealthy = 0
    countinfected = 0
    countremoved = 0
    countdead = 0
    countconfirmed = 0
    for person in people:
        if person.infected:
            countinfected += 1
        elif person.recovered:
            countremoved += 1
        else:
            counthealthy += 1
        if person.dead:
            countdead += 1
        if person.confirmed:
            countconfirmed += 1

    data.append([countremoved/len(people), counthealthy/len(people), countinfected/len(people)])
    data.pop(0)
    ncases = countinfected + countremoved
    nrecovered = countremoved - countdead
    return data, ncases, nrecovered, countdead, counthealthy, countconfirmed


def draw_graph(data):
    x = screen_size[0] + 10
    for list in data:
        y = 50
        height1 = list[0]*100
        height2 = list[1]*100
        height3 = list[2]*100
        if height1 != 0:
            pygame.draw.rect(screen, (125, 125, 125), [x, y, 1, height1])
        if height2 != 0:
            pygame.draw.rect(screen, (0, 0, 255), [x, y+height1, 1, height2])
        if height3 != 0:
            pygame.draw.rect(screen, (255, 0, 0), [x, y+height1+height2, 1, height3])
        x += 1

# Pygame initialization
screen_size = [600, 600]
pygame.init()
screen = pygame.display.set_mode((screen_size[0] + 400, screen_size[1]))
font = pygame.font.SysFont("Arial", 36)
font1 = pygame.font.SysFont("Arial", 18)
running = 1

# Quad tree initialization
npartitions = 2 # Default 2 must be nonzero
quad = QuadTree(npartitions, screen_size[0], screen)

# Set up variables for sim
spread_probability = probability/100
people = []
infected = []
ID = 0
for i in range(npeople-1):
    theta = random.random()*2*math.pi
    people.append(Person(random.random()*screen_size[0], random.random()*screen_size[1], math.cos(theta), math.sin(theta),False, ID))
    ID += 1
patient_zero = Person(random.random()*screen_size[0], random.random()*screen_size[1], math.cos(theta), math.sin(theta),True, ID+1)
people.append(patient_zero)
infected.append(patient_zero)

# Initialize graph
data = []
for i in range (380):
    data.append([0, 1, 0])


runnning = 1
count = 0
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = 0
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen,(255,255,255),[screen_size[0]+88, 350, 240, 240])
    pygame.draw.rect(screen,(0,0,0),[screen_size[0]+91, 380, 234, 206])

    quad.get_objs(infected)

    # Sim mechanics
    if count % 5 != 0:
        for person in people:
            person.draw_person()
            person.update_pos()
            if not person.infected:
                person.update_neighbors(person, quad)
                person.update_health()
            if person.infected:
                person.progress_sickness(infected)

    if count % 5 == 0:
        for person in people:
            person.draw_person()
            person.update_pos()
            person.update_vel()
            if not person.infected:
                person.update_neighbors(person, quad)
                person.update_health()
            if person.infected:
                person.progress_sickness(infected)


    # Metrics tab
    text = font.render("Metrics", True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+150, 12])
    if count % 25 == 0:
        data, ncases, nrecovered, ndead, nhealthy, nconfirmed = sim_analysis(people, data)
    draw_graph(data)
    text = font1.render("Cases: " + str(ncases), True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+10, 160])
    text = font1.render("Deaths: " + str(ndead), True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+100, 160])
    text = font1.render("Recovered: " + str(nrecovered), True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+195, 160])
    text = font1.render("Healthy: " + str(nhealthy), True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+309, 160])

    # Analysis tab
    text = font.render("Analysis", True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+150, 185])
    text = font1.render("Mortality: " + str(round(ndead*100/ncases, 2)) + "%", True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+10, 225])
    text = font1.render("Known Cases: " + str(nconfirmed) , True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+120, 225])
    text = font1.render("Effectiveness: " + str(round(100*nhealthy/npeople, 2))+ "%", True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+260, 225])


    # Parameters tab
    text = font.render("Parameters", True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+130, 255])
    text = font1.render("Population: " + str(npeople), True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+10, 295])
    text = font1.render("Infectivity: " + str(probability), True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+120, 295])
    text = font1.render("Radius: " + str(infection_radius), True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+213, 295])
    text = font1.render("Duration: " + str(duration/10), True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+290, 295])
    text = font1.render("Lethality: " + str(mortality*100) + "%", True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+10, 320])
    text = font1.render("Strictness: " + str(round(strictness,2)), True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+135, 320])
    text = font1.render("Test Percent: " + str(test_percent*100) + "%", True, (255, 255, 255))
    screen.blit(text, [screen_size[0]+265, 320])
    text = font1.render("Hospital", True, (0, 0, 0))
    screen.blit(text, [screen_size[0]+180, 355])


    pygame.display.flip()
    count += 1

    if count > 50:
        count = 0

    if strictness_funct:
        strictness += nconfirmed*response/(npeople*50)
        if strictness > 1:
            strictness = 1

pygame.quit()
