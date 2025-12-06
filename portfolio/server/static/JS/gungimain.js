//将棋の表示(JavaScript) 
const socket = io(); // Flask-SocketIOならこのURL

//接続した時に実行される
socket.on('connect', () => {
console.log('接続成功');
});

/*プレイが始まるまでにやること------------------------------------------------------
・モード（ゲームの種類・対AI/対人）をapp.pyに送信
・対戦相手待ちpopの表示（app.pyから指示があれば）
・ゲーム開始処理（一度目のデータ受信）
*/

const game_mode = document.getElementById("mode").textContent.trim();
const game = document.getElementById("game").textContent.trim();
//まずモードをapp.pyに送信　例えば("pvp",{game:"othello"})
socket.emit(game_mode, { "game": game })


const pop = document.getElementById("popBG");
const hidaripop = document.getElementById("hidaripopBG");
const popuptext = document.getElementById("popUpper");
//対戦相手待ち...waiting受信処理→pop表示
socket.on('waiting', (data) => {// data={"msg": "相手を待っています..."}
    activate_pop([data["msg"]],["ゲーム選択画面に戻る"])
    console.log("waiting受信");
});


let count_matches = 0;//データ保存用
let gamestate = 0;//データ保存用
let on_playing = false;//ゲーム最中（→ゲーム開始～決着）かを判定する変数
//ゲームスタート...start_game受信処理→一度目の種々のデータ受信
socket.on('start_game', (data) => {// data={"gamestate": gamestate[key], "count_matche"s: count_matches})
    count_matches = data["count_matches"];
    gamestate = data["gamestate"];//辞書gamestate["othello"]のキー..."board","current_turn","remaining_time"(→1,2のキーにそれぞれの残り秒数が入っている)
    pop.classList.remove("is_active");
    on_playing = true;
    console.log("start_game受信");
});


