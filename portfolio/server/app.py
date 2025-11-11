# ゲームの進行を管理するサーバーのコード
from flask import Flask, render_template, request
# flask→　HTTPサーバーを建てるためのフレームワーク
from flask_socketio import SocketIO, emit, join_room, leave_room
# flask_socketio→　WebSocket通信を簡単に実装するためのライブラリ
# emit→　サーバーからクライアントに情報を送るための関数
# join_room→　特定のルームにクライアントを参加させるための関数

app = Flask(__name__, template_folder='html')
# app→ Flaskアプリケーションのインスタンス
# app.pyと同じ階層にhtmlフォルダを置く
socketio = SocketIO(app, cors_allowed_origins="*")
# socketio → FlaskアプリケーションにSocket.IOの機能を追加
# SocketIO：サーバーとクライアントどちらにもインストールされていると双方向通信が可能
# cors_allowed_origins="*" → 別ドメインからの接続を許可
# socketio.run()でサーバーを起動できるようになる

game_name = {}
# 各ゲームのロジックファイルを辞書型で管理
gamestate = {}
# 各ゲームの盤面を管理する辞書
count_matches = {"othello_pvp": 0, "othello_pvc": 0, "shogi_pvp": 0, "shogi_pvc": 0, "gungi_pvp": 0, "gungi_pvc": 0}
# 対戦数をカウントする変数(game_boardsのキーに使う)
waiting_players = {"othello": None, "shogi": None, "gungi": None}
# 待機中のプレイヤーを管理する辞書(対人戦用)
connected_users = 0
# 接続したユーザー数をカウントする変数

import time

def make_match_gamestate(game, mode):
    global count_matches, gamestate
    count_matches[f"{game}_{mode}"] += 1
    if game == "othello":
        gamestate[f"{game}_{mode}_{count_matches[f'{game}_{mode}']}"] = {"board": None, "current_turn": None, "move_check": [], "remaining_time": {1: None, 2: None}, "pass_count": 0, "player_1": None, "player_2": None, "turn_count": 1}
        #オセロの試合中にapp.pyで管理するデータの初期化(盤面、現在の手番、残り時間、連続パス数、プレイヤー1、プレイヤー2, 最後に更新した時間)
    else:
        gamestate[f"{game}_{mode}_{count_matches[f'{game}_{mode}']}"] = {"board": None, "current_turn": None, "tegoma": {1:[], 2:[]}, "move_check": [], "selected_place": None, "selected_pos": None, "remaining_time": {1: None, 2: None}, "player_1": None, "player_2": None, "turn_count": 1}
        #将棋、軍議の試合中にapp.pyで管理するデータの初期化(盤面、現在の手番、手駒、残り時間、駒の選択ができているかどうか、選択した駒の場所(tegoma or board)、選択した駒の位置([x,y])、プレイヤー1、プレイヤー2, 最後に更新した時間)
    # 対局中に保存しておくデータの初期化()

@app.route('/')
# route →どのURLにアクセスしたときにどの関数を実行するか。/はトップページのURL
def index():
# htmlで最初の画面を呼び出す。
    global connected_users
    # global → 外の変数を使うよ〜〜
    connected_users += 1
    print("あなたは", connected_users, "人目の来訪者です！キリ番なら記念カキコ！")
    #return "サーバー動いてるんだが？"
    return render_template('start_index.html')
    # html内でsocket.ioに接続する

# クライアント接続時(htmlファイルを読み込むときに実行される)
@socketio.on('connect')
# htmlでsocket.ioが接続されたときに実行される(htmlが開かれたら実行される)
def handle_connect():
    sid = request.sid
    print(f"接続検知: {sid}")
