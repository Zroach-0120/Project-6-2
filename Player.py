from CollideObjectBase import SphereCollideObject
from panda3d.core import Loader, NodePath, Vec3, Filename, CollisionSphere
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from SpaceJamClasses import Drone, Missile
import math, random
from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect
import re
from panda3d.core import CollisionHandlerEvent

class Spaceship(SphereCollideObject):
    def __init__(self, loader: Loader, taskMgr, accept: Callable[[str, Callable], None], 
                 modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, 
                 posVec: Vec3, scaleVec: float, camera, traverser, handler):

        super().__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 0.01)
        
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)
        
        self.loader = loader
        self.render = parentNode
        self.accept = accept
        self.traverser = traverser
        self.handler = handler
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        self.handler = CollisionHandlerEvent()
        self.taskMgr = taskMgr
        self.camera = camera
        self.zoom_factor = 5
        self.cameraZoomSpeed = 10
        self.modelNode.setHpr(0, -90, 0)
      
        self.collisionNode.show()

        self.reloadTime = 0.25
        self.missileDistance = 4000
        self.missileBay = 1
        self.taskMgr.add(self.CheckIntervals, 'checkMissiles', 34)

        self.cntExplode = 0
        self.explodeIntervals = {}
        self.traverser = traverser
        self.handler.addInPattern('into')
        self.accept('into', self.HandleInto)
        self.SetParticles()

        # Boost-related variables
        self.base_speed = 5
        self.current_speed = self.base_speed
        self.boost_multiplier = 3
        self.boost_duration = 10  # seconds
        self.boost_cooldown = 5   # seconds
        self.can_boost = True

    def CheckIntervals(self, task):
        for i in list(Missile.Intervals.keys()):
            if not Missile.Intervals[i].isPlaying():
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()
                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]
                print(i + ' has reached the end of its fire solution')
        return Task.cont

    def Fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward())
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 150
            travVec = fireSolution + self.modelNode.getPos()

            tag = 'Missile' + str(Missile.missileCount)
            posVec = self.modelNode.getPos() + inFront
            currentMissile = Missile(self.loader, "./Assets/Phaser/phaser.egg", self.render, tag, posVec, 4.0)
            self.traverser.addCollider(currentMissile.collisionNode, self.handler)
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos=posVec, fluid=1)
            Missile.Intervals[tag].start()
        else:
            if not self.taskMgr.hasTaskNamed('reload'):
                print('Initializing reload...')
                self.taskMgr.doMethodLater(0, self.Reload, 'reload')
                return Task.cont  

    def HandleInto(self, entry):
        fromNode = entry.getFromNodePath().getName()
        print("fromNode: " + fromNode)
        intoNode = entry.getIntoNodePath().getName()
        print("intoNode: " + intoNode)
    
        intoPosition = Vec3(entry.getSurfacePoint(self.render))
    
        shooter = fromNode.split('_')[0]
        print("Shooter: " + shooter)
    
        victim = intoNode.split('_')[0]
        print("Victim: " + victim)
    
        pattern = r'[0-9]'
        strippedString = re.sub(pattern, '', victim)
    
        if strippedString in ("Drone", "Planet", "Space Station"):
            print(f"{victim} hit at {intoPosition}")
            self.DestroyObject(victim, intoPosition)
    
        if shooter in Missile.Intervals:
            Missile.Intervals[shooter].finish()
        else:
            print(f"Warning: No interval found for shooter '{shooter}'")

    def DestroyObject(self, hitID, hitPosition):
        nodeID = self.render.find(hitID)
        nodeID.detachNode()
        self.explodeNode.setPos(hitPosition)
        self.Explode()

    def Explode(self):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)
        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, duration=4.0)
        self.explodeIntervals[tag].start()

    def ExplodeLight(self, t):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()
        elif t == 0:
            self.explodeEffect.start(self.explodeNode)

    def SetParticles(self):
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig("./Assets/Part-Efx/basic_xpld_efx.ptf")
        self.explodeEffect.setScale(20)
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')

    def Reload(self, task):
        if task.time > self.reloadTime: 
           self.missileBay += 1
        if self.missileBay > 1:
            self.missileBay = 1
            print("Reload complete")
            return Task.done
        elif task.time <= self.reloadTime:
            print("reload proceeding")
            return Task.cont

    def move_forward(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyMoveForward, 'move-forward')
        else:
            self.taskMgr.remove('move-forward')

    def ApplyMoveForward(self, task):
        direction = self.modelNode.getQuat().getForward()
        self.modelNode.setPos(self.modelNode.getPos() + direction * self.current_speed)
        return Task.cont

    def turn_left(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyTurnLeft, 'turn-left')
        else:
            self.taskMgr.remove('turn-left')

    def ApplyTurnLeft(self, task):
        self.modelNode.setH(self.modelNode.getH() + 1.5)
        return Task.cont

    def turn_right(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyTurnRight, 'turn-right')
        else:
            self.taskMgr.remove('turn-right')

    def ApplyTurnRight(self, task):
        self.modelNode.setH(self.modelNode.getH() - 1.5)
        return Task.cont

    def turn_up(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyTurnUp, 'turn-up')
        else:
            self.taskMgr.remove('turn-up')

    def ApplyTurnUp(self, task):
        self.modelNode.setP(self.modelNode.getP() - 1.5)
        return Task.cont

    def turn_down(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyTurnDown, 'turn-down')
        else:
            self.taskMgr.remove('turn-down')

    def ApplyTurnDown(self, task):
        self.modelNode.setP(self.modelNode.getP() + 1.5)
        return Task.cont

    def UpdateCamera(self, task):
        target_pos = self.modelNode.getPos() + Vec3(0, -30, 10)
        current_pos = self.camera.getPos()
        new_pos = current_pos + (target_pos - current_pos) * 0.1
        self.camera.setPos(new_pos)
        self.camera.lookAt(self.modelNode)
        return Task.cont

    def set_camera(self):
        self.UpdateCamera(None)

    def zoom_in(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyZoomIn, 'zoom-in')
        else:
            self.taskMgr.remove('zoom-in')

    def ApplyZoomIn(self, task):
        self.camera.setPos(self.camera.getPos() + Vec3(0, self.cameraZoomSpeed, 0))
        return Task.cont

    def zoom_out(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyZoomOut, 'zoom-out')
        else:
            self.taskMgr.remove('zoom-out')

    def ApplyZoomOut(self, task):
        self.camera.setPos(self.camera.getPos() + Vec3(0, -self.cameraZoomSpeed, 0))
        return Task.cont

    def attach_drone_rings(self, numDronesPerRing=12, radius=20):
        ringParent = self.modelNode.attachNewNode("AllDroneRings")
        angleStep = 2 * math.pi / numDronesPerRing

        for axis in ['x', 'y', 'z']:
            for i in range(numDronesPerRing):
                angle = i * angleStep
                pos = Vec3()
                if axis == 'x':
                    pos.y = math.cos(angle) * radius
                    pos.z = math.sin(angle) * radius
                elif axis == 'y':
                    pos.x = math.cos(angle) * radius
                    pos.z = math.sin(angle) * radius
                elif axis == 'z':
                    pos.x = math.cos(angle) * radius
                    pos.y = math.sin(angle) * radius
                Drone(
                    self.loader,
                    "./Assets/DroneDefender/DroneDefender.obj",
                    ringParent,
                    f"Drone-{axis}-{i}",
                    "./Assets/DroneDefender/octotoad1_auv.png",
                    pos,
                    .5
                )

    # BOOST FUNCTIONS
    def Boost(self):
        if not self.can_boost:
            print("Boost is on cooldown!")
            return

        self.can_boost = False
        self.current_speed = self.base_speed * self.boost_multiplier
        print("Boost activated! Speed tripled.")

        self.taskMgr.doMethodLater(self.boost_duration, self.EndBoost, 'end-boost')

    def EndBoost(self, task):
        self.current_speed = self.base_speed
        print("Boost ended. Speed back to normal.")

        self.taskMgr.doMethodLater(self.boost_cooldown, self.ResetBoost, 'reset-boost')
        return Task.done

    def ResetBoost(self, task):
        self.can_boost = True
        print("Boost ready to use again.")
        return Task.done
