from sr.robot3 import *

robot = Robot()

'''
print('moving .5 power')
robot.motor_board.motors[0].power = 0.4
robot.motor_board.motors[1].power = 0.4
# sleep for 2 second
print('sleep 0.5s')
robot.sleep(0.5)

print('stop')
robot.motor_board.motors[0].power = 0
robot.motor_board.motors[1].power = 0


#roughly 20 degrees, once we get to image orientation, we'll use a markers yaw to determine how far we have come
print('turning')
robot.motor_board.motors[0].power = 0.1
robot.motor_board.motors[1].power = -0.1
robot.sleep(0.5)
print('stop')
robot.motor_board.motors[0].power = 0
robot.motor_board.motors[1].power = 0
'''

#find a marker
def firstSee():
    listmarkers = robot.camera.see()
    if len(listmarkers) > 0:
        print(f'i see {listmarkers[0]} first')
        return listmarkers[0]


asteroidid = [i for i in range(150, 199)]
print(asteroidid)


def firstAsteroid():
    asteroids = []
    listmarkers = robot.camera.see()
    cycle = 0
    for marker in listmarkers:
        if marker.id in asteroidid:
            asteroids.append(marker)

    print(asteroids)
    #doesnt seem to append at all even when there are asteroids
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

def maincycle():

    mid= robot.zone * 7 + 3
    firstseen = firstAsteroid()
    print(firstseen)
    while firstseen == None:
        robot.motor_board.motors[0].power = -0.1
        robot.motor_board.motors[1].power = 0.1
        robot.sleep(0.1)
        firstseen = firstAsteroid()


    satisfy = False
    robot.arduino.pins[4].mode = OUTPUT
    robot.arduino.pins[4].digital_write(True)
    robot.sleep(0.5)
    while satisfy == False:
        if look(firstseen.id) == None:
            robot.motor_board.motors[0].power = -0.1
            robot.motor_board.motors[1].power = 0.1
            robot.sleep(0.1)
        elif look(firstseen.id).position.horizontal_angle < -0.1:
            robot.motor_board.motors[0].power = -0.01
            robot.motor_board.motors[1].power = 0.01
            robot.sleep(0.001)
            print(look(firstseen.id).position.horizontal_angle)
        elif look(firstseen.id).position.horizontal_angle > 0.1:
            robot.motor_board.motors[0].power = 0.01
            robot.motor_board.motors[1].power = -0.01
            robot.sleep(0.001)
            print(look(firstseen.id).position.horizontal_angle)
        else:
            print(look(firstseen.id).position.horizontal_angle)
            print(f'facing target ({firstseen.id})')
            robot.motor_board.motors[0].power = 0
            robot.motor_board.motors[1].power = 0
            satisfy = True
    robot.arduino.pins[4].digital_write(False)
    satisfy = False
    robot.motor_board.motors[0].power = 0.3
    robot.motor_board.motors[1].power = 0.3



    while satisfy == False:
        moment = look(firstseen.id)
        if  moment == None:
            robot.motor_board.motors[0].power = 0
            robot.motor_board.motors[1].power = 0
            satisfy = True
        else:
            robot.sleep(0.1)
            if moment.position.horizontal_angle < -0.1:
                robot.motor_board.motors[0].power = -0.01
                robot.motor_board.motors[1].power = 0.01
                robot.sleep(0.01)
                print(moment.position.horizontal_angle)
            elif moment.position.horizontal_angle > 0.1:
                robot.motor_board.motors[0].power = 0.01
                robot.motor_board.motors[1].power = -0.01
                robot.sleep(0.01)
                print(moment.position.horizontal_angle)
            else:
                print(moment.position.horizontal_angle)
                print(f'facing target ({firstseen.id})')
                robot.motor_board.motors[0].power = 0.3
                robot.motor_board.motors[1].power = 0.3
    robot.sleep(0.5)
    robot.arduino.pins[A4].mode = INPUT
    distance_to_closest_from_grabber = robot.arduino.pins[A4].analog_read()
    print(f'{distance_to_closest_from_grabber}m from sensor')
    #sometimes this reads 5m even though the box is right in front of it :shrug:
    if distance_to_closest_from_grabber > 0.5:
        robot.arduino.pins[3].mode = OUTPUT
        robot.arduino.pins[3].digital_write(True)
        robot.sleep(0.01)

    #grab code
    robot.servo_board.servos[0].position = 1
    robot.servo_board.servos[1].position = 1
    robot.sleep(1)
    robot.servo_board.servos[2].position = -0.5

    robot.sleep(2)

    #go home
    satisfy = False
    while satisfy == False:
        moment3 = look(mid)
        if moment3 == None:
            robot.motor_board.motors[0].power = -0.1
            robot.motor_board.motors[1].power = 0.1
            robot.sleep(0.1)
            print('dont see')
        elif moment3.position.horizontal_angle < -0.1:
            robot.motor_board.motors[0].power = -0.01
            robot.motor_board.motors[1].power = 0.01
            robot.sleep(0.01)
            print(moment3.position.horizontal_angle)
        elif moment3.position.horizontal_angle > 0.1:
            robot.motor_board.motors[0].power = 0.01
            robot.motor_board.motors[1].power = -0.01
            robot.sleep(0.01)
            print(moment3.position.horizontal_angle)
        else:
            print(moment3.position.horizontal_angle)
            print(f'facing target ({mid})')
            midpoint = moment3
            robot.motor_board.motors[0].power = 0
            robot.motor_board.motors[1].power = 0
            satisfy = True
    robot.arduino.pins[4].digital_write(False)
    satisfy = False
    robot.motor_board.motors[0].power = 0.3
    robot.motor_board.motors[1].power = 0.3
    while satisfy == False:
        moment2 = look(mid)
        if moment2 == None:
            print('dont see')
            break
        elif moment2.position.distance < 500:
            robot.motor_board.motors[0].power = 0
            robot.motor_board.motors[1].power = 0
            satisfy = True
        else:
            robot.sleep(0.5)
            print(f'{moment2.position.distance}mm to mid')
    robot.sleep(0.5)

    #go to spaceship
    satisfy = False
    while satisfy == False:
        moment5 = look(robot.zone + 120)
        if moment5 == None:
            robot.motor_board.motors[0].power = -0.1
            robot.motor_board.motors[1].power = 0.1
            robot.sleep(0.1)
            print('dont see')
        elif moment5.position.horizontal_angle < -0.1:
            robot.motor_board.motors[0].power = -0.01
            robot.motor_board.motors[1].power = 0.01
            robot.sleep(0.01)
            print(moment5.position.horizontal_angle)
        elif moment5.position.horizontal_angle > 0.1:
            robot.motor_board.motors[0].power = 0.01
            robot.motor_board.motors[1].power = -0.01
            robot.sleep(0.01)
            print(moment5.position.horizontal_angle)
        else:
            print(moment5.position.horizontal_angle)
            print(f'facing target ({robot.zone + 120})')
            midpoint = moment5
            robot.motor_board.motors[0].power = 0
            robot.motor_board.motors[1].power = 0
            satisfy = True
    robot.arduino.pins[4].digital_write(False)
    satisfy = False
    robot.motor_board.motors[0].power = 0.3
    robot.motor_board.motors[1].power = 0.3
    while satisfy == False:
        moment5 = look(robot.zone + 120)
        if moment5 == None:
            print('dont see')
            break
        elif moment5.position.distance < 600:
            robot.motor_board.motors[0].power = 0
            robot.motor_board.motors[1].power = 0
            satisfy = True
        else:
            if moment5.position.horizontal_angle < -0.1:
                robot.motor_board.motors[0].power = -0.01
                robot.motor_board.motors[1].power = 0.01
                robot.sleep(0.01)
                print(moment5.position.horizontal_angle)
            elif moment5.position.horizontal_angle > 0.1:
                robot.motor_board.motors[0].power = 0.01
                robot.motor_board.motors[1].power = -0.01
                robot.sleep(0.01)
                print(moment5.position.horizontal_angle)
            robot.sleep(0.1)
            robot.motor_board.motors[0].power = 0.3
            robot.motor_board.motors[1].power = 0.3
            print(f'{moment5.position.distance}mm to {moment5.id}')
    robot.sleep(0.2)
    print('raising')
    robot.servo_board.servos[2].position = 1
    robot.sleep(2)
    robot.motor_board.motors[0].power = 0.2
    robot.motor_board.motors[1].power = 0.2
    robot.sleep(1.7)
    robot.motor_board.motors[0].power = 0
    robot.motor_board.motors[1].power = 0
    robot.servo_board.servos[0].position = -1
    robot.servo_board.servos[1].position = -1
    robot.sleep(1)
    robot.motor_board.motors[0].power = -0.3
    robot.motor_board.motors[1].power = -0.3
    robot.sleep(1)
    robot.motor_board.motors[0].power = 0
    robot.motor_board.motors[1].power = 0
    robot.servo_board.servos[2].position = -1
    print('turning')
    robot.motor_board.motors[0].power = -0.1
    robot.motor_board.motors[1].power = 0.1
    robot.sleep(0.9)




    '''print('moving 0.4 power')
    robot.motor_board.motors[0].power = 0.4
    robot.motor_board.motors[1].power = 0.4
    robot.sleep(0.5)
    robot.motor_board.motors[0].power = 0
    robot.motor_board.motors[1].power = 0
    print('turning')
    robot.motor_board.motors[0].power = 0.1
    robot.motor_board.motors[1].power = -0.1
    robot.sleep(0.9)
    robot.motor_board.motors[0].power = 0
    robot.motor_board.motors[1].power = 0
    print('releasing')
    robot.servo_board.servos[2].position = -1
    robot.sleep(2)
    robot.servo_board.servos[0].position = -1
    robot.servo_board.servos[1].position = -1
    robot.sleep(1)
    print('moving -0.4 power')
    robot.motor_board.motors[0].power = -0.4
    robot.motor_board.motors[1].power = -0.4
    robot.sleep(0.5)
    robot.motor_board.motors[0].power = 0
    robot.motor_board.motors[1].power = 0
    print('turning')
    robot.motor_board.motors[0].power = -0.1
    robot.motor_board.motors[1].power = 0.1
    robot.sleep(0.9)
    robot.motor_board.motors[0].power = 0
    robot.motor_board.motors[1].power = 0
    print('moving 0.4 power')
    robot.motor_board.motors[0].power = 0.4
    robot.motor_board.motors[1].power = 0.4
    robot.sleep(1)
    robot.motor_board.motors[0].power = 0
    robot.motor_board.motors[1].power = 0'''


while True:
    maincycle()
