from sr.robot3 import *
import math

robot = Robot()

# Constants
ASTEROID_IDS = [i for i in range(150, 200)]
MID_BASE_ID = robot.zone * 7 + 3
BASE_IDS = [i for i in range(robot.zone * 7, (robot.zone + 1) * 7)]
NUMBER_OF_WALL_MARKERS = 28
EGG_ID = 110
PORT_ID = robot.zone + 120
STARBOARD_ID = robot.zone + 125

# Globals
collected = 0
blackList = []
startTime = robot.time()


# stop the motors
def brake():
    robot.motor_board.motors[0].power = 0
    robot.motor_board.motors[1].power = 0


# drive at a stable pace
def mediumDrive():
    robot.motor_board.motors[0].power = 0.4
    robot.motor_board.motors[1].power = 0.4


# drive backwards at x speed
def backwardsDrive(speed):
    robot.motor_board.motors[0].power = -1 * speed
    robot.motor_board.motors[1].power = -1 * speed


# slow turning, clockwise is true, counter clockwise is false
def slowTurn(clockwise: bool):
    if clockwise == True:
        robot.motor_board.motors[0].power = 0.05
        robot.motor_board.motors[1].power = -0.05
    else:
        robot.motor_board.motors[0].power = -0.05
        robot.motor_board.motors[1].power = 0.05


# fast turning, clockwise is true, counter clockwise is false
def fastTurn(clockwise: bool):
    if clockwise == True:
        robot.motor_board.motors[0].power = 0.1
        robot.motor_board.motors[1].power = -0.1
    else:
        robot.motor_board.motors[0].power = -0.1
        robot.motor_board.motors[1].power = 0.1


# find a desired target marker and return its information
def look(targetid):
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f'look couldnt find {targetid}')
    return None


"""
    target argument may be a list or a integer target id

    returns -1 for 'times up'
    returns marker info for success
"""


# turn counter-clockwise until in line with target, slow turn to a degree of accuracy
def turnSee(target, direction=False):
    if isinstance(target,
                  int):  # If the argument passsed is an integer, convert to a list (this conversion allows for amalgamation of previous turnSee and turnSeeList)
        target = [target, ]

    facing_target = False
    robot.sleep(0.01)
    tempTime = robot.time()
    while facing_target == False:
        # if >5 sec elapsed then reset
        if (robot.time() - tempTime) > 5:
            print('times up')
            return -1
        # if it doesnt see the target than it will turn counter-clockwise until it does
        global looktarget
        looktarget = look(target)
        for item in target:
            looktarget = look(item)
            if looktarget != None:
                break

        if looktarget == None:
            fastTurn(direction)
            robot.sleep(0.1)
            print(f'turnSee could not find {target}')
            continue

        # next 2 elifs are for turning until within a certain angle of accuracy
        if looktarget.position.horizontal_angle < -0.5:
            fastTurn(False)
            robot.sleep(0.05)
            print(looktarget.position.horizontal_angle)
        elif looktarget.position.horizontal_angle > 0.5:
            fastTurn(False)
            robot.sleep(0.05)
            print(looktarget.position.horizontal_angle)
        elif looktarget.position.horizontal_angle < -0.1:
            slowTurn(False)
            robot.sleep(0.05)
            print(looktarget.position.horizontal_angle)
        elif looktarget.position.horizontal_angle > 0.1:
            slowTurn(True)
            robot.sleep(0.05)
            print(looktarget.position.horizontal_angle)
        # is now facing the target, stop turning and end loop
        else:
            print(f'facing target ({target}) \t horiz angle: {looktarget.position.horizontal_angle}')
            brake()
            facing_target = True
    return looktarget


def isAsteroidRetrievable(marker):
    marker_camera_vertical_distance = marker.position.distance * math.sin(marker.position.vertical_angle)
    # If negative, then the marker lies below the camera
    if marker_camera_vertical_distance > 1000:
        print(f'Irretrievable marker no. {marker}; marker_camera_vertical_distance = {marker_camera_vertical_distance}')
        return False
    return True


"""
  Returns closest marker and the direction the robot is currently turning to scan the arena
   => return (closest, clockwise_turn)
"""


