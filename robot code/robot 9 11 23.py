from sr.robot3 import *

robot = Robot()

#port is left starboard is right
#no need to set own spaceship - it is already told by the comp usb
#therefore this is for use with the contingency (stealing other spaceships)

starship0 = [120, 125]
starship1 = [121, 126]
starship2 = [122, 127]
starship3 = [123, 128]
starships =[120, 125, 121, 126, 122, 127, 123, 128]
asteroidsid = [range(150, 199)]
arenaid = [range(0, 27)]
eggid = 110






'''
print('moving .5 power')
robot.motor_board.motors[0].power = 0.4
robot.motor_board.motors[1].power = 0.4
# sleep for 2 second
print('sleep 1s')
robot.sleep(0.5)

print('stop')
robot.motor_board.motors[0].power = 0
robot.motor_board.motors[1].power = 0'''

'''# roughly x degrees, once we get to image orientation, we'll use a markers yaw to determine how far we have come
print('turning')
robot.motor_board.motors[0].power = 0.1
robot.motor_board.motors[1].power = -0.1
robot.sleep(1.2)
print('stop')
robot.motor_board.motors[0].power = 0
robot.motor_board.motors[1].power = 0'''


# find a marker
def firstSee():
    listmarkers = robot.camera.see()
    if len(listmarkers) > 0:
        print(f'i see {listmarkers[0]} first')
        return listmarkers[0]


# find a desired target marker and return its information


def look(targetid):
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f'couldnt find {targetid}')
    return None


def setTeamSpaceship():
    markers = robot.camera.see()
    spaceships = []
    for id in markers:
        if id.id >= 120 and id.id <= 128:
            spaceships.append(id)
    if len(spaceships) == 0:
        print('didnt detect anything')
        return None

    elif len(spaceships) > 1:
        print('detected more than one, returning closest')
        return spaceships[0]
    else:
        print(f'team spaceship is: {spaceships}')
        return spaceships

print(f'i am zone: {robot.zone}')
myportid = robot.zone + 120
mystarboard = robot.zone + 125
print(myportid)


firstseen = firstSee()
print(firstseen)
while setTeamSpaceship() == None:
    #setTeamSpaceship()
    print('turning')
    robot.motor_board.motors[0].power = 0.1
    robot.motor_board.motors[1].power = -0.1
    robot.sleep(0.2)

'''
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
# sometimes this reads 5m even though the box is right in front of it :shrug:
if distance_to_closest_from_grabber > 0.5:
    robot.arduino.pins[3].mode = OUTPUT
    robot.arduino.pins[3].digital_write(True)
    robot.sleep(0.01)

# grab code
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
'''