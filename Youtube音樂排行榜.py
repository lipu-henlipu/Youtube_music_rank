from googleapiclient.discovery import build
import matplotlib.pyplot as plt
import warnings
API_KEY = 'AIzaSyC36CwxBwDQjPkfKisrI--4Ce5Puo1QFyk'
youtube = build('youtube', 'v3', developerKey=API_KEY)

#專門抓取各國當下發燒排行榜前十名
def get_country_trending(country_code):
    print(f"\n正在為您抓取：【{country_code}】 的音樂發燒榜")
    
    req = youtube.videos().list(
        part='snippet,statistics',
        chart='mostPopular',
        regionCode=country_code,
        videoCategoryId='10',
        maxResults=50  #這裡改成點 50 道菜
    )
    res = req.execute() #送出菜單
    
    #建立一個清單來存這50筆資料
    videos_data = []
    for item in res['items']:
        title = item['snippet']['title']
        views = int(item['statistics'].get('viewCount', 0))
        videos_data.append({'title': title, 'views': views})
    
    #將這50筆資料按觀看數由大到小重新排列
    videos_data = sorted(videos_data, key=lambda x: x['views'], reverse=True)
    
    #只取前 10 名
    top_10_videos = videos_data[:10]
    
    #印出表格
    print("-" * 85)
    print(f"{'排名':<4} | {'當下總觀看次數':<15} | {'完整歌曲名稱'}")
    print("-" * 85)
    for rank, video in enumerate(top_10_videos, 1): 
        print(f"第{rank:<2}名 | {video['views']:<20,} | {video['title']}")
    print("-" * 85)
    
    #呼叫畫圖工具
    chart_name = f"{country_code} 當下熱門音樂排行榜"
    draw_chart(top_10_videos, chart_name)

def get_global_top_by_keyword(keyword, is_artist=False):
    print(f"\n正在搜尋：【{keyword}】 的全球歷史最高觀看排行...請稍候")
    if is_artist: #音樂人
        search_keyword = f'"{keyword}"'
        search_req = youtube.search().list(
            part='id',
            q=search_keyword,        
            type='video',
            videoCategoryId='10',
            order='viewCount',
            maxResults=50           
        )
    else: #曲風
        search_keyword = f'{keyword} MV'
        search_req = youtube.search().list(
            part='id',
            q=search_keyword,        
            type='video',
            videoCategoryId='10', 
            order='relevance', 
            maxResults=50           
        )

    search_res = search_req.execute()
    video_ids = [item['id']['videoId'] for item in search_res['items']]
    if not video_ids:
        print("找不到相關影片")
        return

    # 查觀看數
    id_string = ','.join(video_ids)
    video_req = youtube.videos().list(part='snippet,statistics', id=id_string)
    video_res = video_req.execute() 

    # 整理資料
    videos_data = []
    seen_titles = set() 
    
    #抓捕非音樂影片
    bad_words = ['介紹', '解析', '盤點', 'cover', 'reaction', 'shorts', 'teaser', '預告', '片段', '翻唱', 'live', '現場', '致敬', '模仿', '串燒', '合集', 'playlist', '全紀錄', 'vlog', '伴奏', '演奏']

    for item in video_res['items']:
        title = item['snippet']['title']
        channel_title = item['snippet']['channelTitle']
        views = int(item['statistics'].get('viewCount', 0))

        # 檢查是否踩到黑名單
        is_dirty = any(bad.lower() in title.lower() for bad in bad_words)
        
        if is_artist:
            # 條件 1：影片標題「必須」包含歌手的名字
            in_title = keyword.lower() in title.lower()
            
            # 條件 2：是歌手本人的專屬頻道嗎？
            is_artist_channel = keyword.lower() in channel_title.lower()
            
            # 條件 3：是官方唱片公司嗎？(建立官方認證字庫)
            official_keywords = ['vevo', 'official', '官方', '音樂', 'music', '唱片', 'records', 'entertainment', '工作室', 'studio', 'binmusic', 'rock']
            is_label_channel = any(ok in channel_title.lower() for ok in official_keywords)
            
            # 只要標題有名字，且 (是本人頻道 或 是官方唱片公司)，我們就認定它是真 MV！
            is_relevant = in_title and (is_artist_channel or is_label_channel)
        else:
            is_relevant = True

        # 必須是：不髒 + 相關 + 沒重複
        if not is_dirty and is_relevant and title not in seen_titles:
            # 這次把 channel_title 也存起來，等一下印出來看
            videos_data.append({'title': title, 'views': views, 'channel': channel_title})
            seen_titles.add(title)     

    # 總觀看數大排到小
    videos_data = sorted(videos_data, key=lambda x: x['views'], reverse=True)

    if not videos_data:
        print(f"找不到【{keyword}】符合官方來源的MV，請確認歌手名字是否正確")
        return

    # 只取前 10 名
    top_10_videos = videos_data[:10]

    print("-" * 105)
    print(f"{'排名':<4} | {'觀看次數':<15} | {'發布頻道':<20} | {'完整歌曲名稱'}")
    print("-" * 105)
    for rank, video in enumerate(top_10_videos, 1):
        #限制頻道名稱長度避免排版跑掉
        ch_name = (video['channel'][:18] + '..') if len(video['channel']) > 18 else video['channel']
        print(f"第{rank:<2}名 | {video['views']:<18,} | {ch_name:<20} | {video['title']}")
    print("-" * 105)  

    #呼叫畫圖工具
    chart_name = f"{keyword} 全球歷史觀看排行榜"
    draw_chart(top_10_videos, chart_name)

