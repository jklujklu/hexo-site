import json
import time
from bs4 import BeautifulSoup

from api.bean.channel import Channel
from api.bean.response import BaseResponse
from api.bean.videodetail import VideoDetail, VideoEpisode
from api.utils.httpUtils import do_get, check_url


class TencentVideo:
    INDEX = 'https://v.qq.com/'
    CHANNEL = 'https://v.qq.com/channel/{channel}'

    LIST_API = 'https://v.qq.com/x/bu/pagesheet/list?_all=1&channel={channel}&offset={offset}&pagesize=30'
    EPISODES_API = 'https://union.video.qq.com/fcgi-bin/data?' \
                   'otype=json&tid=1390&appid=20001986&appkey=12f7ab002d2ca8bf&idlist={ids}'
    RELATE_API = 'https://node.video.qq.com/x/vlikecgi/related_rec?cid={cid}&rec_num={count}&_={time}'
    VIDEO_INFO_CID_API = 'https://node.video.qq.com/x/api/float_vinfo2?cid={cid}&_={time}'
    VIDEO_INFO_VID_API = 'https://union.video.qq.com/fcgi-bin/data?otype=json&tid=682&appid=20001238' \
                         '&appkey=6c03bbe9658448a4&union_platform=1&idlist={ids}&_={time}'
    PLAYER_URL_API = 'http://47.100.56.99:8000/pc/list/player/{vid}'

    SEARCH_WORD_API = 'https://s.video.qq.com/smartbox?plat=2&ver=0&num={count}&otype=json&query={word}&_={time}'
    SEARCH = 'https://v.qq.com/x/search/?q={key}&cur={page}'

    INTENT_SEARCH_API = 'https://pbaccess.video.qq.com/trpc.videosearch.search_cgi.http/load_intent_list_info?' \
                        'pageContext=query%3D{word}%26boxType%3Dintent%26intentId%3D3%26pageSize%3D{pageSize}' \
                        '&pageNum={page}&query={word}'
    MOBILE_API = 'https://m.v.qq.com/x/m/channel/figure/{channel}?pagelet=1&refreshContext=&request=figure&isPagelet=1'

    def __init__(self):
        pass

    def pc_list_player_url(self, vid):
        rs = do_get(self.PLAYER_URL_API.format(vid=vid), is_json=True)
        return rs

    def pc_list_channels(self):
        """
        获取所有频道
        :return:    频道列表
        """

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
                page_pattern = re.compile(r'x/page/(.+).html')
                cover_pattern1 = re.compile(r'/x/cover/(.+)/(.+).html')
                cover_pattern2 = re.compile(r'/x/cover/(.+).html')

                cid = ''
                vid = ''
                if page_pattern.search(href):
                    vid = page_pattern.findall(href)[0]
                elif cover_pattern1.search(href):
                    cid, vid = cover_pattern1.findall(href)[0]
                elif cover_pattern2.search(href):
                    cid = cover_pattern2.findall(href)[0]

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
                    'cid': cid,
                    'vid': vid,
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
            desc = item.select('.figure_desc')[0]['title'] if item.select('.figure_desc') else ''
            cover = item.select('.figure_pic')[0]['src']
            caption = item.select('.figure_caption')[0].text if item.select('.figure_caption') else ''

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

    def pc_list_video_detail_from_cid(self, cid):
        """
        根据cid查询影片详细信息
        :param cid:
        :return:
        """

        url = self.VIDEO_INFO_CID_API.format(cid=cid, time=int(time.time() * 1000))
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
        temp_list = []
        if len(video_ids) == 1:
            temp = self.pc_list_video_detail_from_vid(','.join(video_ids))
            temp.update({
                'groupName': ''
            })
            episodes.append(temp)
        else:
            count = 0
            is_first = True
            for vid in video_ids:
                temp_list.append(vid)
                count += 1
                if count % 10 == 0 or count == len(video_ids):
                    if is_first:
                        temp = self.pc_list_video_detail_from_vid(','.join(temp_list))
                        is_first = False
                    else:
                        for l in temp_list:
                            temp['groupDetail'].append({
                                'vid': l,
                                'cid': cid,
                                'title': '',
                                'pic': '',
                                'desc': '',
                                'num': ''
                            })
                    # vid_group = '{}-{}'.format((count - 1) // 10 * 10 + 1, count)
                    temp.update({
                        'groupName': '{}-{}'.format((count - 1) // 10 * 10 + 1, count)
                    })
                    episodes.append(temp)
                    temp = {
                        'groupDetail': []
                    }
                    temp_list = []

        cover = rs['c']['pic'] if 'pic' in rs['c'] else ''
        names = rs['nam'][0] if len(rs['nam']) != 0 else []
        caption = rs['rec'] if 'rec' in rs else ''
        return VideoDetail(cid, title, desc, episodes, cover, names, caption)

    def pc_list_video_detail_from_vid(self, vid, group_name=''):
        rs = do_get(self.VIDEO_INFO_VID_API.format(ids=vid, time=int(time.time())), call_back='QZOutputJson')
        print(rs)
        results = json.loads(rs)['results']
        temp = []
        for r in results:
            vid = r['id']
            cid = r['fields']['cover_list'][0] if len(r['fields']['cover_list']) != 0 else []
            pic = r['fields']['pic160x90']
            desc = r['fields']['desc']
            num = r['fields']['series_part_title']
            title = r['fields']['title']
            temp.append({
                'vid': vid,
                'cid': cid,
                'title': title,
                'pic': pic,
                'desc': desc,
                'num': num
            })
        return {
            'groupName': group_name,
            'groupDetail': temp
        }

    def pc_list_video_episodes(self, cids):
        """
        根据cid查询所有分集
        :param cids:    带查询cid，多个以,分割
        :return:
        """

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

    def pc_list_search_word(self, word, count=10):
        results = {
            'data': []
        }
        rs = do_get(self.SEARCH_WORD_API.format(word=word, count=count, time=int(time.time() * 1000)),
                    call_back='QZOutputJson')
        items = json.loads(rs)['item']
        for item in items:
            word = item['word']
            results['data'].append(word)
        return results

    def pc_list_search(self, key, cur=1, is_intent=False):
        def parse_people(html):
            results = {
                'success': True,
                'type': 'people',
                'avatar': '',
                'name': '',
                'hasNext': False,
                'data': []
            }
            dom = BeautifulSoup(html, 'html.parser')
            people_wrapper = dom.select('.result_people')
            if people_wrapper:
                avatar = people_wrapper[0].select('.people_avatar img')[0]['src']
                avatar = check_url(avatar)
                name = people_wrapper[0].select('.people_name')[0].text
                results['avatar'] = avatar
                results['name'] = name
                url = people_wrapper[0].select('a')[0]['href']
                new_html = do_get(url, params={'tabid': 1})
                dom = BeautifulSoup(new_html, 'html.parser')
                rows = dom.select('.mod_row_box')
                for row in rows:
                    if not row.select('.mod_title'):
                        continue
                    tag = row.select('.mod_title')[0].contents[0].strip()
                    items = row.select('.list_item')
                    for item in items:
                        cover = item.select('.figure_pic')[0]['src']
                        cover = check_url(cover)
                        i_title = item.select('.figure')[0]['title']
                        url = item.select('.figure')[0]['href']
                        pattern = re.compile(r'/cover/(.+).html')
                        if not pattern.search(url):
                            continue
                        cid = pattern.findall(url)[0]
                        caption = item.select('.figure_count')[0].text if item.select('.figure_count') else ''
                        results['data'].append({
                            'cid': cid,
                            'cover': cover,
                            'tag': tag,
                            'caption': caption,
                            'title': i_title
                        })
            else:
                results['success'] = False
            return results

        def parse_normal(html):
            results = {
                'success': True,
                'type': 'no_template',
                'hasNext': True,
                'data': []
            }
            dom = BeautifulSoup(html, 'html.parser')
            divs = dom.select('.wrapper_main div[data-index]')
            if len(divs) != 0:
                for div in divs:
                    cid = div.select('.result_item_v')[0]['data-id']
                    title = div.select('.result_title')[0].text.replace('\n', '').replace('\t', '')
                    cover = div.select('.figure_pic')[0]['src']
                    cover = check_url(cover)
                    caption = div.select('.figure_caption')[0].text.strip() if len(
                        div.select('.figure_caption')) != 0 else ''
                    _type = div.select('.type')[0].text.strip()
                    title = title.replace(_type, '')
                    results['data'].append({
                        'cid': cid,
                        'title': title,
                        'caption': caption,
                        'tag': _type,
                        'cover': cover
                    })
            else:
                results['success'] = False
                results['hasNext'] = False
            return results

        def parse_intent(html, word, page=0, page_size=10):
            dom = BeautifulSoup(html, 'html.parser')
            result = {
                'success': True,
                'type': 'intent',
                'hasNext': True,
                'data': []
            }
            if dom.select('.result_intention'):
                rs_json = do_get(self.INTENT_SEARCH_API.format(word=word, page=page, pageSize=page_size), is_json=True)
                items = rs_json['data']['areaBoxList'][0]['itemList']
                for item in items:
                    cid = item['doc']['id']
                    title = item['videoInfo']['title']

                    title = check(title)
                    _type = item['videoInfo']['typeName']
                    _type = check(_type)
                    cover = item['videoInfo']['imgUrl']
                    cover = check_url(cover)
                    # desc = item['videoInfo']['descrip']
                    result['data'].append({
                        'cid': cid,
                        'title': title,
                        'caption': '',
                        'tag': _type,
                        'cover': cover
                    })
                if (page + 1) * page_size >= rs_json['data']['areaBoxList'][0]['totalNum']:
                    result['hasNext'] = False
            else:
                result['success'] = False
            return result

        def check(txt):
            m = '\u0005'
            n = '\u0006'
            return txt.replace(m, '').replace(n, '')

        if is_intent:
            rs = do_get(self.SEARCH.format(key=key, page=1))
        else:
            rs = do_get(self.SEARCH.format(key=key, page=cur))
        people = parse_people(rs)
        videos = parse_normal(rs)
        intent = parse_intent(rs, key, page=cur - 1)
        if people['success']:
            return people
        elif intent['success']:
            return intent
        else:
            return videos

if __name__ == '__main__':
    a = TencentVideo().pc_list_player_url('p00355b45iu')
    print(json.dumps(a))
