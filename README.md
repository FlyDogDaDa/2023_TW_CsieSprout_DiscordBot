# Sprout2023py---蟒著 DeBug 組

[Spec 簡報](https://hackmd.io/@Fireball0424/HkED_0UXn)

[蟒著 DeBug 組簡報](https://docs.google.com/presentation/d/1Ih4T5sq7ECS9mVCIYirw-a00Q7mTqpUUkqbTbPMUfWw/edit?usp=sharing)

# Discord.py 除外有使用到的套件：

abc、asyncio、json、requests、bs4、collections、os、datetime、selenium

您可以使用這串指令快速完成安裝：`pip install asyncio jsons requests bs4 collection os-sys DateTime selenium`

# 使用方法：

- event.py
  - 加入錯誤處理
- todolist.py

  - `add {文字}`
    將`{文字}`加入到代辦清待
  - `list`
    列出目前代辦清單中的內容
  - `remove {index}`
    移除代辦清單中的第`{index}`項內容
  - `sort`
    排序代辦事項清單，並列出代辦清單
  - `clear`
    清空代辦事項清單

- wordle.py

  - `play_wordle`
    加入 wordle 遊戲
  - `ask {單字}`
    猜{單字}是否為正確答案

- gamble.py

  - `Slot`
    呼叫出拉霸遊戲的 UI 介面
  - `Blackjack`
    呼叫出 21 點遊戲的 UI 介面
  - `Horses`
    呼叫出賭馬遊戲的 UI 介面
  - `do_the_dishes`
    獲得硬幣(錢)的指令
  - `walk_the_dog`
    獲得硬幣(錢)的指令
  - `mowing_the_lawn`
    獲得硬幣(錢)的指令
  - `wallet`
    查看使用者當前的餘額

- anime.py
  - `anime_list` {數量}
    顯示`{數量}`個最新的動漫
  - `add_anime {名稱}`
    將動漫`{名稱}`加入到通知清單，注意`{名稱}`需要完全一致才能成功添加。
  - `remove_anime {名稱}`
    將動漫`{名稱}`從通知清單移除，注意`{名稱}`需要完全一致才能成功添加。
  - `show_anime`
    顯示動漫通知清單
- task.py
  此為 anime.py 的附屬程式。每 60 秒從網站上爬蟲，並檢查更新的動漫。動漫更新時依照使用者的通知清單傳送私人訊息，告知使用者動漫更新。
- music.py
  - `play {網址}`
    使用者需要先加入語音頻道，後呼叫此指令讓機器人加入，數秒後將會開始撥放音樂。
  - `leave`
    讓機器人退出語音頻道，正在播放的音樂將會被強制中斷。
  - `pause`
    暫停正在播放的音樂。
  - `resume`
    繼續撥放被暫停的音樂。
  - `stop`
    停止播放音樂。
  - `queue`
    列印出音樂待播佇列的內容。
  - `vote`
    使用者們可以通過這個指令投票，表決是否要跳過當前正在播放的音樂。
  - `find_music`
    通過名稱搜尋音樂，將會列出前 4 首搜尋的音樂，再通過`find_music`指令選擇音樂。
  - `choose_music`
    使用此指令可以選擇`find_music`搜尋到的音樂。

[Discord Bot 程式碼檔案](https://github.com/FlyDogDaDa/2023_TW_CsieSprout_DiscordBot)
