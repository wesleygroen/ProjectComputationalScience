class Car:
    def __init__(self, length, speed):
        self.__length = length
        self.__speed = speed
    
    def length(self):
        return self.__length
        
    def speed(self):
        return self.__speed
    
    def setSpeed(self, speed):
        self.__speed = speed