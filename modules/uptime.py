import asyncio
import aiohttp
from datetime import datetime, timezone

CHECK_INTERVAL = 180
TIMEOUT_SECONDS = 15


async def check_url(session: aiohttp.ClientSession, url: str) -> dict:
    started = asyncio.get_running_loop().time()

    try:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS),
            allow_redirects=True
        ) as response:
            elapsed = round(
                (asyncio.get_running_loop().time() - started) * 1000
            )
            return {
                "url": url,
                "online": response.status < 500,
                "status": response.status,
                "latency_ms": elapsed,
                "checked_at": datetime.now(timezone.utc).isoformat()
            }
    except (aiohttp.ClientError, asyncio.TimeoutError) as error:
        return {
            "url": url,
            "online": False,
            "status": None,
            "error": str(error),
            "checked_at": datetime.now(timezone.utc).isoformat()
        }


async def monitor_url(url: str):
    async with aiohttp.ClientSession() as session:
        while True:
            result = await check_url(session, url)
            print(result)
            await asyncio.sleep(CHECK_INTERVAL)