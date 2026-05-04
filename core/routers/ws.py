from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import psutil
from datetime import datetime
import json

router = APIRouter()

@router.websocket("/ws/stats")
async def stats_streaming(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Initial call to set the baseline
            psutil.cpu_percent(interval=None)
            net_1 = psutil.net_io_counters()
            
            await asyncio.sleep(0.5) 
            
            # Second call to get the average over the sleep period
            cpu_usage = psutil.cpu_percent(interval=None)
            net_2 = psutil.net_io_counters()
            memory = psutil.virtual_memory()
            
            net_in = (net_2.bytes_recv - net_1.bytes_recv) * 8 / 1024 / 1024 / 0.5
            net_out = (net_2.bytes_sent - net_1.bytes_sent) * 8 / 1024 / 1024 / 0.5
            
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time

            data = {
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "memory_used": memory.used / (1024**3),
                "network_in": round(net_in, 2),
                "network_out": round(net_out, 2),
                "uptime": str(uptime).split('.')[0],
                "timestamp": datetime.now().strftime('%H:%M:%S')
            }
            
            await websocket.send_text(json.dumps(data))
    except WebSocketDisconnect:
        print("Client disconnected from stats stream")
    except Exception as e:
        print(f"Error in stats stream: {e}")
