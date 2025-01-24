from lxml import etree
import os

# 檔案路徑
xml_file = "zhwiki-20250101-pages-articles.xml"
output_dir = "articles"

# 建立輸出資料夾
os.makedirs(output_dir, exist_ok=True)

# 定義正確的命名空間
namespace = "{http://www.mediawiki.org/xml/export-0.11/}"

# 解析 XML 並提取文章
context = etree.iterparse(xml_file, events=("end",), tag=f"{namespace}page")
for i, (_, elem) in enumerate(context):
    try:
        title = elem.find(f"{namespace}title").text
        text = elem.find(f"{namespace}revision/{namespace}text").text

        # 文章標題作為檔名
        filename = os.path.join(output_dir, f"article_{i+1}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n\n{text or ''}")

        # 清理元素以節省記憶體
        elem.clear()

    except Exception as e:
        print(f"Error processing page {i}: {e}")

print(f"所有文章已保存至 {output_dir} 資料夾")
