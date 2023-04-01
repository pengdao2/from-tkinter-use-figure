import requests,csv,re,os,time,ctypes
from tqdm import tqdm
from bs4 import BeautifulSoup
import random,pygame
from math import sin, cos, pi, log
from ttkbootstrap.constants import *
from tkinter import messagebox
from base64 import b64decode as b64
from webbrowser import open as wb_open
import ttkbootstrap as ttk
from pygame.sprite import Sprite

# import threading
# # 多线程加速
# def thread_it(func,*args):
#     t = threading.Thread(target=func,args=args)
#     t.setDaemon=True
#     t.start()

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 640
CANVAS_CENTER_X = CANVAS_WIDTH / 2
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2
IMAGE_ENLARGE = 12
HEART_COLOR = "PINK"

def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
    x *= shrink_ratio
    y *= shrink_ratio
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y
    return int(x), int(y)
def scatter_inside(x, y, beta=0.15):
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())
    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy
def shrink(x, y, ratio):
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)  # 这个参数...
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy
def curve(p):
    return 2 * (3 * sin(4 * p)) / (2 * pi)
class Heart:
    def __init__(self, generate_frame=20):
        self._points = set()
        self._edge_diffusion_points = set()
        self._center_diffusion_points = set()
        self.all_points = {}
        self.build(2000)

        self.random_halo = 1000

        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)
    def build(self, number):
        for _ in range(number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self._points.add((x, y))
        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))
        point_list = list(self._points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        # 调整缩放比例
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.520)  # 魔法参数

        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)

        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 10 * curve(generate_frame / 10 * pi)  # 圆滑的周期的缩放比例

        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))

        all_points = []

        # 光环
        heart_halo_point = set()  # 光环的点坐标集合
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)  # 随机不到的地方造成爱心有缺口
            x, y = heart_function(t, shrink_ratio=11.6)  # 魔法参数
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                # 处理新的点
                heart_halo_point.add((x, y))
                x += random.randint(-14, 14)
                y += random.randint(-14, 14)
                size = random.choice((1, 2, 2))
                all_points.append((x, y, size))

        # 轮廓
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))

        # 内容
        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)


def draw(main: ttk.Window, render_canvas: ttk.Canvas, render_heart: Heart, render_frame=0):
    render_canvas.delete('all')
    render_heart.render(render_canvas, render_frame)
    main.after(160, draw, main, render_canvas, render_heart, render_frame + 1)

def wenzi_paqu():
    root_1 = ttk.Window()
    root_1.title('文字爬取')
    root_1.geometry("400x200+650+300")
    global v1
    labe01 = ttk.Label(root_1,text="文字爬取")
    labe01.pack(pady=5)
    v1 = ttk.StringVar(root_1)
    entry = ttk.Entry(root_1,textvariable=v1)
    entry.pack()
    v1.set("请输入你想爬的文字")
    btn01 = ttk.Button(root_1,text="开始爬起来", width=20,command=v1_get)
    btn01.pack()
    btnQuit = ttk.Button(root_1,text="不爬了",command=root_1.destroy)
    btnQuit.pack()
    root_1.mainloop()

