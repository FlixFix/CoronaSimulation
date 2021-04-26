import numpy as np
import pygame
import random
import time
import matplotlib

import matplotlib.pyplot as plt



INFECTION_RATE = 50
# time particle needs to heal after infection in milliseconds
TIME_TO_HEAL = 10
# time  particle is infectious in milliseconds
TIME_INFECTIOUS = 7

# colour definitions
# infected
COLOUR_INFECTED = (255, 153, 51) # orange status 1
# immune
COLOUR_IMMUNE = (255, 51, 153) # pink status 3
# infectious
COLOUR_INFECTIOUS = (255,0 , 0) # rot status 2 --> kann leute mit status 0 anstecken
# healthy
COLOUR_HEALTHY = (0, 102, 204) # blau status 0

# -------- health status -----------
# 0 = healthy --> color COLOUR_HEALTHY
# 1 = infected but not infectious --> color COLOUR_INFECTED
# 2 = infectious --> color COLOUR_INFECTIOUS
# 3 = immune --> color COLOUR_IMMUNE


class Particle:
    def __init__(self, mass, radius, speed, id=0, pos=np.array([400.0, 300.0])):
        self.id =  id
        self.x = 400.0
        self.y = 300.0
        self.pos = pos
        self.mass = mass
        self.rad = radius
        self.speed = speed
        self.rect = None
        self.infected = 0
        self.colour = (0, 255, 0)
        self.infected_time = 0
        self.counted = False
        self.prior_health_status = 0

    def update(self, surf, dt = 1):
        self.update_colour()
        self.collides_with_border(surf)
        self.pos = self.pos + self.speed * dt
        self.rounded_pos = np.array([int(self.pos[0]), int(self.pos[1])])
        self.rect = pygame.draw.circle(surf, self.colour, self.rounded_pos, self.rad)

    def spawn(self, surf):
        self.rect = pygame.draw.circle(surf, self.colour, self.pos, self.rad)

    def collides_with_border(self, surf):
        if self.pos[0] + self.rad >= surf.get_width() or self.pos[0] - self.rad <= 0.0:
            self.speed[0] = - self.speed[0]
        if self.pos[1] + self.rad >= surf.get_height() or self.pos[1] - self.rad <= 0.0:
            self.speed[1] =  - self.speed[1]

    def collides_with_particle(self, particle):
        dist = np.linalg.norm(particle.pos - self.pos)
        if dist <= self.rad + particle.rad:
            return True
        else:
            return False

    def infect(self, other, percent=INFECTION_RATE):
            if random.randrange(100) < percent and other.infected == 0:
                other.infected_time = time.time()
                other.infected = 2
                other.counted = False

    def react_to_other_particle(self, particle):

        # update healthstatus
        self.update_health_status()

        if self.collides_with_particle(particle):
            new_speed = particle.mass / self.mass * particle.speed
            particle.speed = self.mass / particle.mass * self.speed
            if self.infected == 2:
                self.infect(particle)
                particle.update_colour()
            self.speed = new_speed

            if particle.infected == 2:
                particle.infect(self)



    def update_health_status(self):
        if self.infected_time == 0:
            self.infected = 0
        elif time.time() - self.infected_time >= TIME_TO_HEAL:
            self.infected = 3
            self.counted = False
        elif time.time() - self.infected_time >= TIME_INFECTIOUS:
            self.infected = 1
            self.counted = False

        self.update_colour()

    def update_counter(self, simulation):
        if not self.counted:
            if self.infected == 1:
                simulation.cnt_infected += 1
                simulation.cnt_infectious -= 1
            elif self.infected == 2:
                simulation.cnt_healthy -= 1
                simulation.cnt_infectious += 1
            elif self.infected == 3:
                simulation.cnt_immune += 1
                simulation.cnt_infected -= 1
            self.counted = True



    def update_colour(self):
        if self.infected == 0:
            self.colour = COLOUR_HEALTHY
        elif self.infected == 1:
            self.colour = COLOUR_INFECTED
        elif self.infected == 2:
            self.colour = COLOUR_INFECTIOUS
        else:
            self.colour = COLOUR_IMMUNE