//画面作成...要素作成と入力処理設定
//<メインのボード>
for(let r = 1 ; r <= 9 ; r ++){
    for(let c = 1 ; c <= 9 ; c ++){// r:row(行)　c:column(列)
        const block = document.createElement("div");
        document.getElementById("mainB").appendChild(block);
        block.classList.add("komablock");
        block.id = `komablock_r${r}_c${c}`;
        block.style.top = `${11*r-5}%`;
        block.style.left = `${11*c-5}%`;

        //入力処理...クリックされたとき→make_move送信 
        block.addEventListener('click', () =>{
            if (current_turn == "slf" && click_ok == true){
                if(player_index==1){
                    socket.emit("make_move", {"game": "gungi", "mode": game_mode, "count_match": count_matches, "place":"board", x: c-1, y: r-1, "current_player": player_index});//ロジックでは左上が0,0なので-1して調整
                    console.log("make_move送信.player_index=1","x,y=",c-1,r-1)
                }else{//player_indexが２の時は画像が反転しているので座標を調整
                    socket.emit("make_move", {"game": "gungi", "mode": game_mode, "count_match": count_matches, "place":"board", x: 9-c, y: 9-r, "current_player": player_index});//ロジックでは左上が0,0なので-1して調整
                    console.log("make_move送信.player_index=2","x,y=",9-c,9-r)
                }
            }
        });

        for(let h=1 ; h<=3; h++){//画像要素を、各座標各段数分作成
            const img = document.createElement("img");
            document.getElementById("mainB").appendChild(img);
            img.classList.add("komaimg");
            img.id = `komaimg_r${r}_c${c}_h${h}`;
            img.style.top = `${11*r-5-3*(h-1)}%`;
            img.style.left = `${11*c-5}%`;

            //ホバー処理...マウスが駒の上にホバー中、重なった駒を表示させる
            img.addEventListener('mouseenter', () =>{
                if(current_turn == "slf" && click_ok == true){
                    naraberu([r,c]);//表示関数
                }
            });
            img.addEventListener('mouseleave', () =>{
                if(current_turn == "slf"){
                    naraberu_delete()//表示消去関数
                }
            });
            //入力処理...重なりの最上段の駒クリックされたとき→make_move送信 
            img.addEventListener('click', () =>{
            if (current_turn == "slf" && click_ok == true && floor_grid[r-1][c-1] == h){
                    if(player_index==1){
                        socket.emit("make_move", {"game": "gungi", "mode": game_mode, "count_match": count_matches, "place":"board", x: c-1, y: r-1, "current_player": player_index});//ロジックでは左上が0,0なので-1して調整
                        console.log("make_move送信.player_index=1","x,y=",c-1,r-1)
                    }else{
                        socket.emit("make_move", {"game": "gungi", "mode": game_mode, "count_match": count_matches, "place":"board", x: 9-c, y: 9-r, "current_player": player_index});//ロジックでは左上が0,0なので-1して調整
                        console.log("make_move送信.player_index=2","x,y=",9-c,9-r)
                    }
                }
            });
        }
    };
};
//<手ごま>
//手ごま_1（自分（右下））
for(let r = 1 ; r <= 5 ; r ++){
    for(let c = 1 ; c <= 4 ; c ++){// r:row(行)　c:column(列)
        const block = document.createElement("div");
        document.getElementById("tegoma1").appendChild(block);
        block.classList.add("tegomablock");
        block.id = `tegoma1block_r${r}_c${c}`;
        block.style.top = `${20*r-10}%`;
        block.style.left = `${24*c-10}%`;

        const img = document.createElement("img");
        document.getElementById("tegoma1").appendChild(img);
        img.classList.add("tegomaimg");
        img.id = `tegoma1img_r${r}_c${c}`;
        img.style.top = `${20*r-10}%`;
        img.style.left = `${24*c-10}%`;

        const maisuu = document.createElement("div");
        document.getElementById("tegoma1").appendChild(maisuu);
        maisuu.classList.add("tegomamaisuu_self");
        maisuu.id = `tegoma1maisuu_r${r}_c${c}`;
        maisuu.style.top = `${20*r-10-5.5}%`;
        maisuu.style.left = `${24*c-10+8}%`;


        //入力処理...クリックされたとき→make_move送信する
        img.addEventListener('click', () =>{
            if (current_turn == "slf" && click_ok == true){
                socket.emit("make_move", {"game": "gungi", "mode": game_mode, "count_match": count_matches, "place":"tegoma", "koma":tegoma_grid[1][c-1+4*(r-1)]  , "current_player": player_index});
                console.log("make_move送信 駒：",tegoma_grid[1][c-1+4*(r-1)])
            }
        });
    };
};
//手ごま_2（相手（左上））（クリックはできない）
for(let r = 1 ; r <= 5 ; r ++){
    for(let c = 1 ; c <= 4 ; c ++){/* r:row(行)　c:column(列) */
        const block = document.createElement("div");
        document.getElementById("tegoma2").appendChild(block);
        block.classList.add("tegomablock");
        block.id = `tegoma2block_r${r}_c${c}`;
        block.style.bottom = `${20*r-29}%`;
        block.style.right = `${24*c-34}%`;

        const img = document.createElement("img");
        document.getElementById("tegoma2").appendChild(img);
        img.classList.add("tegomaimg");
        img.id = `tegoma2img_r${r}_c${c}`;
        img.style.bottom = `${20*r-29}%`;
        img.style.right = `${24*c-34}%`;

        const maisuu = document.createElement("div");
        document.getElementById("tegoma2").appendChild(maisuu);
        maisuu.classList.add("tegomamaisuu_oppo");
        maisuu.id = `tegoma2maisuu_r${r}_c${c}`;
        maisuu.style.bottom = `${20*(r+1)-29-6}%`;
        maisuu.style.right = `${24*(c+1)-34+8}%`;
        
    };
};

//降参ボタン
const touryou_pop = document.getElementById("touryou_pop");
touryou_pop.addEventListener("click",()=>{
    if(on_playing == true){
        activate_play_pop("降参しますか？")
    }
})

//CPUが考えているときの。。。表示
const thinking_time = document.createElement("div");
thinking_time.id = "thinking_time_CPU";//pvpの時は常に非表示のまま
document.getElementById("mainB").appendChild(thinking_time)
thinking_time.textContent = "......."


//プレイ中の、受け取ったデータへの反応--------------------------------------------
let click_ok = false;//入力できる状態かそうでないかを判定

let now_blight = 0
socket.on('blight', (data) => {// emit("blight", {"blight_list": valid_moves, "place": place}, to = request.sid) placeはblightに関してはboardのみ？だから使わなくてOK？
    now_blight = data["blight_list"];// javascript側で今光らせているところを保存しておく（特にcansel_brightで用いる）
    blight(now_blight);/* 光らせる関数を実行 */
    console.log("blight受信");
});
socket.on('cansel_bright', () => {/* dataなし。brightをblightに直してもらうか問題 */
    cansel_bright(now_blight);
    console.log("cansel_blight受信");
});

