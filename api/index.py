from fastapi import FastAPI
import uvicorn
from qqVideo import TencentVideo

app = FastAPI()

ten = TencentVideo('config/tencent.json', '/var/log/web_api/tencent.log')


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/pc/list/channels")
def list_channels():
    return ten.pc_list_channels()


@app.get("/pc/list/index/{channel}")
def list_channel_index(channel: str):
    return ten.pc_list_channel_index(channel)


@app.get("/pc/list/channels/{channel}")
def list_channel_videos(channel: str, offset=10):
    return ten.pc_list_channel_videos(channel, offset)


@app.get("/pc/list/video/{cid}")
def list_video_detail(cid: str):
    return ten.pc_list_video_detail(cid)


@app.get("/pc/list/episodes/{cids}")
def list_video_detail(cids: str):
    return ten.pc_list_video_episodes(cids)


@app.get("/pc/list/related/{cid}")
def list_video_related(cid: str, count=10):
    return ten.pc_list_related_videos(cid, count=count)


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8000)
