import asyncio
import platform


async def wait_for_wifi(ssid_prefix):
    system = platform.system()

    if system == 'Linux':
        await wait_for_wifi_linux(ssid_prefix)
    elif system == 'Darwin':
        await wait_for_wifi_macos(ssid_prefix)
    else:
        raise Exception(f'wait_for_wifi not implemented for {system}')


async def wait_for_wifi_linux(ssid_prefix):
    while True:
        s,e = await run_shell('iwgetid -r')
        if e:
            raise Exception(e)
        if s and s.startswith(ssid_prefix): 
            return
        await asyncio.sleep(0.25)


async def wait_for_wifi_macos(ssid_prefix):
    async def get_devices():
        s, e = await run_shell('networksetup -listallhardwareports')

        if s:
            devices = []
            found_wifi = False
            for line in s.splitlines():
                if not found_wifi:
                    # looking for something like "Hardware Port: Wi-Fi"
                    if 'Wi-Fi' in line:
                        found_wifi = True
                else:
                    # ... then next like should be like "Device: en1"
                    devices.append(line[len('Device: '):])
                    found_wifi = False
            return devices
        else:
            raise Exception(e)

    # find all WiFi devices
    devices = await get_devices()
 
    # wait for any one of them to connect
    waiting_for = f'Current Wi-Fi Network: {ssid_prefix}'
    while True:
        for device in devices:
            s,e = await run_shell(f'networksetup -getairportnetwork {device}')
            if s and s.startswith(waiting_for):
                return
        await asyncio.sleep(0.25)


async def run_shell(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    if proc.returncode == 0:
        return stdout.decode(), None
    else:
        return None, stderr.decode()
