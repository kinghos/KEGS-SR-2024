from sr.robot3 import *

robot = Robot()


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

#find a marker
def firstSee():
    listmarkers = robot.camera.see()
    if len(listmarkers) > 0:
        print(f'i see {listmarkers[0]} first')
        return listmarkers[0]
#find a desired target marker and return its information


def look(targetid):
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f'couldnt find {targetid}')
    return None


firstseen = firstSee()
print(firstseen)

satisfy = False
robot.arduino.pins[4].mode = OUTPUT
robot.arduino.pins[4].digital_write(True)
robot.sleep(0.5)
while satisfy == False:
    if look(firstseen.id) == None:
        robot.motor_board.motors[0].power = -0.01
        robot.motor_board.motors[1].power = 0.01
        robot.sleep(0.01)
    elif look(firstseen.id).position.horizontal_angle > 0.05 or look(firstseen.id).position.horizontal_angle < -0.05:
        robot.motor_board.motors[0].power = -0.01
        robot.motor_board.motors[1].power = 0.01
        robot.sleep(0.01)
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
    if look(firstseen.id) == None:
        robot.motor_board.motors[0].power = 0
        robot.motor_board.motors[1].power = 0
        satisfy = True
    else:
        robot.sleep(0.5)
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
robot.servo_board.servos[2].position = 1

robot.sleep(2)

print('moving -0.4 power')
robot.motor_board.motors[0].power = -0.4
robot.motor_board.motors[1].power = -0.4
robot.sleep(0.01)

while True:
    robot.arduino.pins[2].mode = INPUT
    hurt_bum = robot.arduino.pins[2].digital_read()
    robot.sleep(0.01)
    if hurt_bum == True:
        print('ow')
        robot.motor_board.motors[0].power = 0
        robot.motor_board.motors[1].power = 0
        robot.sleep(0.01)