import types


def mbed_platforms():
    return ['*']


def pio_required_fields():
    return ['description', 'keywords']


def strip_mbed_url(resource):
    if isinstance(resource, str):
        # if isinstance(resource, types.StringTypes):
        resource = resource.replace("https://os.mbed.com", "")
    elif type(resource) is list:
        for i, value in enumerate(resource):
            resource[i] = strip_mbed_url(value)
    return resource


def make_mbed_url(resource):
    print("+=" * 20)
    print(type(resource))
    print(resource)
    if isinstance(resource, str):
        # if isinstance(resource, types.StringTypes):
        if resource[0] == '/':
            resource = "https://os.mbed.com" + resource
    elif type(resource) is dict:
        resource = "https://os.mbed.com" + resource['url']
    # elif type(resource)
    elif type(resource) is list:
        if not(type(resource[0]) is dict):
            resource = "https://os.mbed.com" + resource[0]
        # for i, value in enumerate(resource):
        # resource[i]= make_mbed_url(value)
    return resource


'''
EthernetInterface_mbedofficial.json
lwipeth_mbedofficial.json
lwip_mbedofficial.json
lwipsys_mbedofficial.json
mbed_gokmenascioglu.json
mbed_mbedofficial.json
mbedrtos_mbedofficial.json
mbedsrc_mbedofficial.json
Socket_mbedofficial.json
USBDevice_mbedofficial.json
'FATFileSystem',
ls -1 $HOME/.platformio/packages/framework-mbed/libs/*|grep -v TARGET|sort|grep -v ^$HOME|grep -v ^$|grep -v \\.h
ChaN
EthernetInterface
lwip
lwip-eth
lwip-sys
Socket
USBAudio
USBDevice
USBHID
USBHost
USBHost3GModule
USBHostHID
USBHostHub
USBHostMIDI
USBHostMSD
USBHostSerial
USBMIDI
USBMSD
USBSerial
'''


def is_mbed_core_library(url='', name='', owner=''):
    blacklist = [
        'mbed',
        'mbed-rtos',
        'mbed-src',
        'mbed-rpc',
        'lwip',
        'lwip-eth',
        'lwip-sys',
        'EthernetInterface',
        'Socket',
    ]
    if "https://" in url:
        url = strip_mbed_url(url).split('/')
        owner = url[2]
        name = url[4]
        print("**** is_mbed_core_library(): split url from", url, "to", owner,
              "and", name)

    if name in blacklist:
        print("**** is_mbed_core_library():", name,
              "is blacklisted as core library")
        return 1

    return 0


def has_non_ascii_char(value):
    return any(ord(c) > 128 for c in value)


def get_commits_number(commit_string):
    print('Processing commit')
    return int(commit_string.replace("Files at revision ", "").split(":")[0])


def is_fork(item):
    return 'fork' in item


def get_import_number(import_string):
    print('Processing import')
    return int(import_string.strip()) + 1
