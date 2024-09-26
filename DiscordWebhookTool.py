import os
import sys
import json
import datetime
import requests
import tkinter as ntk
import customtkinter as tk
from tkinter import filedialog

tk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
tk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class DiscordWebhookClient:
    
    def send_discord_message(webhook_url, user_name, avatar_url, message, files, use_file_spoiler, log_label):
        """メッセージを送信する"""
        if not webhook_url:
            log_label.configure(text="※Webhook Url の入力は必須です。", text_color="red")
            print("※Webhook Urlの入力は必須です。")
            return
        
        if not message.strip() and not files:
            log_label.configure(text="※メッセージ又はファイルのどちらかは入力が必須です。", text_color="red")
            print("※メッセージ又はファイルのどちらかは入力が必須です。")
            return
        
        # Discord Webhook へのメッセージ送信処理
        try:
            # メッセージのパラメータ設定
            data = {
                "content": message,
            }
            
            # ユーザー名の指定
            if user_name:
                data["username"] = user_name
            #アイコンの指定
            if avatar_url:
                data["avatar_url"] = avatar_url
                
            # ファイルが選択されている場合はファイルも添付する
            if files:
                files_data = {}
                for idx, file_path in enumerate(files):
                    # ファイル名の前に spoiler を追加する
                    if use_file_spoiler:
                        file_name = f"SPOILER_{os.path.basename(file_path)}"
                    else:
                        file_name = os.path.basename(file_path)
                    files_data[f"file{idx}"] = (file_name, open(file_path, "rb"))
                response = requests.post(webhook_url, data=data, files=files_data)
            else:
                response = requests.post(webhook_url, json=data)
            
            # レスポンスコードが200番台であれば成功とみなす
            if response.status_code // 100 == 2:
                log_label.configure(text = "メッセージが正常に送信されました。", text_color="green")
                print("メッセージが正常に送信されました。")
            else:
                log_label.configure(text=f"※エラーが発生しました。レスポンスコード {response.status_code}", text_color="red")
                print(f"※エラーが発生しました。レスポンスコード {response.status_code}")
        except Exception as e:
            log_label.configure(text=f"※エラーが発生しました。{e}", text_color="red")
            print(f"※エラーが発生しました。{e}")
    
    #--------------------#
    
    def send_discord_embed_message(webhook_url, user_name, avatar_url, title, description, title_url, use_time_stamp, bar_color, footer_icon_path, footer_text, thumbnail_file_path, image_file_path, author_text, author_url, author_icon_path, field_list, log_label):
        """埋め込みメッセージを送信する"""
        
        if not webhook_url:
            log_label.configure(text="※Webhook Url の入力は必須です。", text_color="red")
            print("※Webhook Urlの入力は必須です。")
            return
        
        try:
            payload = {
                "payload_json" : {
                    "embeds": [
                        {
                            "title": title,
                            "description": description,
                            "url": title_url,
                            "color"         : bar_color,
                            "footer": {
                                "text"      : footer_text,
                            },
                            "author": {
                                "name"      : author_text,
                                "url"       : author_url,
                            },
                        }
                    ]
                }
            }
            
            # ユーザー名の指定
            if user_name:
                payload['payload_json']["username"] = user_name
                
            #アイコンの指定
            if avatar_url:
                payload['payload_json']["avatar_url"] = avatar_url
                
            #タイムスタンプの指定
            if use_time_stamp:
                # 現在の日時を取得
                current_datetime = datetime.datetime.now()
                
                # 日本時間から9時間引く
                adjusted_datetime = current_datetime - datetime.timedelta(hours=9)
                
                # タイムスタンプに変換
                timestamp = adjusted_datetime.strftime("%Y-%m-%d %H:%M:%S")
                
                # タイムスタンプを設定
                payload['payload_json']['embeds'][0]["timestamp"] = timestamp
            
            files_data = {}

            # フッターアイコンの指定
            if footer_icon_path:
                # ファイル名から拡張子を取得
                file_name, extension = os.path.splitext(footer_icon_path)
                # 拡張子のみを抽出
                extension_only = extension
                #送信した際のファイル名
                send_file_name = "footer_icon_image" + extension_only
                files_data["icon_url"] = (send_file_name, open(footer_icon_path, "rb").read())
                # "footer"フィールドを追加する
                payload['payload_json']['embeds'][0]["footer"] = {
                    "icon_url"       : "attachment://" + send_file_name,
                    "text"           : footer_text,
                }
            
            ## thumbnailの指定
            if thumbnail_file_path:
                # ファイル名から拡張子を取得
                file_name, extension = os.path.splitext(thumbnail_file_path)
                # 拡張子のみを抽出
                extension_only = extension
                #送信した際のファイル名
                send_file_name = "sub_title_image" + extension_only
                files_data["thumbnail_image"] = (send_file_name, open(thumbnail_file_path, "rb"))
                
                # "image"フィールドを追加する
                payload['payload_json']['embeds'][0]["thumbnail"] = {
                    "url"       : "attachment://" + send_file_name
                }
            
            # タイトル写真の指定
            if image_file_path:
                # ファイル名から拡張子を取得
                file_name, extension = os.path.splitext(image_file_path)
                # 拡張子のみを抽出
                extension_only = extension
                #送信した際のファイル名
                send_file_name = "main_title_image" + extension_only
                
                files_data["title_image"] = (send_file_name, open(image_file_path, "rb"))
                
                # "image"フィールドを追加する
                payload['payload_json']['embeds'][0]["image"] = {
                    "url"       : "attachment://" + send_file_name
                }
            
            # author(ヘッダー)アイコンの指定
            if author_icon_path:
                # ファイル名から拡張子を取得
                file_name, extension = os.path.splitext(author_icon_path)
                # 拡張子のみを抽出
                extension_only = extension
                #送信した際のファイル名
                send_file_name = "header_icon_image" + extension_only
                files_data["author_icon_image"] = (send_file_name, open(author_icon_path, "rb"))
                
                # "image"フィールドを追加する
                payload['payload_json']['embeds'][0]["author"] = {
                    "name"      : author_text,
                    "url"       : author_url,
                    "icon_url"  : "attachment://" + send_file_name,
                }
                
            if len(field_list) != 0:
                payload['payload_json']['embeds'][0]["fields"] = field_list
            
            payload['payload_json'] = json.dumps(payload['payload_json'], ensure_ascii=False)
            response = requests.post(webhook_url, files=files_data, data=payload)
            
            # レスポンスコードが200番台であれば成功とみなす
            if response.status_code // 100 == 2:
                log_label.configure(text = "メッセージが正常に送信されました。", text_color="green")
                print("メッセージが正常に送信されました。")
            else:
                log_label.configure(text=f"※エラーが発生しました。レスポンスコード {response.status_code}", text_color="red")
                print(f"※エラーが発生しました。レスポンスコード {response.status_code}")
        except Exception as e:
            log_label.configure(text=f"※エラーが発生しました。{e}", text_color="red")
            print(f"※エラーが発生しました。{e}")
    
    #--------------------#
    
    def edit_discord_message(webhook_url, message_id, new_message, log_label):
        """送信済みメッセージを編集する"""
        if not webhook_url:
            log_label.configure(text="※Webhook Url の入力は必須です。", text_color="red")
            print("※Webhook Url の入力は必須です。")
            return
        
        if not message_id:
            log_label.configure(text="※Message Id の入力は必須です。", text_color="red")
            print("※メッセージId の入力は必須です。")
            return
        
        if not new_message.strip():
            log_label.configure(text="※新しいメッセージの入力は必須です。", text_color="red")
            print("※新しいメッセージの入力は必須です。")
            return
        
        try:
            # PATCHリクエストを送信してメッセージを編集する
            data = {"content": new_message}
            response = requests.patch(f"{webhook_url}/messages/{message_id}", json=data)
            
            # レスポンスコードが200番台であれば成功とみなす
            if response.status_code // 100 == 2:
                log_label.configure(text="メッセージが編集されました。", text_color="green")
                print("メッセージが編集されました。")
            else:
                log_label.configure(text=f"※エラーが発生しました。レスポンスコード {response.status_code}", text_color="red")
                print(f"※エラーが発生しました。レスポンスコード {response.status_code}")
        except Exception as e:
            log_label.configure(text=f"※エラーが発生しました。{e}", text_color="red")
            print(f"※エラーが発生しました。{e}")
    
    #--------------------#
    
    def delete_discord_message(webhook_url, message_id, log_label):
        """送信済みメッセージの削除"""
        
        if not webhook_url:
            log_label.configure(text="※Webhook Url の入力は必須です。", text_color="red")
            print("※Webhook Url の入力は必須です。")
            return
        
        if not message_id:
            log_label.configure(text="※Message Id の入力は必須です。", text_color="red")
            print("※Message Id  の入力は必須です。")
            return
        
        try:
            response = requests.delete(f"{webhook_url}/messages/{message_id}")
        
            # レスポンスコードが200番台であれば成功とみなす
            if response.status_code // 100 == 2:
                log_label.configure(text="メッセージが削除されました。", text_color="green")
                print("メッセージが削除されました。")
            else:
                log_label.configure(text=f"※エラーが発生しました。レスポンスコード {response.status_code}", text_color="red")
                print(f"※エラーが発生しました。レスポンスコード {response.status_code}")
        except Exception as e:
            log_label.configure(text=f"※エラーが発生しました。{e}", text_color="red")
            print(f"※エラーが発生しました。{e}")

