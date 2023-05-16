# Chatwife
A Chatgpt tool to chat with your wife (supports typing or talking) 一个和你老婆聊天的程序（支持打字和语音输入）

## Getting Started (开始）

### Prerequisites （环境准备工作）

```
git clone https://github.com/liyunlongaaa/Chatwife.git
cd Chatwife
conda create -n Chatwife python=3.9
conda activate Chatwife
pip install -r requirements.txt
```
### 修改配置文件config.ini
![image](https://github.com/liyunlongaaa/Chatwife/assets/49556860/16780e53-d1d9-4f03-af78-6bbbf57cb613)

### 下载语音识别模型
[https://www.aliyundrive.com/s/VTYy4qHothh](https://www.aliyundrive.com/s/VTYy4qHothh)

下载完后把所有ASR\resources文件夹如图所示:
![image](https://github.com/liyunlongaaa/Chatwife/assets/49556860/292de701-52b3-4fd7-88f4-6ae07ab86baf)


### 下载语音合成模型
[https://www.aliyundrive.com/s/VTYy4qHothh](https://www.aliyundrive.com/s/PBCXR3XpDZS)

下载完后把所有文件放入TTS\文件夹如图所示:
![image](https://github.com/liyunlongaaa/Chatwife/assets/49556860/4aa8918a-0edd-4143-bdc4-ed35208bb2ab)

### 和老婆文字聊天

```
python Chatwife.py
```
![image](https://github.com/liyunlongaaa/Chatwife/assets/49556860/7df19201-98df-45d0-8d9f-1d075c05127b) <br>
按0或1后回车Enter, 选择你老婆说话的语言 <br>
![image](https://github.com/liyunlongaaa/Chatwife/assets/49556860/bd53922e-eab7-42dc-845d-989878eff2da) <br>
之后选择你老婆的人设，我喜欢你老婆是大学生，所以选0后回车 <br>
![image](https://github.com/liyunlongaaa/Chatwife/assets/49556860/c363eb45-2da0-47e7-8c8d-2b4b691d4361) <br>
选择你老婆的声线，这里我喜欢御姐 <br>
![image](https://github.com/liyunlongaaa/Chatwife/assets/49556860/2dc37303-7d26-4903-a850-26812268ab25) <br>
之后取个名字或者加载以前的记忆，开始聊天 <br>
![image](https://github.com/liyunlongaaa/Chatwife/assets/49556860/d8044edd-8944-43d8-9160-14dc67e9cad3)



### 和老婆语音聊天

```
python Chatwife_speech.py
```
步骤和上面一样，只是聊天方式变为：长按V说话，松开后则将语音发送给你老婆。 可按键盘左上角的ESC键结束聊天


## TODO
- [x] 支持语音输入
- [ ] 打字和语音随时切换
- [ ] 记忆优化
- [ ] 支持更多的语言模型

## License
本项目仅供大家学习参考，不可商业，否则后果完全由使用者承担！！！

## Acknowledgments

* 非理性编程(bilibili)
