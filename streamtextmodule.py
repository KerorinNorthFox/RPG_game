import time

def stream_text(text, sleep_time=0.15) -> None:
    char_list: list[str] = list(text)
    for chara in char_list:
        print(chara, end='', flush=True)
        time.sleep(sleep_time)
    print('\n')

if __name__ == '__main__':
    # てすと
    text: str = 'あいうえお\nかきくけこ\nさしすせそ\nたちつてと\nなにぬねの\nはひふへほ\nまみむめも\nやゆよ\nらりるれろ\nわをん'
    stream_text(text)