let timerID_hidaripop = 0
socket.on('error', (data) => {/* emit("error", {"msg": "おけないよん"}, to = request.sid) */
    if(hidaripop.classList.contains("is_active")){//既にポップが表示されていたら、非表示になるまでの時間を上書きする
        clearTimeout(timerID_hidaripop);
        hidaripop.classList.remove("blight_to_normal");
        void hidaripop.offsetWidth;
    }
    hidaripop.innerHTML = "＜"+data["msg"]+"＞";
    hidaripop.classList.add("is_active");
    hidaripop.classList.add("blight_to_normal");
    console.log("error受信");
    timerID_hidaripop = setTimeout(() => {
    // 1.5秒後に実行される非表示処理
        hidaripop.classList.remove("is_active");
        hidaripop.classList.remove("blight_to_normal");
        console.log("errorpop消去");
    }, 1500); // 単位はミリ秒（1000ms = 1秒）
});

socket.on('nari_check',(data)=>{
    activate_play_pop("成りますか？");
    click_ok = false;//成りチェックのフェーズはいったら次のターンまで入力処理は要らないのでfalse
    console.log("nari_check受信");
})


socket.on('game_data',(data)=>{//emit("game_data", {"gamestate": gamestate[key], "count_matches": count_matches})
    if((game_mode == "pvc") && (data["gamestate"]["current_turn"] == player_index)){//CPUの一手が送られてくるまでにラグがあるので、その間表示していた「。。。」を、ここで消す
        thinking_time.classList.remove("is_active");
    }
    if(data["gamestate"]["current_turn"] == player_index){
        current_turn = "slf";
        board_update(data["gamestate"]["board"],data["gamestate"]["tegoma"]);
        console.log("game_data受信","current_turn:自分");
    }
    else if(!(data["gamestate"]["current_turn"] == player_index)){
        current_turn = "opp";
        board_update(data["gamestate"]["board"],data["gamestate"]["tegoma"]);
        console.log("game_data受信","current_turn:相手");
    }
    //console.log("送られてきた手ごま：",data["gamestate"]["tegoma"])
});

socket.on('game_over', (data) => {/* emit("game_over", {"board": board, "scores": outcome["scores"]}または{"reason": "opponent_disconnected","winner": state["winner"]}, room = key) */
    if (game_mode == "pvc"){//相手がAIなら「。。。」の表示消す
        thinking_time.classList.remove("is_active");
    }
    if (!(data["reason"] == "opponent_disconnected") && !(data["reason"] == "give_up")){
        board_update(data["board"],gamestate["tegoma"]);
        console.log(data["board"]);
        console.log("最後のboard_update（盤面更新）");
    }
    setTimeout(() => {//相手の切断→こちらの勝ち
        if (data["reason"] == "opponent_disconnected"){
            activate_pop(["YOU WIN","相手が切断しました"], ["もう一度","止める"]);
        }
    },1000)

    if(data["reason"] == "give_up"){//どちらかの降参
        setTimeout(() => {
            if (data["winner"] == `player_${player_index}`){
                activate_pop(["YOU WIN","相手が降参しました"], ["もう一度","止める"]);
            }else{
                activate_pop(["YOU LOSE","降参しました"], ["もう一度","止める"]); 
            }
        },1000)
    }
    console.log("game_over受信")
});

socket.on("game_over_win",(data) => {
    setTimeout(() => {
            activate_pop(["YOU WIN","終局です"], ["もう一度","止める"]);
    },1000)
})

socket.on("game_over_lose",(data) => {
    setTimeout(() => {
            activate_pop(["YOU LOSE","終局です"], ["もう一度","止める"]);
    },1000)
})



socket.on('pass', (data) => {/* emit("pass", {"current_turn": gamestate[key]["current_turn"]}, room = key) */
    if (player_index == data["current_turn"]){
        activate_pop(["＜相手 がパスしました＞"],[]);
        console.log("pass受信","current_turn:自分");
        current_turn = "slf";
    }
    if (!(player_index == data["current_turn"])){
        activate_pop(["＜YOU がパスしました＞"],[])
        console.log("pass受信","current_turn:相手");
        current_turn = "opp";
    }
    timerID_MainPop = setTimeout(() => {
    // 1秒後に実行される非表示処理
        pop.classList.remove("is_active");
        on_playing = true;
    }, 1000); // 単位はミリ秒（1000ms = 1秒）
});

