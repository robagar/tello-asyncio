import asyncio


async def wait_for_wifi(ssid_prefix):
    while True:
        proc = await asyncio.create_subprocess_shell(
            'iwgetid -r',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            s = stdout.decode()
            if s.startswith(ssid_prefix): return

        await asyncio.sleep(0.25)


