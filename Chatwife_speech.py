import json
from scipy.io.wavfile import write
from text import text_to_sequence
from models import SynthesizerTrn
import utils
import commons
import sys
import re
import torch
from torch import no_grad, LongTensor
from winsound import PlaySound
from ChatBot import ChatBot
from translateBaidu import translate_baidu
from tools import *
import os
import datetime
from termcolor import colored
from azure_speech import playSoundWithAzure
import configparser
import Config
from ASR.ASRService import ASRService
from pynput import keyboard as kb

# gpu 加速
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if device.type == "cuda":
    print("已开启GPU加速!")

chinese_model_path = "./model/" 
chinese_config_path = "./model/cn_config.json"
japanese_model_path = "./model/"
japanese_config_path = "./model/jp_config.json"
record_path = "./chat_record/"
character_path = "./characters/"
input_path = "./input.wav"
#chatWaifu

def get_input():
    print(">>>", end='')
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_input = input() + f'\n[系统时间: {time}]'
    sys.stdout.write('\r' + '>>>' + '主人请长按V输入语音与我对话哦~')
    sys.stdout.flush()
    return user_input

def get_text_tensor(text, hps, cleaned=False):
    if cleaned:
        text_norm = text_to_sequence(text, hps.symbols, [])
    else:
        text_norm = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm

def get_label_value(text, label, default, warning_name='value'): 
    value = re.search(rf'\[{label}=(.+?)\]', text)   #在文本text中搜索指定标签label的值,标签的格式为[label=值]，并删除不参与翻译，如果没有，返回默认default
    if value:
        try:
            text = re.sub(rf'\[{label}=(.+?)\]', '', text, 1)
            value = float(value.group(1))
        except:
            print(f'Invalid {warning_name}!')
            sys.exit(1)
    else:
        value = default
    return value, text

def remove_label(text, label):  #清除[{label}]
    if f'[{label}]' in text:
        return True, text.replace(f'[{label}]', '')
    else:
        return False, text


def generateSound(TTS_model, inputString, id, hps_ms): 
    if '--escape' in sys.argv:
        escape = True
    else:
        escape = False

    #model = input('0: Chinese')
    #config = input('Path of a config file: ')

    if n_symbols != 0:
        if not emotion_embedding:
            #while True:
            if(1 == 1):
                choice = 't'
                if choice == 't':
                    text = inputString
                    if text == '[ADVANCED]':
                        text = "我不会说"
                    length_scale, text = get_label_value(
                        text, 'LENGTH', 1, 'length scale')
                    noise_scale, text = get_label_value(
                        text, 'NOISE', 0.667, 'noise scale')
                    noise_scale_w, text = get_label_value(
                        text, 'NOISEW', 0.8, 'deviation of noise')    
                    # length_scale = 1
                    # noise_scale = 0.667
                    # noise_scale_w = 0.8    #就是用的是默认值
                    cleaned, text = remove_label(text, 'CLEANED')
                    stn_tst = get_text_tensor(text, hps_ms, cleaned=cleaned)  #不超过n_symbols的整形

                    speaker_id = id  #vits支持多说话人的语音合成,sid是用来标识不同说话人的，选某一个。如从'speakers': ['特别周', '无声铃鹿', '东海帝皇（帝宝，帝王）', '丸善斯基', '富士奇迹', '小栗帽', '黄金船', '伏特加', '大和赤骥', '大树快车', '草上飞', '菱亚马逊', '目白麦昆', '神鹰', '好歌剧', '成田白仁', '鲁道夫象征（皇帝）', '气槽', '爱丽数码', '星云天空', '玉藻十字', '美妙姿势', '琵琶晨光', '摩耶重炮', '曼城茶座', '美浦波旁', '目白赖恩', '菱曙', '雪中美人', '米浴', '艾尼斯风神', '爱丽速子（爱丽快子）', '爱慕织姬', '稻荷一', '胜利奖券', '空中神宫', '荣进闪耀', '真机伶', '川上公主', '黄金城（黄金城市）', '樱花进王', '采珠', '新光风', '东商变革', '超级小海湾', '醒目飞鹰（寄寄子）', '荒漠英雄', '东瀛佐敦', '中山庆典',......,  所以，默认config中的不同角色对应相同的sid可能是有问题的？如果是不同的vits模型那就没问题（目前看来是这样的）~
                    out_path = "output.wav"

                    with no_grad():
                        x_tst = stn_tst.unsqueeze(0).to(device)
                        x_tst_lengths = LongTensor([stn_tst.size(0)]).to(device)
                        sid = LongTensor([speaker_id]).to(device)
                        audio = TTS_model.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale,
                                               noise_scale_w=noise_scale_w, length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()
                write(out_path, hps_ms.data.sampling_rate, audio)