# クライアント切断時
@socketio.on('disconnect')
def handle_disconnect():
# 切断(リロード)された場合にタイマーとか試合が終了するようにする。しないと二重で送られてバグる
    global gamestate
    sid = request.sid
    print(f"切断検知: {sid}")

    if sid in waiting_players.values():
        # 待機中のプレイヤーが切断した場合、待機リストから削除
        for game, player_sid in waiting_players.items():
            if player_sid == sid:
                waiting_players[game] = None
                break
        return

    for key, state in list(gamestate.items()):
        p1 = state.get("player_1")
        p2 = state.get("player_2")

        # どの試合のプレイヤーかを判定
        if sid == p1 or sid == p2:

            # 試合のモードを取得（key形式: othello_pvp_1 など）
            parts = key.split("_")
            game = parts[0]
            mode = parts[1]

            # AI戦
            if mode == "pvc":
                state["disconnected"] = True

            # 対人戦
            elif mode == "pvp":
                state["disconnected"] = True
                if sid == p1:
                    winner_sid = p2
                else:
                    winner_sid = p1

                # 勝者を確定して通知
                state["winner"] = "player_1" if sid == p2 else "player_2"
                print(f"{key}: 切断による勝敗確定 → {state['winner']} の勝ち")

                if winner_sid != "AI":
                    socketio.emit("game_over", {
                        "reason": "opponent_disconnected",
                        "winner": state["winner"]
                    }, to=winner_sid)

            break


# index.html内でゲーム(オセロ、将棋、軍議)とモード(pvp,pvc)を選択する。
# htmlは、選択したゲームとモードによって参照URLを変える。例)http://13.231.31.181:8000/othello?mode=pvp
# また、htmlはemit("pvp", {game: "othello or shogi or gungi"})の形式でもゲームとモードをサーバーに送信する。

@app.route('/othello')
#URL末尾に/othelloがついたときに実行される。例)http://13.231.31.181:8000/othello
def othello_page():
    global count_matches, game_name
    import logic.othello.logic_othello as othello  # ゲームのロジックファイルを読み込む
    # logic_othello.py内でインポートするときはファイル名の前に'.'をつけること！注意
    mode = request.args.get("mode", "pvc")  # URLパラメータからmodeを受け取る。 デフォルトはpvc
    game_name["othello"] = othello
    return render_template("othello.html", game = "othello", mode = mode, count_matches = count_matches[f"othello_{mode}"])
    # modeをhtmlに渡す。html内でmodeによって処理を変える。
    # html内では、{{ mode }} が "pvp" または "pvc" に置き換えられる。

@app.route('/shogi')
def shogi_page():
    global count_matches, game_name
    import logic.shogi.logic_shogi as shogi
    mode = request.args.get("mode", "pvc")
    game_name["shogi"] = shogi
    return render_template("shogi.html", game = "shogi", mode = mode, count_matches = count_matches[f"shogi_{mode}"])
    # htmlには、試合の識別子としてmodeとcount_matches を渡す。

@app.route('/gungi')
def gungi_page():
    global count_matches, game_name
    import logic.gungi.logic_gungi as gungi
    mode = request.args.get("mode", "pvc")
    game_name["gungi"] = gungi
    return render_template("gungi.html", game = "gungi", mode = mode, count_matches = count_matches[f"gungi_{mode}"])

# プレイヤーが対AI戦を選択してゲームに参加したとき
@socketio.on("pvc")
def handle_pvc(data):
    #data = {game: "othello"}
    global gamestate, count_matches, game_name
    game = data["game"]  # "othello", "shogi", "gungi"
    count_matches[f"{game}_pvc"] += 1
    # 試合の識別子を作成
    make_match_gamestate(game, "pvc")
    # 試合のデータを初期化
    match = count_matches[f"{game}_pvc"]
    key = f"{game}_pvc_{match}"

    player = hash(time.time()) % 2 + 1
    # hash(time.time()) → 現在の時間を整数に変換してハッシュ化
    gamestate[key][f"player_{player}"] = request.sid
    gamestate[key][f"player_{player % 2 + 1}"] = "AI"
    
    game_data = game_name[game].game_start()
    # 各ゲームのlogicファイル内で定義されているgame_start()関数を呼び出して初期盤面を取得
    # game_data = {"board": board, "remaining_time": {1: 300, 2: 300}, "current_turn": 1,(将棋 or 軍議ならば→ "tegoma": {1: [], 2: []})}のような形
    gamestate[key]["board"] = game_data["board"]
    gamestate[key]["remaining_time"] = game_data["remaining_time"]
    gamestate[key]["current_turn"] = game_data["current_turn"]
     
    if game != "othello":
        gamestate[key]["tegoma"] = game_data["tegoma"]
        # 将棋、軍議の場合は手駒の情報も追加
    emit("start_game", {"gamestate": gamestate[key], "count_matches": count_matches})

    # 現在の手番を通知
    send_signal(key, "turn")

    socketio.start_background_task(timer, game, "pvc", match)
    # バックグラウンドでtimer関数を実行(非同期処理)

