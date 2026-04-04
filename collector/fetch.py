import requests
import trafilatura


def fetch_article(url: str):
    try:
        resp = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )
    except requests.RequestException as e:
        return {
            "success": False,
            "url": url,
            "error": f"请求失败: {e}"
        }

    if resp.status_code != 200:
        return {
            "success": False,
            "url": url,
            "error": f"HTTP {resp.status_code}"
        }

    try:
        html = resp.content.decode("utf-8", errors="ignore")
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": f"解码失败: {e}"
        }

    extracted = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        favor_precision=True,
    )

    if not extracted:
        return {
            "success": False,
            "url": url,
            "error": "正文抽取失败"
        }

    return {
        "success": True,
        "url": url,
        "content": extracted
    }


if __name__ == "__main__":
    url = input("请输入文章 URL：").strip()
    article = fetch_article(url)

    if not article["success"]:
        print("失败：", article["error"])
    else:
        print(article["content"][:1000])