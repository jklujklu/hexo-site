from fastapi import FastAPI
import uvicorn
from api.qqVideo import TencentVideo

app = FastAPI()

ten = TencentVideo()


@app.get("/api/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/pc/list/channels")
def list_channels():
    return ten.pc_list_channels()


@app.get("/api/pc/list/index/{channel}")
def list_channel_index(channel: str):
    return ten.pc_list_channel_index(channel)


@app.get("/api/pc/list/channels/{channel}")
def list_channel_videos(channel: str, offset=0):
    return ten.pc_list_channel_videos(channel, offset)


@app.get("/api/pc/list/video/{cid}")
def list_video_detail(cid: str):
    return ten.pc_list_video_detail_from_cid(cid)


@app.get("/api/pc/list/cid/{vid}")
def list_cid(vid: str, group_name=''):
    return ten.pc_list_video_detail_from_vid(vid, group_name)


@app.get("/api/pc/list/episodes/{cids}")
def list_video_detail(cids: str):
    return ten.pc_list_video_episodes(cids)


@app.get("/api/pc/list/related/{cid}")
def list_video_related(cid: str, count=10):
    return ten.pc_list_related_videos(cid, count=count)


@app.get("/api/pc/list/player/{vid}")
def list_video_player_url(vid: str):
    return ten.pc_list_player_url(vid)


@app.get("/api/pc/list/word/{key}")
def list_search_word(key: str):
    return ten.pc_list_search_word(key)


@app.get("/api/pc/list/search/{key}")
def list_search_results(key: str, page=1, mode=''):
    if mode == 'intent':
        is_intent = True
    else:
        is_intent = False
    return ten.\
        pc_list_search(key, cur=int(page), is_intent=is_intent)


if __name__ == '__main__':
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
