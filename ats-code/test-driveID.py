# drive_id
# drive_id is an integer between 0 to 63. It is a unique identifier for the driver
# it is not recommended to run too many servo drives on a serial connection daisy chained together
# doing this can cause lag on the connection

stage1_drive_id = 10
# drive id for stage 1 servo drive that runs the stage 1 set of rollers

stage2_drive_id = 20
# drive id for stage 2 servo drive that runs the stage 2 set of rollers

radius_drive_id = 21
# drive id for the servo drive that controls
# the stage 2 platform that changes the bend radius of the machine

angle_drive_id = 22


# drive id for the servo drive that controls
# the angle of the entire stage 2 platform.
# the servo driven by this servo drive is attached to the rack and pinion on stage 2 of the machine

def start_byte(drive_id):
    '''
    Takes in the drive_id of type int
    If the drive ID is within the acceptable range then it returns a binery literal that represents the drive id
    The binary literal that is returned is the ASCII characters that represent the binary number that corresponds to the
    drive id integer.
    '''

    if drive_id >= 0 and drive_id <= 63:
        drive_id = 0 + stage1_drive_id
        single_byte = drive_id.to_bytes(1, byteorder='big', signed=True)
        # byteorder= big means most significant bit is at the beginning of the array

        return single_byte
    else:
        return 0


def binary_display_int(integer):
    '''
    Takes in an integer
    Returns the binary representation of the argument as a string

    A helpful tool to check the binary representation of an integer
    '''
    binary_number = bin(integer)[2:].zfill(8)
    # bin converts the integer to a binary string with 0b in front
    # using the [2:] reference we can just show what we want to see, 0's and 1's.
    return binary_number


def binary_display_byte(byte):
    '''
    Takes in a byte
    returns the binary representation of the arguement as a string

    A helpful tool to check the binary representation of a byte
    '''
    byte_as_integer = int.from_bytes(byte, byteorder='big', signed=True)
    # class method that takes in a byte and returns the integer
    # byte order needs to be big if you want the MSB on the left side. Byte order= little gives you MSB on the right.
    # the signed argument indicates whether two's complement is used to represent the integer

    binary_number = bin(byte_as_integer)[2:].zfill(8)
    # bin converts the integer to a binary string with 0b in front
    # using the [2:] reference we can just show what we want to see, 0's and 1's.

    return binary_number


print(binary_display_byte(start_byte(stage1_drive_id)))
# test new functions