def closestAsteroid():
    seen_opposite_left_id = False  # If starting at zone 0, ids in question are 13 and 14
    seen_opposite_right_id = False  # If starting at zone 0, id in question are 20 and 21 (consider 2 for contingency)
    seen_base_middle_id = False  # Added contingency
    asteroids = []
    clockwise_turn = False  # which way to turn for scanning of arena

    while not (seen_opposite_left_id and seen_opposite_right_id) or not seen_base_middle_id:

        if seen_opposite_left_id and not seen_opposite_right_id:
            clockwise_turn = True
        elif seen_opposite_right_id and not seen_opposite_left_id:
            clockwise_turn = False

        fastTurn(clockwise_turn)

        listmarkers = robot.camera.see()
        for marker in listmarkers:
            if marker.id in blackList:
                break
            if marker.id == (((robot.zone + 2) % 4) * 7) or marker.id == (
                    ((robot.zone + 2) % 4) * 7 - 1) % NUMBER_OF_WALL_MARKERS:
                seen_opposite_left_id = True
                print("seen opposite left")
            if marker.id == (((robot.zone + 3) % 4) * 7) or marker.id == (
                    ((robot.zone + 3) % 4) * 7 - 1) % NUMBER_OF_WALL_MARKERS:
                seen_opposite_right_id = True
                print("seen opposite right")
            if marker.id == MID_BASE_ID:
                seen_base_middle_id = True
            if marker.id in ASTEROID_IDS and isAsteroidRetrievable(marker):
                asteroids.append(marker)

    brake()
    if len(asteroids) == 0:
        print("closestAsteroid couldnt find anything")
        return None

    closest = None
    for marker in asteroids:
        if closest == None:
            closest = marker
        if marker.position.distance < closest.position.distance:
            closest = marker
    return (closest, clockwise_turn)


def untilUnsee(target_id):
    print('untilunsee')
    lost_sight_of_target = False
    while lost_sight_of_target == False:
        # set target asteroid information to temp variable, in case it cannot see it later
        moment = look(target_id)
        # if it doesnt see the target asteroid then stop and exit loop
        if moment == None:
            robot.sleep(0.1)
            brake()
            lost_sight_of_target = True
        else:
            # keep moving
            robot.sleep(0.1)
            # course correction
            if moment.position.horizontal_angle < -0.1:
                slowTurn(False)
                robot.sleep(0.01)
                print(moment.position.horizontal_angle)
            elif moment.position.horizontal_angle > 0.1:
                slowTurn(True)
                robot.sleep(0.01)
                print(moment.position.horizontal_angle)
            else:
                # keep going at 0.3 power and print current angle
                print(f'facing target ({moment.id}) \t horiz angle: {moment.position.horizontal_angle}')
                mediumDrive()


def correctDrive(targetid, distance):
    arrived_at_target = False
    tempTime = robot.time()
    while arrived_at_target == False:
        if (robot.time() - tempTime) > 10:
            print('times up')
            drop()
            backwardsDrive(0.5)
            robot.sleep(0.9)
            brake()
            reset()
        # set target marker (ship) information to temp variable, in case it cannot see it later
        target = look(targetid)
        # if it doesnt see the marker than just break out, better to muck up once than to have an error and just obliterate the whole robot
        if target == None:
            print('correctDrive can\'t find target marker')
            brake()
            turnSee(targetid)
        # stop if it gets close to the target
        elif target.position.distance < distance:
            brake()
            arrived_at_target = True
        else:
            # course correction
            if target.position.horizontal_angle < -0.1:
                slowTurn(False)
                robot.sleep(0.01)
                print(target.position.horizontal_angle)
            elif target.position.horizontal_angle > 0.1:
                slowTurn(True)
                robot.sleep(0.01)
                print(target.position.horizontal_angle)
            else:
                # drive at 0.3 power and print distance to marker
                robot.sleep(0.1)
                mediumDrive()
                print(f'{target.position.distance}mm to {target.id}')


def spaceshipDeposit(spaceship_id):
    print('going to spaceship')

    # drive forward
    mediumDrive()

    correctDrive(spaceship_id, 600)
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


