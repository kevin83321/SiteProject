# Log

> **簡介**：記錄模組
>
> **CopyRight^©^** : 希奇資本股份有限公司 XiQiCapital
>
> **Author** : 鄭圳宏 Kevin Cheng
>
> **Create** : 2020.09.17
>
> **Update** : 2020.09.17

## 	Logger.py

> - ***Logger***
>
>   編輯紀錄檔的類別
>
>   - *sendError*
>
>     發生錯誤訊息時傳送錯誤訊息
>
>   - *_initial_log_path*
>
>     初始化儲存log檔的路徑
>
>   - *_write_log*
>
>     寫入log檔
>
>   - *_write_ts_log*
>
>     寫入時間序列有關的log（有時間戳，且有固定格式長度的資料）
>
>   - *critical*
>
>     忘了為何而寫，暫時無用
>
>   - *error*
>
>     接收錯誤訊息並寫入log
>
>   - *debug*
>
>     用於debug，暫時無用
>
>   - *warn*
>
>     用於接收warning，暫時無用
>
>   - *info*
>
>     忘了為何而寫，暫時無用
>
>   - *order_failed*
>
>     負責下單失敗的訊息
>
>   - *order_msg*
>
>     負責下單無失敗的所有訊息
>
>   - *signal_msg*
>
>     負責所有的訊號
>
>   - *fill_msg*
>
>     負責下單成功後的回填部位訊息
>
>   - *holding_msg*
>
>     負責更新部位後的所有持有部位的訊息
>
>   - *account_msg*
>
>     跟帳戶有關的訊息，未實現
>
>   - *_sendNotify*
>
>     傳送提醒至Line, Telegram

## 	TransforException.py

> - *GetException*
>
>   將例外的訊息轉換成較容易閱讀的訊息，方便除錯