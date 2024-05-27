from dp_algo import max_path_sum_with_path
import tkinter as tk
import random
import math
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Brain():

    def __init__(self, botp, canvas):
        self.bot = botp

        self.path = [
            (0, 0),
        ]

        self.path2 = []

        self.canvas = canvas
        self.path_count = 0

    def generate_path(self):
        map = self.bot.dynamic_map
        currentGrid = int(self.bot.x // 100), int(self.bot.y // 100)
        targetGrid = self.find_most_dirt(map)
        mat = np.array(map)
        min_x, min_y = min(currentGrid[0], targetGrid[0]), min(currentGrid[1], targetGrid[1])
        max_x, max_y = max(currentGrid[0], targetGrid[0]), max(currentGrid[1], targetGrid[1])
        mat = mat[min_x:max_x + 1, min_y:max_y + 1]

        down = currentGrid[0] < targetGrid[0]
        right = currentGrid[1] < targetGrid[1]

        # anticlockwise
        if down:
            if right:
                k = 0
            else:
                k = 1
        else:
            if right:
                k = 3
            else:
                k = 2

        mat = np.rot90(mat, k=k)
        path = max_path_sum_with_path(mat)

        tmp = np.zeros(mat.shape)
        for i, pos in enumerate(path, start=1):
            tmp[*pos] = i

        final_path = []
        tmp = np.rot90(tmp, k=-k)
        for i in range(len(path)):
            pos = np.where(tmp == i + 1)
            final_path.append((pos[0][0], pos[1][0]))

        final_path = [(x + min_x, y + min_y) for x, y in final_path]
        # print("currentGrid, targetGrid", currentGrid, targetGrid)
        # print("path", final_path)
        return final_path

    def find_most_dirt(self, map):
        x, y = 0, 0
        count = 0
        for m in range(9, -1, -1):
            for n in range(9, -1, -1):
                tmp = map[m][n]
                if tmp >= count:
                    count = tmp
                    x, y = m, n

        return x, y

    @staticmethod
    def grid_to_coordinates(grid):
        return grid[0] * 100 + 50, grid[1] * 100 + 50

    # modify this to change the robot's behaviour
    def thinkAndAct(self, x, y, sl, sr, count):

        newX = None
        newY = None

        targetGrid = self.path[0]
        target = Brain.grid_to_coordinates(targetGrid)

        self.paint_rect(target, targetGrid, "blue", "target")

        speedLeft = speedRight = 50
        # move towards target
        dr = self.bot.distanceToRightSensor(target[0], target[1])
        dl = self.bot.distanceToLeftSensor(target[0], target[1])
        if dr > dl:
            speedLeft = 5
            speedRight = -0
        elif dl > dr:
            speedLeft = -0
            speedRight = 5

        if dl < 100 and abs(dr - dl) < dl * 0.2:  # approximately the same
            speedLeft = speedRight = 5

        # check for arrival
        if target[0] - 20 < x < target[0] + 20 and target[1] - 20 < y < target[1] + 20:
            next_targetGrid = self.find_most_dirt(self.bot.dynamic_map)
            self.path.append(next_targetGrid)
            del self.path[0]

        # toroidal geometry
        if x > 1000:
            newX = 0
        if x < 0:
            newX = 1000
        if y > 1000:
            newY = 0
        if y < 0:
            newY = 1000

        return speedLeft, speedRight, newX, newY

    def paint_rect(self, target, targetGrid, fill, tags, delete=True):
        if delete:
            self.canvas.delete(tags)

        center_x = target[0]
        center_y = target[1]
        r = 50
        x1 = center_x - r
        y1 = center_y - r
        x2 = center_x + r
        y2 = center_y + r
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=fill, tags=tags)
        self.canvas.create_text(center_x, center_y, text=str(self.bot.dynamic_map[targetGrid[0]][targetGrid[1]]),
                                fill=fill, tags=tags)

    def thinkAndAct2(self, x, y, sl, sr, count):
        newX = None
        newY = None

        if not self.path2:
            self.path2 = self.generate_path()
            self.path_count = len(self.path2[1:-1])

        targetGrid = self.path2[0]
        finalGrid = self.path2[-1]

        target = Brain.grid_to_coordinates(targetGrid)
        final = Brain.grid_to_coordinates(finalGrid)

        self.paint_rect(target, targetGrid, "red", "target")
        for i, grid in enumerate(self.path2[1:-1]):
            target_tmp = Brain.grid_to_coordinates(grid)
            self.paint_rect(target_tmp, grid, "black", "path_" + str(i), True)
        self.paint_rect(final, finalGrid, "blue", "final")

        speedLeft = speedRight = 5
        # move towards target
        dr = self.bot.distanceToRightSensor(target[0], target[1])
        dl = self.bot.distanceToLeftSensor(target[0], target[1])
        if dr > dl:
            speedLeft = 5
            speedRight = -0
        elif dl > dr:
            speedLeft = -0
            speedRight = 5

        if dl < 100 and abs(dr - dl) < dl * 0.2:  # approximately the same
            speedLeft = speedRight = 5

        # check for arrival
        if target[0] - 20 < x < target[0] + 20 and target[1] - 20 < y < target[1] + 20:
            del self.path2[0]

        # check for arrival
        if final[0] - 20 < x < final[0] + 20 and final[1] - 20 < y < final[1] + 20:
            for i in range(self.path_count):
                self.canvas.delete("path_" + str(i))
            # self.path_count = 0

        # toroidal geometry
        if x > 1000:
            newX = 0
        if x < 0:
            newX = 1000
        if y > 1000:
            newY = 0
        if y < 0:
            newY = 1000

        return speedLeft, speedRight, newX, newY