socket.on('time_out', (data) => {// emit("time_out", {}, room=key)
    activate_pop(["＜タイムアウトしました＞"],[])
    console.log("time_out受信")
    // setTimeoutで1000ミリ秒（1秒）の遅延を設定
    setTimeout(() => {
    // 1秒後に実行される非表示処理
        pop.classList.remove("is_active");
        on_playing = true;
    }, 1000); // 単位はミリ秒（1000ms = 1秒）
});

let player_index_detect = false;
let player_index = 1
const time_1 = document.getElementById(`time_1`);
const turn_1 = document.getElementById(`turn_1`);
const time_2 = document.getElementById(`time_2`);
const turn_2 = document.getElementById(`turn_2`);
socket.on("your_turn",()=>{//データなし。ターンが切り替わっただけ
    click_ok = true
    if(player_index_detect == false){//最初のターンが自分か相手か判明したタイミングで、自分の番号が１か２か確定する
        player_index = gamestate["current_turn"];
        player_index_detect = true;//一度（最初）しか自分のindexをうけとらない
        current_turn = "slf";
        turn_1.innerHTML = "YOU";//<br>(下)";
        turn_2.innerHTML = "対戦相手";//<br>(上)";
        time_1.textContent = String(gamestate["remaining_time"][player_index]);
        time_2.textContent = String(gamestate["remaining_time"][player_index%2+1]);
        board_update(gamestate["board"],gamestate["tegoma"]);
        console.log("初手＝こちら,自分のindex=",player_index)
    }
    turn_1.classList.add("now");
    time_1.classList.add("now");
    turn_2.classList.remove("now");
    time_2.classList.remove("now");
    //current_turn = "slf"
    console.log("your_turn受信")
})

socket.on("opponent_turn",()=>{//データなし。ターンが切り替わっただけ
    click_ok = false;
    answer_to_click_first = false;
    answer_to_click_second = false;
    if(player_index_detect == false){
        player_index = gamestate["current_turn"] % 2 + 1;
        player_index_detect = true;//一度（最初）しか自分のindexをうけとらない
        current_turn = "opp";

        turn_1.innerHTML = "YOU";//<br>(下)";
        turn_2.innerHTML = "対戦相手";//<br>(上)";
        time_1.textContent = String(gamestate["remaining_time"][player_index]);
        time_2.textContent = String(gamestate["remaining_time"][player_index%2+1]);
        board_update(gamestate["board"],gamestate["tegoma"]);
        console.log("初手＝相手,自分のindex=",player_index);
    }
    turn_1.classList.remove("now");
    time_1.classList.remove("now");
    turn_2.classList.add("now");
    time_2.classList.add("now");
    //current_turn = "opp";
    console.log("opponent_turn受信")
    if (game_mode == "pvc"){
        thinking_time.classList.add("is_active");
        setTimeout(() => {
        // 1秒後に実行される非表示処理
            socket.emit("make_AI_move",{"game": game, "mode":game_mode, count_match: count_matches});
            console.log("make_AI_move送信");
        }, 200+100*getRandomInt(1,8)); // 単位はミリ秒（1000ms = 1秒）
    }
})

socket.on('time_update', (data)=>{/* socketio.emit("time_update", {
                                "remaining_time": gamestate[key]["remaining_time"][gamestate[key]["current_turn"]],
                                "current_turn": gamestate[key]["current_turn"]
                                  }, room=key) */
    if (player_index == data["current_turn"]){
        time_1.textContent = String(data["remaining_time"]);
        //console.log("time_update受信","playerのターンindex:",player_index,"現在のターン：",data["current_turn"],"残り時間",data["remaining_time"]);
    }
    if (!(player_index == data["current_turn"])){
        time_2.textContent = String(data["remaining_time"]);
        //console.log("time_update受信","playerのターンindex:",player_index,"現在のターン：",data["current_turn"],"残り時間",data["remaining_time"]);
    }
})

socket.on("game_end",()=>{
    activate_pop(["Thank You For Playing!","ブラウザを閉じてください"],[])
    console.log("game_end受信")
})

socket.on("game_continue",()=>{//もう一度遊ぶ場合はpop表示一秒後にスタート画面に戻る
    activate_pop(["Thank You For Playing!","自動で画面遷移します"],[])
    console.log("game_continue受信")
    setTimeout(()=>{
        window.location.href = "../"
    },1000)
})



// 関数用意-----------------------------------------------------
/**
 * min (含む) から max (含む) までのランダムな整数を生成する関数
 * @param {number} min 最小値
 * @param {number} max 最大値
 * @returns {number} 乱数
 */
