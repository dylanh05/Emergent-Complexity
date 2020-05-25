import pygame

class QuadTree():
    # Assumes screen size is a square, initializes tree
    def __init__(self, npartitions, screen_size, surf):
        # Treelocs stores all of the points to define the quad tree
        # Each loc is given by [p1, p2] where p1 is the northwest corner, p2 is southeast corner
        self.surf = surf
        self.treelocs = []
        self.layers = npartitions
        # Quads stores all objects within each quad, top to bottom (ie, first index is top left quad, last index is bottom right)
        self.quads = [[] for i in range(4**npartitions)]
        cpart = screen_size
        for i in range(npartitions):
            self.treelocs = []
            pos = 0
            cpart = cpart/2
            for j in range(2 ** (i+1)):
                pos1 = 0
                for k in range(2 ** (i+1)):
                    pos1 += cpart
                    self.treelocs.append([[pos, pos1 - cpart],[pos+cpart, pos1]])
                pos += cpart
        #self.treelocs.append(layer)

    # For quadtree visualization
    def draw_tree(self):
        #for layer in self.treelocs:
        for quad in self.treelocs:
            for coor in quad:
                pygame.draw.circle(self.surf,(255,255,255),(int(coor[0]),int(coor[1])),2)

    # Finds all of the objects within each quad and stores them in quads. Each object must have attribute x and y to be found
    def get_objs(self, objs):
        self.quads = [[] for i in range(4**self.layers)]
        for obj in objs:
            quadcount = 0
            for quad in self.treelocs:
                if quad[0][0] < obj.x < quad[1][0] and quad[0][1] < obj.y < quad[1][1]:
                    self.quads[quadcount].append(obj)
                quadcount += 1

    def find_quad(self, obj, quads):
        quadcount = 0
        for quad in quads:
            if quad[0][0] < obj.x < quad[1][0] and quad[0][1] < obj.y < quad[1][1]:
                return quadcount
            quadcount += 1
        return 0

