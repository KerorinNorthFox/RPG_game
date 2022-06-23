import time

def streamText(text, sleep_time=0.15):
    char_list = list(text)
    for chara in char_list:
        print(chara, end='', flush=True)
        time.sleep(sleep_time)
    print('\n')

if __name__ == '__main__':
    # てすと
    text = 'あいうえお\nかきくけこ\nさしすせそ\nたちつてと\nなにぬねの\nはひふへほ\nまみむめも\nやゆよ\nらりるれろ\nわをん'
    streamText(text)