function getRandomInt(min, max) {
    // 最小値と最大値を整数に変換（念のため）
    min = Math.ceil(min);
    max = Math.floor(max);
    
    // (max - min + 1) で範囲の大きさを求め、min を足す
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

let timerID_MainPop= false;
function activate_pop(text,buttonText){//text=["一行目","二行目",...], buttonText=["a","b","c"]
    click_ok = false;
    on_playing = false;
    if(pop.classList.contains("is_active")){//既にポップが表示されていたらリセットする
        if (!(timerID_MainPop == false)){
            clearTimeout(timerID_MainPop);
            void pop.offsetWidth;
        }
    }
    number_of_button = buttonText.length;
    number_of_text = text.length;
    ready_text = text[0];
    if(number_of_text >=2){
        for(let i=1 ; i <= number_of_text-1 ; i ++){
            ready_text = ready_text+"<br>"+text[i];
        }
    }
    popuptext.innerHTML = ready_text;
    pop.classList.add("is_active");

    for(let i=1 ; i <= number_of_button ; i ++){
        const button = document.getElementById(`button${i}`);
        button.style.display = "grid";
        button.textContent = buttonText[i-1];
        if (number_of_button == 1){
            button.style.left = `${i*50}%`;
            button.style.aspectRatio = "2/1";
            button.addEventListener("click",()=>{
                button_Push(ready_text,buttonText[i-1])
            })
        }
        if (number_of_button == 2){
            button.style.left = `${i*50-25}%`;
            button.style.aspectRatio = "3/2";
            button.addEventListener("click",()=>{
                button_Push(ready_text,buttonText[i-1])
            })
        }
        if (number_of_button == 3){
            button.style.left = `${i*33-16}%`;
            button.style.aspectRatio = "1/1";
            button.addEventListener("click",()=>{
                button_Push(ready_text,buttonText[i-1])
            })
        }
    }
    for(let i=3 ; i>=number_of_button+1 ; i --){
        const button = document.getElementById(`button${i}`);
        button.style.display = "none";//３つのうち使わなかったボタンは隠しておく
    }
}

const play_pop = document.getElementById("on_play_pop");
const play_pop_text = document.getElementById("play_pop_text");
const sbutton1 = document.getElementById("sbutton1");
const sbutton2 = document.getElementById("sbutton2");
function activate_play_pop(text){
    play_pop.classList.add("is_active")//ポップ表示する
    play_pop_text.innerHTML = text;
    sbutton1.addEventListener("click",()=>{
        play_pop.classList.remove("is_active");//ボタン押されたらすぐきえる
        button_Push(text,"yes");
    })
    sbutton2.addEventListener("click",()=>{
        play_pop.classList.remove("is_active");
        button_Push(text,"no");
    })
}


function button_Push(situation,button_text){
    if(button_text == "ゲーム選択画面に戻る"){
        console.log("ゲーム選択画面に戻ります");
        window.location.href = "../";//../でさっきまで開いていたhtmlに飛ぶ
    }
    if(((situation.includes("WIN"))||(situation.includes("LOSE"))||(situation.includes("DRAW"))) && button_text == "もう一度"){
        socket.emit("finish",{"game": "gungi", "mode":game_mode, "count_match": count_matches, "end_or_continue": "continue"});
        console.log("finish(countinue)送信");
    }
    if(((situation.includes("WIN"))||(situation.includes("LOSE"))||(situation.includes("DRAW"))) && button_text == "止める"){
        socket.emit("finish",{"game": "gungi", "mode":game_mode, "count_match": count_matches, "end_or_continue": "end"});
        console.log("finish(end)送信");
    }
    if(((situation.includes("成り"))) && button_text == "yes"){
        socket.emit("check",{"game": "gungi", "mode":game_mode, "count_match": count_matches, "check":"nari", "current_turn":player_index});
        console.log("check送信");
    } 
    if(((situation.includes("成り"))) && button_text == "no"){
        socket.emit("check",{"game": "gungi", "mode":game_mode, "count_match": count_matches, "check":"cancel", "current_turn":player_index});
        console.log("check送信");
    } 
    if(((situation.includes("降参"))) && button_text == "yes"){
        socket.emit("give_up",{});
        console.log("give_up送信");
    }
    if(((situation.includes("降参"))) && button_text == "no"){
        play_pop.classList.remove("is_active");
    }
}

/*
# 駒の番号定義：
#1.	帥（すい）: 1枚
#2.	大将（たいしょう）: 1枚
#3.	中将（ちゅうじょう）: 1枚
#4.	小将（しょうしょう）: 2枚
#5.	侍（さむらい）: 2枚
#6.	槍（やり）: 3枚
#7.	忍（しのび）: 2枚
#8.	騎馬（きば）: 2枚
#9.	兵（ひょう）: 4枚
#10.	砦（とりで）: 2枚
#11.	砲（ほう）: 1枚
#12.	筒（つつ）: 1枚
#13.	弓（ゆみ）: 2枚
#14.	謀（ぼう）: 1枚
# 101〜114: 相手の駒（+100）
*/
const img_index = {
                    1:"siro/",2:"kuro/"}
let r_adjust = 0;
let c_adjust = 0;
let board_data_now_disp = Array(9).fill(Array(9).fill(Array(3).fill(0)));
let tegoma_grid = {1:Array(20).fill(0), 2:Array(20).fill(0)};
function board_update(grid,tegoma){;// grid[row][column]
    board_data_now_disp = grid;//このgridは下側がindex1のプレイヤー
    floor_grid_update(grid);
    //console.log("current_turn",current_turn);
    //将棋盤の盤面の更新
    for(let r = 1 ; r <= 9 ; r ++){
        for(let c = 1 ; c <= 9 ; c ++){/* r:row(行)　c:column(列) */
            if (player_index == 1){
                r_adjust = r;
                c_adjust = c;
            }else{
                r_adjust = 10-r
                c_adjust = 10-c
            }
            for( let height = 0 ; height<=2 ; height ++ ){//3段目まで
                const img = document.getElementById(`komaimg_r${r_adjust}_c${c_adjust}_h${height+1}`);
                if(grid[r-1][c-1][height] >=1 && grid[r-1][c-1][height] <=14 ){
                    img.src = "../static/JS/gungi_image/siro/"+String(grid[r-1][c-1][height])+"_"+`${height+1}`+".png";
                    if(player_index == 1){
                        img.style.transform = `rotate(0deg) translate(-50%,-50%)`;//回転の基準は真ん中（デフォルト）
                    }else{
                        img.style.transform = `rotate(180deg) translate(50%,50%)`;
                    }
                    img.style.display = "block";
                }else if(grid[r-1][c-1][height] >=101 && grid[r-1][c-1][height] <=114 ){//相手の駒（つまり回転させる）
                    img.src = "../static/JS/gungi_image/kuro/"+String(grid[r-1][c-1][height])+"_"+`${height+1}`+".png";
                    if(player_index == 1){
                        img.style.transform = `rotate(180deg) translate(50%,50%)`;//回転の基準は真ん中（デフォルト）
                    }else{
                        img.style.transform = `rotate(0deg) translate(-50%,-50%)`;
                    }
                    img.style.display = "block";
                }else{
                    img.style.display = "none";
                }
                if (current_turn== "slf" && floor_grid[r-1][c-1] == height+1){//最上段だけホバーで光るクラスを追加
                    img.classList.add("hover_light");
                }else{
                    img.classList.remove("hover_light");
                }
            }
        }
    }
    //自分の手ごま描画　使うデータ：tegoma_grid[player_index] 表示する手ごま板:tegoma1
    
    let number = 0
    let obj = Object.keys(tegoma[player_index])
    console.log("てごま",tegoma)
    for (const key of obj){
        let r = Math.trunc(number / 4) + 1
        let c = (number % 4) + 1
        const img = document.getElementById(`tegoma1img_r${r}_c${c}`);
        img.src = "../static/JS/gungi_image/"+img_index[player_index]+key+".png";
        img.style.display = "block";
        tegoma_grid[1][number] = Number(key);
        if (current_turn== "slf"){
            img.classList.add("hover_light");
        }else{
            img.classList.remove("hover_light");
        }

        const img_maisuu = document.getElementById(`tegoma1maisuu_r${r}_c${c}`);
        img_maisuu.textContent = String(tegoma[player_index][key]);
        img_maisuu.style.display = "grid";

        number += 1;
    }

    for (let i=number; i<=19; i++){
        let r = Math.trunc(i / 4) + 1
        let c = (i % 4) + 1
        const img = document.getElementById(`tegoma1img_r${r}_c${c}`);
        img.style.display = "none";
        const img_maisuu = document.getElementById(`tegoma1maisuu_r${r}_c${c}`);
        img_maisuu.style.display = "none";
        tegoma_grid[1][i] = 0;
    }

    console.log("手ごまのデータ1：",tegoma,"手ごまのデータ2:",tegoma_grid);
    console.log("盤面のデータ：",grid);

    //相手の手ごま描画　使うデータ：tegoma_grid[player_index%2+1] 表示する手ごま板:tegoma2
    number = 0
    obj = Object.keys(tegoma[player_index %2 +1])
    for (const key of obj){
        let r = Math.trunc(number / 4) + 1
        let c = (number % 4) + 1
        const img = document.getElementById(`tegoma2img_r${r}_c${c}`);
        img.src = "../static/JS/gungi_image/"+img_index[player_index %2 +1]+String(key)+".png";
        img.style.transform = "rotate(180deg) translate(50%,50%)";
        img.style.display = "block";

        const img_maisuu = document.getElementById(`tegoma2maisuu_r${r}_c${c}`);
        img_maisuu.textContent = String(tegoma[player_index %2 +1][key]);
        img_maisuu.style.display = "grid";

        number += 1;
    }

    for (let i=number; i<=19; i++){
        let r = Math.trunc(i / 4) + 1
        let c = (i % 4) + 1
        const img = document.getElementById(`tegoma2img_r${r}_c${c}`);
        img.style.display = "none";

        const img_maisuu = document.getElementById(`tegoma2maisuu_r${r}_c${c}`);
        img_maisuu.style.display = "none";
    }



}
/*
let tegoma_grid = {1:Array(20).fill(0),2:Array(20).fill(0)};//手ごま用のgrid
*/
/*例えば自分の駒だったら（相手なら１８０度回転）tegoma_gridの配列の要素は順に
    0123
    4567
    8...
    ...19
と手ごま上の位置を対応*/
//app.pyでもらったデータを、使いやすい形に並べなおす
/*
function rearrange(hands){//hands = {1:{},2:{}}// tegoma = {1:{1:5},2:{}};
    for(let turn = 1; turn <= 2 ; turn ++){
        const kinds_of_hands = Object.keys(hands[turn]);
        //console.log("turn:",turn,"持っている手ごまの種類:",kinds_of_hands)
        let numbering = 0
        for(const key of kinds_of_hands){//各種類
            //console.log("turn:",turn,"考えている駒の種類：",key)
            for(let i=1; i <= hands[turn][key] ; i++){//各種類の所持数分まわす
                tegoma_grid[turn][numbering] = Number(key);
                numbering += 1
            }
        }
        for(let i = numbering ; i <= 19 ;i ++){//こまおきの残りのところは空白
            tegoma_grid[turn][i] = 0;
        }
        
    }
}
*/
function blight(blt){
    for(let i = 0; i < blt.length; i ++){
        let c = blt[i][0]+1;/* data["blight_list"]のi+1個目の要素のx座標 */
        let r = blt[i][1]+1;
        if (player_index == 1){
            r_adjust = r;
            c_adjust = c;
        }else{
            r_adjust = 10-r
            c_adjust = 10-c
        }
        const bltkoma = document.getElementById(`komablock_r${r_adjust}_c${c_adjust}`); /* 光らせる要素を座標を含むidからgetしてbltkomaに代入する */
        const bltkoma_img = document.getElementById(`komaimg_r${r_adjust}_c${c_adjust}`);
        bltkoma.style.transition = "background-color 0.1s ease";
        bltkoma.style.backgroundColor = "rgba(254, 255, 235, 1)";
        //bltkoma_img.style.filter = "brightness(200%)";

    }
}

function cansel_bright(blt){
    for(let i = 0; i < blt.length; i ++){
        let c = blt[i][0]+1;/* data["blight_list"]のi+1個目の要素のx座標 */
        let r = blt[i][1]+1;
        if (player_index == 1){
            r_adjust = r;
            c_adjust = c;
        }else{
            r_adjust = 10-r
            c_adjust = 10-c
        }
        const bltkoma = document.getElementById(`komablock_r${r_adjust}_c${c_adjust}`); /* 光らせる要素を座標を含むidからgetしてbltkomaに代入する */
        const bltkoma_img = document.getElementById(`komaimg_r${r_adjust}_c${c_adjust}`);
        bltkoma.style.transition = "background-color 0s ease";
        bltkoma.style.backgroundColor = "rgb(208, 195, 70)";/* 元の色に戻す */
        //bltkoma_img.style.filter = "brightness(100%)";

    };
}

const narabe1 = document.createElement("img");
const narabe2 = document.createElement("img");
const narabe3 = document.createElement("img");
const center = document.getElementById("center")
center.appendChild(narabe1);
center.appendChild(narabe2);
center.appendChild(narabe3);

narabe1.classList.add("komaimg");
narabe2.classList.add("komaimg");
narabe3.classList.add("komaimg");

narabe1.style.display = "none";
narabe2.style.display = "none";
narabe3.style.display = "none";

narabe1.style.zIndex = "199";
narabe2.style.zIndex = "200";
narabe3.style.zIndex = "201";

narabe1.style.top = "53%";
narabe2.style.top = "53%";
narabe3.style.top = "53%";

function naraberu(position){//pos = (r,c) board_data_now_dispの座標(+(1.1))に対応（つまりindex1のプレイヤーが下側としたときの座標）
    let num_of_narabe = 0
    let pos = [-1,-1];
    if(player_index == 2){
        pos[0] = 10-position[0];
        pos[1] = 10-position[1];
    }else{
        pos[0] = position[0];
        pos[1] = position[1];
    }
    console.log("board_data_now_disp,座標：x,y=",pos[1]-1,pos[0]-1)
    for (let h = 1 ; h <= 3 ; h ++){
        if (board_data_now_disp[pos[0]-1][pos[1]-1][h-1]!=0){
            num_of_narabe = h
            if(h==1){
                if (board_data_now_disp[pos[0]-1][pos[1]-1][h-1] <= 14){
                    narabe1.src = "../static/JS/gungi_image/siro/"+String(board_data_now_disp[pos[0]-1][pos[1]-1][h-1])+".png";
                }else if (board_data_now_disp[pos[0]-1][pos[1]-1][h-1]>=101){
                    narabe1.src = "../static/JS/gungi_image/kuro/"+String(board_data_now_disp[pos[0]-1][pos[1]-1][h-1])+".png";
                }
            }else if(h==2){
                if (board_data_now_disp[pos[0]-1][pos[1]-1][h-1] <= 14){
                    narabe2.src = "../static/JS/gungi_image/siro/"+String(board_data_now_disp[pos[0]-1][pos[1]-1][h-1])+".png";
                }else if (board_data_now_disp[pos[0]-1][pos[1]-1][h-1]>=101){
                    narabe2.src = "../static/JS/gungi_image/kuro/"+String(board_data_now_disp[pos[0]-1][pos[1]-1][h-1])+".png";
                }
            }else if(h==3){
                if (board_data_now_disp[pos[0]-1][pos[1]-1][h-1] <= 14){
                    narabe3.src = "../static/JS/gungi_image/siro/"+String(board_data_now_disp[pos[0]-1][pos[1]-1][h-1])+".png";
                }else if (board_data_now_disp[pos[0]-1][pos[1]-1][h-1]>=101){
                    narabe3.src = "../static/JS/gungi_image/kuro/"+String(board_data_now_disp[pos[0]-1][pos[1]-1][h-1])+".png";
                }
            }
        }
    }//num_of_narabe= 0 or 1 or 2 or 3

    if(num_of_narabe == 1){
        narabe1.style.left = "15%";
        narabe1.style.display = "block";
        narabe2.style.display = "none";
        narabe3.style.display = "none";
    }else if(num_of_narabe == 2){
        narabe1.style.left = "10%";
        narabe2.style.left = "20%";
        narabe1.style.display = "block";
        narabe2.style.display = "block";
        narabe3.style.display = "none";
    }else if(num_of_narabe == 3){
        narabe1.style.left = "5%";
        narabe2.style.left = "15%";
        narabe3.style.left = "25%";
        narabe1.style.display = "block";
        narabe2.style.display = "block";
        narabe3.style.display = "block";
    }else{
        narabe1.style.display = "none";
        narabe2.style.display = "none";
        narabe3.style.display = "none";
    }
}

function naraberu_delete(){
    narabe1.style.display = "none";
    narabe2.style.display = "none";
    narabe3.style.display = "none";
}

let floor_grid = [
                    [0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]];
function floor_grid_update(grid){//各座標に、データの(r,c)の段数を入れたgridを返す
    for(let r = 1 ; r <= 9 ; r++){
        for(let c = 1 ; c <= 9 ; c++){
            if(grid[r-1][c-1][0] == 0){
                floor_grid[r-1][c-1] = 0;
            }else if(grid[r-1][c-1][1] == 0){
                floor_grid[r-1][c-1] = 1;
            }else if(grid[r-1][c-1][2] == 0){
                floor_grid[r-1][c-1] = 2;
            }else{
                floor_grid[r-1][c-1] = 3;
            }
        }
    }
}