import asyncio
from http import HTTPStatus
import json

import aiohttp
import aiohttp.client_exceptions
from validators import url as url_validator


async def measure_response_time(session, url):
    """
    Fetching an url by performing GET request. Measure the response time.
    :param aiohttp.ClientSession session: All requests in one session, for connection pooling.
    :param str url: Full URL for request.
    :return dict: Dict containing measurements info. For example:
            {
                "url": "https://google.com",
                "status_code": 200,
                "time": 0.05735192599968286
            }
    """
    start = asyncio.get_event_loop().time()
    try:
        async with session.get(url) as response:
            await response.read()
            stop = asyncio.get_event_loop().time()
            return {"url": url, "status_code": response.status, "time": stop - start}
    except Exception:
        stop = asyncio.get_event_loop().time()
        return {"url": url, "status_code": None, "time": stop - start}


async def main(request_body):
    try:
        request_urls = json.loads(request_body)
    except json.decoder.JSONDecodeError:
        return {
            "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY,
            "body": "Bad json payload",
        }
    if not all(map(url_validator, request_urls)):
        return {
            "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY,
            "body": "Not a valid URL in payload.",
        }
    urls_to_measure = []
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        for url in request_urls:
            measure_data = measure_response_time(session, url)
            urls_to_measure.append(measure_data)
        measurements_results = await asyncio.gather(*urls_to_measure)
    response_data = {"results": [], "errors": []}
    for original_url, measurement_result in zip(request_urls, measurements_results):
        if measurement_result["status_code"] is None:
            response_data["errors"].append(measurement_result)
        else:
            response_data["results"].append(measurement_result)
    return {
        "statusCode": HTTPStatus.OK,
        "body": json.dumps(response_data),
        "headers": {"Content-Type": "application/json"},
    }


def handler(event, context):
    return asyncio.run(main(event["body"]))