# プレイヤーが対人戦を選択してゲームに参加したとき
@socketio.on("pvp")
def handle_join(data):
    #data = {game: "othello"}
    global waiting_players, count_matches, gamestate
    game = data["game"]  # "othello", "shogi", "gungi"
    player_id = request.sid
    # request.sid → 接続しているクライアントの一意のID(名前みたいなもの)

    if waiting_players[game] is None:
        # まだ待機者がいない → この人を待機させる
        waiting_players[game] = player_id
        emit("waiting", {"msg": "相手を待っています..."})
    elif player_id != waiting_players[game]:
        # 待機者がいた → ペアを作ってルームを作成
        count_matches[f"{game}_pvp"] += 1
        make_match_gamestate(game, "pvp")
        match = count_matches[f"{game}_pvp"]
        key = f"{game}_pvp_{match}"

        opponent_id = waiting_players[game]
        print(player_id, "vs", opponent_id)
        # 待機者リセット
        waiting_players[game] = None
        room = f"{game}_pvp_{match}"
        join_room(room, sid=opponent_id)
        join_room(room, sid=player_id)

        player = hash(time.time()) % 2 + 1
        gamestate[key][f"player_{player}"] = request.sid
        gamestate[key][f"player_{player % 2 + 1}"] = opponent_id

        game_data = game_name[game].game_start()            
        # ルームごとに盤面を保存
        gamestate[key]["board"] = game_data["board"]
        gamestate[key]["remaining_time"] = game_data["remaining_time"]
        gamestate[key]["current_turn"] = game_data["current_turn"]

        if game != "othello":
            gamestate[key]["tegoma"] = game_data["tegoma"]
        # 両方にゲーム開始を通知
        gamestate[key]["main_update_time"] = game_data["remaining_time"][gamestate[key]["current_turn"]]
        emit("start_game", {"gamestate": gamestate[key], "count_matches": count_matches}, room = room)

        # 現在の手番を通知
        send_signal(key, "turn")

        socketio.start_background_task(timer, game, "pvp", match)
        # バックグラウンドのタイマーを開始
        
        return