class Simulation:
    def __init__(self):
        self.particles = []
        self.dt = 1
        self.number_of_particles = len(self.particles)
        self.height = 600
        self.width = 800

        self.cnt_infected = 0
        self.cnt_infectious = 0
        self.cnt_healthy = 0
        self.cnt_immune = 0

        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.start_time = 0
        self. legend_surf = pygame.Surface((100, 50))


    def add_particle(self,mass, rad, speed, pos, infected=0):
        self.particles.append(Particle(mass, rad, speed, self.number_of_particles, pos))
        self.particles[len(self.particles) - 1].infected = infected
        if self.particles[len(self.particles) - 1].infected != 0:
            self.particles[len(self.particles) - 1].infected_time = time.time()
            self.cnt_infectious += 1
        self.number_of_particles += 1


    def random_init(self, number_of_particles, max_mass, max_radius):
        counter = 0
        while counter < number_of_particles:
            rand_mass = 5
            rand_radius = 10
            rand_speedx = random.randint(-10, 10)
            if rand_speedx == 0:
                rand_speedx = 10
            rand_speedy = random.randint(-10, 10)
            if rand_speedy == 0:
                rand_speedy = 10
            rand_speed = np.array([rand_speedx, rand_speedy])
            rand_posx = random.randint(0 + rand_radius, self.width - rand_radius)
            rand_posy = random.randint(0 + rand_radius, self.height - rand_radius)
            rand_pos = np.array([rand_posx, rand_posy])
            self.add_particle(rand_mass, rand_radius, rand_speed, rand_pos)
            self.number_of_particles += 1
            counter += 1
            self.total_elapsed_time = 0
            self.cnt_healthy += 1

    def cleanse(self):
        for particle in self.particles:
            particle.infected = False
        self.particles[0].infected = True

    def update_data(self, data_time, data_infected):
        data_time.append(time.time() - self.start_time)
        data_infected.append(self.cnt_infectious)


    def create_legend(self):
        self.legend_surf.fill((255, 255, 255))
        pygame.draw.polygon(self.legend_surf, (160, 160, 160), [(0, 0), (98, 0), (98, 48), (0, 48), (0, 0)], 2)

        pygame.draw.circle(self.legend_surf, COLOUR_HEALTHY, (10, 10), 5)
        pygame.draw.circle(self.legend_surf, COLOUR_INFECTIOUS, (10, 22), 5)
        pygame.draw.circle(self.legend_surf, COLOUR_INFECTED, (10, 34), 5)
        pygame.draw.circle(self.legend_surf, COLOUR_IMMUNE, (10, 46), 5)

        font = pygame.font.Font('freesansbold.ttf', 12)

        text_healthy = font.render('Healthy', True, COLOUR_HEALTHY, (255, 255, 255))
        self.legend_surf.blit(text_healthy, (20, 4))

        text_infectious = font.render('Infectious', True, COLOUR_INFECTIOUS, (255, 255, 255))
        self.legend_surf.blit(text_infectious, (20, 16))

        text_infected = font.render('Infected', True, COLOUR_INFECTED, (255, 255, 255))
        self.legend_surf.blit(text_infected, (20, 28))

        text_immune = font.render('Immune', True, COLOUR_IMMUNE, (255, 255, 255))
        self.legend_surf.blit(text_immune, (20, 40))


    def plot_results(self, time, cases):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(time, cases)
        plt.show()




    def run(self):

        surf = pygame.display.set_mode((self.width, self.height))
        surf.fill((255, 255 , 255))

        self.create_legend()
        # self.add_particle(10, 50, np.array([1, 1]), np.array([400, 300]))
        # self.add_particle(30, 50, np.array([1, 1]), np.array([100, 200]))

        self.random_init(50, 2, 20)
        self.start_time = time.time()
        data_time = [0]
        data_infected = [0]

        complete_data = [data_time, data_infected]
        # plot_surf = plot(data_time, data_infected)
        # plot_data_cnt = len(data_time)

        # add infected particle
        self.add_particle(5, 10, np.array([10, 10]), np.array([50, 50]), 2)

        for el in self.particles:
            el.spawn(surf)


        while True:


            pressed = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            if pressed[pygame.K_ESCAPE]:
                self.plot_results(data_time, data_infected)
                pygame.quit()
                quit()

            if pressed[pygame.K_r]:
                self.cleanse()
                self.add_particle(5, 10, np.array([10, 10]), np.array([50, 50]), 2)

            surf.fill((255, 255, 255))


            for el in self.particles:
                for other_particle in self.particles:
                    if (other_particle.id != el.id):
                        el.react_to_other_particle(other_particle)
                el.update(surf, self.dt)
                el.update_counter(self)
                self.update_data(data_time, data_infected)


            self.screen.blit(self.legend_surf, (695, 545))
            # if len(data_time) > plot_data_cnt:
            #     plot_surface = plot(data_time, data_infected)
            #     self.screen.blit(plot_surf, (0, 0))


            pygame.display.update()

        




if __name__ == '__main__':
    game = Simulation()
    game.run()