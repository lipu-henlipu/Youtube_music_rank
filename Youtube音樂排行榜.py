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

def get_global_top_by_keyword(keyword):
    print(f"\n正在搜尋：【{keyword}】 的全球歷史最高觀看排行")
    # 這樣可以抓到那些被分類在「娛樂」但觀看數極高的 MV
    search_keyword = f"{keyword} MV"
    search_req = youtube.search().list(
        part='id',
        q=search_keyword,        
        type='video',
        order='viewCount',
        maxResults=50           #增加到50筆，確保觀看數最高的幾個一定在名單內
    )
    search_res = search_req.execute()
    video_ids = [item['id']['videoId'] for item in search_res['items']]
    if not video_ids:
        print("找不到相關影片，請嘗試其他關鍵字！")
        return

    #查觀看數
    id_string = ','.join(video_ids)
    video_req = youtube.videos().list(part='snippet,statistics', id=id_string)
    video_res = video_req.execute() 

    #整理資料
    videos_data = []
    seen_titles = set() #用來過濾重複或極度相似的影片  

    for item in video_res['items']:
        title = item['snippet']['title']
        views = int(item['statistics'].get('viewCount', 0))

        # 去掉重複標題的影片，如果標題完全一樣就跳過
        if title not in seen_titles:
            videos_data.append({'title': title, 'views': views})
            seen_titles.add(title)     

    #總觀看數大排到小
    #因為搜尋 50 筆回來後，順序可能因 API 權重略有變動，我們自己排最準
    videos_data = sorted(videos_data, key=lambda x: x['views'], reverse=True)

    #只取前 10 名
    top_10_videos = videos_data[:10]

    #印出結果
    print("-" * 85)
    print(f"{'排名':<4} | {'全球歷史總觀看次數':<13} | {'完整歌曲名稱'}")
    print("-" * 85)
    for rank, video in enumerate(top_10_videos, 1):
        print(f"第{rank:<2}名 | {video['views']:<20,} | {video['title']}")
    print("-" * 85)  

    #呼叫畫圖工具
    chart_name = f"{keyword} 全球歷史觀看排行榜"
    draw_chart(top_10_videos, chart_name)

def draw_chart(top_10_videos, chart_title):
    #解決matplotlib中文字體顯示亂碼
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Malgun Gothic', 'MS Gothic', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    warnings.filterwarnings("ignore", category=UserWarning)

    # 因為歌名可能太長會把圖表擠歪，我們這裡畫圖時稍微把歌名截斷 (取前15字)
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
    plt.figure(figsize=(12, 6)) # 設定畫布大小(寬12, 高6)

    #畫出水平長條圖
    bars = plt.barh(titles, views, color='skyblue') 

    #設定圖表的標題與座標軸標籤
    plt.title(f'📊 {chart_title}', fontsize=16, fontweight='bold', pad=15)
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