# プレイヤーが手を打ったとき
@socketio.on("make_move")
# 各ゲームのjs内でsocket.emit("make_move", {game: "othello", mode: "pvp", count_match: 数字, place:"board", x: x, y: y, current_player: 1})のように送信される
# 送信されるデータは、pythonでは辞書型に変換される。
# game = "othello" / "shogi" / "gungi"
# x, y = プレイヤーが打った座標
# player = 1 or 2
def handle_make_move(data):
    global gamestate
    # data = {game: "othello", mode:"pvp", count_match: 数字, place:"board" or "tegoma", koma:数字, x: x, y: y, current_player: 1}
    # placeがboard→駒の座標で判別、tegoma→駒の種類で判別
    game = data["game"]
    mode = data["mode"]
    match = data["count_match"][f"{game}_{mode}"]
    key = f"{game}_{mode}_{match}"
    place = data["place"]
    if place == "tegoma":
        x, y = None, None
        koma = data["koma"]
    elif place == "board":
        x, y = data["x"], data["y"]
        koma = None
    player = data["current_player"]
    board = gamestate[key]["board"]

    if (place != "board" and place != "tegoma"):
        # placeがboardでもtegomaでもない場合、エラー
        emit("error", {"msg": "おけないよん"}, to = request.sid)
        return
    
    if mode == "pvp" :
        if request.sid != gamestate[key][f"player_{player}"]:
            #pvpで、手を打とうとしたプレイヤーが現在の手番のプレイヤーではない場合
            emit("error", {"msg": "おけないよん"}, to = request.sid)
            return

    if game == "othello":
    # オセロの場合
        outcome = game_name[game].handle_player_move(board, player, [x,y])
        # 移動判定、勝敗判定、ターン交代を行う。
        #outcome = {"status": "success" or "error","board_grid": board.grid,"current_turn": current_turn, "winner": gamestate.winner,"scores": {"black": black_count, "white": white_count}}
        if outcome["status"] == "error":
            # 打てない場合
            emit("error", {"msg": "おけないよん"}, to = request.sid)
            return
        else:
            # 打てた場合
            gamestate[key]["board"] = outcome["board_grid"]
            gamestate[key]["current_turn"] = outcome["current_turn"]
            if outcome["winner"] is not None:
                # 勝者が決定している場合
                gamestate[key]["winner"] = outcome["winner"]
                if mode == "pvp":
                    emit("game_over", {"board": gamestate[key]["board"], "scores": outcome["scores"]}, room = key)
                else:
                    emit("game_over", {"board": gamestate[key]["board"], "scores": outcome["scores"]})
                send_signal(key, "game_over")
                return
            else:
                # 勝者が決定していないのであればターン交代(パスの確認を挟む)
                swich_turn_god(game, mode, match)
                return
    else:
    # 将棋、軍議の場合
        tegoma = gamestate[key]["tegoma"][player]
        if gamestate[key]["move_check"] == []:
        # 1回目の選択ができていない場合
            valid_moves = game_name[game].get_valid_moves(board, tegoma, player, place, [x,y], koma)
            #[x,y] もしくは koma が None
            if valid_moves != []:
            # 選択した駒が動ける場合
                gamestate[key]["move_check"] = valid_moves
                gamestate[key]["selected_place"] = place
                if place == "tegoma":
                    gamestate[key]["selected_pos"] = koma
                else:
                    gamestate[key]["selected_pos"] = [x,y]
                emit("blight", {"blight_list": valid_moves, "place": place}, to = request.sid)
                return
            else:
            # 選択した駒が動けない場合
                emit("error", {"msg": "おけないよん"}, to = request.sid)
                return
        else:
        # 1回目の選択ができている場合(2回目の選択)
            emit("cansel_bright", {}, to = request.sid)
            # 光らせている場所を消す
            if place == "tegoma":
            # 手駒には動かせないのでエラー
                emit("error", {"msg": "おけないよん"}, to = request.sid)
                return
            if [x,y] in gamestate[key]["move_check"]:
            # 動ける場所リストの中に選択した場所がある場合
                outcome = game_name[game].handle_player_move(board, tegoma, player, gamestate[key]["selected_place"], gamestate[key]["selected_pos"], [x,y])
                # gamestate[key]["selected_pos"]には、tegomaなら数字、boardなら[x,y]が入る。注意
                # 動ける前提で勝敗判定、(将棋:成定),(軍議:ツケ,謀の能力)の発生判定と移動判定(ターン切り替えは含まない。)を行う。
                # outcome = {"winner": None or 1 or 2,"nari_check": True or False,"tuke_check": True or False,"bou_check": True or False, "board_grid": board.grid,"tegoma": tegoma}
                gamestate[key]["board"] = outcome["board_grid"]
                gamestate[key]["tegoma"] = outcome["tegoma"]
                # 勝敗がついている場合でも手駒を更新するので、王や帥を取った際に手駒に追加しないよう注意
                gamestate[key]["move_check"] = []
                gamestate[key]["selected_place"] = None
                if outcome["winner"] is not None:
                    gamestate[key]["winner"] = outcome["winner"]
                    if mode == "pvp":
                        emit("game_over", {"board": gamestate[key]["board"], "tegoma": outcome["tegoma"], "scores": outcome["scores"]}, room = key)
                        send_signal(key, "game_over")
                    else:
                        emit("game_over", {"board": gamestate[key]["board"], "tegoma": outcome["tegoma"], "scores": outcome["scores"]})
                        send_signal(key, "game_over")
                    return
                else:
                    if game == "shogi" and outcome["nari_check"]:
                        # 将棋の成りが発生する場合、htmlにcheckを送るとともにselected_posに該当座標を保存しておく。
                        emit("blight", {"blight_list": [[x,y]], "place": place}, to = request.sid)
                        # わかりやすいように成る駒を光らせる
                        gamestate[key]["selected_pos"] = [x,y]
                        emit("nari_check", {"board": outcome["board_grid"], "tegoma": outcome["tegoma"]}, to = request.sid)
                    elif game == "gungi" and (outcome["tuke_check"]):
                        # 軍議のツケが発生する場合、selected_posに該当座標を保存しておく。
                        emit("blight", {"blight_list": [[x,y]], "place": place}, to = request.sid)
                        # わかりやすいようにツケる駒を光らせる
                        gamestate[key]["selected_pos"] = [x,y]
                        emit("tuke_check", {"board": outcome["board_grid"], "tegoma": outcome["tegoma"]}, to = request.sid)
                        if game == "gungi" and (outcome["bou_check"]):
                            gamestate[key]["bou_check_after_tuke"] = True
                        # ツケ+謀があった場合、htmlはツケの処理　→　emitでapp.pyに送る → 謀の処理 → emitでapp.pyに送る の順番で行う
                    elif game == "gungi" and (outcome["bou_check"]):
                        # 軍議の謀が発生する場合、selected_posに該当座標を保存しておく。
                        emit("blight", {"blight_list": [[x,y]], "place": place}, to = request.sid)
                        # わかりやすいように謀駒を光らせる
                        gamestate[key]["selected_pos"] = [x,y]
                        emit("bou_check", {"board": outcome["board_grid"], "tegoma": outcome["tegoma"]}, to = request.sid)
                    else:
                        # 何のチェックも発生しなかった場合、ターン交代
                        gamestate[key]["current_turn"] = gamestate[key]["current_turn"] % 2 + 1
                        swich_turn_god(game, mode, match)

