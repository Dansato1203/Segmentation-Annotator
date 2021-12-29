# color_base_annotator
セマンティックセグメンテーション用の訓練データを作成するツールです．  

## 動作環境
以下の環境で動作を確認しています．  
- OS: Ubuntu 18.04.5 LTS
- Python 3.7.11
- OpenCV 4.3.0
- PIL 8.1.0

## Usage
1. ```script```ディレクトリ内にある```main.py```を実行してください．  
```python
$ python3 main.py
```
2. アノテーションしたい画像データの入っているディレクトリを指定してください．  
```
input your image dir : {YOUR IMAGE_DIR}
```
3. トラックバーでしきい値を調整することができます．
<img src=https://github.com/Dansato1203/images/blob/master/color_base_annotator/annotation.gif width=500px/>  
