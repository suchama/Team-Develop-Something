/*socket使うときに解放する
const socket = io('http://106.155.3.71:8000'); // Flask-SocketIOならこのURL

//接続した時に実行される
socket.on('connect', () => {
console.log('接続成功');
});
*/


/*popの要素作成*/
/*
center(作成済み)
    popbg(作成済み)
        poptextbg(作成済み)
            poptext(作成済み)
    button(作成済み、位置指定だけjs)
*/
/*ボタンの左右位置の指定*/
const btn1 = document.getElementById("button1");
const btn2 = document.getElementById("button2");
const btn3 = document.getElementById("button3");
const btn4 = document.getElementById("pvp");
const btn5 = document.getElementById("pvc");
const btn6 = document.getElementById("modoru");

btn1.style.left = "20.83%";
btn2.style.left = "50%";
btn3.style.left = "79.17%";
btn4.style.left = "30%";
btn5.style.left = "70%";
btn6.style.left = "50%";

//あとはボタンを押したときの制御をjsでかく。

//クリックされたとき
/*

    ゲームクリック→ゲームの選択肢を非表示、ゲームモードの選択肢を表示、質問文を変更

*/

let gamemodeurl = "";
let gameurl = "";
btn1.addEventListener('click', () => {
    /*btn1.style.backgroundColor = 'rgba(248, 236, 63, 1)';*/
    gamemodeurl = "/othello";
    document.getElementById("popTextBG").innerHTML = "どちらのモードで遊びますか？"
    btn1.style.display = "none";
    btn2.style.display = "none";
    btn3.style.display = "none";
    btn4.style.display = "grid";
    btn5.style.display = "grid";
    btn6.style.display = "grid";
});

btn2.addEventListener('click', () => {
    /*btn1.style.backgroundColor = 'rgba(248, 236, 63, 1)';*/
    gamemodeurl = "/shogi";
    document.getElementById("popTextBG").innerHTML = "どちらのモードで遊びますか？"
    btn1.style.display = "none";
    btn2.style.display = "none";
    btn3.style.display = "none";
    btn4.style.display = "grid";
    btn5.style.display = "grid";
    btn6.style.display = "grid";
});

btn3.addEventListener('click', () => {
    /*btn1.style.backgroundColor = 'rgba(248, 236, 63, 1)';*/
    gamemodeurl = "/gungi";
    document.getElementById("popTextBG").innerHTML = "どちらのモードで遊びますか？";
    btn1.style.display = "none";
    btn2.style.display = "none";
    btn3.style.display = "none";
    btn4.style.display = "grid";
    btn5.style.display = "grid";
    btn6.style.display = "grid";
});

btn4.addEventListener('click', () => {
    gameurl = gamemodeurl +"?"+"mode=pvp"/* 例えばurlは　/othello?mode='pvp'　 */
    window.location.href = gameurl;/* これで次のurlに遷移できる？ */
});

btn5.addEventListener('click', () => {
    gameurl = gamemodeurl +"?"+"mode=pvc"/* 例えばurlは　/othello?mode='pvp'　 */
    window.location.href = gameurl;/* これで次のurlに遷移できる？ */
});

btn6.addEventListener('click', () => {
    document.getElementById("popTextBG").innerHTML = "どのゲームを遊びますか？";
    btn1.style.display = "grid";
    btn2.style.display = "grid";
    btn3.style.display = "grid";
    btn4.style.display = "none";
    btn5.style.display = "none";
    btn6.style.display = "none";
});


/* これでオセロのpvpが起動できたら他も同じように実装する */
