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
    print(f"Driving at med power")
    robot.motor_board.motors[0].power = 0.4
    robot.motor_board.motors[1].power = 0.4

def speedDrive(speed):
    robot.motor_board.motors[0].power = speed
    robot.motor_board.motors[1].power = speed

def rampDrive(ramp_speed_start, speed=1):
    power = (robot.time() - ramp_speed_start) * 2 # Ramp speed up
    if power >= speed:
        speedDrive(speed)
    else:
        speedDrive(power)

# drive backwards at x speed
def backwardsDrive(speed):
    robot.motor_board.motors[0].power = -1 * speed
    robot.motor_board.motors[1].power = -1 * speed


# slow turning, clockwise is true, counter clockwise is false
def slowTurn(clockwise: bool):
    if clockwise == True:
        robot.motor_board.motors[0].power = 0.01
        robot.motor_board.motors[1].power = -0.01
    else:
        robot.motor_board.motors[0].power = -0.01
        robot.motor_board.motors[1].power = 0.01

def mediumTurn(clockwise: bool):
    if clockwise == True:
        robot.motor_board.motors[0].power = 0.15
        robot.motor_board.motors[1].power = -0.15
    else:
        robot.motor_board.motors[0].power = -0.15
        robot.motor_board.motors[1].power = 0.15

# fast turning, clockwise is true, counter clockwise is false
def fastTurn(clockwise: bool):
    if clockwise == True:
        robot.motor_board.motors[0].power = 0.5
        robot.motor_board.motors[1].power = -0.5
    else:
        robot.motor_board.motors[0].power = -0.5
        robot.motor_board.motors[1].power = 0.5


# find a desired target marker and return its information
# ⇒ return None if not found, return marker if found
def look(targetid):
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f'look couldnt find {targetid}')
    return None


# Returns True if facing target, False if not
# Default value of 0.15 for threshold, in which case it uses mediumTurn
def accurateTurn(target, threshold = 0.15):
    if threshold > 0.1:
        med_threshold = threshold
    else:
        med_threshold = 2*threshold

    if target.position.horizontal_angle < -0.5:
        fastTurn(False)
        print(target.position.horizontal_angle)
    elif target.position.horizontal_angle > 0.5:
        fastTurn(True)
        print(target.position.horizontal_angle)
    elif target.position.horizontal_angle < -med_threshold:
        mediumTurn(False)
        print(target.position.horizontal_angle)
    elif target.position.horizontal_angle > med_threshold:
        mediumTurn(True)
        print(target.position.horizontal_angle)
    elif target.position.horizontal_angle < -threshold:
        slowTurn(False)
        print(target.position.horizontal_angle)
    elif target.position.horizontal_angle > threshold:
        slowTurn(True)
        print(target.position.horizontal_angle)
    else:
        return True
    return False


"""
    turn counter-clockwise until in line with target, slow turn to a degree of accuracy
    target argument may be a list or a integer target id

    ⇒ returns -1 for 'times up'
    ⇒ returns marker info for success
"""
def turnSee(target, direction=False, accurate=True):
    print(f"Turning to {target}, with clockwise direction = {direction}, and accurate = {accurate}")
    robot.sleep(0.1) # Allow for braking to have settled the robot
    if isinstance(target, int):  # If the argument passsed is an integer, convert to a list (this conversion allows for amalgamation of previous turnSee and turnSeeList)
        target = [target, ]

    facing_target = False
    tempTime = robot.time()
    seen_base = False
    seen_opposite = False
    made_a_rev = False
    while facing_target == False:
        # if >5 sec elapsed then reset
        if (robot.time() - tempTime) > 5:
            print('turnSee() times up')
            return -1
        # if it doesnt see the target than it will turn counter-clockwise until it does
        global looktarget
        for item in target:
            looktarget = look(item)
            if looktarget != None:
                brake()
                break

        if looktarget == None:
            fastTurn(direction)
            print(f'turnSee could not find {target}')
            if look(MID_BASE_ID) != None:
                seen_base = True
                print("seen base")
            elif look(((robot.zone + 2) % 4) * 7 + 3) != None or look(((robot.zone + 2) % 4) * 7 + 1) != None or look(((robot.zone + 2) % 4) * 7 + 5) != None:
                seen_opposite = True
                print("seen opposite")
            if seen_base and seen_opposite:
                seen_base = False
                seen_opposite = False
                made_a_rev = True
                print("Made a full revolution w/o seeing target")
            if made_a_rev and seen_opposite:
                print("Fail (revolution made w/o target)")
                return -1
            continue

        # Accurately turn to target. If facing, stop turning & end loop
        # The first time you turn, turn more accurately to prevent robot stopping and turning every second just to be within the 0.1 threshold
        if accurate:
            threshold = 0.05
        else:
            threshold = 0.3
        print(f"turning to {threshold} accuracy", end='\t')
        if accurateTurn(looktarget, threshold):
            brake()
            facing_target = True
    print(f'turnSee() facing target ({target}) \t horiz angle: {looktarget.position.horizontal_angle}')
    return looktarget


