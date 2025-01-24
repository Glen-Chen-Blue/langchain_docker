import os
import requests
from bs4 import BeautifulSoup

def download_arxiv_pdfs(topic, num_to_download):
    if num_to_download < 0:
        print("Num to download must be greater than 0.")
        return
    folderName = f"{topic}_{num_to_download}".replace(" ", "_")
    os.makedirs(folderName, exist_ok=True)
    page = -1
    num = 0
    while(num_to_download > num):
        page += 1
        base_url = f"https://arxiv.org/search/?query={topic}&searchtype=title&abstracts=show&order=-announced_date_first&size=200&start={200*page}"
        response = requests.get(base_url)
        if response.status_code != 200:
            print(f"Error status：{response.status_code}")
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_links = [item.select_one("p > span > a:nth-of-type(1)") for item in soup.select("ol > li")]
        if not pdf_links:
            print("No PDF links found.")
            return
        for _, link in enumerate(pdf_links):
            if num_to_download == num:
                return
            if link.text.strip() != "pdf":
                continue
            pdf_url = link['href']
            file_name = os.path.join(folderName, f"paper_{num+1}.pdf")
            try:
                pdf_response = requests.get(pdf_url)
                if pdf_response.status_code == 200:
                    with open(file_name, 'wb') as pdf_file:
                        pdf_file.write(pdf_response.content)
                    print(f"Download: {file_name}")
                    num += 1
                else:
                    print(f"Download error: {pdf_url} status: {pdf_response.status_code}")
            except Exception as e:
                print(f"Download error: {pdf_url} Because: {e}")

if __name__ == "__main__":
    try:
        topic = input("Input topic: ")
        num_to_download = int(input("Download nums: "))
        download_arxiv_pdfs(topic, num_to_download)
    except ValueError:
        print("Please input a number.")