def draw_chart(top_10_videos, chart_title):
    #解決matplotlib中文、韓文等字體顯示亂碼
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Malgun Gothic', 'MS Gothic', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    warnings.filterwarnings("ignore", category=UserWarning)

    # 因為歌名可能太長會把圖表擠歪，我們這裡畫圖時稍微把歌名截斷(取前15字)
    titles = []
    views = []
    for video in top_10_videos:
        short_title = video['title'][:15] + '..' if len(video['title']) > 15 else video['title']
        titles.append(short_title)
        views.append(video['views'])

    #因為matplotlib畫圖是由下往上畫，為了讓第1名在最上面，我們要把清單反轉

    titles.reverse()
    views.reverse()

    #開始畫圖
    plt.figure(figsize=(12, 6)) # 設定畫布大小(寬12,高6)

    #畫出水平長條圖
    bars = plt.barh(titles, views, color='skyblue') 

    #設定圖表的標題與座標軸標籤
    plt.title(f'{chart_title}', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('歷史總觀看次數', fontsize=12)
    plt.ylabel('歌曲名稱', fontsize=12)

    #在每個長條圖的尾巴，加上數字
    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2,
                 f' {int(width):,} 次',
                 va='center', ha='left', fontsize=10)

    #自動調整排版
    plt.tight_layout()
    plt.show()

# 互動式選單介面
while True:
    print("\n" + "="*40)
    print("YouTube 數據分析：多功能音樂熱門榜單系統")
    print("="*40)
    print("1.各國音樂發燒榜 (當下熱門流行)")
    print("2.特定音樂類型/曲風 (全球歷史總排行)")
    print("3.特定歌手/音樂人 (全球歷史神曲排行)")
    print("4.離開系統")
    print("="*40)

    choice = input("請輸入選項 (1, 2, 3, 4)：")

    if choice == '1':
        country = input("請輸入國家代碼 (例如：TW 台灣, US 美國, JP 日本, KR 韓國)：").upper()
        get_country_trending(country)  
    elif choice == '2':
        genre = input("請輸入曲風 (例如：KPOP, 獨立音樂, 搖滾)：")
        get_global_top_by_keyword(genre)
    elif choice == '3':
        artist = input("請輸入歌手姓名 (例如：周杰倫,草東沒有派對)：")
        get_global_top_by_keyword(artist)
    elif choice == '4':
        print("結束系統")
        break
    else:
        print("輸入錯誤，請重新輸入數字！")