def v1_get():
    str = v1.get()
    if str == "请输入你想爬的文字":
        messagebox.showinfo('请不要输入空值','为了你的体验，请不要输入空值！')
    messagebox.showinfo("文字即将爬取", "请点击下方确认键开始爬取\n")

    str_1 = v1.get()
    txt = str_1

    url = f'https://baike.baidu.com/item/{str_1}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
                      'Cookie: zhishiTopicRequestTime=1665061346951; BAIKE_SHITONG=%7B%22data%22%3A%22082ed4234e6fdeeb36fbb8f6516e15684b318089b04722abe4165deeee86492ef6108424a4a6f7061a2243396fa855ffb924157557e3e560601510617b7378a1f56d8180baa6a51c1d229bd7cad5e8ea4dc7ce3f4f5d2c43022cd5e8be1a7ea2%22%2C%22key_id%22%3A%2210%22%2C%22sign%22%3A%224430171e%22%7D; BAIDUID=BA89F667ECC0184892FA46221E06CAE1:FG=1; BIDUPSID=BA89F667ECC0184892FA46221E06CAE1; PSTM=1664776469; MCITY=-257%3A; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BAIDUID_BFESS=BA89F667ECC0184892FA46221E06CAE1:FG=1; BA_HECTOR=a184200121ala5a0ah21f00f1hjtdvb1a; ZFY=OwsNH0MWxyssFB52j69nGNN24uWyZwuiel1zQyc:BLyg:C; BDRCVFR[gQU9D8KBoX6]=IdAnGome-nsnWnYPi4WUvY; delPer=0; PSINO=6; BDRCVFR[JHHugauqPim]=mk3SLVN4HKm; Hm_lvt_55b574651fcae74b0a9f1cf9c8d7c93a=1665055178,1665058922,1665061346; Hm_lpvt_55b574651fcae74b0a9f1cf9c8d7c93a=1665061367; baikeVisitId=7532e8ef-0335-4dd2-aa4d-cccdcde70d5e; ab_sr=1.0.1_OGM0MmU1NDU4MWQxNTJmYWI0ODcxYWUzMDdmNzI4MGU0NjhlNWRjODNmZTdhZTQzYjNjYTBjMzc0NTg0ODRiMDU5ZDk3YjdiMGZmMjdmMjk2ZTMyN2JjMTgxOWRjNDkxMGY5MGFmYzkyYzY2NzYyMjJiYjVmZWI5MjVlZWFjNjg2ODYyMGU1ZWE0OThkNjZkNTg2NDRiOTQ0YmIyNjhiNg==; H_PS_PSSID=; RT="z=1&dm=baidu.com&si=vvihwll3tl&ss=l8x2j8v8&sl=7&tt=4ug&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ul=2vgh&hd=hhv"'
    }

    r = requests.get(url, headers=headers)
    t = '<meta name="description" content="(.*?)">'
    q = re.findall(t, r.text)

    t = ''
    res = ''.join(q)

    if res == '':
        messagebox.showinfo('提醒','你想爬取的东西没有更新，请等更新后再爬吧')
    else:
        with open(f'./{txt}.txt', 'w') as f:
            f.write(f'{str}\n')
            f.write(res)
        messagebox.showinfo('恭喜','已经全部爬完了')

def tupian_paqu():
    root_2 = ttk.Window()
    root_2.title('图片爬取')
    root_2.geometry("400x200+660+320")
    global v2
    labe01 = ttk.Label(root_2,text="图片爬取")
    labe01.pack()
    labe01 = ttk.Label(root_2, text="最多只能爬30张")
    labe01.pack(pady=5)
    v2 = ttk.StringVar(root_2)
    entry = ttk.Entry(root_2,textvariable=v2)
    entry.pack()
    v2.set("请输入你想爬的图片")
    global tupian_paqu_v3
    tupian_paqu_v3 = ttk.StringVar(root_2)
    entry = ttk.Entry(root_2, textvariable=tupian_paqu_v3)
    entry.pack()
    tupian_paqu_v3.set("请输入你想爬的个数")
    btn01 = ttk.Button(root_2,text="开始爬起来", width=20, command=v2_get)
    btn01.pack()
    btnQuit = ttk.Button(root_2,text="不爬了", command=root_2.destroy)
    btnQuit.pack()
    root_2.mainloop()