#--------------------#

class DiscordWebHookTool(tk.CTk):
    
    def __init__(self):
        """初期化"""
        super().__init__()
        self.title("DiscordWebHookTool - made by Haruru")  # ウィンドウのタイトル
        self.grid_rowconfigure(5, weight=1)  # 行5を可変幅に設定
        self.grid_columnconfigure(1, weight=1)  # 列1を可変幅に設定
        
        def disable_resize(event=None):
            return "break"  # イベントを無視して処理を中断する
        
        # サイズ変更を無効にする
        self.resizable(False, False)
        
        # サイズ変更イベントをバインドし、イベントハンドラーを設定する
        self.bind("<Configure>", disable_resize)
        
        # ウィンドウを一番左上に配置
        #self.attributes("-topmost", True)  # ウィンドウを最前面に表示
        self.geometry("+0+0") 
        
        self.pages = []  # ページのリスト
        self.create_main_menu()  # メインメニューの作成
        self.create_send_message_page()  # メッセージを送信するページの作成
        self.create_send_embed_message_page()  # 埋め込みメッセージを送信するページの作成
        self.create_edit_message_page()  # 送信済みメッセージを編集するページの作成
        self.create_delete_message_page()  # 送信済みメッセージを削除するページの作成
        self.create_pin_webhook_page()  # 固定Webhookを設定するページの作成
        
        self.create_embed_header_page() # 埋め込みメッセージのヘッダーページの作成
        self.create_embed_footer_page() # 埋め込みメッセージのフッターページの作成
        self.create_embed_field_page() # 埋め込みメッセージのフィールドページの作成

        self.show_page(0)  # 最初のページを表示
    
    def get_default_font(self, size):
        """フォントの指定"""
        return ("Helvetica", size)
    
    def show_page(self, page_num):
        """ページの切り替え"""
        for idx, page in enumerate(self.pages):
            if idx == page_num:
                page.pack(fill="both", expand=True)
            else:
                page.pack_forget()
    
    def create_return_menu_input(self, page, row, pagenum = 0):
        """戻るボタン"""
        return_button = tk.CTkButton(page, width=75, text="戻る", command=lambda: self.show_page(pagenum))
        return_button.grid(row=row, column=0, padx=10, pady=10, sticky='w')
        
    def get_current_webhook(self):
        """現在の設定URLを取得する"""
        # C直下にDiscordWebHookToolフォルダが存在しない場合は作成する
        folder_path = "C:/DiscordWebHookTool"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # webhook.txtが存在しない場合は作成する
        file_path = os.path.join(folder_path, "webhook.txt")
        if not os.path.exists(file_path):
            open(file_path, "w").close()  # ファイルを作成するだけ
            
        # ファイルが存在し、かつ中身がある場合はその内容を値として返す
        if os.path.exists(file_path) and os.stat(file_path).st_size > 0:
            with open(file_path, "r") as file:
                return file.read()
        return ""
    
    def use_current_webhook_action(self, box_check, webhook_url_var, webhook_url_box):
            """Webhookをチェック"""
            if box_check:
                webhook_url = self.get_current_webhook()  # 現在のWebhookを取得
                if webhook_url:
                    # テキストボックスにWebhook URLを表示
                    webhook_url_var.set(webhook_url)
                    # テキストボックスを入力不可にする
                    webhook_url_box.configure(state="disabled")
                else:
                    webhook_url_var.set("")  # テキストボックスを空にする
                    # テキストボックスを入力可能にする
                    webhook_url_box.configure(state="normal")
            else:
                webhook_url_var.set("")  # テキストボックスを空にする
                # テキストボックスを入力可能にする
                webhook_url_box.configure(state="normal")
    
    def create_webhoook_url_input(self, page, row):
        """Webhook Url フィールドの作成"""
        # Webhook Url ラベル
        label = tk.CTkLabel(page, text='Webhook Url を入力してください ')
        label.grid(row=row, column=0, padx=10, pady=10)
        
        # テキストボックス
        webhook_url_var = tk.StringVar()  # StringVar を作成
        webhook_url_box = tk.CTkEntry(page, width=300, textvariable=webhook_url_var)
        webhook_url_box.grid(row=row, column=1, padx=10, pady=10, sticky='w')
        # 右クリックで中身を削除
        webhook_url_box.bind("<Button-3>", lambda event: webhook_url_box.delete(0, tk.END))

        # チェックボックス
        use_current_webhook = tk.CTkCheckBox(page, text="固定Webhookを使用", command=lambda: self.use_current_webhook_action(use_current_webhook.get(), webhook_url_var, webhook_url_box))
        use_current_webhook.grid(row=row, column=2, padx=10, pady=10, sticky='w')
        return webhook_url_var
    
    def create_text_box_field_input(self, page, title, row):
        """フィールドの作成"""
        # ラベル
        label = tk.CTkLabel(page, text=title)
        label.grid(row=row, column=0, padx=10, pady=10)
        
        # テキストボックス
        text_box_var = tk.StringVar()  # StringVar を作成
        text_box_box = tk.CTkEntry(page, width=300, textvariable=text_box_var)
        text_box_box.grid(row=row, column=1, padx=10, pady=10, sticky='w')
        # 右クリックで中身を削除
        text_box_box.bind("<Button-3>", lambda event: text_box_box.delete(0, tk.END))
        
        return text_box_var
    
    def create_message_box_field_input(self, page, title, row):
        # メッセージ入力ラベル
        label = tk.CTkLabel(page, text=title)
        label.grid(row=row, column=0, padx=10, pady=10)
        
        # メッセージ入力用テキストボックス
        message_box = tk.CTkTextbox(page, width=300, height=50)
        message_box.grid(row=row, column=1, padx=10, pady=10, sticky='w')
        message_box.bind("<Button-3>", lambda event: message_box.delete(1.0, tk.END))
        return message_box
    
    def create_log_label_input(self, page, row):
        log_label = tk.CTkLabel(page, text='', text_color="red", font=self.get_default_font(15), wraplength=712)
        log_label.grid(row=row, column=0, columnspan=5, padx=10, pady=10, sticky='w')
        return log_label
    
    def create_file_select_field_input(self, page, title, row):
        def select_file(selected_file):
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
            if file_path:
                selected_file.configure(state="normal")
                selected_file.delete(0, tk.END)  # テキストボックスをクリア
                selected_file.insert(tk.END, file_path)
                selected_file.configure(state="disabled")
        
        # ファイル選択ラベル
        label = tk.CTkLabel(page, text=title)
        label.grid(row=row, column=0, padx=10, pady=10)
        
        # ファイル選択テキストボックス
        selected_file_var = tk.StringVar()  # StringVar を作成
        selected_file_box = tk.CTkEntry(page, width=300, state="disabled", textvariable=selected_file_var)
        selected_file_box.grid(row=row, column=1, padx=10, pady=10, sticky='w')
        selected_file_box.bind("<Button-3>", lambda event: clear_textbox(selected_file_box))
        
        def clear_textbox(textbox):
            textbox.configure(state="normal")
            textbox.delete(0, tk.END)
            textbox.configure(state="readonly")
            
        # ファイル選択ボタン
        select_file_button = tk.CTkButton(page, text="ファイルを選択", command=lambda: select_file(selected_file_box))
        select_file_button.grid(row=row, column=2, padx=10, pady=10)
        
        return selected_file_var
    
    #--------------------#
    
    # メインメニューの作成
    def create_main_menu(self):
        page = tk.CTkFrame(master=self)
        
        label = tk.CTkLabel(page, text="DiscordWebHookTool", text_color="cornflowerblue", font=self.get_default_font(20))
        label.grid(row=0, column=0, padx=12, pady=12, columnspan=2)

        # ページ選択用ラジオボタン
        self.page_choice = tk.IntVar()
        self.page_choice.set(1)
        tk.CTkRadioButton(page, text="メッセージを送信する", variable=self.page_choice, value=1, font=self.get_default_font(10)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.CTkRadioButton(page, text="埋め込みメッセージを送信する", variable=self.page_choice, value=2, font=self.get_default_font(10)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        tk.CTkRadioButton(page, text="送信済みメッセージを編集する", variable=self.page_choice, value=3, font=self.get_default_font(10)).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        tk.CTkRadioButton(page, text="送信済みメッセージを削除する", variable=self.page_choice, value=4, font=self.get_default_font(10)).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        tk.CTkRadioButton(page, text="固定Webhookを設定する", variable=self.page_choice, value=5, font=self.get_default_font(10)).grid(row=5, column=0, padx=10, pady=5, sticky="w")

        # 決定ボタン
        decision_button = tk.CTkButton(page, text="決定", width=75, command=lambda: self.show_page(self.page_choice.get()))
        decision_button.grid(row=6, column=0, padx=10, pady=10)
        # ページを追加
        self.pages.append(page)
    
    #--------------------#

    # メッセージを送信するページの作成
    def create_send_message_page(self):
        """メッセージを送信するページの作成"""
        
        def select_files():
            file_path = filedialog.askopenfilenames()
    
            file_paths.extend(file_path)
    
            file_count = len(file_paths)
    
            if file_count > 0:
                files_text = "\n".join(file_paths)
                selected_filelist_box.configure(state="normal")
                selected_filelist_box.delete("1.0", tk.END)
                selected_filelist_box.insert(tk.END, files_text)
                selected_filelist_box.configure(state="disabled")
        
        page = tk.CTkFrame(master=self)
        
        # Webhook Url フィールドの作成
        webhook_url_var = self.create_webhoook_url_input(page, 0)
        
        # ユーザー名フィールドの作成
        user_name_var = self.create_text_box_field_input(page, "ユーザー名を入力してください ", 1)
        
        # Avatar Url フィールドの作成
        avatar_url_var = self.create_text_box_field_input(page, "Avatar Url を入力してください ", 2)
        
        # メッセージ入力用フィールドの作成
        send_message_box = self.create_message_box_field_input(page, "メッセージを入力してください ", 3)
        
        # ファイル選択ラベル
        label = tk.CTkLabel(page, text="ファイルを選択してください ")
        label.grid(row=4, column=0, padx=10, pady=10)
        
        # ファイルパスを保持するリスト
        file_paths = []
        
        # 選択されたファイルを表示するテキストボックス
        selected_filelist_box = tk.CTkTextbox(page, width=300, height=50, state="disabled")
        selected_filelist_box.grid(row=4, column=1, padx=10, pady=10, sticky='w')
        selected_filelist_box.bind("<Button-3>", lambda event: clear_textbox(selected_filelist_box))
        def clear_textbox(textbox):
            # 選択されたファイルパスをクリアする
            file_paths.clear()
            textbox.configure(state="normal")
            textbox.delete(1.0, tk.END)
            textbox.configure(state="disabled")
        
        # ファイル選択ボタン
        select_file_button = tk.CTkButton(page, text="ファイルを選択", command=select_files)
        select_file_button.grid(row=4, column=2, padx=3, pady=3)
        
        # チェックボックス
        use_file_spoiler = tk.CTkCheckBox(page, text="ファイルを隠す")
        use_file_spoiler.grid(row=5, column=0, padx=10, pady=10, sticky='w')
        
        # ログラベル
        log_label = self.create_log_label_input(page, 7)
        
        # 送信ボタン
        decision_button = tk.CTkButton(page, width=75, text="送信", command=lambda: DiscordWebhookClient.send_discord_message(webhook_url_var.get(), user_name_var.get(), avatar_url_var.get(), send_message_box.get("1.0", tk.END), file_paths, use_file_spoiler.get(), log_label))
        decision_button.grid(row=6, column=2, padx=10, pady=10, sticky='e')
        
        # 戻るボタン
        self.create_return_menu_input(page, 6)
        # ページを追加
        self.pages.append(page)
        
    #--------------------#
    
    def create_send_embed_message_page(self):
        """埋め込みメッセージを送信するページの作成"""
        
        def validate_input(action, value_if_allowed):
            # 入力が空白でないことを確認
            if value_if_allowed.strip() == "":
                return True
            # 入力が数字のみで構成されていることを確認
            try:
                # 入力が0から255の範囲にあることを確認
                if int(value_if_allowed) < 0 or int(value_if_allowed) > 255:
                    return False
                return True
            except ValueError:
                return False
        
        def update_color(event=None):
            # RGB値を取得
            red = 0
            green = 0
            blue = 0
            if red_entry_var.get():
                red = int(red_entry_var.get())
            if green_entry_var.get():
                green = int(green_entry_var.get())
            if blue_entry_var.get():
                blue = int(blue_entry_var.get())
            # RGB値を16進数に変換して、ラベルの背景色を更新
            color_hex = '#{:02x}{:02x}{:02x}'.format(red, green, blue)
            color_pick_box.configure(fg_color=color_hex)
        
        def discord_bar_color():
            red = 0
            green = 0
            blue = 0
            if red_entry_var.get():
                red = int(red_entry_var.get())
            if green_entry_var.get():
                green = int(green_entry_var.get())
            if blue_entry_var.get():
                blue = int(blue_entry_var.get())
            # RGB値を16進数の文字列に変換
            hex_color = '#{:02x}{:02x}{:02x}'.format(red, green, blue)
            # 16進数の文字列を10進数の整数に変換
            decimal_color = int(hex_color[1:], 16)
            return decimal_color

        page = tk.CTkFrame(master=self)
        
        # Webhook Url フィールドの作成
        webhook_url_var = self.create_webhoook_url_input(page, 0)
        
        # ユーザー名フィールドの作成
        user_name_var = self.create_text_box_field_input(page, "ユーザー名を入力してください ", 1)
        
        # Avatar Url フィールドの作成
        avatar_url_var = self.create_text_box_field_input(page, "Avatar Url を入力してください ", 2)
        
        # タイトル入力フィールドの作成
        title_box = self.create_message_box_field_input(page, "タイトルを入力してください ", 3)
        
        # 説明入力フィールドの作成
        description_box = self.create_message_box_field_input(page, "説明を入力してください ", 4)
        
        # タイトルUrl フィールドの作成
        title_url_var = self.create_text_box_field_input(page, "タイトルUrlを入力してください ", 5)
        
        # 色選択ラベル
        color_label = tk.CTkLabel(page, text="バーの色を選択してください ")
        color_label.grid(row=6, column=0, padx=10, pady=10, sticky='n')
        
        def color_reset(color_entry_var):
            color_entry_var.set("0")
            update_color()
        
        # red num
        red_entry_var = tk.StringVar(value="0")  # StringVar を作成
        red_entry_box = tk.CTkEntry(page, width=95, textvariable=red_entry_var)
        red_entry_box.grid(row=6, column=1, padx=10, pady=10, sticky='w')
        red_entry_box.configure(validate="key")
        red_entry_box.configure(validatecommand=(page.register(validate_input), "%d", "%P"))
        red_entry_box.bind('<KeyRelease>', update_color)
        red_entry_box.bind("<Button-3>", lambda event: color_reset(red_entry_var))
        
        # green num
        green_entry_var = tk.StringVar(value="0")  # StringVar を作成
        green_entry_box = tk.CTkEntry(page, width=95, textvariable=green_entry_var)
        green_entry_box.grid(row=6, column=1, padx=10, pady=10)
        green_entry_box.configure(validate="key")
        green_entry_box.configure(validatecommand=(page.register(validate_input), "%d", "%P"))
        green_entry_box.bind('<KeyRelease>', update_color)
        green_entry_box.bind("<Button-3>", lambda event: color_reset(green_entry_var))
        
        # blue num
        blue_entry_var = tk.StringVar(value="0")  # StringVar を作成
        blue_entry_box = tk.CTkEntry(page, width=95, textvariable=blue_entry_var)
        blue_entry_box.grid(row=6, column=1, padx=10, pady=10, sticky='e')
        blue_entry_box.configure(validate="key")
        blue_entry_box.configure(validatecommand=(page.register(validate_input), "%d", "%P"))
        blue_entry_box.bind('<KeyRelease>', update_color)
        blue_entry_box.bind("<Button-3>", lambda event: color_reset(blue_entry_var))
        
        #色表示
        color_pick_var = tk.StringVar()  # StringVar を作成
        color_pick_box = tk.CTkEntry(page, width=95, fg_color="#000000", state="readonly",textvariable=color_pick_var)
        color_pick_box.grid(row=6, column=2, padx=10, pady=10, sticky='w')
        
        #メイン写真選択フィールド作成
        selected_file_var = self.create_file_select_field_input(page, "写真を選択してください ", 7)
        
        #thumbnail
        selected_thumbnail_file_var = self.create_file_select_field_input(page, "サムネイルを選択してください", 8)
        
        # タイトル入力ラベル
        label = tk.CTkLabel(page, text="サブオプション ")
        label.grid(row=9, column=0, padx=10, pady=10)
        
        # ヘッダーボタン
        header_button = tk.CTkButton(page, width=140, text="ヘッダー", command=lambda: self.show_page(6))
        header_button.grid(row=9, column=1, padx=10, pady=10, sticky='w')
        
        # フッターボタン
        footer_button = tk.CTkButton(page, width=140, text="フッター", command=lambda: self.show_page(7))
        footer_button.grid(row=9, column=1, padx=10, pady=10, sticky='e')
        
        # フィールドボタン
        field_button = tk.CTkButton(page, width=140, text="フィールド", command=lambda: self.show_page(8))
        field_button.grid(row=9, column=2, padx=10, pady=10)
        
        # ログラベル
        log_label = self.create_log_label_input(page, 11)
        
        # 送信ボタン
        decision_button = tk.CTkButton(page, width=75, text="送信", command=lambda: DiscordWebhookClient.send_discord_embed_message(webhook_url_var.get(), 
                                                                                                                                    user_name_var.get(), 
                                                                                                                                    avatar_url_var.get(), 
                                                                                                                                    title_box.get("1.0", tk.END), 
                                                                                                                                    description_box.get("1.0", tk.END), 
                                                                                                                                    title_url_var.get(), 
                                                                                                                                    self.timestamp_flg.get(), 
                                                                                                                                    discord_bar_color(), 
                                                                                                                                    self.selected_footer_icon_file_var.get(), 
                                                                                                                                    self.footer_text_box.get("1.0", tk.END),
                                                                                                                                    selected_thumbnail_file_var.get(), 
                                                                                                                                    selected_file_var.get(), 
                                                                                                                                    self.header_text_box.get("1.0", tk.END),
                                                                                                                                    self.header_url_var.get(),
                                                                                                                                    self.selected_header_icon_file_var.get(),
                                                                                                                                    self.field_list,
                                                                                                                                    log_label))
        
        decision_button.grid(row=10, column=2, padx=10, pady=10, sticky='e')
        
        # 戻るボタン
        self.create_return_menu_input(page, 10)
        # ページを追加
        self.pages.append(page)
    
    #--------------------#
    
    def create_embed_header_page(self):
        """埋め込みメッセージのヘッダーページの作成"""
        page = tk.CTkFrame(master=self)
        
        #ヘッダー選択フィールド作成
        self.selected_header_icon_file_var = self.create_file_select_field_input(page, "ヘッダーアイコンを選択してください ", 0)
        
        # ヘッダーテキストフィールドの作成
        self.header_text_box = self.create_message_box_field_input(page, "ヘッダーテキストを入力してください ", 1)
        
        # header Url フィールドの作成
        self.header_url_var = self.create_text_box_field_input(page, "ヘッダーUrl を入力してください ", 2)
        
        # 戻るボタン
        self.create_return_menu_input(page, 4, 2)
        # ページを追加
        self.pages.append(page)
    
    #--------------------#
    
    def create_embed_footer_page(self):
        """埋め込みメッセージのフッターページの作成"""
        page = tk.CTkFrame(master=self)
        
        #フッター選択フィールド作成
        self.selected_footer_icon_file_var = self.create_file_select_field_input(page, "フッターアイコンを選択してください ", 0)
        
        # フッターテキストフィールドの作成
        self.footer_text_box = self.create_message_box_field_input(page, "フッターテキストを入力してください ", 1)
        
        # チェックボックス
        self.timestamp_flg = tk.CTkCheckBox(page, text="TimeStampを使用")
        self.timestamp_flg.grid(row=1, column=2, padx=10, pady=10, sticky='w')
        
        # 戻るボタン
        self.create_return_menu_input(page, 2, 2)
        # ページを追加
        self.pages.append(page)
    
    #--------------------#
    
    def create_embed_field_page(self):
        """埋め込みメッセージのフィールドページの作成"""
        
        def add_field_to_list():
            """
            フィールドをリストに追加する関数
            """
            # 入力されたフィールド名、フィールドの説明を取得
            field_name = field_name_box.get("1.0", tk.END)
            field_value = field_value_box.get("1.0", tk.END)
            # インラインフラグの値を取得
            inline = inline_flg.get()
            
            # フィールド情報を辞書にしてリストに追加
            self.field_list.append({
                "name": field_name,
                "value": field_value,
                "inline": inline
            })
            current_lenfield_label.configure(text=f"現在のフィールド数 : {len(self.field_list)}")
            
        def field_clear():
            if self.field_list:
                self.field_list.pop()
            current_lenfield_label.configure(text=f"現在のフィールド数 : {len(self.field_list)}")

        page = tk.CTkFrame(master=self)
        
        self.field_list = []
        
        # フィールドネームテキストフィールドの作成
        field_name_box = self.create_message_box_field_input(page, "フィールドタイトルを入力してください ", 0)
        
        # フィールドネームテキストフィールドの作成
        field_value_box = self.create_message_box_field_input(page, "フィールドの説明を入力してください ", 1)
        
        # チェックボックス
        inline_flg = tk.CTkCheckBox(page, text="inline")
        inline_flg.grid(row=1, column=2, padx=10, pady=10, sticky='w')
        
        # 現在のフィールド要素数を表示
        current_lenfield_label = tk.CTkLabel(page, text=f"現在のフィールド数 : {len(self.field_list)}")
        current_lenfield_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='w')
        
        # フィールドのクリアボタン
        clear_button = tk.CTkButton(page, width=75, text="1つ消す", command=lambda: field_clear())#追加アクション
        clear_button.grid(row=2, column=2, padx=10, pady=10, sticky='e')
        
        # 追加ボタン
        decision_button = tk.CTkButton(page, width=75, text="追加", command=lambda: add_field_to_list())#追加アクション
        decision_button.grid(row=3, column=2, padx=10, pady=10, sticky='e')
        
        # 戻るボタン
        self.create_return_menu_input(page, 3, 2)
        # ページを追加
        self.pages.append(page)
    
    #--------------------#
    
    def create_edit_message_page(self):
        """送信済みメッセージを編集するするページの作成"""
        page = tk.CTkFrame(master=self)
        
        # Webhook Url フィールドの作成
        webhook_url_var = self.create_webhoook_url_input(page, 0)
        
        # メッセージIDフィールドの作成
        message_id_var = self.create_text_box_field_input(page, "Message Id を入力してください ", 1)
        
        # 新しいメッセージ入力フィールドの作成
        send_new_message_box = self.create_message_box_field_input(page, "新しいメッセージを入力してください ", 2)
        
        # ログラベル
        log_label = self.create_log_label_input(page, 4)
        
        # 編集ボタン
        decision_button = tk.CTkButton(page, width=75, text="編集", command=lambda: DiscordWebhookClient.edit_discord_message(webhook_url_var.get(), message_id_var.get(), send_new_message_box.get("1.0", tk.END), log_label))
        decision_button.grid(row=3, column=2, padx=10, pady=10, sticky='e')
        
        # 戻るボタン
        self.create_return_menu_input(page, 3)
        # ページを追加
        self.pages.append(page)
    
    #--------------------#
    
    def create_delete_message_page(self):
        """送信済みメッセージを削除するするページの作成"""
        page = tk.CTkFrame(master=self)
        
        # Webhook Url フィールドの作成
        webhook_url_var = self.create_webhoook_url_input(page, 0)
        
        # メッセージIDフィールドの作成
        message_id_var = self.create_text_box_field_input(page, "Message Id を入力してください ", 1)
        
        # ログラベル
        log_label = self.create_log_label_input(page, 3)
        
        # 削除ボタン
        decision_button = tk.CTkButton(page, width=75, text="削除", command=lambda: DiscordWebhookClient.delete_discord_message(webhook_url_var.get(), message_id_var.get(), log_label))
        decision_button.grid(row=2, column=2, padx=10, pady=10, sticky='e')
       
        # 戻るボタン
        self.create_return_menu_input(page, 2)
        # ページを追加
        self.pages.append(page)
    
    #--------------------#
        
    # 固定Webhookを設定するページの作成
    def create_pin_webhook_page(self):
        
        def pin_webhook_action(new_webhook_url, file_path, current_url_label, log_label):
            """新しいWebhook Urlをファイルに書き込み"""
            if new_webhook_url:  # テキストボックスが空でない場合のみ書き込みを行う
                with open(file_path, "w") as file:
                    file.write(new_webhook_url) # new_webhook_urlをファイルに書き込みました
                   
                current_url_label.configure(text=f"現在の固定URL : {new_webhook_url}")
        
                log_label.configure(text="Webhook Url の更新が完了しました。", text_color="green")
            else:
                log_label.configure(text="※Webhook Url の入力は必須です。", text_color="red")
        
        # C直下にDiscordWebHookToolフォルダが存在しない場合は作成する
        folder_path = "C:/DiscordWebHookTool"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # webhook.txtが存在しない場合は作成する
        file_path = os.path.join(folder_path, "webhook.txt")
        if not os.path.exists(file_path):
            open(file_path, "w").close()  # ファイルを作成するだけ
        
        page = tk.CTkFrame(self)
        
        # Webhook Url ラベル
        label = tk.CTkLabel(page, text='Webhook Url を入力してください ', font=self.get_default_font(12))
        label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    
        # Webhook Url テキストボックス
        set_webhook_url_var = tk.StringVar()
        set_webhook_url_box = tk.CTkEntry(page, width=700, font=self.get_default_font(12), textvariable=set_webhook_url_var)
        set_webhook_url_box.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        # 右クリックで中身を削除
        set_webhook_url_box.bind("<Button-3>", lambda event: set_webhook_url_box.delete(0, tk.END))
        
        # 現在の固定 Webhook Url を表示
        current_url_label = tk.CTkLabel(page, text=f"現在の固定URL : {self.get_current_webhook()}", font=self.get_default_font(12), wraplength=910)
        current_url_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='w')
        
        # ログラベル
        log_label = self.create_log_label_input(page, 3)
        
        # 決定ボタン
        decision_button = tk.CTkButton(page, width=75, text="決定", command=lambda: pin_webhook_action(set_webhook_url_var.get(), file_path, current_url_label, log_label))
        decision_button.grid(row=2, column=1, padx=10, pady=10, sticky='e')
        
        # 戻るボタン
        self.create_return_menu_input(page, 2)
        # ページを追加
        self.pages.append(page)
                
    #--------------------#

def temp_path(relative_path):
    try:
        #Retrieve Temp Path
        base_path = sys._MEIPASS
    except Exception:
        #Retrieve Current Path Then Error 
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

window = DiscordWebHookTool()

# アイコンを設定
logo_path = temp_path("icon.ico")  # アイコンファイルのパスを取得
window.iconbitmap(logo_path)  # アイコンを設定

# pyinstaller DiscordWebhookTool.pyw --onefile --noconsole --icon=icon.ico --add-data "icon.ico;./

window.mainloop()

