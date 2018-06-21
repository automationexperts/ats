import binascii

byte = b"b''asdfalsjdfakjsdwlasfjiwjfl"
byte2 = b'R\xbaV\x87\xe4bKDT@\xff\x80|\x8c\xb7^\xb6e\x1d\x14j\xcaf\xbc\xf6\xcc\xe2\xb6\x8a\xbb\x1e&~"\xa4D\x80\x00D\x00\x04\xc0"\xd2:\xba\x13\x8e\x7f\x95\xb8\xbe`D\xe7\x80\xccl\xdc\xb4\xb1\t<\x1cZ\x8aPA\xbc\xe4DA\x00D\xbe\xe5\xe9\x8d@v>\x17\xb2\xcaQ/\xde\xd3\x8e20\x10<\x9d\xaeI\xbfkQJ'

print(byte2)
print("length = ", len(byte2))
print(byte2[1])
print(type(byte2[1]))


# bytestrlist = list(byte)
# print(bytestrlist)

# ord()
# gives you the
# print(bytestrlist[0])

# i = 0

# for byte in bytestrlist:
#    byte = ord(byte)
#    print(byte)


def convert_bytes_to_listint(byte):
    '''
    Pass in a byte literal of type "bytes". This type may contain ASCII characters.
    This function returns that byte literal broken up into a list and converted into integer values from 0 to 255.
    '''
    bytelist = list(byte)
    return bytelist


print("---------------------------------")
bytelist = convert_bytes_to_listint(byte)
print(bytelist)

bytelist2 = convert_bytes_to_listint(byte2)
print(bytelist2)
print(len(bytelist2))
print("---------------------------------")

# convert byte string into list of integers


# for i in range (0,len(mybyte)-1,2):
#    print(i)