def v2_get():
    messagebox.showinfo("图片即将爬取", "请点击下方确认键开始爬取")
    str_it = v2.get()
    if str_it == "请输入你想爬的图片":
        messagebox.showinfo('请不要输入空值','为了你的体验，请不要输入空值！')
    paqushuliang = int(tupian_paqu_v3.get())
    if tupian_paqu_v3.get().isdigit():
        pass
    else:
        messagebox.showinfo('出错了，别乱搞', '输入的爬取数量应该是一个数字才对！\n别乱搞，我写的软件哪里有这么多bug！（跺脚）\n拜拜你嘞！')
        exit()
    if int(tupian_paqu_v3.get()) > 30:
        messagebox.showinfo('出错了，别乱搞','最多只能爬30张，一张都不能多爬\n拜拜你嘞！')
        exit()

    url = "https://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&dyTabStr=MCwzLDIsNiwxLDQsNSw3LDgsOQ%3D%3D&word=" + "{}".format(
        str_it)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64 ;X64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36',
        'Cookie': 'BDIMGISLOGIN=0; BDqhfp=%E6%97%85%E6%B8%B8%E6%99%AF%E7%82%B9%E5%9B%BE%E7%89%87%E4%B8%8B%E8%BD%BD%26%26NaN-1undefined%26%260%26%261; winWH=%5E6_1366x624; PSTM=1662910317; BIDUPSID=85F08F089D4AE0D420142AC91EB4B18D; BAIDUID=26FF5DF8B009E9D24E730EC40AA2ADE8:FG=1; BDUSS=UJ4OGkzNFJBYk9IRjd5WEF0REFYZ2lNZGNaeFdNb2RQczVFSzU1RjdRYkpOMGhqSVFBQUFBJCQAAAAAAQAAAAEAAABi8eIWaGExMoLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMmqIGPJqiBjY; BDUSS_BFESS=UJ4OGkzNFJBYk9IRjd5WEF0REFYZ2lNZGNaeFdNb2RQczVFSzU1RjdRYkpOMGhqSVFBQUFBJCQAAAAAAQAAAAEAAABi8eIWaGExMoLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMmqIGPJqiBjY; BAIDUID_BFESS=26FF5DF8B009E9D24E730EC40AA2ADE8:FG=1; ZFY=Y:BiqLat:Au15:ABXhhyGYU0pcqbHGSe8Ie9RgUxYz1VV4:C; BDRCVFR[dG2JNJb_ajR]=mk3SLVN4HKm; BDRCVFR[tox4WRQ4-Km]=mk3SLVN4HKm; BDRCVFR[-pGxjrCMryR]=mk3SLVN4HKm; userFrom=null; ab_sr=1.0.1_YjhhN2NjNjVlMjk4YWQ3Y2QzYTY2YThjZWNkODE5ZTg4M2ViNTQ0N2Q0Njc5NDZjNzBhNTQwYTVlZDkxN2I0ZDZhZGRjYmQ1YjM2YTAyM2UyY2I4YjViY2Y5ZjFkYjFlYzY1NTM5MDdhNGQwOWJkZjBhYTM1NTA5ZTEyMTllMmZmOGE1ZDg0NjA5OGY4OWQxNjQ4NzZiNmIwNDk3NGI1MQ=='
    }

    image = '{} 图片'.format(str_it)
    if not os.path.exists(image):
        os.mkdir(image)

    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    time.sleep(1)

    t = '"middleURL":"(.*?)",'
    result = re.findall(t, r.text)
    name = 0
    for img in result:
        res = requests.get(img, headers=headers)
        s = img.split('.')[-1]
        if name < paqushuliang:
            name += 1
            with open(f'./{image}/{str(name)}.jpg', mode='wb') as file:
                file.write(res.content)
                #print(f'第{name}张')
        else:
            break
    messagebox.showinfo('恭喜',f'已经全部爬取完毕，共爬取{name}张')

