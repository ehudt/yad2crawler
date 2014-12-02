from bs4                import BeautifulSoup

template = ur"""
<html>
    <head>
        <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" />
    </head>
    <body style="text-align:right; direction:rtl;">
        <div id="img">%IMG%</div>
        <br>
        <div id="details">%DETAILS%</div>
        <br>
        <div id="options">%OPTIONS%</div>
    </body>
</html>
"""

styles_img = "vertical-align: middle;"
styles_kv = "margin-top: 10px; font-family: verdana,arial,sans-serif; font-size:11px; color:#333333; border-width: 1px; border-color: #999999; border-collapse: collapse;"
styles_kv_key = "background:#b5cfd2 url('http://www.textfixer.com/img/cell-blue.jpg'); border-width: 1px; padding: 8px; border-style: solid; border-color: #999999;"
styles_kv_value = "background:#dcddc0 url('http://www.textfixer.com/img/cell-grey.jpg'); border-width: 1px; padding: 8px; border-style: solid; border-color: #999999;"
styles_options = "margin-top: 10px; font-family: verdana,arial,sans-serif; font-size:11px; color:#333333; border-width: 1px; border-color: #999999; border-collapse: collapse; text-align:center;"
styles_options_th = "background:#b5cfd2 url('http://www.textfixer.com/img/cell-blue.jpg'); border-width: 1px; padding: 8px; border-style: solid; border-color: #999999;"
styles_options_td = "background:#dcddc0 url('http://www.textfixer.com/img/cell-grey.jpg'); border-width: 1px; padding: 8px; border-style: solid; border-color: #999999;"

class PageParser(object):
    def __init__(self, html):
        self.soup = BeautifulSoup(html)

    def get_div(self, cls, src=None):
        src = src or self.soup
        return src.find("div", {"class": cls})

    def add_imgs(self, page, url):
        img_div = self.get_div("ad-image")
        img = img_div.find("img")
        src = img.attrs["src"]
        img_url = img_div.findAll("a")[0].attrs["href"]
        map_url = img_div.findAll("a")[-1].attrs["href"]

        html = ""
        
        html += "<a href=\"" + (img_url.strip("/").replace("m.yad2.co.il/app/PicGallery.php", "http://www.yad2.co.il/Nadlan/ViewImage.php") if img_url != map_url else "") + "\"><img src=\"" + src + "\" width=\"140\" height=\"105\" style=\"" + styles_img + "\" /></a>"
        html += "&nbsp;" * 5
        html += "<a href=\"" + url + "\"><img src=\"https://cdn1.iconfinder.com/data/icons/windows-8-metro-style/512/link.png\" width=\"50\" style=\"" + styles_img + "\"></a>"
        html += "&nbsp;" * 10
        html += "<a href=\"" + map_url + "\"><img src=\"http://simpleicon.com/wp-content/uploads/map-8.png\" width=\"60\" style=\"" + styles_img + "\"></a>"        

        return page.replace("%IMG%", html)

    def add_details(self, page):
        html = "<table style=\"" + styles_kv + "\">"
        details = self.get_div("ad-details")
        for kv in details.findAll("div", attrs={"class": "key-value"}):
            key = self.get_div("key", kv)
            value = self.get_div("value", kv)
            html += "<tr><td style=\"" + styles_kv_key + "\">" + key.text.strip() + "</td><td style=\"" + styles_kv_value + "\">" + value.text.strip() + "</td></tr>"

        ad_options = self.get_div("ad-options")
        clearfix = self.get_div("clearfix", ad_options)
        key = self.get_div("key", clearfix)
        value = self.get_div("value", clearfix)
        html += "<tr><td style=\"" + styles_kv_key + "\">" + key.text.strip() + "</td><td style=\"" + styles_kv_value + "\">" + value.text.strip() + "</td></tr>"

        more_details = self.get_div("more-details")
        key = self.get_div("more-details-title")
        value = self.get_div("more-details")
        html += "<tr><td style=\"" + styles_kv_key + "\">" + key.text.strip() + "</td><td style=\"" + styles_kv_value + "\">" + (value.text.strip() if value else "") + "</td></tr>"

        html += "</table>"

        return page.replace("%DETAILS%", html)

    def add_ad_options(self, page):
        html = "<table style=\"" + styles_options + "\">"

        ad_options = self.get_div("ad-options")
        entries = ad_options.findAll("span", attrs={"class": None})

        html += "<tr>"
        for entry in entries:            
            if entry.find("span"):
                html += "<th style=\"" + styles_options_th + "\">" + entry.text.strip() + "</th>"
        html += "</tr>"

        html += "<tr>"
        for entry in entries:
            span = entry.find("span")
            if span:
                style = entry.find("span").attrs['style']
                exists = "left top" in style
                html += "<td style=\"" + styles_options_td + "\">" + ("<center>X</center>" if exists else "") + "</td>"
        html += "</tr>"

        return page.replace("%OPTIONS%", html)

    def create_apartment_page(self, url):
        page = template
        page = self.add_imgs(page, url)
        page = self.add_details(page)
        page = self.add_ad_options(page)

        return page