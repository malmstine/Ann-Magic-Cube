import json
from itertools import starmap

from fastapi import FastAPI, WebSocket

from main import MsgTypes, calculate, to_fragment, colors

app = FastAPI()


def serialize_cube(cube):
    res_data = []
    for item in set(cube.cube):
        res_data.append({
            "item": item,
            "color": colors[item],
            "coords": tuple(
                cube.get_coords(cell)
                for cell, x in cube.catsisland if x == item
            )
        })
    return res_data


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def consumer(gen):
        count_variants = None
        last_progress = 0
        for msgtype, value in gen:
            match msgtype:
                case MsgTypes.VARIANTS:
                    count_variants = value
                    await websocket.send_json({
                        "variants": value
                    })
                    continue

                case MsgTypes.PROGRESS:
                    progress = int(value / count_variants * 100)
                    if progress != last_progress:
                        await websocket.send_json({
                            "progress": progress
                        })
                        last_progress = progress
                        await websocket.receive()
                    continue

                case MsgTypes.FOUNDED:
                    res_data = serialize_cube(value)
                    await websocket.send_json({
                        "result": res_data
                    })
                    continue

                case MsgTypes.TOTAL:
                    await websocket.send_json({
                        "time": value
                    })
                    continue

                case MsgTypes.END:
                    return

    while True:
        data = await websocket.receive_json()

        try:
            figures = starmap(to_fragment, enumerate(data, start=1))
            figures = list(figures)
            await consumer(
                calculate(figures)
            )
        except StopIteration:
            pass