def shiping_paqu():
    root_3 = ttk.Window()
    root_3.title('视频爬取')
    root_3.geometry("400x200+670+340")
    global v3
    labe01 = ttk.Label(root_3,text="视频爬取")
    labe01.pack()
    v3 = ttk.StringVar(root_3)
    entry = ttk.Entry(root_3,textvariable=v3)
    entry.pack()
    v3.set("请输入你想爬的视频名字")
    global shiping_paqu_v3
    shiping_paqu_v3 = ttk.StringVar(root_3)
    entry = ttk.Entry(root_3, textvariable=shiping_paqu_v3)
    entry.pack()
    shiping_paqu_v3.set("请输入你想爬的个数")
    btn01 = ttk.Button(root_3,text="开始爬起来", width=20, command=v3_get)
    btn01.pack()
    btnQuit = ttk.Button(root_3,text="不爬了", command=root_3.destroy)
    btnQuit.pack()
    root_3.mainloop()

def v3_get():
    str = v3.get()
    if str == "请输入你想爬的视频名字":
        messagebox.showinfo('请不要输入空值','为了你的体验，请不要输入空值！')
        exit()
    name_1 = shiping_paqu_v3.get()
    if name_1.isdigit():
        pass
    else:
        messagebox.showinfo('出错了，别乱搞', '输入的爬取数量应该是一个数字才对！\n别乱搞，我写的软件哪里有这么多bug！（跺脚）\n')
        exit()
    if int(name_1) > 5:
        messagebox.showinfo('警告', '最多只能爬？个视频，可能爬取到的视频数量不是你想要的')

    messagebox.showinfo("视频即将爬取", "请点击下方确认键开始爬取\n因爬取视频需要耗费较长时间爬取下载\n请耐心等待！")
    video = f'{str} 视频'
    if not os.path.exists(video):
        os.mkdir(video)

    url = f'https://baike.baidu.com/item/{str}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
                      'Cookie: zhishiTopicRequestTime=1665061346951; BAIKE_SHITONG=%7B%22data%22%3A%22082ed4234e6fdeeb36fbb8f6516e15684b318089b04722abe4165deeee86492ef6108424a4a6f7061a2243396fa855ffb924157557e3e560601510617b7378a1f56d8180baa6a51c1d229bd7cad5e8ea4dc7ce3f4f5d2c43022cd5e8be1a7ea2%22%2C%22key_id%22%3A%2210%22%2C%22sign%22%3A%224430171e%22%7D; BAIDUID=BA89F667ECC0184892FA46221E06CAE1:FG=1; BIDUPSID=BA89F667ECC0184892FA46221E06CAE1; PSTM=1664776469; MCITY=-257%3A; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BAIDUID_BFESS=BA89F667ECC0184892FA46221E06CAE1:FG=1; BA_HECTOR=a184200121ala5a0ah21f00f1hjtdvb1a; ZFY=OwsNH0MWxyssFB52j69nGNN24uWyZwuiel1zQyc:BLyg:C; BDRCVFR[gQU9D8KBoX6]=IdAnGome-nsnWnYPi4WUvY; delPer=0; PSINO=6; BDRCVFR[JHHugauqPim]=mk3SLVN4HKm; Hm_lvt_55b574651fcae74b0a9f1cf9c8d7c93a=1665055178,1665058922,1665061346; Hm_lpvt_55b574651fcae74b0a9f1cf9c8d7c93a=1665061367; baikeVisitId=7532e8ef-0335-4dd2-aa4d-cccdcde70d5e; ab_sr=1.0.1_OGM0MmU1NDU4MWQxNTJmYWI0ODcxYWUzMDdmNzI4MGU0NjhlNWRjODNmZTdhZTQzYjNjYTBjMzc0NTg0ODRiMDU5ZDk3YjdiMGZmMjdmMjk2ZTMyN2JjMTgxOWRjNDkxMGY5MGFmYzkyYzY2NzYyMjJiYjVmZWI5MjVlZWFjNjg2ODYyMGU1ZWE0OThkNjZkNTg2NDRiOTQ0YmIyNjhiNg==; H_PS_PSSID=; RT="z=1&dm=baidu.com&si=vvihwll3tl&ss=l8x2j8v8&sl=7&tt=4ug&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ul=2vgh&hd=hhv"'
    }

    r = requests.get(url, headers=headers)
    t = 'mp4":"(.*?)"'
    result = re.findall(t, r.text)
    while '' in result:
        result.remove('')
    b = []
    for m in result:
        a = m.replace("\\", "")
        b.append(a)
    # b = []
    # for m in result:
    #     a = m + '.mp4'
    #     b.append(a)
    # name_1 = int(entry_2.get())
    name = 0
    for vio in b:
        res = requests.get(vio, headers=headers,stream=True)
        content_size = int(res.headers['Content-Length'])/1024
        if name < int(name_1):
            name += 1
            with open(f'./{video}/{name}.mp4', mode='wb') as f:
                # 升级为进度形式
                for data in tqdm(iterable=res.iter_content(1024), total=content_size, unit='k', desc=f'视频爬到第{name}个'):
                    f.write(data)
        else:
            break
    messagebox.showinfo('恭喜',f'已经全部爬完，爬了{name}个视频')

