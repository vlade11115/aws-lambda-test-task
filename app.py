import asyncio
import json

import aiohttp
import aiohttp.client_exceptions


async def fetch(session, url):
    start = asyncio.get_event_loop().time()
    try:
        async with session.get(url) as response:
            await response.read()
            stop = asyncio.get_event_loop().time()
            return {"url": url, "status_code": response.status, "time": stop - start}
    except aiohttp.client_exceptions.ClientError:
        stop = asyncio.get_event_loop().time()
        return {"url": url, "status_code": None, "time": stop - start}


async def main(request_body):
    try:
        urls = json.loads(request_body)
    except json.decoder.JSONDecodeError:
        return {"statusCode": 400, "body": "Bad json payload"}
    urls_to_fetch = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            response_data = fetch(session, url)
            urls_to_fetch.append(response_data)
        response_urls = await asyncio.gather(*urls_to_fetch)
    return {"statusCode": 200, "body": json.dumps(response_urls)}


def handler(event, context):
    return asyncio.run(main(event["body"]))