# ⇒ True/False return
def isAsteroidRetrievable(marker):
    marker_camera_vertical_distance = marker.position.distance * math.sin(marker.position.vertical_angle)
    # If negative, then the marker lies below the camera
    if marker_camera_vertical_distance > 1200:
        print(f'Irretrievable marker no. {marker}; marker_camera_vertical_distance = {marker_camera_vertical_distance}')
        return False
    return True


"""
  Returns closest marker and the direction the robot is currently turning to scan the arena
   => return (closest, clockwise_turn)
   ⇒ returns None if it can't find anything
   ⇒ returns -1 if times up
"""
def closestAsteroid():
    print("closestAsteroid()")
    seen_opposite_left_id = False  # If starting at zone 0, ids in question are 13 and 14
    seen_opposite_right_id = False  # If starting at zone 0, id in question are 20 and 21 (consider 2 for contingency)
    seen_base_middle_id = False  # Added contingency
    asteroids = []
    clockwise_turn = False  # which way to turn for scanning of arena
    tempTime = robot.time()

    while not ((seen_opposite_left_id and seen_opposite_right_id) or seen_base_middle_id):
        
        if (robot.time() - tempTime) > 5:
            print('closesAsteroid() times up')
            return -1
        
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
            if marker.id == (((robot.zone + 3) % 4) * 7) or marker.id == (
                    ((robot.zone + 3) % 4) * 7 - 1) % NUMBER_OF_WALL_MARKERS:
                seen_opposite_right_id = True
            if marker.id == MID_BASE_ID:
                seen_base_middle_id = True
            if marker.id in ASTEROID_IDS and isAsteroidRetrievable(marker):
                asteroids.append(marker)

    if len(asteroids) == 0:
        print("closestAsteroid() couldnt find anything")
        return None

    brake()

    closest = None
    for marker in asteroids:
        if closest == None:
            closest = marker
        if marker.position.distance < closest.position.distance:
            closest = marker
    return (closest, clockwise_turn)


# ⇒ returns -1 for times up
def untilUnsee(target_id):
    print(f'untilUnsee({target_id})')
    lost_sight_of_target = False
    ramp_speed_start = None
    tempTime = robot.time()
    while lost_sight_of_target == False:

        if (robot.time() - tempTime) > 10:
            print('times up')
            return -1
        
        # set target asteroid information to temp variable, in case it cannot see it later
        moment = look(target_id)
        # if it doesnt see the target asteroid then stop and exit loop
        if moment == None:
            robot.sleep(0.2)
            brake()
            lost_sight_of_target = True
            return
        elif accurateTurn(moment, 0.12): # Course correction
            if ramp_speed_start == None:
                ramp_speed_start = robot.time()
            if moment.position.distance > 500:
                rampDrive(ramp_speed_start, 1)
            else:
                rampDrive(ramp_speed_start, 0.4)
        else: # If had to turn, then reset ramping
            ramp_speed_start = None
    return