def login():
    if v_choose.get() == -1:
        wenzi_paqu()
    elif v_choose.get() == 0:
        tupian_paqu()
    elif v_choose.get() == 1:
        shiping_paqu()

def more_useufl():
    root_4 = ttk.Window()
    root_4.geometry('200x150+500+400')
    root_4.title('更多功能')
    kuwo_button = ttk.Button(root_4,text='音乐爬取器',command=ttk_use,bootstyle=(WARNING, OUTLINE))
    kuwo_button.pack(side='top')
    kuwo_button = ttk.Button(root_4, text='电影播放', command=video_root, bootstyle=(WARNING, OUTLINE))
    kuwo_button.pack(side='top')
    kuwo_button = ttk.Button(root_4, text='爱心跳动', command=HeartBeating, bootstyle=(WARNING, OUTLINE))
    kuwo_button.pack(side='top')
    root_4.mainloop()

def get_headers():
    headers = {
        'cookie': '_ga=GA1.2.2006462815.1658494129; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1661329731; _gid=GA1.2.1651218176.1661329731; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1661331297; _gat=1; kw_token=JOFLGGHT82I',
        'csrf': 'JOFLGGHT82I',
        'Host': 'www.kuwo.cn',
        'Referer': 'http://www.kuwo.cn/search/list?key=%E5%91%A8%E6%9D%B0%E4%BC%A6',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    return headers

def get_singer_id():
    url = f'http://www.kuwo.cn/api/www/search/searchArtistBykeyWord?key={singer_names}&pn=1&rn=30&httpsStatus=1&reqId=1abef9d1-2cf0-11ed-9908-c92824ae7619'
    json_data = requests.get(url=url, headers=get_headers()).json()
    data_list = json_data['data']['list']
    # for num, data in enumerate(data_list):
    #     name = data['name']
    #     id = data['id']
    #     country = data['country']
    #     print(f'{num + 1}.歌手：{name}||id：{id}||国家：{country}')
    #     if num == 9:
    #         break
    singer_info = data_list[0]
    singer_name = singer_info['name']
    singer_filename = f'music\\{singer_name}\\'
    if not os.path.exists(singer_filename):
        os.mkdir(singer_filename)
    return singer_info['id'], singer_filename

def download_onepage_by_singer(singer_id, page, filename):
    url = f'http://www.kuwo.cn/api/www/artist/artistMusic?artistid={singer_id}&pn={page}&rn=30&httpsStatus=1&reqId=514ec291-2cf1-11ed-bb28-4d9eea769149'
    try:
        json_data = requests.get(url=url, headers=get_headers()).json()
        data_list = json_data['data']['list']
        for data in data_list:
            artist = data['artist'].replace(' ', '_')
            name = data['name'].replace(' ', '').replace('/', '_').replace('|', '_')
            rid = data['rid']
            album = data['album']
            try:
                info_url = f'https://www.kuwo.cn/api/v1/www/music/playUrl?mid={rid}&type=convert_url3&br=320kmp3'
                music_url = requests.get(url=info_url).json()['data']['url']
                music_data = requests.get(url=music_url).content
                open(f'{filename}{artist}_{name}_{album}.mp3', mode='wb').write(music_data)
            except:
                messagebox.showinfo('下载失败', f'歌曲下载失败: {name}, 歌手为: {artist}, 歌曲id为: {rid}')
    except:
        return

    download_onepage_by_singer(singer_id, page + 1, filename)

def download_by_singer():
    singer_id, filename = get_singer_id()
    page = 1
    download_onepage_by_singer(singer_id, page, filename)

def page_num():
    f_out = open('缓存\\num.txt', 'r+')
    a = f_out.read()
    a = int(a) + 1
    f_out.seek(0)
    f_out.truncate()
    f_out.write(str(a))
    return a

# 歌曲下载
def load_ing(id):
    if id == '0':
        try:
            download_by_songname(page_num())
        except:
            print('没有下一页啦')
    else:
        try:
            song_data = data_list[int(id) - 1]
            artist = song_data['artist'].replace(' ', '_')
            name = song_data['name'].replace(' ', '').replace('/', '_').replace('|', '_')
            rid = song_data['rid']
            album = song_data['album']
            try:
                info_url = f'https://www.kuwo.cn/api/v1/www/music/playUrl?mid={rid}&type=convert_url3&br=320kmp3'
                music_url = requests.get(url=info_url).json()['data']['url']
                music_data = requests.get(url=music_url).content
                open(f'{filename}{artist}_{name}_{album}.mp3', mode='wb').write(music_data)

                messagebox.showinfo('下载完成',f'歌曲下载成功: {name}, 歌手为: {artist}, 歌曲id为: {rid}')
            except:
                messagebox.showinfo('下载失败',f'歌曲下载失败: {name}, 歌手为: {artist}, 歌曲id为: {rid}')
        except:
            print('确认你的选项是否正确')

def Music_Str():
    with open('缓存\\num.txt', 'w') as f:
        f.write('1')
    global song_name
    song_name = music_str.get()
    page =1
    download_by_songname(page)

def Music_String():
    global singer_names
    singer_names = music_strs.get()
    progressbar = ttk.Progressbar(
        mode=INDETERMINATE,
        bootstyle=(STRIPED, SUCCESS)
    )
    progressbar.pack(fill=BOTH, side='bottom')
    progressbar.start(10)
    download_by_singer()

# 确定id
def get_id_many():
    id_num = '0'
    load_ing(id_num)
def get_id_many1():
    id_num = '1'
    load_ing(id_num)
def get_id_many2():
    id_num = '2'
    load_ing(id_num)
def get_id_many3():
    id_num = '3'
    load_ing(id_num)
def get_id_many4():
    id_num = '4'
    load_ing(id_num)
def get_id_many5():
    id_num = '5'
    load_ing(id_num)
# 歌曲选择
def download_by_songname(page):
    url = f'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={song_name}&pn={page}&rn=30&httpsStatus=1&reqId=06544250-2ced-11ed-b9a3-e1f09b62dba5'
    json_data = requests.get(url=url, headers=get_headers()).json()
    global data_list
    data_list = json_data['data']['list']
    u32 = ctypes.windll.user32
    b = ttk.Toplevel()
    # b.iconbitmap('缓存\\logo.ico')
    b.title('选择下载哪首歌曲')
    b.geometry('600x400+320+10')
    function_1 = []
    function_1.append(get_id_many1)
    function_1.append(get_id_many2)
    function_1.append(get_id_many3)
    function_1.append(get_id_many4)
    function_1.append(get_id_many5)
    for num, data in enumerate(data_list[:5]):
        name = data['name']
        artist = data['artist']
        album = data['album']
        ttk.Button(b,text=f'{num + 1}.歌曲：{name}||歌手：{artist}||专辑：{album}',bootstyle=(WARNING, OUTLINE),command=function_1[num]).place(x=30,y=num*50)
    ttk.Button(b,text='下一页',bootstyle=(WARNING, OUTLINE),command=get_id_many).place(x=30,y=250)
        # print(f'{num + 1}.歌曲：{name}||歌手：{artist}||专辑：{album}')
    # print('0.下一页')
    def go():
            b_back = u32.GetParent(b.winfo_id())
            u32.SetParent(b_back, root.winfo_id())

    root.after(1, go)

def SecondaryWindow(root):
    u32 = ctypes.windll.user32

    def go():
        b_back = u32.GetParent(b.winfo_id())
        u32.SetParent(b_back, root.winfo_id())

    b = ttk.Toplevel()
    b.title('选择下载哪首歌曲')
    b.geometry('390x450+300+10')
    root.after(1, go)

# 主窗口
def ttk_use():
    # 全局变量filename
    global filename
    # 创建文件夹
    filename = 'music\\'
    if not os.path.exists(filename):
        os.mkdir(filename)
    global root
    root = ttk.Window(themename="superhero")
    # root.iconbitmap('缓存\\logo.ico')
    root.title('音乐爬取')
    root.geometry('1000x500+500+400')
    # 文本
    labe01 = ttk.Label(root,text="请输入你想爬的歌曲名称:")
    labe01.place(relx=0,x=65,y=15,anchor=ttk.NW)
    # 文本框
    global music_str
    music_str = ttk.StringVar(root)
    entry = ttk.Entry(root,textvariable=music_str,width=25)
    entry.place(relx=0,x=45,y=45,anchor=ttk.NW)
    music_str.set('歌曲名称')
    # 按钮
    b1 = ttk.Button(root,text='开始爬',bootstyle=(SUCCESS,OUTLINE),command=Music_Str)
    b1.place(relx=0,x=100,y=85)
    # 文本
    labe01 = ttk.Label(root, text="请输入你想爬的全部歌手名称:")
    labe01.place(relx=0,x=50,y=150,anchor=ttk.NW)
    # 文本框
    global music_strs
    music_strs = ttk.StringVar(root)
    entry = ttk.Entry(root, textvariable=music_strs, width=25)
    entry.place(relx=0, x=45, y=180, anchor=ttk.NW)
    music_strs.set('歌手名称')
    # 按钮
    b1 = ttk.Button(root, text='开始爬', bootstyle=(SUCCESS, OUTLINE), command=Music_String)
    b1.place(relx=0, x=100, y=220)
    btnQuit = ttk.Button(root, text="不爬了", command=root.destroy,bootstyle=(DANGER, OUTLINE),width=25)
    btnQuit.place(relx=0, x=40, y=300, anchor=ttk.NW)
    root.mainloop()

# 控件
def progressbar():
    progressbar = ttk.Progressbar(
                mode=INDETERMINATE,
                bootstyle=(STRIPED, SUCCESS)
            )
    progressbar.pack(fill=BOTH, side='bottom')
    progressbar.start(10)

def video():
    name = video_str.get()
    url = f'https://v.qq.com/x/search/?q={name}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'  }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    root = BeautifulSoup(response.text,'lxml')
    result = root.select('.result_btn_line a')
    t = 'href="(.*?)" target="_blank"'
    try:
        result_1 = result[0]
        result_1 = str(result_1)
        result_2 = ''
        try:
            result_2 = result[1]
            result_2 = str(result_2)
            result_2 = re.findall(t, result_2)
        except:
            pass
        result_1 = re.findall(t,result_1)
        result = []
        if result_2 == '':
            result = result_1
        else:
            result.append(result_1)
            result.append(result_2)
        # result = re.search(t,response.text)
        # print(result)
        video_num = 0
        for i in result:
            video_num += 1
            if video_num == 2:
                messagebox.showinfo('注意', '当前电影为中英双语电影，将要\n按顺序打开中、英双网页')
        else:
            for i in result:
                for j in i:
                    url_tenxun = 'http://www.wmxz.wang/video.php?url='+j
                    print(url_tenxun)
                    wb_open(url_tenxun,new=0,autoraise=True)
                # with open('视频.mp4','wb')as f:
                #     f.write(response_tenxun.content)
    except:
        messagebox.showinfo('waring','当前程序只支持打开电影，暂时不支持电视\n或者动漫或者其他乱七八糟的东西')