def planetDeposit():
    print("going to planet for deposition")

    for i in range(3, 7):
        if turnSee(BASE_IDS[i], True) != -1:
            correctDrive(BASE_IDS[i], 500)
            break

    brake()

    drop()


# Returns a list of distances between the base markers and a target marker
def baseMarkerDistanceFinder(target_marker):
    marker_target_distances = []
    for base_id in BASE_IDS:
        base_marker = look(base_id)
        if base_marker == None:
            continue
        distance_to_base_id = base_marker.position.distance
        marker_target_distances.append(abs(distance_to_base_id - target_marker.position.distance))
    return marker_target_distances


# TO DO
def eggMover(direction_of_turn):
    print("Moving egg out of base")
    mediumDrive()
    robot.sleep(0.3)
    # get previous asteroid carried out of the way
    brake()
    drop()
    backwardsDrive(0.5)
    robot.sleep(0.3)
    brake()
    fastTurn(True)
    robot.sleep(0.7)
    mediumDrive()
    robot.sleep(2)
    brake()

    turnSee(EGG_ID, not direction_of_turn)
    # move forward
    mediumDrive()
    # drive forward until no longer able to see asteroid
    untilUnsee(EGG_ID)

    grab()

    # Do 10 or 24 from the POV of zone 0 (whichever is seen first)
    neither_arena_marker_seen = True
    while neither_arena_marker_seen:
        arena_marker1 = look((((robot.zone + 1) % 4) * 7 + 3) % NUMBER_OF_WALL_MARKERS)
        arena_marker2 = look((((robot.zone + 3) % 4) * 7 + 3) % NUMBER_OF_WALL_MARKERS)
        if arena_marker1 == None and arena_marker2 == None:
            fastTurn(True)
        else:
            neither_arena_marker_seen = False
    print(arena_marker1)
    print(arena_marker2)
    if arena_marker1 == None:
        chosen_arena_marker = arena_marker2
    elif arena_marker2 == None:
        chosen_arena_marker = arena_marker1
    elif arena_marker1.position.distance > arena_marker2.position.distance:
        chosen_arena_marker = arena_marker2
    else:
        chosen_arena_marker = arena_marker1

    correctDrive(chosen_arena_marker.id, 800)
    robot.sleep(0.2)
    drop()
    robot.sleep(0.2)
    backwardsDrive(0.5)
    robot.sleep(0.9)
    brake()

    #reset()
    return


"""
  Returns whether egg is arena and the direction the robot is currently turning to scan the base
   => return (is_egg_in_base, clockwise_turn)
"""


def eggChecker():
    seen_base_left_id = False  # If starting at zone 0, ids in question are 27, 0, 1 (consider 3 for extra contingency)
    seen_base_right_id = False  # If starting at zone 0, id in question are 5, 6, 7 (consider 3 for extra contingency)
    is_egg_in_base = False
    while not (seen_base_left_id and seen_base_right_id):
        clockwise_turn = False  # which way to turn for scanning of arena
        if seen_base_left_id and not seen_base_right_id:
            clockwise_turn = True
        elif seen_base_right_id and not seen_base_left_id:
            clockwise_turn = False
        fastTurn(clockwise_turn)

        listmarkers = robot.camera.see()
        for marker in listmarkers:
            if marker.id == (BASE_IDS[0] - 1) % NUMBER_OF_WALL_MARKERS or marker.id == BASE_IDS[0] or marker.id == \
                    BASE_IDS[1]:
                seen_base_left_id = True
            if marker.id == (BASE_IDS[0] + 1) % NUMBER_OF_WALL_MARKERS or marker.id == BASE_IDS[-1] or marker.id == \
                    BASE_IDS[-2]:
                seen_base_right_id = True
            if marker.id == EGG_ID:
                # Check if the egg is near our base using difference in distances between each base marker and the egg marker
                if len(list(filter(lambda distance: distance < 300, baseMarkerDistanceFinder(marker)))) > 0:
                    print("EGG IN BASE!!!")
                    is_egg_in_base = True
                    return (is_egg_in_base, clockwise_turn)
    return (is_egg_in_base, clockwise_turn)


def reset():
    maincycle()


