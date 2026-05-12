import os
import json
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from mis.movie2 import update_movies

if os.path.exists('serviceAccountKey.json'):
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)


from flask import Flask, render_template, request, make_response, jsonify
from datetime import datetime
import random


app = Flask(__name__)
db = firestore.client()

@app.route("/")
def index():
    link = "<h1>歡迎進入黃士豪的網站首頁</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>今天日期</a><hr>"
    link += "<a href=/about>關於士豪</a><hr>"
    link += "<a href=/welcome?nick=士豪&dep=靜宜資管>GET傳值</a><hr>"
    link += "<a href=/account>POST傳值(帳號密碼)</a><hr>"
    link += "<a href=/calc>簡易計算機</a><hr>"
    link += "<a href=/cup>擲茭</a><hr>"
    link += "<br><a href=/read>讀取Firestore資料(根據lab遞減排序,取前4)</a><br>"
    link += "<br><a href=/search>搜尋老師</a><br>"
    link += "<br><a href=/movie1>查詢即將上市電影</a><br>"
    link += "<br><a href=/movie2>讀取電影網站即將上映影片，寫入Firestore</a><br>"
    link += "<br><a href=/movie3>搜尋電影資料庫</a><br>"
    link += "<br><a href=/road>易肇事路口查詢</a><br>"
    link += "<br><a href=/weather>氣象預報查詢</a><br>"
    link += "<br><a href=/rate>本週新片進DB</a><br>"

    return link

@app.route("/webhook", methods=["POST"])

def webhook():

    req = request.get_json(force=True)

    action = req["queryResult"]["action"]


    if (action == "rateChoice"):


        rate = req["queryResult"]["parameters"]["rate"]

        collection_ref = db.collection("本週新片含分級")

        docs = collection_ref.where("rate", "==", rate).get()


        info = "我是黃士豪設計的電影聊天機器人。查詢結果如下：\n"
        info += "您選擇的分級是：" + rate + "\n"

        movie_list = ""
        count = 0
        for doc in docs:
            count += 1
            movie_data = doc.to_dict()
            movie_list += f"{count}. {movie_data['title']}\n"

        if count > 0:
            info += f"本週共有 {count} 部相關影片：\n\n" + movie_list
        else:
            info += "抱歉，本週新片中目前沒有這個分級的電影喔！"

    return make_response(jsonify({"fulfillmentText": info}))


@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route("/weather", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        import requests, json
        city = request.form.get("city", "")
        city = city.replace("台", "臺")
        
        token = "rdec-key-123-45678-011121314"
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=" + token + "&format=JSON&locationName=" + str(city)
        
        try:
            Data = requests.get(url)
            location_data = json.loads(Data.text)["records"]["location"][0]
            Weather = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            Rain = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
            
            result = f"<h1>{city}目前天氣預報</h1>"
            result += f"<p>{Weather}，降雨機率：{Rain}%</p>"
            result += "<br><a href='/weather'>重新查詢</a> | <a href='/'>回首頁</a>"
            return result
            
        except Exception as e:
            return f"<h1>查詢失敗</h1><p>請確認縣市名稱輸入正確（例如：台中市）。</p><a href='/weather'>返回重試</a>"

    return """
    <h1>縣市氣象預報查詢</h1>
    <form method="POST">
        <input type="text" name="city" placeholder="請輸入縣市(如:台中市)" required>
        <button type="submit">查詢天氣</button>
    </form>
    <br><a href='/'>回首頁</a>
    """

@app.route("/road")
def road():
    url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
    
    Data = requests.get(url)
    JsonData = json.loads(Data.text)
    
    Result = "<h1>台中市易肇事路口統計</h1>"
    for item in JsonData:
        Result += item["路口名稱"] + "：發生" + item["總件數"] + "件，主因是" + item["主要肇因"] + "<br><br>"
    
    Result += "<br><a href='/'>回首頁</a>"
    return Result

@app.route("/movie3", methods=["GET", "POST"])
def movie3():
    if request.method == "POST":
        keyword = request.form.get("keyword", "")
        db = firestore.client()
        docs = db.collection("電影").get()
        
        info = f"<h1>關於『{keyword}』的電影查詢結果：</h1>"
        found = False
        
        for doc in docs:
            movie_data = doc.to_dict()
            title = movie_data.get("title", "")
            
            if keyword in title:
                found = True
                showLength = movie_data.get("showLength", "尚無片長資訊")
                length_display = showLength if showLength == "尚無片長資訊" else f"{showLength} 分鐘"

                info += f"片 名：{title}<br>"
                
                pic = movie_data.get('picture', '')
                info += f"海 報：<br><img src='https://www.atmovies.com.tw{pic}' width='200' alt='電影海報'><br>"
                
                link = movie_data.get('hyperlink', '#')
                info += f"影片介紹：<a href='{link}' target='_blank'>點我觀看</a><br>"
                
                info += f"片 長：{length_display}<br>"
                info += f"上映日期：{movie_data.get('showDate', '無資料')}<br><br><hr>"
        
        if not found:
            info += f"抱歉，在資料庫中找不到包含『{keyword}』的電影。<br>"
            
        info += "<br><a href='/movie3'>重新查詢</a> | <a href='/'>回首頁</a>"
        return info
    
    return """
    <h1>電影資料庫查詢</h1>
    <form method="POST">
        <input type="text" name="keyword" placeholder="請輸入電影名稱關鍵字(例如：女)" required>
        <button type="submit">查詢</button>
    </form>
    <br><a href='/'>回首頁</a>
    """

@app.route("/movie2")
def movie2():
    num = update_movies()
    return f"<h1>已成功從電影網站抓取 {num} 部影片並寫入資料庫！</h1><a href='/'>回到網站首頁</a>"

@app.route("/movie1")
def movie1():
    url = "https://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")

    R = ""
    for item in result:
        name = item.find("img").get("alt")
        link = "https://www.atmovies.com.tw" + item.find("a").get("href")
        
        R += f"{name}<br>"
        R += f"<a href='{link}' target='_blank'>{link}</a><br><br>"
    
    return R

