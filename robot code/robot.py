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
        robot.motor_board.motors[0].power = 0.01
        robot.motor_board.motors[1].power = -0.01
    else:
        robot.motor_board.motors[0].power = -0.01
        robot.motor_board.motors[1].power = 0.01

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


#choose asteroid, go to asteroid, go to base, go to spaceship, put asteroid in spaceship, repeat
def maincycle(collected):

    #the middle of out base area's marker - if you are area 3 then your middle is 26
    mid = robot.zone * 7 + 3

    #lift up the forklift a bit to ensure no collision with raised platform/other boxes
    robot.servo_board.servos[2].position = -0.2

    #set a target asteroid to pick up
    firstasteroid = firstAsteroid()


    #if it didnt see an asteroid, it will turn counter-clockwise until it does and set that as its target
    while firstasteroid == None:
        print('I did not see an asteroid to target')
        slowTurn(False)
        robot.sleep(0.1)
        firstasteroid = firstAsteroid()
    print(f'I have set {firstasteroid.id} as the target asteroid')
    print(f'The target asteroid has these stats: {firstasteroid}')

    #turn until it is in line with the target asteroid
    turnSee(firstasteroid.id)

    #move forward
    mediumDrive()

    #drive forward until no longer able to see asteroid
    untilUnsee(firstasteroid)

    robot.sleep(0.5)

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
    #lower forklift
    robot.servo_board.servos[2].position = -1

    robot.sleep(1)

    #grab box
    robot.servo_board.servos[0].position = 0.6
    robot.servo_board.servos[1].position = 0.6

    robot.sleep(1)

    #lift up with forklift a bit
    robot.servo_board.servos[2].position = -0.2

    robot.sleep(2)

    turnSee(mid)

    print('going to mid')
    correctDrive(mid, 500)

    robot.sleep(0.5)

    print('going to spaceship')

    #go to spaceship
    turnSee(robot.zone+120)

    #drive forward
    mediumDrive()

    correctDrive(robot.zone + 120, 600)
    print('finished correct driving')

    robot.sleep(0.2)

    #deposit into ship sequence
    print('raising')
    robot.servo_board.servos[2].position = 1

    robot.sleep(2)

    #drive a little forward
    robot.motor_board.motors[0].power = 0.2
    robot.motor_board.motors[1].power = 0.2

    robot.sleep(1.6)

    brake()

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

    #fully open pincers
    print('release')
    robot.servo_board.servos[0].position = -1
    robot.servo_board.servos[1].position = -1

    robot.sleep(1)

    collected += 1

    backwardsDrive(0.5)

    robot.sleep(1)

    brake()

    robot.servo_board.servos[2].position = -0.2

    print('turning')
    fastTurn(False)

    robot.sleep(0.9)

    return collected




#just repeat forever - do things here for stuff such as contingencys or returning to base at time limit
#collected is a variable that stores the number of times it has run the maincycle function
#did this since you cant change global variables from within a function
collected = 0
while True:
    collected = maincycle(collected)