def video_root():
    messagebox.showinfo('注意','本程序属于学习使用，不用于商业使用，\n如望欣赏电影，请支持正版')
    root = ttk.Window(themename="superhero")
    root.title('电影网页播放')
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    dialog_width = 300
    dialog_height = 300
    root.geometry("%dx%d+%d+%d" % (
    dialog_width, dialog_height, (screenwidth - dialog_width) / 2, (screenheight - dialog_height) / 2))
    # 文本
    labe01 = ttk.Label(root,text="请输入你想看的电影名称:",bootstyle=WARNING)
    labe01.pack(pady=30)
    # 文本框
    global video_str
    video_str = ttk.StringVar(root)
    entry = ttk.Entry(root,textvariable=video_str,width=25)
    entry.pack()
    video_str.set('电影名称')
    # 按钮
    b1 = ttk.Button(root,text='打开',bootstyle=(SUCCESS,OUTLINE),command=video)
    b1.pack(pady=30)
    btnQuit = ttk.Button(root, text="走了", command=root.destroy,bootstyle=(DANGER, OUTLINE),width=25)
    btnQuit.pack()
    root.mainloop()

def HeartBeating():
    root = ttk.Window()  # 一个Tk
    screenwidth = primary_root.winfo_screenwidth()
    screenheight = primary_root.winfo_screenheight()
    dialog_width = 600
    dialog_height = 600
    root.geometry("%dx%d+%d+%d" % (
        dialog_width, dialog_height, (screenwidth - dialog_width) / 2, (screenheight - dialog_height) / 2))
    root.title('爱心跳动')
    canvas = ttk.Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    canvas.pack()
    heart = Heart()  # 心
    draw(root, canvas, heart)  # 开始画
    root.mainloop()