if __name__ == "__main__":
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    
    Config.checkApi(config)
    model_id = Config.choseLang(config)
    
    system_prompt, char_name = Config.choseChar()
    
    id, key = Config.getModel(model_id)
    
    if model_id == 0:
        model_config = chinese_config_path
    elif model_id == 1:
        model_config = japanese_config_path
    model_path = "./model/" + key + '/' + key + '.pth'
    #TTS model 
    hps_ms = utils.get_hparams_from_file(model_config)
    n_speakers = hps_ms.data.n_speakers if 'n_speakers' in hps_ms.data.keys() else 0
    n_symbols = len(hps_ms.symbols) if 'symbols' in hps_ms.keys() else 0   #n_symbols表示词表的大小,即模型的输入文本所使用的词典中词的总数。
    emotion_embedding = hps_ms.data.emotion_embedding if 'emotion_embedding' in hps_ms.data.keys() else False
    TTS_model = SynthesizerTrn(
        n_symbols,
        hps_ms.data.filter_length // 2 + 1,
        hps_ms.train.segment_size // hps_ms.data.hop_length,
        n_speakers=n_speakers,
        emotion_embedding=emotion_embedding,
        **hps_ms.model)
    TTS_model.eval()
    utils.load_checkpoint(model_path, TTS_model)
    TTS_model = TTS_model.to(device)

    #ASR model
    ASR_config_path = 'ASR/resources/config.yaml'
    ASR_model = ASRService(ASR_config_path)

    # 检查历史记录
    clear = False
    if not os.path.exists(record_path):
        os.mkdir(record_path)
    record_path += char_name + '.json'
    if os.path.exists(record_path):
        print(colored('检查到历史记录存在，是否继续使用？(y/n)', 'green'),)
        load_record = input('>>>')
        if load_record == 'n':
            os.remove(record_path)
        else:
            os.system('cls')
            clear = True
            with open(record_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                for item in messages:
                    if item['role'] == 'user':   
                        print('>>>' + item['content'])       #输出聊天历史记录
                    elif item['role'] == 'assistant':
                        print(item['content'])
    if not os.path.exists(record_path):
        name = input(f'给{char_name}取一个名字吧: ')
        system_prompt += 'Your name is ' + name + '.'

    gpt = ChatBot(api_key=config.get('API', 'openai_key'),
                  setting=system_prompt,
                  save_path=record_path)

    if not clear:
        os.system('cls')
    controller = utils.controll_recorder()
    while True:
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #user_input = input() + f'\n[系统时间: {time}]'
        sys.stdout.write(">>>" + '主人请长按V输入语音与我对话哦~')
        sys.stdout.flush()

        controller.listener = kb.Listener(on_press=controller.on_press, on_release=controller.on_release)
        controller.listener.start()
        controller.listener.join()
        if controller.terminate == True:
            exit()

        input_message = ASR_model.infer(input_path) 
        print(">>>", input_message)

        sys.stdout.write('\r' + '信息正在飞快传往异次元...')
        sys.stdout.flush()

        input_message += f'\n[系统时间: {time}]'
        if model_id == 0:
            answer = gpt.send_message(input_message).replace('\n','')
            if 'zh-CN' in key:
                sys.stdout.write('\r' + ' '*50 + '\r')
                print(answer, flush=True)
                playSoundWithAzure(key, brackets_delete(answer))
            else:
                generateSound(TTS_model, "[ZH]"+ brackets_delete(answer) +"[ZH]", id, hps_ms=hps_ms)
                sys.stdout.write('\r' + ' '*50 + '\r')
                print(answer, flush=True)
                PlaySound(r'.\output.wav', flags=1)
        elif model_id == 1:
            answer = gpt.send_message(input_message).replace('\n','')  #得到中文
            trans = translate_baidu(brackets_delete(answer), config.get('API', 'baidu_appid'), config.get('API', 'baidu_secretKey'))  #中文转日文
            if trans == None:
                print(colored('错误: 翻译 API 错误！', 'red'))
            generateSound(TTS_model, brackets_delete(trans), id, hps_ms)  #产生声音并保存
            sys.stdout.write('\r' + ' '*50 + '\r')
            print(answer, flush=True)
            PlaySound(r'.\output.wav', flags=1)  #播放生成的语音