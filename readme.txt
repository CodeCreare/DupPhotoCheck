・注意
	自由に使って頂いて構いませんが、動作結果に伴う責任は使用者にありますので、
	理解して活用ください。

・準備
	pytz, winshell, Pillow, ImageHash, pywin32のpythonライブラリを、pipでインストールしている必要があります。
	pipの使い方はここでは省略します。

	DupPhotoCheck.pyのs_dir_baseが、作業結果を格納するフォルダになります。

・使用方法
	python DupPhotoCheck.py E:\Work\Private\Photo\Data\201401

	と実行すると、そのパス直下に入ってる写真について類似、動画については同じもの、を、
	s_dir_baseで指定したフォルダに整理していきます。



