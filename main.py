import asyncio  # 非同期処理用ライブラリ
import websockets  # WebSocket用ライブラリ
from websockets.exceptions import (
    ConnectionClosedError,
    InvalidURI,
)  # 　例外処理判定用ライブラリ
import logging  # ログ吐き出し用ライブラリ
import json  # jsonデータ取得用ライブラリ
import pyautogui as pg # 自動操作用ライブラリ
from time import sleep # 処理待機用ライブラリ
import math # 計算用ライブラリ

logging.basicConfig(level=logging.INFO)

class Listen:
    """WebSocket通信の管理クラス"""

    def __init__(self, url, reconnect_interval=5):
        """WebSocket接続先のURLと再接続時間の初期化"""
        self.url = url  # WebSocket接続先
        self.reconnect_interval = reconnect_interval  # 再接続時間（秒）
        self.websocket = None  # WebSocketインスタンス初期化

    async def connect(self):
        """WebSocket鯖に接続、エラー時に再接続を行う"""
        while True:
            try:  # 接続チェックと接続開始
                logging.info("サーバーへ接続しています...")
                self.websocket = await websockets.connect(self.url)
                logging.info("接続しました！")
                await self.listen_comment()  # メッセージの待機を開始
            except (ConnectionClosedError, InvalidURI) as e:  # エラー時の再接続処理
                logging.error(f"接続に失敗しました: {e}")
                logging.info(f"{self.reconnect_interval}秒後に再接続します...")
                await self.close_connection()  # 接続を閉じる
                await asyncio.sleep(self.reconnect_interval)
                await self.connect()
            except Exception as e:  # 予期しないエラー時にエラーを吐き出す
                logging.error(f"予期しないエラーが発生しました: {e}")
                await self.close_connection()  # 接続を閉じる
                break

    async def listen_comment(self):
        """メッセージの受信と受信内容ごとの処理"""
        try:
            async for message in self.websocket:
                # logging.info(f"受信したメッセージ: {message}")
                self.handle_message(message)
        except ConnectionClosedError:
            logging.warning("接続が切断されました。再接続します...")
            await self.close_connection()  # 接続を閉じる
            await asyncio.sleep(self.reconnect_interval)
            await self.connect()
        except Exception as e:
            logging.error(f"リスニング中にエラーが発生: {e}")
            await self.close_connection()  # 接続を閉じる
            await asyncio.sleep(self.reconnect_interval)
            await self.connect()

    async def close_connection(self):
        """WebSocket接続を安全に閉じる"""
        if self.websocket is not None:
            await self.websocket.close()  # WebSocket接続を閉じる
            logging.info("WebSocket接続を閉じました。")

    def handle_message(self, message):
        """受信メッセージで処理を分岐"""
        data = json.loads(message) # コメントデータ
        chat_price = 0 # スパチャ金額初期化

        try:
            # print(f'コメントNo：{data["data"]["comments"][0]["meta"]}')
            print(f'コメント：{data["data"]["comments"][0]["data"]["comment"]}')
            print(f'スパチャ額：{data["data"]["comments"][0]["data"]["price"]}')

            # スパチャ額更新
            chat_price = int(data["data"]["comments"][0]["data"]["price"])
            # スポーンインスタンス生成
            sp = Spawn(chat_price)
            # 湧き情報更新
            sp.choose_spawn_pattern()
            # 敵出現処理
            sp.spawn_enemy()

            """
            今後、スパチャ額で湧く敵の数とか変更予定(別クラスで実装)
            100円ならYippee
            200円ならアイレスドッグ
            500円ならアイレスドッグ*2
            5000円でマスク5体など...
            """
            
        except:
            pass

class Spawn:
    """敵を湧かせるマクロ制御クラス"""

    def __init__(self, chat_price):
        """スパチャ額の取得、敵ナンバーのリセット"""
        self.chat_price = chat_price
        # self.enemy_id = "" # エネミーID
        self.enemy_id = 0 # アイレスドッグ固定(仮)
        self.enemy_num = 0 # 敵の湧く数

    def choose_spawn_pattern(self):
        """スパチャ額に応じて湧くエネミー、湧く数を確定(案)"""
        self.enemy_num = int(self.chat_price/200) # 200円毎に敵の数増える
        """
        match math.floor(self.chat_price/100):
            case 0:
                pass
            case 1: # 100円以上200円未満
                self.enemy_id = 1
                self.spawn_enemy()
            case 2: # 200円以上300円未満
                self.enemy_id = 2
            case 3: # 300円以上400円未満
                self.enemy_id = 3
            case 4: # 400円以上500円未満
                self.enemy_id = 4
            case 5 | 10: # 500円以上600円未満, 1000円以上1100未満
                self.enemy_id = 5
            case _:
                pass
        """

    def spawn_enemy(self):
        sleep(10)
        """指定したエネミー番号の敵を指定分出現させる"""
        for i in range(self.enemy_num):
            pg.keyDown('altleft')
            pg.press('num0')
            pg.keyUp('altleft')
            print("イッヌが湧いたよ")
            # 1秒待機
            sleep(1)
        

class Main:
    """アプリの全体制御メインクラス"""

    def __init__(self, url):
        """Listenクラスのインスタンス作成"""
        self.listener = Listen(url)

    async def start(self):
        logging.info("WebSocket接続を開始します...")
        await self.listener.connect()  # WebSocket接続開始


# エントリーポイント
if __name__ == "__main__":
    url = "ws://127.0.0.1:11180/sub"  # WebSocket接続先指定
    main_app = Main(url)  # Mainインスタンス生成

    try:
        asyncio.run(main_app.start())
    except KeyboardInterrupt:
        logging.info("処理を終了します")
