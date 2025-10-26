
//socket使うときに解放する
const socket = io('http://106.155.3.71:8000'); // Flask-SocketIOならこのURL

//接続した時に実行される
socket.on('connect', () => {
console.log('接続成功');
});

//プレイが始まるまでにやること------------------------------------------------------
//まずモードを送信　例えば("pvp",{game:"othello"})
const game_mode = document.getElementById("mode").textContent.trim();
const game = document.getElementById("game").textContent.trim();
socket.emit(game_mode, { "game": game })

//相手探し中
let current_turn = 1/*  */
const pop = document.getElementById("popBG");
const hidaripop = document.getElementById("hidaripopBG");
const popuptext = document.getElementById("popUpper");
/* waitは最初かくしておいてwaitがきたら出現させる 消すときどうしよう...*/
socket.on('waiting', (data) => {/* emit("waiting", {"msg": "相手を待っています..."}) */
    activate_pop([data["msg"]],[])
});

// startさせる
const count_matches = 0/* 起動してから何試合したか */
const gamestate = 0
socket.on('start_game', (data) => {/* emit("start_game", {"gamestate": gamestate[key], "count_matche"s: count_matches}) */
    count_matches = data["count_matches"];/* 受け取ったデータをこっち側にも保存 */
    gamestate = data["gamestate"];//gamestate["othello"]は"board","current_turn","remaining_time"(→1,2のキーに残り秒数が入っている)
    //currentturnが自分か相手か？
    pop.classList.remove("is_active");/* 表示されていたらpopを消す */
});


//画面作成-----------------------------------------------------------
let now_click = (0,0)//(row,column)
/* メインのボード */
for(let r = 1 ; r <= 8 ; r ++){
    for(let c = 1 ; c <= 8 ; c ++){/* r:row(行)　c:column(列) */
        const block = document.createElement("div");
        document.getElementById("mainB").appendChild(block);
        block.classList.add("komablock");
        block.id = `komablock_r${r}_c${c}`;
        block.style.top = `${12*r-4}%`;
        block.style.left = `${12*c-4}%`;

        const img = document.createElement("img");
        img.classList.add("komaimg");
        img.id = `komaimg_r${r}_c${c}`;
        img.style.top = `${12*r-4}%`;
        img.style.left = `${12*c-4}%`;

        /* マウスが駒の上に来た時とはずれたときの操作 */
        block.addEventListener('mouseenter', () =>{
            if(current_turn == "slf"){
                block.style.transition = "background-color 0.3s ease";
                block.style.backgroundColor = "rgb(249, 255, 167)";
            }
        });
        block.addEventListener('mouseleave', () =>{
            if(current_turn == "slf"){
                block.style.transition = "background-color 0s ease";
                block.style.backgroundColor = "rgb(254, 201, 255)";
            }
        });
        /* クリックされたら送信する */
        block.addEventListener('click', () =>{
            if(current_turn == "slf"){
                now_click = (r,c)
                block.style.transition = "background-color 0s ease";
                block.style.backgroundColor = "rgba(125, 255, 130, 1)";/* ここはblightの受信の方で処理する? */
                socket.emit("make_move", {"game": "othello", "mode": game_mode, "count_match": count_matches, "place":"board", x: c, y: r, "current_player": player_index});
            }
        });
    };
};


//プレイ中の、受け取ったデータへの反応--------------------------------------------
let now_blight = 0
socket.on('blight', (data) => {// emit("blight", {"blight_list": valid_moves, "place": place}, to = request.sid) placeはblightに関してはboardのみ？だから使わなくてOK？
    now_blight = data["blight_list"];// javascript側で今光らせているところを保存しておく（特にcansel_brightで用いる）
    blight(now_blight);/* 光らせる関数を実行 */
});
socket.on('cansel_bright', () => {/* dataなし。brightをblightに直してもらうか問題 */
    cancel_blight(now_blight)
});

socket.on('error', (data) => {/* emit("error", {"msg": "おけないよん"}, to = request.sid) */
    hidaripop.textContent = "＜"+data["msg"]+"＞";
    hidaripop.classList.add("is_active");
    setTimeout(() => {
    // 1秒後に実行される非表示処理
    hidaripop.classList.remove("is_active");
    }, 1500); // 単位はミリ秒（1000ms = 1秒）
});

