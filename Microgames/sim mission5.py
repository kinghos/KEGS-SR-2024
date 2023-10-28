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

while satisfy == False:
    if look(firstseen.id) == None:
        robot.motor_board.motors[0].power = -0.01
        robot.motor_board.motors[1].power = 0.01
        robot.sleep(0.01)
    elif look(firstseen.id).position.horizontal_angle > 0.1 or look(firstseen.id).position.horizontal_angle < -0.1:
        robot.motor_board.motors[0].power = -0.01
        robot.motor_board.motors[1].power = 0.01
        robot.sleep(0.01)
    else:
        print(f'facing target ({firstseen.id})')
        robot.motor_board.motors[0].power = 0
        robot.motor_board.motors[1].power = 0
        satisfy = True
satisfy = False
robot.motor_board.motors[0].power = 0.3
robot.motor_board.motors[1].power = 0.3

while satisfy == False:
    if look(firstseen.id) == None:
        robot.motor_board.motors[0].power = 0
        robot.motor_board.motors[1].power = 0
        satisfy = True
    else:
        robot.sleep(0.01)

#grab code
robot.servo_board.servos[0].position = 1
robot.servo_board.servos[1].position = 1
robot.sleep(1)
robot.servo_board.servos[2].position = 1