class Bot():

    def __init__(self, namep, passiveObjectsp, counterp, algo: int = 1):
        self.name = namep
        # initial position
        self.x = 50
        self.y = 50
        self.theta = math.pi / 8
        self.ll = 60  # axle width
        self.sl = 0.0
        self.sr = 0.0
        self.passiveObjects = passiveObjectsp
        self.counter = counterp

        self.dynamic_map = self.map()
        self.algo = algo
        self.thinkAndActTime = 0

    def thinkAndAct(self, agents, passiveObjects):
        if self.algo == 1:
            self.sl, self.sr, xx, yy = self.brain.thinkAndAct(self.x, self.y, self.sl, self.sr,
                                                              self.counter.dirtCollected)
        elif self.algo == 2:
            self.sl, self.sr, xx, yy = self.brain.thinkAndAct2(self.x, self.y, self.sl, self.sr,
                                                               self.counter.dirtCollected)

        else:
            xx = yy = None

        if xx is not None:
            self.x = xx
        if yy is not None:
            self.y = yy

        self.thinkAndActTime += 1

    def setBrain(self, brainp):
        self.brain = brainp

    # returns the result from the ceiling-mounted dirt camera
    def map(self):
        map = np.zeros((10, 10), dtype=np.int16)
        for p in self.passiveObjects:
            if isinstance(p, Dirt):
                xx = int(math.floor(p.centreX / 100.0))
                yy = int(math.floor(p.centreY / 100.0))
                map[xx][yy] += 1
        return map

    def distanceTo(self, obj):
        xx, yy = obj.getLocation()
        return math.sqrt(math.pow(self.x - xx, 2) + math.pow(self.y - yy, 2))

    def distanceToRightSensor(self, lx, ly):
        return math.sqrt((lx - self.sensorPositions[0]) * (lx - self.sensorPositions[0]) + \
                         (ly - self.sensorPositions[1]) * (ly - self.sensorPositions[1]))

    def distanceToLeftSensor(self, lx, ly):
        return math.sqrt((lx - self.sensorPositions[2]) * (lx - self.sensorPositions[2]) + \
                         (ly - self.sensorPositions[3]) * (ly - self.sensorPositions[3]))

    # what happens at each timestep
    def update(self, canvas, passiveObjects, dt):
        self.move(canvas, dt)

    # draws the robot at its current position
    def draw(self, canvas):
        points = [(self.x + 30 * math.sin(self.theta)) - 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y - 30 * math.cos(self.theta)) - 30 * math.cos((math.pi / 2.0) - self.theta), \
                  (self.x - 30 * math.sin(self.theta)) - 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y + 30 * math.cos(self.theta)) - 30 * math.cos((math.pi / 2.0) - self.theta), \
                  (self.x - 30 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y + 30 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta), \
                  (self.x + 30 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y - 30 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta) \
                  ]
        canvas.create_polygon(points, fill="blue", tags=self.name)

        self.sensorPositions = [(self.x + 20 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                                (self.y - 20 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta), \
                                (self.x - 20 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                                (self.y + 20 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta) \
                                ]

        centre1PosX = self.x
        centre1PosY = self.y
        canvas.create_oval(centre1PosX - 16, centre1PosY - 16, \
                           centre1PosX + 16, centre1PosY + 16, \
                           fill="gold", tags=self.name)

        wheel1PosX = self.x - 30 * math.sin(self.theta)
        wheel1PosY = self.y + 30 * math.cos(self.theta)
        canvas.create_oval(wheel1PosX - 3, wheel1PosY - 3, \
                           wheel1PosX + 3, wheel1PosY + 3, \
                           fill="red", tags=self.name)

        wheel2PosX = self.x + 30 * math.sin(self.theta)
        wheel2PosY = self.y - 30 * math.cos(self.theta)
        canvas.create_oval(wheel2PosX - 3, wheel2PosY - 3, \
                           wheel2PosX + 3, wheel2PosY + 3, \
                           fill="green", tags=self.name)

        sensor1PosX = self.sensorPositions[0]
        sensor1PosY = self.sensorPositions[1]
        sensor2PosX = self.sensorPositions[2]
        sensor2PosY = self.sensorPositions[3]
        canvas.create_oval(sensor1PosX - 3, sensor1PosY - 3, \
                           sensor1PosX + 3, sensor1PosY + 3, \
                           fill="yellow", tags=self.name)
        canvas.create_oval(sensor2PosX - 3, sensor2PosY - 3, \
                           sensor2PosX + 3, sensor2PosY + 3, \
                           fill="yellow", tags=self.name)

    # handles the physics of the movement
    # cf. Dudek and Jenkin, Computational Principles of Mobile Robotics
    def move(self, canvas, dt):
        if self.sl == self.sr:
            R = 0
        else:
            R = (self.ll / 2.0) * ((self.sr + self.sl) / (self.sl - self.sr))
        omega = (self.sl - self.sr) / self.ll
        ICCx = self.x - R * math.sin(self.theta)  # instantaneous centre of curvature
        ICCy = self.y + R * math.cos(self.theta)
        m = np.matrix([[math.cos(omega * dt), -math.sin(omega * dt), 0], \
                       [math.sin(omega * dt), math.cos(omega * dt), 0], \
                       [0, 0, 1]])
        v1 = np.matrix([[self.x - ICCx], [self.y - ICCy], [self.theta]])
        v2 = np.matrix([[ICCx], [ICCy], [omega * dt]])
        newv = np.add(np.dot(m, v1), v2)
        newX = newv.item(0)
        newY = newv.item(1)
        newTheta = newv.item(2)
        newTheta = newTheta % (2.0 * math.pi)  # make sure angle doesn't go outside [0.0,2*pi)
        self.x = newX
        self.y = newY
        self.theta = newTheta
        if self.sl == self.sr:  # straight line movement
            self.x += self.sr * math.cos(self.theta)  # sr wlog
            self.y += self.sr * math.sin(self.theta)
        canvas.delete(self.name)
        self.draw(canvas)

    def collectDirt(self, canvas, passiveObjects, count):
        toDelete = []
        for idx, rr in enumerate(passiveObjects):
            if isinstance(rr, Dirt):
                if self.distanceTo(rr) < 30:
                    canvas.delete(rr.name)
                    toDelete.append(idx)
                    count.itemCollected(canvas)

        for ii in sorted(toDelete, reverse=True):
            del passiveObjects[ii]

        # update dynamic map
        self.dynamic_map = self.map()

        return passiveObjects


class Dirt:
    def __init__(self, namep, xx, yy):
        self.centreX = xx
        self.centreY = yy
        self.name = namep

    def draw(self, canvas):
        body = canvas.create_oval(self.centreX - 1, self.centreY - 1, \
                                  self.centreX + 1, self.centreY + 1, \
                                  fill="grey", tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY


class Counter:
    def __init__(self):
        self.dirtCollected = 0

    def itemCollected(self, canvas):
        self.dirtCollected += 1
        canvas.delete("dirtCount")
        canvas.create_text(
            50, 50, anchor="w", text="Dirt collected: " + str(self.dirtCollected), tags="dirtCount"
        )


def initialise(window):
    window.resizable(False, False)
    canvas = tk.Canvas(window, width=1000, height=1000)
    canvas.pack()
    return canvas


def buttonClicked(x, y, agents):
    for rr in agents:
        if isinstance(rr, Bot):
            rr.x = x
            rr.y = y


def createObjects(canvas, algo: int = 1):
    agents = []
    passiveObjects = []

    i = 0
    # place dirt everywhere else
    for xx in range(0, 10):
        for yy in range(0, 10):
            for _ in range(20 + random.randrange(-10, 10)):
                x = xx * 100 + random.randrange(10, 90)
                y = yy * 100 + random.randrange(10, 90)

                dirt = Dirt("Dirt" + str(i), x, y)
                i += 1
                passiveObjects.append(dirt)
                dirt.draw(canvas)

    count = Counter()

    # place Bot
    bot = Bot("Bot1", passiveObjects, count, algo)
    brain = Brain(bot, canvas)
    bot.setBrain(brain)
    agents.append(bot)
    bot.draw(canvas)

    canvas.bind("<Button-1>", lambda event: buttonClicked(event.x, event.y, agents))

    return agents, passiveObjects, count


def moveIt(canvas, agents, passiveObjects, count, limit: int = 1500   ):
    for rr in agents:
        rr.thinkAndAct(agents, passiveObjects)
        rr.update(canvas, passiveObjects, 1.0)
        passiveObjects = rr.collectDirt(canvas, passiveObjects, count)

        if rr.thinkAndActTime >= limit:
            canvas.winfo_toplevel().destroy()
            return

    canvas.after(1, moveIt, canvas, agents, passiveObjects, count,limit)


def main():
    window = tk.Tk()
    canvas = initialise(window)
    agents, passiveObjects, count = createObjects(canvas)
    moveIt(canvas, agents, passiveObjects, count)
    window.mainloop()

    print("complete: total dirt collected " + str(count.dirtCollected))


def write_csv(filename, new_row: dict):
    # append data
    with open(filename, 'a', newline='') as file:
        fieldnames = ["algo", "limit", "dirt_count", ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow(new_row)


def experiment():
    runtimes = 1
    algo = 1

    for i in range(runtimes):
        limit = 1000
        window = tk.Tk()
        canvas = initialise(window)
        agents, passiveObjects, count = createObjects(canvas, algo=algo)
        moveIt(canvas, agents, passiveObjects, count, limit=limit)
        window.mainloop()

        dirt_count = count.dirtCollected
        print("complete: total dirt collected", dirt_count)
        if algo ==2:
            csv_file = "dirt_count_algo2.csv"
            d = {"algo": algo, "limit": limit, "dirt_count": dirt_count}
            write_csv(csv_file, d)
        else:
            csv_file = "dirt_count_algo1.csv"
            d = {"algo": algo, "limit": limit, "dirt_count": dirt_count}
            write_csv(csv_file, d)


def plot():
    csv_file = "dirt_count.csv"
    df = pd.read_csv(csv_file)
    if df.empty:
        return



if __name__ == '__main__':
    # main()

    experiment()