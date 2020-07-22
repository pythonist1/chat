import asyncio
import datetime
import websockets
import json



USERS = set()

async def chat(websocket, path):

    nickname = ''
    await websocket.send(json.dumps('## Hello ##\n## Please enter your nickname and press "ENTER":\n'))
    async for message in websocket:
        data = json.loads(message)
        if json.loads(message) == '\r':
            break
        nickname += data
    if len(USERS) > 0:
        await asyncio.wait([user.send(json.dumps(F'\n  ## {nickname} LOG ON ##')) for user in USERS])
    USERS.add(websocket)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    await websocket.send(json.dumps(now + '\n## Welcome to the matrix chat ##\n  ## Press "ENTER" to write ##   ## Please be polite ##'))

    print(USERS)

    try:
        while True:

            await websocket.send('')
            OtherUSERS = USERS.copy()
            OtherUSERS.discard(websocket)
            async for message in websocket:
                data = json.loads(message)
                if data == '\r':
                    await asyncio.wait([user.send(json.dumps('\n' + nickname + '> ')) for user in USERS])
                print(data)
                if len(OtherUSERS) < 1:
                    break
                if data == '\r':
                    break
                await asyncio.wait([user.send(message) for user in OtherUSERS])

    except websockets.exceptions.ConnectionClosed:

            USERS.discard(websocket)
            print('closed')
            if len(USERS) > 0:
                await asyncio.wait([user.send(json.dumps(F'\n  ## USER LOG OFF {nickname} ##')) for user in USERS])

start_server = websockets.serve(chat, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
