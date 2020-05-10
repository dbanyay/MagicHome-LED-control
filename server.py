import asyncio
import websockets
from time import sleep, perf_counter

async def ph(websocket, path):
    while True:
        time_start = perf_counter()
        print('socket executed')
        await websocket.send(str(perf_counter() - time_start))
        sleep(wait_time)


wait_time = 100/1000

start_server = websockets.serve(ph, "localhost", 5000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()