socket.on('game_data',(data)=>{//emit("game_data", {"gamestate": gamestate[key], "count_matches": count_matches})
    board_update(data["gamestate"]["board"]);
}


socket.on('game_over', (data) => {/* emit("game_over", {"board": board, "scores": outcome["scores"]}, room = key) */
    activate_pop(["ゲームオーバー","black"+str(data["scores"]["black"])+"-"+str(data["scores"]["white"]+"white")], ["もう一度","止める"])
});

socket.on('pass', (data) => {/* emit("pass", {"current_turn": gamestate[key]["current_turn"]}, room = key) */
    activate_pop(["＜パスしました＞"],[])
    setTimeout(() => {
    // 1秒後に実行される非表示処理
        pop.classList.remove("is_active");
    }, 1000); // 単位はミリ秒（1000ms = 1秒）
});

socket.on('time_out', (data) => {// emit("time_out", {}, room=key)
    activate_pop(["＜タイムアウトしました＞"],[])
    // setTimeoutで1000ミリ秒（1秒）の遅延を設定
    setTimeout(() => {
    // 1秒後に実行される非表示処理
        pop.classList.remove("is_active");
    }, 1000); // 単位はミリ秒（1000ms = 1秒）
});

let player_index_detect = false;
let player_index = 0
const time_1 = document.getElementById(`time_1`);
const turn_1 = document.getElementById(`turn_1`);
const time_2 = document.getElementById(`time_2`);
const turn_2 = document.getElementById(`turn_2`);
socket.on("your_turn",()=>{//データなし。ターンが切り替わっただけ
    if(player_index_detect == false){//最初のターンが自分か相手か判明したタイミングで、自分の番号が１か２か確定する
        player_index = gamestate["current_turn"];
        player_index_detect == true;
    }
    current_turn = "slf";
    turn_1.classList.add("now");
    turn_2.classList.remove("now");
})

socket.on("opponent_turn",()=>{//データなし。ターンが切り替わっただけ
    if(player_index_detect == false){
        player_index = (gamestate["current_turn"] + 1) % 2;
        player_index_detect == true;
    }
    current_turn = "opp";
    turn_1.classList.remove("now");
    turn_2.classList.add("now");
})

socket.on('timer_update', (data)=>{/* socketio.emit("time_update", {
                                "remaining_time": gamestate[key]["remaining_time"][gamestate[key]["current_turn"]],
                                "current_turn": gamestate[key]["current_turn"]
                                  }, room=key) */
    if (player_index == data["current_turn"]){
        time_1.textContent = str(data["remaining_time"]);
    }
    if (not (player_index == data["current_turn"])){
        time_2.textContent = str(data["remaining_time"]);
    }
    time.classList.add("now");/* クラス名に、明るさをつかさどるものを追加 */
    turn.classList.add("now");

})

socket.on("game_end",()=>{
    activate_pop(["Thank You For Playing!","ブラウザを閉じてください"],[])
})

socket.on("game_continue",()=>{//もう一度遊ぶ場合はpop表示一秒後にスタート画面に戻る
    activate_pop(["Thank You For Playing!","1秒後に自動で画面遷移します"],[])
    setTimeout(()=>{
        window.location.href = "../index.html"
    },1000)
})


// 関数用意-----------------------------------------------------
function activate_pop(text,buttonText){//buttonText=["a","b","c"]
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
            button.style.left = `${i*50}`;
            button.addEventListener("click",()=>{
                button_Push(ready_text,buttonText[i-1])
            })
        }
        if (number_of_button == 2){
            button.style.left = `${i*50-25}`;
            button.addEventListener("click",()=>{
                button_Push(ready_text,buttonText[i-1])
            })
        }
        if (number_of_button == 3){
            button.style.left = `${i*33-16}`;
            button.addEventListener("click",()=>{
                button_Push(ready_text,buttonText[i-1])
            })
        }
    }
    for(let i=3 ; i>=number_of_button+1 ; i --){
        const button = document.getElementById(`button${i}`);
        button.style.dicplay = "none";//３つのうち使わなかったボタンは隠しておく
    }
}

function button_Push(situation,button_text){
    if((situation.includes("ゲームオーバー")) && button_text == "もう一度"){
        emit("finiish",{"game": "othello", "mode":game_mode, "count_match": count_matches, "end_or_continue": "continue"})
    }
    if((situation.includes("ゲームオーバー")) && button_text == "止める"){
        emit("finiish",{"game": "othello", "mode":game_mode, "count_match": count_matches, "end_or_continue": "end"})
    }
}

function board_update(grid){// grid[row][column]
    for(let r = 1 ; r <= 8 ; r ++){
        for(let c = 1 ; c <= 8 ; c ++){/* r:row(行)　c:column(列) */
            if(grid[r][c] == 1){
                const img = document.getElementById(`komaimg_r${r}_c${c}`);
                img.src = "othello_img/画像１.jpg";
                img.alt = "オセロ黒石";
                img.style.display = "block";//オセロでは表示をhideすることはないので、blockになったら最後までblock
            }
            if(grid[r][c] == 2){
                const img = document.getElementById(`komaimg_r${r}_c${c}`);
                img.src = "othello_img/画像2.jpg";
                img.alt = "オセロ白石";
                img.style.display = "block";
            }
        }
    }
}

function blight(blt){
    for(let i = 0; i < blt.length; i ++){
        let c = blt[i][0];/* data["blight_list"]のi+1個目の要素のx座標 */
        let r = blt[i][1];
        const bltkoma = document.getElementById(`komablock_r${r}_c${c}`); /* 光らせる要素を座標を含むidからgetしてbltkomaに代入する */
        block.style.transition = "background-color 0.1s ease";
        bltkoma.style.backgroundColor = "rgba(254, 255, 235, 1)";
    }
}

function cansel_bright(blt){
    for(let i = 0; i < blt.length; i ++){
        let c = blt[i][0];/* data["blight_list"]のi+1個目の要素のx座標 */
        let r = blt[i][1];
        const bltkoma = document.getElementById(`komablock_r${r}_c${c}`); /* 光らせる要素を座標を含むidからgetしてbltkomaに代入する */
        block.style.transition = "background-color 0s ease";
        bltkoma.style.backgroundColor = "rgb(254, 201, 255)";/* 元の色に戻す */
    };
}