# AIの手を実行する。(時間だけ送られるので、JSはAIのターン受信→好きな時間空ける→emit送信 すればok)
@socketio.on("make_AI_move")
def handle_make_AI_move(data):
    # data = {game: "shogi", mode:"pvp", count_match: 数字}
    global gamestate
    game = data["game"]
    mode = data["mode"]
    match = data["count_match"][f"{game}_{mode}"]
    key = f"{game}_{mode}_{match}"
    current_turn = gamestate[key]["current_turn"]
    if game == "othello":
        outcome = game_name[game].check_pass(gamestate[key]["board"], current_turn)
        # outcome = {"pass": True or False}
        if outcome["pass"]:
            # パスする場合、手番交代
            gamestate[key]["current_turn"] = gamestate[key]["current_turn"] % 2 + 1
            gamestate[key]["pass_count"] += 1
            if mode == "pvp":
                emit("pass", {"current_turn": gamestate[key]["current_turn"]}, room = key)
            else:
                emit("pass", {"current_turn": gamestate[key]["current_turn"]})
            outcome = game_name[game].check_pass(gamestate[key]["board"], current_turn)
            # 連続パスかどうか確認
            if outcome["pass"]:
                # 連続パスの場合、ゲーム終了
                if mode == "pvp":
                    emit("game_over", {"board": gamestate[key]["board"], "scores": outcome["scores"]}, room = key)
                    send_signal(key, "game_over")
                else:
                    emit("game_over", {"board": gamestate[key]["board"], "scores": outcome["scores"]})
                    send_signal(key, "game_over")
                return
            gamestate[key]["pass_count"] = 0
    
    # AIの手を実行
    outcome = game_name[game].handle_ai_move(gamestate[key], gamestate[key]["current_turn"])
    #outcome = {"board_grid": board.grid,"current_turn": current_turn, "winner": gamestate.winner,"scores": {"black": black_count, "white": white_count}}
    #オセロならスコア、将棋、軍議なら手駒も更新される。
    if "winner" in gamestate[key] and game == "othello":
        if mode == "pvp":
            emit("game_over", {"board": gamestate[key]["board"], "scores": outcome["scores"]}, room = key)
            send_signal(key, "game_over")
        else:
            emit("game_over", {"board": gamestate[key]["board"], "scores": outcome["scores"]})
            send_signal(key, "game_over")
        return
    elif "winner" in gamestate[key] and (game == "shogi" or game == "gungi"):
        if mode == "pvp":
            emit("game_over", {"board": gamestate[key]["board"], "tegoma": gamestate[key]["tegoma"]}, room = key)
            send_signal(key, "game_over")
        else:
            emit("game_over", {"board": gamestate[key]["board"], "tegoma": gamestate[key]["tegoma"]})
            send_signal(key, "game_over")
        return
    else:
        # AIの手の中でcurrent_turnが変わっていることになっている。わかりづらくてすまん。
        swich_turn_god(game, mode, match)
        return

