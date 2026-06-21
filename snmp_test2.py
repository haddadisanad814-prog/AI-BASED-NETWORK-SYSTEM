import asyncio
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine, CommunityData, UdpTransportTarget,
    ContextData, ObjectType, ObjectIdentity, get_cmd
)

async def main():
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
        snmpEngine,
        CommunityData('public', mpModel=0),
        await UdpTransportTarget.create(('127.0.0.1', 161)),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))
    )

    if errorIndication:
        print("ERROR:", errorIndication)
    elif errorStatus:
        print("ERROR:", errorStatus)
    else:
        for varBind in varBinds:
            print(varBind)

    snmpEngine.close_dispatcher()

asyncio.run(main())