# Returns -1 for a fail caused by targetid disappearing
# Brakes and returns None when completed
# Resets if times up
def correctDrive(targetid, distance):
    print(f"correctDrive({targetid}, {distance})")
    arrived_at_target = False
    tempTime = robot.time()
    ramp_speed_start = None
    while arrived_at_target == False:
        if (robot.time() - tempTime) > 10:
            print('times up')
            drop()
            backwardsDrive(0.5)
            robot.sleep(0.9)
            brake()
            reset()
            return
        # set target marker (ship) information to temp variable, in case it cannot see it later
        target = look(targetid)
        # if it doesnt see the marker than just break out, better to muck up once than to have an error and just obliterate the whole robot
        if target == None:
            print('correctDrive can\'t find target marker')
            brake()
            if turnSee(targetid) == -1:
                print(f"{targetid} disappeared?")
                return -1
        # stop if it gets close to the target
        elif target.position.distance < distance:
            brake()
            arrived_at_target = True
        elif accurateTurn(target): # Course correction
            if ramp_speed_start == None:
                ramp_speed_start = robot.time()
            if target.position.distance > 1.5*distance:
                rampDrive(ramp_speed_start, 1)
            else:
                rampDrive(ramp_speed_start, 0.4)
            # print(f'{target.position.distance}mm to {target.id}, power max = {(robot.time() - ramp_speed_start)*4} or lower')
        else:  # If had to turn, then reset ramping
            ramp_speed_start = None


# receives list of pins and target distance
# returns -1 if 5m away
def ultrasoundDrive(pins, distance):
    print(f"ultrasoundDrive({distance})")
    for pin in pins:
        robot.arduino.pins[pin].mode = INPUT
    distance_to_pins = min([robot.arduino.pins[analog_pin].analog_read() for analog_pin in pins])
    tempTime = robot.time()
    prev_distance_to_pins = distance_to_pins
    prev_distance_to_pins = 0
    while distance_to_pins > distance:
        if (robot.time() - tempTime) > 3:
            print('times up')
            return -1
        if (robot.time() - tempTime) > 0.5 and (distance_to_pins - prev_distance_to_pins) < 0.01: # distance hasn't changed from what it was 0.5 seconds ago
            print('ultrasound distance not changing')
            return -1
        distance_to_pins = min([robot.arduino.pins[analog_pin].analog_read() for analog_pin in pins])
        print(f"{distance_to_pins}m away from {pins}")
        robot.sleep(0.1)
        if distance_to_pins == 0.5: # Ultrasound doesn't see anything
            print("0.5m away!")
            return -1
    return

# ⇒ Returns -1 if correctdrive fails
def spaceshipDeposit(spaceship_id):
    print('spaceshipDeposit()')

    turnSee(spaceship_id, True, True)
    if correctDrive(spaceship_id, 600) == -1:
        return -1
    print('finished correct driving to spaceship')

    # deposit into ship sequence
    print('raising')
    robot.servo_board.servos[2].position = 1

    speedDrive(0.2)

    if ultrasoundDrive([A0, A1], 0.6) == -1: # drive to 0.6m away from spaceship using bottom sensors
        print("ultrasound failed")
        drop()
        reset()
        return
    
    brake()
    robot.sleep(0.8)
    speedDrive(0.15)

    if ultrasoundDrive([A0, A1], 0.15) == -1: # drive to 0.45m away from spaceship using bottom sensors
        print("ultrasound failed")
        drop()
        reset()
        return
    brake()

    global collected
    # efficient stacking
    print(f'i have collected {collected} asteroids so far')
    if collected % 2 == 0:
        print('depositing to 1')
        mediumTurn(True)
        robot.sleep(0.08)
        brake()

    else:
        print('depositing to 2')
        mediumTurn(False)
        robot.sleep(0.08)
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


# ⇒ Returns -1 for failure (can't find the base markers)
def planetDeposit():
    print("planetDeposit()")

    for i in range(3, 7):
        if turnSee(BASE_IDS[i], True) != -1:
            correctDrive(BASE_IDS[i], 500)
            brake()
            drop()
            return
        
    return -1


