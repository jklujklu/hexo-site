class VideoDetail:
    def __init__(self, cid, title, description, video_ids, cover, names, caption):
        self.cid = cid
        self.title = title
        self.description = description
        self.video_ids = video_ids
        self.cover = cover
        self.names = names
        self.caption = caption
        pass


class VideoEpisode:
    def __init__(self, cid, count, episodes):
        self.cid = cid
        self.count = count
        self.episodes = episodes


class VideoPlayerUrl:
    def __init__(self, vid, title, urls):
        self.vid = vid
        self.title = title
        self.urls = urls
