import time

SLEEP_TIME = 0.15

def streamText(text):
    char_list = list(text)
    for chara in char_list:
        print(chara, end='', flush=True)
        time.sleep(SLEEP_TIME)
    print('\n')

if __name__ == '__main__':
    # てすと
    text = 'あいうえお\nかきくけこ\nさしすせそ\nたちつてと\nなにぬねの\nはひふへほ\nまみむめも\nやゆよ\nらりるれろ\nわをん'
    streamText(text)