# Finds distances between the base markers and a target marker
# ⇒ returns -1 for times up
def baseMarkerDistanceFinder(target_marker):
    print(f"baseMarkerDistanceFinder({target_marker.id}) Calculating distances")
    marker_target_distances = []
    base_marker_found = False
    tempTime = robot.time()
    while not base_marker_found:
        if (robot.time() - tempTime) > 10:
            print('times up')
            return -1
        turnSee(BASE_IDS, False, False)
        for base_id in BASE_IDS:
            base_marker = look(base_id)
            if base_marker == None:
                continue
            base_marker_found = True
            print(f"Base marker calculated for: {base_id}. base distance: {base_marker.position.distance}, target distance: {target_marker.position.distance}")
            marker_target_distances.append(abs(base_marker.position.distance - target_marker.position.distance))
        return marker_target_distances


# Moves egg to the nearest enemy base
# ⇒ No return value
def eggMover(direction_of_turn):
    print("eggMover(): Moving egg out of base")
    # get previous asteroid carried out of the way
    brake()
    drop()
    backwardsDrive(0.3)
    robot.sleep(0.1)
    brake()
    fastTurn(True)
    robot.sleep(0.1)
    mediumDrive()
    robot.sleep(0.5)
    brake()

    if turnSee(EGG_ID, not direction_of_turn) == -1:
        backwardsDrive(0.4)
        robot.sleep(1.5)
        brake()
        eggChecker()
        return
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

    reset()


"""
  Returns whether egg is arena and the direction the robot is currently turning to scan the base
   => return (is_egg_in_base, clockwise_turn)
"""
def eggChecker():
    print("eggChecker()")
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
            if marker.id == (BASE_IDS[0] - 1) % NUMBER_OF_WALL_MARKERS or marker.id == BASE_IDS[0] or marker.id == BASE_IDS[1]:
                seen_base_left_id = True
            if marker.id == (BASE_IDS[0] + 1) % NUMBER_OF_WALL_MARKERS or marker.id == BASE_IDS[-1] or marker.id == BASE_IDS[-2]:
                seen_base_right_id = True
            if marker.id == EGG_ID and seen_base_right_id:
                print(marker)
                # Check if the egg is near our base using difference in distances between each base marker and the egg marker
                print(baseMarkerDistanceFinder(marker))
                
                if len(list(filter(lambda distance: distance < 300, baseMarkerDistanceFinder(marker)))) > 0:
                    print("EGG IN BASE!!!")
                    is_egg_in_base = True
                    return (is_egg_in_base, clockwise_turn)
    return (is_egg_in_base, clockwise_turn)


def reset():
    print("RESET!!!")
    maincycle()
    return


def grab():
    print("grab()")
    # Lowering forklift and grabbing halfway at the same time for efficiency
    robot.servo_board.servos[2].position = -1 #lower
    robot.servo_board.servos[0].position = 0.3 # prepare for grabbing
    robot.servo_board.servos[1].position = 0.3 # prepare for grabbing
    robot.sleep(0.1)
    robot.servo_board.servos[0].position = 0
    robot.servo_board.servos[1].position = 0
    robot.servo_board.servos[2].position = -1 #lower
    robot.sleep(0.8)

    # grab box
    speedDrive(0.2)
    robot.servo_board.servos[0].position = 0.5
    robot.servo_board.servos[1].position = 0.5

    if ultrasoundDrive([A4], 0.15) == -1:
        print("Ultrasound driving has failed (we probably don't have an asteroid in the claw)")
        drop()
        reset()
        return
    brake()
    backwardsDrive(0.1)
    robot.sleep(0.25)
    robot.servo_board.servos[0].position = 0.6
    robot.servo_board.servos[1].position = 0.6
    robot.sleep(0.25)
    
    # lift up with forklift a bit
    robot.servo_board.servos[2].position = -0.8
    robot.sleep(0.3)