def grab():
    # lowering forklift here
    robot.servo_board.servos[2].position = -1
    robot.sleep(0.7)

    # read distance to sensor using s o n a r woah
    robot.arduino.pins[A4].mode = INPUT
    distance_to_closest_from_grabber = robot.arduino.pins[A4].analog_read()

    print(f'{distance_to_closest_from_grabber}m from sensor')
    # sometimes this reads 5m even though the box is right in front of it :shrug:
    # no clue why

    if distance_to_closest_from_grabber == 0.5:
        print('distance is 5m')
        robot.sleep(0.01)

    # grab box
    robot.servo_board.servos[0].position = 0.6
    robot.servo_board.servos[1].position = 0.6
    robot.sleep(0.6)

    # lift up with forklift a bit
    robot.servo_board.servos[2].position = -0.8
    robot.sleep(0.3)


def drop():
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


# choose asteroid, go to asteroid, go to base, go to spaceship, put asteroid in spaceship, repeat
def maincycle():
    # lift up the forklift a bit to ensure no collision with raised platform/other boxes
    # lowered this a bit because box pickup interferred a bit with vision
    robot.servo_board.servos[2].position = -0.2
    robot.servo_board.servos[0].position = -1
    robot.servo_board.servos[1].position = -1

    # set a target asteroid to pick up
    asteroid_info = closestAsteroid()
    firstasteroid = asteroid_info[0]

    asteroid_direction_of_turn = not asteroid_info[1]

    # if it didnt see an asteroid, it will turn counter-clockwise until it does and set that as its target
    while firstasteroid == None:
        print('I did not see an asteroid to target')
        slowTurn(False)
        robot.sleep(0.1)
        asteroid_info = closestAsteroid()
        firstasteroid = asteroid_info[0]
        asteroid_direction_of_turn = not asteroid_info[
            1]  # if we turned CW to scan the arena, we turn CCW to find the asteroid
    print(
        f'I have set {firstasteroid.id} as the target asteroid. To reach this asteroid I will turn clockwise = {asteroid_direction_of_turn}')
    print(f'The target asteroid has these stats: {firstasteroid}')

    #add current asteroid to list of blacklisted asteroids so that robot doesnt target already retrieved asteroids such as those in the spaceship
    blackList.append(firstasteroid.id)

    # turn until it is in line with the target asteroid
    turnSee(firstasteroid.id, asteroid_direction_of_turn)

    # move forward
    mediumDrive()

    # drive forward until no longer able to see asteroid
    untilUnsee(firstasteroid.id)

    grab()

    egg_info = eggChecker()
    is_egg_in_base = egg_info[0]
    egg_direction_of_turn = not egg_info[1]

    if is_egg_in_base:
        eggMover(egg_direction_of_turn)


    seeLeftBase = turnSee(BASE_IDS[2], egg_direction_of_turn)
    if seeLeftBase == -1:
        seeMid = turnSee(BASE_IDS)
        if seeMid != -1:
            correctDrive(seeMid.id, 500)
    else:
        print(f'going to {BASE_IDS[2]} (base)')
        correctDrive(BASE_IDS[2], 500)


    robot.sleep(0.2)

    # go to spaceship
    seeSpaceship = turnSee([PORT_ID, STARBOARD_ID], False)
    spaceship_marker = look(seeSpaceship.id)

    '''# For each base marker seen, calculate distance between the base marker and the port marker. 
    # If all of these distances are over 300, then the spaceship is considered out of our base
    marker_spaceship_distances = baseMarkerDistanceFinder(spaceship_marker)
    print(f'spaceship markers {marker_spaceship_distances}')
    marker_spaceship_distances_under_300 = list(filter(lambda distance : distance < 300, marker_spaceship_distances))

    print("Distance between base marker(s) and spaceship:", marker_spaceship_distances_under_300)'''

    if seeSpaceship == -1 or spaceship_marker.position.distance > 1000:  # If can't find spaceship or if it is too far from robot
        print(f'spaceship distance {spaceship_marker.position.distance}')
        print('depositing in planet')
        planetDeposit()
    else:
        print('depositing in spaceship')
        spaceshipDeposit(spaceship_marker.id)

    print('turning')
    fastTurn(False)

    robot.sleep(0.9)


# game time is 150 seconds
while True:
    currentProgram = maincycle()