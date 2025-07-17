from panda3d.core import NodePath, Vec3, CollisionNode, CollisionSphere, CollisionHandlerQueue, CollisionRay, Filename
import random, math
from direct.task import Task
from CollideObjectBase import *

class Universe(InverseSphereCollideObject):
    def __init__(self, loader, modelPath, parentNode, nodeName, texPath, posVec, scaleVec):
        # Use a much larger radius for the universe boundary
        # The 0.9 radius was too small for your universe scale
        super().__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 0.9)
        
        self.modelNode.reparentTo(parentNode)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)
        
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)


class Planet(SphereCollideObject):
    def __init__(self, loader, modelPath, parentNode, nodeName, texPath, posVec, scaleVec):
        super().__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 1.5)
        
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        
        self.collisionNode.node().addSolid(CollisionSphere(0, 0, 0, 5))
        self.collisionNode.show()


class Drone(CollideableObject):
    droneCount = 0
    
    def __init__(self, loader, modelPath, parentNode, nodeName, texPath, posVec, scaleVec):
        super().__init__(loader, modelPath, parentNode, nodeName)
        
        self.modelNode.reparentTo(parentNode)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)
        
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        Drone.droneCount += 1

        self.collisionNode.node().addSolid(CollisionSphere(0, 0, 0, 0.05))
        self.collisionNode.show()  

    @staticmethod
    def return_to_pool(drone):
        """Returns the drone to the pool when it is destroyed."""
        Drone.dronePool.append(drone.modelNode)
        drone.modelNode.removeNode()


class SpaceStation(CapsuleCollideableObject):
    def __init__(self, loader, modelPath, parentNode, nodeName, texPath, posVec, scaleVec):
        super().__init__(loader, modelPath, parentNode, nodeName, 1, -1, 5, 1, -1, -5, 1.5)
        
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
    

class Missile(SphereCollideObject):
     fireModels = {}
     cNodes = {}
     collisionSolids = {}
     Intervals = {}
     missileCount = 0

     def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float = 1.0):
         super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3.0)
         self.modelNode.setScale(scaleVec)
         self.modelNode.setPos(posVec)
         Missile.missileCount += 1
         Missile.fireModels[nodeName] = self.modelNode
         Missile.cNodes[nodeName] = self.collisionNode
         Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
         Missile.cNodes[nodeName].show()
         print("Fire rocket #" + str(Missile.missileCount))