def drop():
    print('drop()')
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
    robot.servo_board.servos[2].position = -0.6
    robot.servo_board.servos[0].position = -1
    robot.servo_board.servos[1].position = -1

    # set a target asteroid to pick up
    asteroid_info = closestAsteroid()

    # if it didnt see an asteroid, it will turn counter-clockwise until it does and set that as its target
    while asteroid_info == None or asteroid_info == -1:
        print('I did not see an asteroid to target')
        asteroid_info = closestAsteroid()

    firstasteroid = asteroid_info[0]
    asteroid_direction_of_turn = not asteroid_info[1]  # if we turned CW to scan the arena, we turn CCW to find the asteroid

    print(f'I have set {firstasteroid.id} as the target asteroid. To reach this asteroid I will turn clockwise = {asteroid_direction_of_turn}')
    print(f'The target asteroid has these stats: {firstasteroid}')

    #add current asteroid to list of blacklisted asteroids so that robot doesnt target already retrieved asteroids such as those in the spaceship
    blackList.append(firstasteroid.id)

    # turn until it is in line with the target asteroid
    can_see_asteroid = turnSee(firstasteroid.id, asteroid_direction_of_turn)
    if can_see_asteroid == -1:
        print("Lost asteroid sight")
        reset()
        return

    # drive forward until no longer able to see asteroid
    if untilUnsee(firstasteroid.id) == -1:
        backwardsDrive(0.5)
        robot.sleep(0.9)
        brake()
        reset()

    grab()
    
    egg_info = eggChecker()
    is_egg_in_base = egg_info[0]
    egg_direction_of_turn = not egg_info[1]

    if is_egg_in_base:
        eggMover(egg_direction_of_turn)

    brake()
    seeLeftBase = turnSee(BASE_IDS[2], egg_direction_of_turn)
    if seeLeftBase == -1: # If it can't see base marker 2
        see_first_base = turnSee(BASE_IDS) # Then find the first base marker it does see
        if see_first_base != -1: # If it has been found, drive to it
            if correctDrive(see_first_base.id, 500) == -1: # If driving fails, reset
                drop()
                reset()
                return
        else: # If no base markers are visible
            drop()
            reset()
            return
    else: # If base marker 2 found, drive to it
        brake()
        print(f'going to {BASE_IDS[2]} (base)')
        if correctDrive(BASE_IDS[2], 500) == -1: # If driving fails, reset
            drop()
            reset()
            return


    robot.sleep(0.2)

    seeSpaceship = None
    if collected < 6:
        # number of collected asteroids is less than 6
        # go to spaceship
        seeSpaceship = turnSee([PORT_ID, STARBOARD_ID], False, False)
        if seeSpaceship != -1: # If spaceship has been found
            spaceship_marker = look(seeSpaceship.id)
    
    if collected >= 6 or seeSpaceship == -1: # If spaceship not found
        if planetDeposit() == -1:
            drop()
            reset()
            return
        reset()
        return

    # For each base marker seen, calculate distance between the base marker and the port marker. 
    # If all of these distances are over 300, then the spaceship is considered out of our base
    marker_spaceship_distances = baseMarkerDistanceFinder(spaceship_marker)
    print(f'Distance between base marker(s) and spaceship: {marker_spaceship_distances}')

    if marker_spaceship_distances == -1:
        if planetDeposit() == -1:
            drop()
            reset()
            return

    marker_spaceship_distances_under_700 = list(filter(lambda distance : distance < 700, marker_spaceship_distances))

    print("Distance between base marker(s) and spaceship under 700:", marker_spaceship_distances_under_700)

    # if we can't see spaceship or it is too far away from base & from ourselves, then deposit in planet
    if seeSpaceship == -1 or (len(marker_spaceship_distances_under_700) == 0 and spaceship_marker.position.distance > 1000): # If can't find spaceship or it is too far from second base marker
    #if seeSpaceship == -1 or spaceship_marker.position.distance > 1000:  # If can't find spaceship or if it is too far from robot
        print(f'spaceship distance {spaceship_marker.position.distance}')
        if planetDeposit() == -1:
            drop()
            reset()
            return
    else:
        print('depositing in spaceship')
        if spaceshipDeposit(spaceship_marker.id) == -1:
            drop()
            reset()
            return



# game time is 150 seconds
while True:
    currentProgram = maincycle()
