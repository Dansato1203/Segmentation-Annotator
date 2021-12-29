# color_base_annotator
特定の色を抽出してセマンティックセグメンテーション用の訓練データを作成するツールです．  
### Example: Green Extraction
<div align="center">
<img src=https://github.com/Dansato1203/images/blob/master/color_base_annotator/annotation_example.png width=700px/>  
</div>
<br />

## 動作環境
以下の環境で動作を確認しています．  
- OS: Ubuntu 18.04.5 LTS
- Python 3.7.11
- OpenCV 4.3.0
- PIL 8.1.0
- numpy 1.19.5

## Usage
1. ```script```ディレクトリ内にある```main.py```を実行してください．  
```python
$ python3 main.py
```
<br />
  
2. アノテーションしたい画像データの入っているディレクトリを指定してください．  
```
input your image dir : {YOUR IMAGE_DIR}
```
<br />
  
3. トラックバーでHSVパラメータのしきい値を調整することができます．
<div align="center">
<img src=https://github.com/Dansato1203/images/blob/master/color_base_annotator/annotation.gif width=500px/>  
</div>
<br />
  
4. マウスの左クリックで円を描画し，余分な箇所を削除することができます．  
また，描画する円の半径を変更することも可能です．   
<div align="center">
<img src=https://github.com/Dansato1203/images/blob/master/color_base_annotator/mouseevent.gif width=500px/> 
</div>
<br />  

## Advanced
何種類化の色を抽出した画像を合成することで多クラスのセグメンテーション用訓練データを作成することも可能です．  
### Example: Green & White Extraction  
<div align="center">
<img src=https://github.com/Dansato1203/images/blob/master/color_base_annotator/000020_label.png width=350px/> 
</div>
<br />  

## LICENSE
Copyright (c) 2021 Dan Sato  
This repository is licensed under The MIT License, see [LICENSE](https://github.com/Dansato1203/color_base_annotator/blob/master/LICENSE).