def delete_cache():
    files = os.listdir('缓存')
    primary_root.destroy()
    for file in files:
        os.remove(os.path.join('缓存', file))
    os.rmdir('缓存')

def main():
    global primary_root
    primary_root = ttk.Window(themename="superhero")
    primary_root.title('版本1.1.0.1')
    # primary_root.iconbitmap('缓存\\logo.ico')
    screenwidth = primary_root.winfo_screenwidth()
    screenheight = primary_root.winfo_screenheight()
    dialog_width = 400
    dialog_height = 350
    primary_root.geometry("%dx%d+%d+%d" % (
    dialog_width, dialog_height, (screenwidth - dialog_width) / 2, (screenheight - dialog_height) / 2))
    #root.geometry("400x350+700+430")
    global v_choose
    v_choose = ttk.IntVar()
    r1 = ttk.Radiobutton(text='爬视频',variable=v_choose,value=1,bootstyle='round-toggle').pack(ipady=3)
    r2 = ttk.Radiobutton(text='爬图片',variable=v_choose,value=0,bootstyle='round-toggle').pack(ipady=3)
    r3 = ttk.Radiobutton(text='爬文字',variable=v_choose,value=-1,bootstyle='round-toggle').pack(ipady=3)
    ttk.Button(text='确定',command=login).pack()
    progressbar = ttk.Progressbar(mode=INDETERMINATE,bootstyle=(STRIPED, DANGER))
    progressbar.pack(fill=BOTH, side='bottom')
    progressbar.start(10)
    buttons = ttk.Button(text="更多功能", width=7,command=more_useufl,bootstyle=SUCCESS)
    buttons.pack(side='right')
    primary_root.protocol('WM_DELETE_WINDOW', delete_cache)
    primary_root.mainloop()

if __name__ == '__main__':
    if not os.path.exists('缓存'):
        os.mkdir('缓存')
    main()