def swich_turn_god(game, mode, match):
    global gamestate
    key = f"{game}_{mode}_{match}"
    # 現在の盤面情報とターン数を送信
    gamestate[key]["turn_count"] += 1
    if  mode == "pvc":
        emit("game_data", {"gamestate": gamestate[key], "count_matches": count_matches, "turn_count": gamestate[key]["turn_count"]})
    else:
        emit("game_data", {"gamestate": gamestate[key], "count_matches": count_matches, "turn_count": gamestate[key]["turn_count"]}, room = key)
    #オセロのパス確認、AIの手番、現在の手番かどうかをそれぞれに送信する
    if gamestate[key][f"remaining_time"][gamestate[key]["current_turn"]] < 60:
    # 残り時間が60秒未満の場合、60秒にする
        gamestate[key]["remaining_time"][gamestate[key]["current_turn"]] = 60
    if game == "othello":
    # オセロのパス確認
        current_turn = gamestate[key]["current_turn"]
        outcome = game_name[game].check_pass(gamestate[key]["board"], current_turn)
        # outcome = {"pass": True or False}
        if outcome["pass"]:
            # パスする場合、手番交代
            gamestate[key]["current_turn"] = gamestate[key]["current_turn"] % 2 + 1
            gamestate[key]["pass_count"] += 1
            if mode == "pvp":
                emit("pass", {"current_turn": gamestate[key]["current_turn"]}, room = key)
            else:
                emit("pass", {"current_turn": gamestate[key]["current_turn"]})
            outcome = game_name[game].check_pass(gamestate[key]["board"], current_turn)
            # 連続パスかどうか確認
            if outcome["pass"]:
                # 連続パスの場合、ゲーム終了
                if mode == "pvp":
                    emit("game_over", {"board": gamestate[key]["board"], "scores": outcome["scores"]}, room = key)
                    send_signal(key, "game_over")
                else:
                    emit("game_over", {"board": gamestate[key]["board"], "scores": outcome["scores"]})
                    send_signal(key, "game_over")
                return
            gamestate[key]["pass_count"] = 0
    # 現在の手番の送信
    send_signal(key, "turn")

# 勝敗が決まったとき、または手番が変わったときに相手に通知する用(対人戦でも対AI戦でもok)
def send_signal(key, event):
    # event = "game_over" or "turn"
    # key = f"{game}_{mode}_{match}"
    global gamestate
    if event == "game_over":
        winner = gamestate[key]["winner"]
        players = {
            "game_over_win":gamestate[key][f"player_{winner}"],
            "game_over_lose":gamestate[key][f"player_{winner % 2 + 1}"]
        }
    elif  event == "turn":
        current_turn = gamestate[key]["current_turn"]
        players = {
            "your_turn":gamestate[key][f"player_{current_turn}"],
            "opponent_turn":gamestate[key][f"player_{current_turn % 2 + 1}"]
        }
    else:
        return
    for event, player in players.items():
        if player != "AI":
            emit(event, {}, to = player)
    return

