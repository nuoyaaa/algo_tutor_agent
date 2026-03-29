from rag.qa import ask

if __name__ == "__main__":
    while True:
        query = input("请输入问题：")
        if query.strip().lower() in {"exit", "quit", "q"}:
            print("已退出。")
            break

        answer = ask(query)
        print("\n回答：", answer)
        print()