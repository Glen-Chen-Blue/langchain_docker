from lxml import etree

xml_file = "zhwiki-20250101-pages-articles.xml"

# 打印根元素和子標籤
with open(xml_file, "rb") as f:
    for event, elem in etree.iterparse(f, events=("start",)):
        print(elem.tag)
        break
