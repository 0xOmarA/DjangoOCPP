from ocpp_lib.call import Call
from ocpp_lib.types import RemoteStartTransaction_Req, IdToken
import asyncio

async def main():
    response = await Call.CallHandler.issue_command(
        charger_id = "ESP32_Charger",
        request = RemoteStartTransaction_Req(
            idTag = IdToken(
                IdToken = "ep2033mddow2",
            ),
            connectorId = 1
            ),
        shouldAwait = True
    )

asyncio.run(main)