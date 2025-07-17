from direct.showbase.ShowBase import ShowBase
import math, sys, random
import DefensePaths as defensePaths
import SpaceJamClasses as SpaceJamClasses
from panda3d.core import Vec3
from Player import Spaceship
from SpaceJamClasses import Drone
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, CollisionHandlerEvent, TransparencyAttrib
from direct.gui.OnscreenImage import OnscreenImage
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Initialize collision traverser and handlers
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.collisionHandler = CollisionHandlerEvent()  # For boundary detection

        # Setup your scene objects, including Hero
        self.SetupScene()

        # Set up collision system properly
        self.SetupCollisions()

        # Show collision solids for debugging
        self.cTrav.showCollisions(self.render)

        self.SetKeyBindings()
        self.taskMgr.add(self.UpdateCamera, "UpdateCamera")

        # Free camera flag
        self.freeCamera = False
        self.enableParticles()
    def SetupScene(self):
        self.Universe = SpaceJamClasses.Universe(
            self.loader, "./Assets/Universe/Universe.obj", self.render,
            'Universe', "Assets/Universe/Universe2.jpg", (0, 0, 0), 18008
        )
        self.Planet1 = SpaceJamClasses.Planet(
            self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet1',
            "./Assets/Planets/WaterPlanet2.png", (0,0,0), 250
        )
        self.Planet2 = SpaceJamClasses.Planet(
            self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet2',
            "./Assets/Planets/eris.jpg", (0, 6000, 0), 300
        )
        self.Planet3 = SpaceJamClasses.Planet(
            self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet3',
            "./Assets/Planets/cheeseplanet.png", (500, -5000, 200), 500
        ) 
        self.Planet4 = SpaceJamClasses.Planet(
            self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet4',
            "./Assets/Planets/earth.jpg", (300, 6000, 500), 150
        ) 
        self.Planet5 = SpaceJamClasses.Planet(
            self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet5',
            "./Assets/Planets/redmoon.png", (700, -2000, 100), 500
        )
        self.Planet6 = SpaceJamClasses.Planet(
            self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet6',
            "./Assets/Planets/venus.jpg", (0, -980, -1480), 700
        )
        self.SpaceStation1 = SpaceJamClasses.SpaceStation(
            self.loader, "./Assets/SpaceStation/spaceStation.x", self.render, 'SpaceStation1',
            "./Assets/SpaceStation/SpaceStation1_Dif2.png", (1500, 1800, -100), 40
        )

        self.Hero = Spaceship(
            self.loader, self.taskMgr, self.accept, "Assets/Spaceships/spacejet.3ds",
            self.render, 'Hero', "Assets/Spaceships/spacejet_C.png",
            Vec3(900, 1200, -58), 50, self.camera, self.cTrav, self.collisionHandler
        )
        self.Hero.attach_drone_rings()
        
        self.EnableHUD()
        self.planets = [
        self.Planet1,
        self.Planet2,
        self.Planet3,
        self.Planet4,
        self.Planet5,
        self.Planet6
]
    def SetupCollisions(self):
        
        self.pusher.addCollider(self.Hero.collisionNode, self.Hero.modelNode)
        self.cTrav.addCollider(self.Hero.collisionNode, self.pusher)

        
        solid_objects = [self.Planet1, self.Planet2, self.Planet3, self.Planet4, 
                        self.Planet5, self.Planet6, self.SpaceStation1]
        
        for obj in solid_objects:
            self.pusher.addCollider(obj.collisionNode, obj.modelNode)
            self.cTrav.addCollider(obj.collisionNode, self.pusher)

        
        self.collisionHandler.addInPattern('%fn-into-%in')
        self.collisionHandler.addOutPattern('%fn-out-%in')
        self.cTrav.addCollider(self.Universe.collisionNode, self.collisionHandler)
        
       
        self.accept('Hero_cNode-into-Universe_cNode', self.onUniverseBoundary)

    def onUniverseBoundary(self, entry):
        """Handle when objects hit the universe boundary"""
        print("Object hit universe boundary!")

    def SetKeyBindings(self):
        self.accept('a', self.Hero.turn_left, [1])
        self.accept('a-up', self.Hero.turn_left, [0])
        self.accept('d', self.Hero.turn_right, [1])
        self.accept('d-up', self.Hero.turn_right, [0])
        self.accept('s', self.Hero.move_forward, [1])
        self.accept('s-up', self.Hero.move_forward, [0])
        self.accept('w', self.Hero.turn_up, [1])
        self.accept('w-up', self.Hero.turn_up, [0])
        self.accept('x', self.Hero.turn_down, [1])
        self.accept('x-up', self.Hero.turn_down, [0])
        self.accept('shift', self.Hero.Boost)
        self.accept("r", self.StartPlanetRotation)

    

        self.accept('z', self.Hero.zoom_out, [1])  
        self.accept('z-up', self.Hero.zoom_out, [0])
        self.accept('x', self.Hero.zoom_in, [1])  
        self.accept('x-up', self.Hero.zoom_in, [0])

        self.accept('f', self.ToggleFreeCamera)
        self.accept('space', self.Hero.Fire)
    def UpdateCamera(self, task):
        if not self.freeCamera:
            self.disableMouse()
            self.camera.reparentTo(self.Hero.modelNode)
            self.camera.setFluidPos(0, 1, 0)
        else: 
            self.enableMouse()
        return task.cont

    def ToggleFreeCamera(self):
        self.freeCamera = not self.freeCamera
        if self.freeCamera:
            print("Free camera mode enabled.")
        else:
            print("Free camera mode disabled, camera following ship.")

    def RotatePlanets(self, task):
        for planet in self.planets:
            planet.modelNode.setH(planet.modelNode.getH() + 0.2)  # speed 
        return task.cont

    def StartPlanetRotation(self):
        if not hasattr(self, 'planetRotationTask'):
            self.planetRotationTask = self.taskMgr.add(self.RotatePlanets, "rotate-planets")

    def StopPlanetRotation(self):
        if hasattr(self, 'planetRotationTask'):
            self.taskMgr.remove("rotate-planets")
        del self.planetRotationTask


    def EnableHUD(self):
        self.hud = OnscreenImage(image = "./Assets/Hud/Reticleiv.jpg", pos = Vec3(0,0,0), scale = 0.1)
        self.hud.setTransparency(TransparencyAttrib.MAlpha)
        #self.hud.reparentTo(self.aspect2d)

    def DrawBaseballSeams(self, centralObject, droneName, step, numSeams, radius=1):
        unitVec = defensePaths.BaseballSeams(step, numSeams, B=0.4)
        unitVec.normalize()
        position = unitVec * radius * 10
        SpaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", centralObject.modelNode, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 1)

    def DrawCloudDefense(self, centralObject, droneName):
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 10
        SpaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", centralObject.modelNode, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 1)

app = MyApp()

fullCycle = 60
for j in range(fullCycle):
    SpaceJamClasses.Drone.droneCount += 1
    nickName = "Drone" + str(SpaceJamClasses.Drone.droneCount)
    app.DrawCloudDefense(app.Planet1, nickName)
    app.DrawBaseballSeams(app.SpaceStation1, nickName, j, fullCycle, 2)

app.run()