from sr.robot3 import *
robot = Robot()

#all marker ids of asteroids in an epic list
asteroidid = [i for i in range(150, 200)]



#stop the motors
def brake():
    robot.motor_board.motors[0].power = 0
    robot.motor_board.motors[1].power = 0

#drive at a stable pace
def mediumDrive():
    robot.motor_board.motors[0].power = 0.3
    robot.motor_board.motors[1].power = 0.3

#drive backwards at x speed
def backwardsDrive(speed):
    robot.motor_board.motors[0].power = -1*speed
    robot.motor_board.motors[1].power = -1*speed

#clockwise is true
#counter clockwise is false
#slow turning
def slowTurn(leftright: bool):
    if leftright == True:
        robot.motor_board.motors[0].power = 0.05
        robot.motor_board.motors[1].power = -0.05
    else:
        robot.motor_board.motors[0].power = -0.05
        robot.motor_board.motors[1].power = 0.05

#clockwise is true
#counter clockwise is false
#faster turning
def fastTurn(leftright: bool):
    if leftright == True:
        robot.motor_board.motors[0].power = 0.1
        robot.motor_board.motors[1].power = -0.1
    else:
        robot.motor_board.motors[0].power = -0.1
        robot.motor_board.motors[1].power = 0.1


#look at all of the markers and only return those that are asteroids
def firstAsteroid():
    asteroids = []
    listmarkers = robot.camera.see()
    cycle = 0
    for marker in listmarkers:
        if marker.id in asteroidid:
            asteroids.append(marker)
    #print(f'i see asteroids: {asteroids}')
    if len(asteroids) > 0:
        print(f'i see {asteroids[0]} first')
        return asteroids[0]
    else:
        print('i dont see any asteroids')
        return None


#find a desired target marker and return its information
def look(targetid):
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f'couldnt find {targetid}')
    return None


#turn counter-clockwise until in line with target, slow turn to a degree of accuracy
def turnSee(target):
    #satisfy is the name of the temp variable i use for while loops, i will find a better way another time
    satisfy = False

    robot.sleep(0.01)

    while satisfy == False:

        #if it doesnt see the target than it will turn counter-clockwise until it does
        looktarget = look(target)

        if looktarget == None:
            fastTurn(False)
            robot.sleep(0.1)
        #next 2 elifs are for turning until within a certain angle of accuracy
        elif looktarget.position.horizontal_angle < -0.1:
            slowTurn(False)
            robot.sleep(0.001)
            print(looktarget.position.horizontal_angle)
        elif looktarget.position.horizontal_angle > 0.1:
            slowTurn(True)
            robot.sleep(0.001)
            print(looktarget.position.horizontal_angle)
        #is now facing the target, stop turning and end loop
        else:
            print(looktarget.position.horizontal_angle)
            print(f'facing target ({target})')
            brake()
            satisfy = True


def untilUnsee(target):
    print('untilunsee')
    # reset the silly loop condition
    satisfy = False
    #epic loop condition
    while satisfy == False:
        #set target asteroid information to temp variable, in case it cannot see it later
        moment = look(target.id)
        #if it doesnt see the target asteroid then stop and exit loop
        if  moment == None:
            robot.sleep(0.1)
            brake()
            satisfy = True
        else:
            #keep moving
            robot.sleep(0.1)
            #course correction
            if moment.position.horizontal_angle < -0.1:
                slowTurn(False)
                robot.sleep(0.01)
                print(moment.position.horizontal_angle)
            elif moment.position.horizontal_angle > 0.1:
                slowTurn(True)
                robot.sleep(0.01)
                print(moment.position.horizontal_angle)
            else:
                #keep going at 0.3 power and print current angle
                print(moment.position.horizontal_angle)
                print(f'facing target ({moment.id})')
                mediumDrive()


def correctDrive(targetid, distance):
    # reset funny loop condition
    lowered = False
    satisfy = False
    while satisfy == False:
        #set target marker (ship) information to temp variable, in case it cannot see it later
        target = look(targetid)
        #if it doesnt see the marker than just break out, better to muck up once than to have an error and just obliterate the whole robot
        if target == None:
            print('dont see')
            brake()
            #break - just waits now, maybe put a turnSee
            turnSee(targetid)
        #stop if it gets close to the ship
        elif target.position.distance < distance:
            brake()
            satisfy = True
        # lower down the forklift in case it gets too close to see over the box potentially
        elif target.position.distance < distance + 200 and lowered == False:
            robot.servo_board.servos[2].position = -0.4
            brake()
            robot.sleep(0.5)
            lowered = True
            mediumDrive()
        else:
            #course correction
            if target.position.horizontal_angle < -0.1:
                slowTurn(False)
                robot.sleep(0.05)
                print(target.position.horizontal_angle)
            elif target.position.horizontal_angle > 0.1:
                slowTurn(True)
                robot.sleep(0.05)
                print(target.position.horizontal_angle)
            else:
                #drive at 0.3 power and print distance to marker
                robot.sleep(0.1)
                mediumDrive()
                print(f'{target.position.distance}mm to {target.id}')


#choose asteroid, go to asteroid, go to base, go to spaceship, put asteroid in spaceship, repeat
def maincycle():
    correctDrive(1, 700)
    correctDrive(2, 700)
    correctDrive(3, 700)
    correctDrive(4, 700)