@app.route("/spider1")
def spider1():
    R = ""
    url = "https://flash2026-a.vercel.app/about"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select("td a")

    for item in result:
        R += item.text + "<br>" + item.get("href") + "<br><br>"
    return R

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form.get("keyword", "")
        collection_ref = db.collection("靜宜資管2026a")
        docs = collection_ref.stream()
        
        results = []
        for doc in docs:
            user = doc.to_dict()
            name = user.get("name", "")
            lab = user.get("lab", "無資料")
  
            if keyword in name:
                results.append({"name": name, "lab": lab})
        
        rows = "".join([f"<tr><td>{r['name']}</td><td>{r['lab']}</td></tr>" for r in results])
        
        return f"""
        <h1>查詢結果</h1>
        <table border="1">
            <tr><th>姓名</th><th>研究室</th></tr>
            {rows if rows else '<tr><td colspan="2">找不到相關資料</td></tr>'}
        </table>
        <br><a href='/search'>返回重新搜尋</a> | <a href='/'>回首頁</a>
        """
    
    return """
    <h1>老師研究領域查詢</h1>
    <form method="POST">
        <input type="text" name="keyword" placeholder="請輸入老師名字關鍵字" required>
        <button type="submit">查詢</button>
    </form>
    """

@app.route("/read")
def read():
    db = firestore.client()

    Temp = ""
    collection_ref = db.collection("靜宜資管2026a")
    docs = collection_ref.order_by("lab").limit(3).get()
    for doc in docs:
        Temp += str(doc.to_dict()) + "<br>"


    return Temp

@app.route("/mis")
def course():
	return "<h1>資訊管理導論</h1><a href=/>回到網站首頁<a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime = str(now))

@app.route("/about")
def about():
	return render_template("mis2a.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    x = request.values.get("nick")
    y = request.values.get("dep")
    return render_template("welcome.html", name=x, dep=y)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/calc", methods=["GET", "POST"])
def calculate():
    if request.method == "POST":
        try:
            x = int(request.form["x"])
            y = int(request.form["y"])
            opt = request.form["opt"]
            result = 0

            if opt == "/" and y == 0:
                return "<h1>錯誤：除數不能為 0</h1><a href='/calc'>返回重試</a>"

            match opt:
                case "+": result = x + y
                case "-": result = x - y
                case "*": result = x * y
                case "/": result = x / y
            
            return f"<h1>計算結果</h1><p>{x} {opt} {y} = {result}</p><a href='/calc'>再次計算</a> | <a href='/'>回首頁</a>"
        
        except ValueError:
            return "<h1>請輸入整數數字</h1><a href='/calc'>返回重試</a>"
    else:
        return render_template("calc.html")

@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)


if __name__ == "__main__":
	app.run()