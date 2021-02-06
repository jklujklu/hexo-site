import json
import time
from bs4 import BeautifulSoup

from bean.channel import Channel
from bean.response import BaseResponse
from bean.videodetail import VideoDetail, VideoEpisode
from utils.httpUtils import do_get
from utils.logUtils import Logger


class TencentVideo:
    INDEX = 'https://v.qq.com/'
    CHANNEL = 'https://v.qq.com/channel/{channel}'

    LIST_API = 'https://v.qq.com/x/bu/pagesheet/list?_all=1&channel={channel}&offset={offset}&pagesize=30'
    EPISODES_API = 'https://union.video.qq.com/fcgi-bin/data?' \
                   'otype=json&tid=1390&appid=20001986&appkey=12f7ab002d2ca8bf&idlist={ids}'
    RELATE_API = 'https://node.video.qq.com/x/vlikecgi/related_rec?cid={cid}&rec_num={count}&_={time}'
    VIDEO_INFO_API = 'https://node.video.qq.com/x/api/float_vinfo2?cid={cid}&_={time}'
    PLAYER_URL_API = 'https://vd.l.qq.com/proxyhttp'

    MOBILE_API = 'https://m.v.qq.com/x/m/channel/figure/{channel}?pagelet=1&refreshContext=&request=figure&isPagelet=1'

    def __init__(self, config_path, log_path):
        self.config_path = config_path
        self.log_path = log_path
        self.logger = Logger(__name__, self.log_path)

    def pc_list_channels(self):
        """
        获取所有频道
        :return:    频道列表
        """

        self.logger.info('list channels')
        channels = []
        rs = do_get(self.INDEX)
        dom = BeautifulSoup(rs, 'html.parser')
        cells = dom.select('#mod_main_nav a')
        for cell in cells:
            href = cell['href']
            # 去除子菜单和无关项
            if href.startswith('/channel') and href.find('?') == -1:
                temp = Channel(href[href.rfind('/') + 1:], cell.text)
                # 去重
                if temp not in channels:
                    channels.append(temp)
        return BaseResponse(channels)

    def pc_list_channel_index(self, channel):

        def parse(html):
            v_lists = []
            cover_type = 'hz'
            for i in html.select('.list_item'):
                if 'data-float' not in i.select('.figure')[0].attrs:
                    continue

                href = i.select('.figure')[0]['href']
                # print(href)
                import re
                pattern = re.compile(r'/x/.+/(.+)/(.+)')
                if pattern.search(href):
                    vid = pattern.findall(href)[0][0]
                else:
                    vid = i.select('.figure')[0]['data-float']
                score = i.select('.figure_score')[0].text.strip() if i.select('.figure_score') else ''
                title = i.select('.figure_title')[0]['title'] if i.select('.figure_title') else ''
                cover_tag = i.select('.figure_pic')[0]
                if 'lz_next' in cover_tag.attrs:
                    cover = cover_tag['lz_next']
                elif 'lz_src' in cover_tag.attrs:
                    cover = cover_tag['lz_src']
                else:
                    cover = cover_tag['src']

                if cover.find('vcover_vt_pic') != -1 or cover.find('qqlive') != -1:
                    cover_type = 'vt'
                elif cover.find('vcover_hz_pic') != -1:
                    cover_type = 'hz'

                caption = i.select('.figure_caption')[0].text.strip() if i.select('.figure_caption') else ''
                desc = i.select('.figure_desc')[0]['title'] if i.select('.figure_desc') else ''

                if cover.startswith('//'):
                    cover = 'https:' + cover
                v_lists.append({
                    'cid': vid,
                    'title': title,
                    'caption': caption,
                    'score': score,
                    'desc': desc,
                    'cover': cover,
                })
            return v_lists, cover_type

        url = self.CHANNEL.format(channel=channel)
        rs = do_get(url, is_json=False)
        dom = BeautifulSoup(rs, 'html.parser')
        boxs = dom.select('.mod_row_box')
        results = {
            'data': []
        }
        for box in boxs:
            if box.select('.mod_hd'):
                label = box.select('.mod_title')[0].text.strip()
                items = box.select('.mod_figure')
                tabs = []
                if box.select('.mod_title_tabs'):
                    tabs = box.select('.tab_item')
                if len(tabs) != 0:
                    for tab, item in zip(tabs, items):
                        label = tab.text.strip()
                        lists, cover_type = parse(item)
                        if len(lists) != 0:
                            results['data'].append({
                                'title': label,
                                'showTitle': True,
                                'contentCode': 101 if cover_type == 'hz' else 106,
                                'widgets': lists
                            })
                else:
                    if len(items) == 0:
                        continue
                    lists, cover_type = parse(items[0])
                    if len(lists) != 0:
                        results['data'].append({
                            'title': label,
                            'showTitle': True,
                            'contentCode': 101 if cover_type == 'hz' else 106,
                            'widgets': lists
                        })
        return results

    def pc_list_channel_params(self, channel):
        """
        获取频道信息，包含可用筛选参数、页数、视频数
        :param channel:     频道对应的字符串
        :return:
        """

        self.logger.info('list channels params')

        # 变量声明
        params = []  # 所有可用筛选
        results_count = 0  # 记录总数
        page_count = 0  # 页数

        url = self.LIST_API.format(channel=channel, offset=0)
        rs = do_get(url)
        dom = BeautifulSoup(rs, 'html.parser')

        # 获取总数、页数
        results_count = dom.select('.filter_result')[0]['data-total']
        page_count = dom.select('.filter_result')[0]['data-pagemax']

        # 获取所有类型
        lines = dom.select('.filter_line')
        for line in lines:
            # 变量声明
            label = ''  # 字段含义
            key = ''  # 字段
            key_map = {}  # 键值对

            # 获取字段中文名称
            label = line.select('.filter_label')[0].text

            tags = line.select('.filter_item')

            # 获取参数键值
            for tag in tags:
                key = tag['data-key']
                key_map.update({tag['data-value']: tag.text})

            params.append({
                'field': key,
                'label': label,
                'key_map': key_map
            })
        return {
            'channel': channel,
            'count': results_count,
            'page': page_count,
            'params': params
        }
        pass

    def pc_list_channel_videos(self, channel, offset=0, params={}):
        """
        获取所有视频
        :param channel: 频道
        :param offset:  偏移量
        :param params:  额外筛选参数
        :return:
        """

        self.logger.info('list channel videos')

        url = self.LIST_API.format(channel=channel, offset=offset)
        rs = do_get(url, params)
        lists = self.pc_parse_list(rs)
        return {
            'channel': channel,
            'offset': offset,
            'params': params,
            'count': len(lists),
            'list': lists
        }

    @staticmethod
    def pc_parse_list(list_html):
        """
        根据HTML解析视频列表
        :param list_html:   源HTML
        :return:
        """
        video_list = []
        dom = BeautifulSoup(list_html, 'html.parser')
        items = dom.select('.list_item')
        for item in items:
            title = ''  # 标题
            desc = ''  # 简述
            caption = ''  # 提示文字
            cover = ''  # 封面
            is_vip = False  # 是否为VIP视频
            is_pay = False  # 是否为付费视频
            is_vip_pay = False  # 是否为超前点播
            is_ticket = False  # 是否为用券
            mark_icon = ''  # 视频角标
            score = '0.0'  # 评分
            play_count = '0'  # 播放量

            title = item.select('.figure_title')[0]['title']
            desc = item.select('.figure_desc')[0]['title']
            cover = item.select('.figure_pic')[0]['src']
            caption = item.select('.figure_caption')[0].text

            if item.select('.mark_v_VIP'):
                is_vip = True
                mark_icon = item.select('.mark_v_VIP')[0]['src']

            if item.select('.mark_v_会员付费解锁'):
                is_vip_pay = True
                mark_icon = item.select('.mark_v_会员付费解锁')[0]['src']

            if item.select('.mark_v_付费'):
                is_pay = True
                mark_icon = item.select('.mark_v_付费')[0]['src']

            if item.select('.mark_v_VIP用券'):
                is_ticket = True
                mark_icon = item.select('.mark_v_VIP用券')[0]['src']

            if cover.startswith('//'):
                cover = 'https:' + cover
            if mark_icon.startswith('//'):
                mark_icon = 'https:' + mark_icon

            try:
                score = item.select('.figure_score')[0].text.strip()
            except IndexError:
                pass

            try:
                play_count = item.select('.figure_count')[0].text
            except IndexError:
                pass

            video_list.append({
                'title': title,
                'caption': caption,
                'desc': desc,
                'score': score,
                'playCount': play_count,
                'isVip': is_vip,
                'isVipPay': is_vip_pay,
                'isTicket': is_ticket,
                'isPay': is_pay,
                'markIcon': mark_icon,
                'cover': cover
            })
        return video_list

    def pc_list_video_detail(self, cid):
        """
        根据cid查询影片详细信息
        :param cid:
        :return:
        """

        self.logger.info('list video detail ---> {}'.format(cid))

        url = self.VIDEO_INFO_API.format(cid=cid, time=int(time.time() * 1000))
        rs = do_get(url, is_json=True)
        if 'c' not in rs:
            return False
        title = rs['c']['title']
        desc = rs['c']['description']
        video_ids = rs['c']['video_ids']

        episodes = []
        temp = {
            'groupDetail': []
        }

        if len(video_ids) == 1:
            temp['groupDetail'].append({
                'vid': video_ids[0],
                'num': 1
            })
            temp.update({
                'groupName': ''
            })
            episodes.append(temp)
        else:
            count = 0
            for vid in video_ids:
                temp['groupDetail'].append({
                    'vid': vid,
                    'num': count + 1
                })
                count += 1
                if count % 10 == 0 or count == len(video_ids):
                    vid_group = '{}-{}'.format((count - 1) // 10 * 10 + 1, count)
                    temp.update({
                        'groupName': vid_group
                    })
                    episodes.append(temp)
                    temp = {
                        'groupDetail': []
                    }

        cover = rs['c']['pic']
        names = rs['nam'][0] if len(rs['nam']) != 0 else []
        caption = rs['rec'] if 'rec' in rs else ''
        return VideoDetail(cid, title, desc, episodes, cover, names, caption)

    def pc_list_video_episodes(self, cids):
        """
        根据cid查询所有分集
        :param cids:    带查询cid，多个以,分割
        :return:
        """

        self.logger.info('list video episodes ---> {}'.format(cids))

        results = []
        rs = do_get(self.EPISODES_API.format(ids=cids), call_back='QZOutputJson')
        collections = json.loads(rs)['results']
        for c in collections:
            cid = c['id']
            vids = c['fields']['video_ids']
            results.append(VideoEpisode(cid, len(vids), vids))
        return BaseResponse(results)

    def pc_list_related_videos(self, cid, count=10):
        """
        根据cid返回类型影片
        :param cid:     原影片
        :param count:   推荐数量
        :return:
        """
        self.logger.info('list related video ---> {}'.format(cid))

        results = {
            'source': cid,
            'data': []
        }
        rs = do_get(self.RELATE_API.format(cid=cid, count=count, time=int(time.time() * 1000)), is_json=True)
        videos = rs['data']['recItemList']
        for video in videos:
            cid = video['itemId']
            title = video['unionInfo']['title']
            subtitle = video['unionInfo']['second_title']
            cover_h = video['unionInfo']['new_pic_hz']
            cover_v = video['unionInfo']['new_pic_vt']
            score = video['unionInfo']['score']['score']
            status = video['unionInfo']['episode_updated']
            results['data'].append({
                'cid': cid,
                'title': title,
                'subTitle': subtitle,
                'coverVT': cover_v,
                'coverHZ': cover_h,
                'score': score,
                'status': status
            })
        return results

    def get_mobile_recommend(self, channel, params={}):
        rs = do_get(self.MOBILE_API.format(channel=channel), params=params, is_json=True)
        dom = BeautifulSoup(rs['html'], 'html.parser')
        json_str = dom.select('#channel_sync')[0]['value']
        from urllib.parse import unquote
        json_str = unquote(json_str)
        results = {
            'nextParams': {
                'key': 'pageContext',
                'value': ''
            },
            'data': []
        }
        data_list = json.loads(json_str)['modData']['modList']
        for data in data_list:
            video_set = {
                'title': '',
                'updateUrl': '',
                'list': []
            }
            try:
                title = data['cms_data']['title']
                update = data['cms_data']['op_datakey']
            except KeyError:
                title = data['meta']['title']
                update = data['meta']['op_datakey']
            if not title:
                title = 'banner'
            video_set['title'] = title
            video_set['updateUrl'] = update.replace('+', '&')
            videos = data['list']
            for video in videos:
                video_set['list'].append({
                    'cover': video['pic'] if 'pic' in video.keys() else '',
                    'title': video['title'] if 'title' in video.keys() else '',
                    'sub_title': video['subtitle'] if 'subtitle' in video.keys() else '',
                    'duration': video['duration'] if 'duration' in video.keys() else '',
                    'caption': video['timelong'] if 'timelong' in video.keys() else '',
                    'cid': video['cid'] if 'cid' in video.keys() else ''
                })
            results['data'].append(video_set)
        next_page = json.loads(json_str)['modData']['pageContext']
        results['nextParams']['value'] = next_page
        return results

    def get_mobile_channels(self):
        all_channels = []
        rs = do_get(self.MOBILE_API, is_json=True)
        dom = BeautifulSoup(rs['html'], 'html.parser')
        json_str = dom.select('#channel_sync')[0]['value']
        from urllib.parse import unquote
        json_str = unquote(json_str)
        print(json_str)
        channels = json.loads(json_str)['allChannels']['list']
        for channel in channels:
            name = channel['channelName']
            tag = channel['channelTag']
            if channel['externalLink']:
                continue
            all_channels.append({
                'name': name,
                'tag': tag,
                'dataUrl': self.MOBILE_API.format(channel=tag)
            })
        return {
            'count': len(all_channels),
            'channels': all_channels
        }
