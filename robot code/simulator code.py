from sr.robot3 import *
import math
robot = Robot()

#all marker ids of asteroids in an epic list
ASTEROID_IDS = [i for i in range(150, 200)]
MID_BASE_ID = robot.zone * 7 + 3
BASE_IDS = [i for i in range(robot.zone * 7, (robot.zone + 1) * 7)]
collected = 0
startTime = robot.time()


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


#slow turning, clockwise is true, counter clockwise is false
def slowTurn(clockwise: bool):
    if clockwise == True:
        robot.motor_board.motors[0].power = 0.05
        robot.motor_board.motors[1].power = -0.05
    else:
        robot.motor_board.motors[0].power = -0.05
        robot.motor_board.motors[1].power = 0.05

#fast turning, clockwise is true, counter clockwise is false
def fastTurn(clockwise: bool):
    if clockwise == True:
        robot.motor_board.motors[0].power = 0.1
        robot.motor_board.motors[1].power = -0.1
    else:
        robot.motor_board.motors[0].power = -0.1
        robot.motor_board.motors[1].power = 0.1


#look at all of the markers and only return those that are asteroids
def firstAsteroid():
    asteroids = list(filter(lambda marker : (marker.id in ASTEROID_IDS and isAsteroidRetrievable(marker)), robot.camera.see()))
    if len(asteroids) > 0:
        print(f'i see {asteroids[0]} first')
        return asteroids[0]
    else:
        print('i dont see any asteroids')
        return None

def firstWallMarkers():
    wallMarkers = list(filter(lambda marker : (marker.id in BASE_IDS), robot.camera.see()))
    if len(wallMarkers) > 0:
        print(f'i see {wallMarkers[0]} first')
        return wallMarkers[0]
    else:
        print('i dont see any of our wall markers')
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
    target = [target,]
    #satisfy is the name of the temp variable i use for while loops, i will find a better way another time
    satisfy = False
    hasbeenseen = False

    robot.sleep(0.01)
    tempTime = robot.time()
    while satisfy == False:
        #if >10 sec elapsed then reset
        if (robot.time() - tempTime) > 10:
            print('times up')
            return -1
        #if it doesnt see the target than it will turn counter-clockwise until it does
        global looktarget
        looktarget = look(target)
        for item in target:
            looktarget = look(item)
            if looktarget != None:
                break

        if looktarget == None:
            fastTurn(False)
            robot.sleep(0.1)
            print(f'could not find {target}')

        #need to find a way to make it deposit into area if it cannot find the spaceship
        #something like if target == spaceship and done 360 == true: goToMidAndDeposItInArea()

        #next 2 elifs are for turning until within a certain angle of accuracy
        elif looktarget.position.horizontal_angle < -0.1:
            hasbeenseen = True
            slowTurn(False)
            robot.sleep(0.05)
            print(looktarget.position.horizontal_angle)
        elif looktarget.position.horizontal_angle > 0.1:
            hasbeenseen = True
            slowTurn(True)
            robot.sleep(0.05)
            print(looktarget.position.horizontal_angle)
        #is now facing the target, stop turning and end loop
        else:
            hasbeenseen = True
            print(looktarget.position.horizontal_angle)
            print(f'facing target ({target})')
            brake()
            satisfy = True
    return looktarget


def allAsteroid():
    seenArenaWall = 0
    while seenArenaWall < 2:
        asteroids = []
        listmarkers = robot.camera.see()
        cycle = 0
        for marker in listmarkers:
            if marker.id in ASTEROID_IDS:
                asteroids.append(marker)
            if marker.id == MID_BASE_ID:
                seenArenaWall += 1
    return listmarkers

def isAsteroidRetrievable(marker):
    marker_camera_vertical_distance = marker.position.distance * math.sin(marker.position.vertical_angle)
    # If negative, then the marker lies below the camera
    if marker_camera_vertical_distance > 1000:
        print(f'IRRETRIEVABLE marker no. {marker}; marker_camera_vertical_distance = {marker_camera_vertical_distance}')
        return False
    return True

def closestAsteroid():
    seen_opposite_left_id = False # If starting at zone 0, ids in question are 13 and 14
    seen_opposite_right_id = False # If starting at zone 0, id in question are 20 and 21 (consider 2 for contingency)
    asteroids = []
    while (not seen_opposite_left_id) and (not seen_opposite_right_id):
        fastTurn(False)
        listmarkers = robot.camera.see()
        for marker in listmarkers:
            if marker.id == ((robot.zone + 2) * 7) or ((robot.zone + 2) * 7 - 1):
                seen_opposite_left_id = True
            if marker.id == ((robot.zone + 3) * 7) or ((robot.zone + 2) * 7 - 1):
                seen_opposite_right_id = True
            if marker.id in ASTEROID_IDS and isAsteroidRetrievable(marker):
                asteroids.append(marker)

    brake()
    if len(asteroids) == 0:
        print("couldnt find anything")
        return None

    closest = None
    for marker in asteroids:
        if closest == None:
            closest = marker
        if marker.position.distance < closest.position.distance:
            closest = marker
    return closest



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
        else:
            #course correction
            if target.position.horizontal_angle < -0.1:
                slowTurn(False)
                robot.sleep(0.01)
                print(target.position.horizontal_angle)
            elif target.position.horizontal_angle > 0.1:
                slowTurn(True)
                robot.sleep(0.01)
                print(target.position.horizontal_angle)
            else:
                #drive at 0.3 power and print distance to marker
                robot.sleep(0.1)
                mediumDrive()
                print(f'{target.position.distance}mm to {target.id}')