def timer(game, mode, match):
    global gamestate
    key = f"{game}_{mode}_{match}"
    while True:
        # すでに勝敗がついていたら終了
        if "winner" in gamestate[key] or gamestate[key].get("disconnected", False):
            break

        if gamestate[key]["remaining_time"][gamestate[key]["current_turn"]] <= 0:
            # 時間切れ(相手の手番に)
            gamestate[key]["current_turn"] = gamestate[key]["current_turn"] % 2 + 1
            if mode == "pvp":
                emit("time_out", {}, room=key)
            else:
                emit("time_out", {})
            swich_turn_god(game, mode, match)

        # 1秒ごとに更新情報を送る
        if mode == "pvp":
            socketio.emit("time_update", {
                "remaining_time": gamestate[key]["remaining_time"][gamestate[key]["current_turn"]],
                "current_turn": gamestate[key]["current_turn"]
            }, room=key)
        else:
            socketio.emit("time_update", {
                "remaining_time": gamestate[key]["remaining_time"][gamestate[key]["current_turn"]],
                "current_turn": gamestate[key]["current_turn"]
            })

        gamestate[key]["remaining_time"][gamestate[key]["current_turn"]] -= 1

        time.sleep(1)

@socketio.on("check")
def handle_check(data):
    global gamestate
    # data = {game: "shogi", mode:"pvp", count_match: 辞書, check: "nari" or "tuke" or "bou" or "cancel", current_turn: current_turn}
    game = data["game"]
    mode = data["mode"]
    match = data["count_match"][f"{game}_{mode}"]
    key = f"{game}_{mode}_{match}"
    check = data["check"]
    x, y = gamestate[key]["selected_pos"]
    player = data["current_turn"]
    board = gamestate[key]["board"]
    tegoma = gamestate[key]["tegoma"]

    emit("cansel_bright", {}, to = request.sid)
    # 光らせている場所を消す

    if request.sid != gamestate[key][f"player_{player}"]:
        emit("error", {"msg": "おけないよん"}, to = request.sid)
        return

    if check == "cancel":
        gamestate[key]["selected_pos"] = None
        return

    if game == "shogi" and check == "nari":
        outcome = game_name[game].handle_nari(board, player, gamestate[key]["selected_pos"], [x,y])
        # outcome = {"board_grid": board.grid,"current_turn": current_turn}
        gamestate[key]["board"] = outcome["board_grid"]
        gamestate[key]["selected_pos"] = None
    elif game == "gungi" and check == "tuke":
        outcome = game_name[game].handle_tuke(board, player, gamestate[key]["selected_pos"], [x,y])
        # outcome = {"board_grid": board.grid,"current_turn": current_turn}
        gamestate[key]["board"] = outcome["board_grid"]
        gamestate[key]["selected_pos"] = None
    elif game == "gungi" and check == "bou":
        outcome = game_name[game].handle_bou(board, tegoma, player, gamestate[key]["selected_pos"], [x,y])
        # 謀は手駒の更新がある
        # outcome = {"board_grid": board.grid,"tegoma": tegoma,"current_turn": current_turn}
        gamestate[key]["board"] = outcome["board_grid"]
        gamestate[key]["tegoma"] = outcome["tegoma"]
        gamestate[key]["selected_pos"] = None
    
    if (game == "gungi" and check == "tuke") and ("bou_check_after_tuke" in gamestate[key]):
        remove = gamestate[key].pop("bou_check_after_tuke")
        # 削除するためなのでremove変数は使わなくてok
        return
    else:
        gamestate[key]["current_turn"] = gamestate[key]["current_turn"] % 2 + 1
        swich_turn_god(game, mode, match)
        return

@socketio.on("finish")
def handle_finish(data):
    global gamestate
    # data = {game: "othello", mode:"pvp", count_match: 辞書, "end_or_continue": "end" or "continue"}
    game = data["game"]
    mode = data["mode"]
    match = data["count_match"][f"{game}_{mode}"]
    key = f"{game}_{mode}_{match}"
    choose = data["end_or_continue"]
    print(choose)
    if mode == "pvp":
        room = key
        leave_room(room, sid=gamestate[key]["player_1"])
        leave_room(room, sid=gamestate[key]["player_2"])
    if choose == "end":
        emit("game_end", {})
        return
    elif choose == "continue":
        emit("game_continue", {})
        # html側はリロードして最初の画面に戻る
        return
    

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
