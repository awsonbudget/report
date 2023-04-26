import time
import asyncio
import httpx
from tqdm import tqdm

NUM_REQUESTS = 1000  # Number of requests to send
CONCURRENCY = 10  # Number of requests to send concurrently
URL = "https://winter2023-comp598-group06-02.cs.mcgill.ca/light/sort/200/200/"  # The endpoint to send requests to
timeout = httpx.Timeout(60.0)


async def send_request():
    async with httpx.AsyncClient(timeout=timeout) as client:
        start_time = time.monotonic()
        code = 0
        try:
            response = await client.get(URL)
            code = response.status_code
        except httpx.ConnectError:
            code = 408
        end_time = time.monotonic()
        return code, end_time - start_time


async def send_requests():
    start_time = time.monotonic()
    tasks = []
    latencies = []
    for _ in tqdm(range(NUM_REQUESTS), desc="Sending requests"):
        task = asyncio.ensure_future(send_request())
        task.add_done_callback(lambda t: latencies.append(t.result()[1]))
        tasks.append(task)
        if len(tasks) == CONCURRENCY:
            await asyncio.gather(*tasks)
            tasks = []
    if tasks:
        await asyncio.gather(*tasks)
    end_time = time.monotonic()
    return end_time - start_time, latencies


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    total_time, latencies = loop.run_until_complete(send_requests())
    avg_throughput = NUM_REQUESTS / total_time
    avg_latency = sum(latencies) / NUM_REQUESTS
    print(f"Average throughput: {avg_throughput:.2f} requests/second")
    print(f"Average latency: {avg_latency:.2f} seconds")