def spaceshipDeposit():
    print('going to spaceship')

    # drive forward
    mediumDrive()

    correctDrive(robot.zone + 120, 600)
    print('finished correct driving')

    robot.sleep(0.2)

    # deposit into ship sequence
    print('raising')
    robot.servo_board.servos[2].position = 1

    robot.sleep(2)

    # drive a little forward
    robot.motor_board.motors[0].power = 0.2
    robot.motor_board.motors[1].power = 0.2

    robot.sleep(1.6)

    brake()
    global collected
    # effecient stacking
    print(f'i have collected {collected} asteroids so far')
    if collected % 2 == 0:
        print('depositing to 1')
        fastTurn(True)
        robot.sleep(0.2)
        brake()

    else:
        print('depositing to 2')
        fastTurn(False)
        robot.sleep(0.2)
        brake()

    # fully open pincers
    print('release')
    robot.servo_board.servos[0].position = -1
    robot.servo_board.servos[1].position = -1

    collected += 1

    robot.sleep(1)

    backwardsDrive(0.5)

    robot.sleep(1)

    brake()

    robot.servo_board.servos[2].position = -0.2



def reset():
    maincycle()


#choose asteroid, go to asteroid, go to base, go to spaceship, put asteroid in spaceship, repeat
def maincycle():

    #lift up the forklift a bit to ensure no collision with raised platform/other boxes
    #lowered this a bit because box pickup interferred a bit with vision
    robot.servo_board.servos[2].position = -0.2
    robot.servo_board.servos[0].position = -1
    robot.servo_board.servos[1].position = -1

    #set a target asteroid to pick up
    firstasteroid = closestAsteroid()


    #if it didnt see an asteroid, it will turn counter-clockwise until it does and set that as its target
    while firstasteroid == None:
        print('I did not see an asteroid to target')
        slowTurn(False)
        robot.sleep(0.1)
        firstasteroid = closestAsteroid()
    print(f'I have set {firstasteroid.id} as the target asteroid')
    print(f'The target asteroid has these stats: {firstasteroid}')

    #turn until it is in line with the target asteroid
    turnSee(firstasteroid.id)

    #move forward
    mediumDrive()

    #drive forward until no longer able to see asteroid
    untilUnsee(firstasteroid)
    
    #lowering forklift here
    robot.servo_board.servos[2].position = -1
    robot.sleep(0.7)

    #read distance to sensor using s o n a r woah
    robot.arduino.pins[A4].mode = INPUT
    distance_to_closest_from_grabber = robot.arduino.pins[A4].analog_read()

    print(f'{distance_to_closest_from_grabber}m from sensor')
    #sometimes this reads 5m even though the box is right in front of it :shrug:
    #no clue why

    if distance_to_closest_from_grabber == 0.5:
        print('distance is 5m')
        robot.sleep(0.01)

    #grab code
    #should make these numbers a little smaller since it will squish the box to death
    #it goes from -1 to 1 btw
    #could make effecient box stacking by moving from side to side so that it doesnt overflow so easily

    #grab box
    robot.servo_board.servos[0].position = 0.6
    robot.servo_board.servos[1].position = 0.6

    robot.sleep(0.6)

    #lift up with forklift a bit
    robot.servo_board.servos[2].position = -0.8

    #robot.sleep(1.2)
    
    seeLeftBase = turnSee(BASE_IDS[2])
    if seeLeftBase == -1:
        seeMid = turnSee(BASE_IDS)
        if seeMid != -1:
            correctDrive(seeMid.id, 500)
    else:
        print(f'going to {BASE_IDS[2]} (base)')
        correctDrive(BASE_IDS[2], 500)


    #robot.servo_board.servos[2].position = -0.4

    robot.sleep(0.5)

    # go to spaceship
    seeSpaceship = turnSee(robot.zone + 120)
    if seeSpaceship != -1:
        #deposit in spaceship
        spaceshipDeposit()
    elif seeSpaceship == -1:
        #deposit in planet
        #turn and drive a bit to avoid obscuring the MID_BASE_ID marker
        fastTurn(True)
        robot.sleep(1)
        # drive a little forward
        robot.motor_board.motors[0].power = 0.2
        robot.motor_board.motors[1].power = 0.2

        robot.sleep(1.6)

        brake()

        print('release')
        robot.servo_board.servos[0].position = -1
        robot.servo_board.servos[1].position = -1
        global collected
        collected += 1

        robot.sleep(1)

        backwardsDrive(0.5)

        robot.sleep(1)

        brake()

        robot.servo_board.servos[2].position = -0.2



    print('turning')
    fastTurn(False)

    robot.sleep(0.9)


#game time is 150 seconds
while True:
    currentProgram = maincycle()