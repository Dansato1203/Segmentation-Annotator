# color_base_annotator
特定の色を抽出してセマンティックセグメンテーション用の訓練データを作成するツールです．  

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
  
  
3. トラックバーでHSVパラメータのしきい値を調整することができます．
<div align="center">
<img src=https://github.com/Dansato1203/images/blob/master/color_base_annotator/annotation.gif width=500px/>  
</div>
  
  
4. マウスの左クリックで円を描画し，余分な箇所を削除することができます．  
また，描画する円の半径を変更することも可能です．   
<div align="center">
<img src=https://github.com/Dansato1203/images/blob/master/color_base_annotator/mouseevent.gif width=500px/> 
</div>
  
  
