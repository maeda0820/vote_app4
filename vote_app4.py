import streamlit as st
import pandas as pd
import os

# 背景色を水色（15%の不透明度）に設定するCSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: rgba(173,216,230,0.15);
    }
    </style>
    """,
    unsafe_allow_html=True
)

FILENAME = "votes.csv"
PRAISES_FILE = "praises.csv"
USER_CREDENTIALS_FILE = "user_credentials.csv"
VOTES_COUNT_FILE = "votes_count.csv"  # 投票回数を記録するファイル

# ユーザー情報の初期化
if os.path.exists(USER_CREDENTIALS_FILE):
    user_credentials_df = pd.read_csv(USER_CREDENTIALS_FILE)
else:
    user_credentials_df = pd.DataFrame(columns=["id", "password", "department"])

# 投票データの読み込み
if os.path.exists(FILENAME):
    df = pd.read_csv(FILENAME)
else:
    df = pd.DataFrame(columns=["id", "department", "month", "category", "suggestion", "votes"])

# 投票回数の初期化
if os.path.exists(VOTES_COUNT_FILE):
    votes_count_df = pd.read_csv(VOTES_COUNT_FILE)
else:
    votes_count_df = pd.DataFrame(columns=["id", "votes_count"])

# 自分を褒めた記録の読み込み
if os.path.exists(PRAISES_FILE):
    praises_df = pd.read_csv(PRAISES_FILE)
else:
    praises_df = pd.DataFrame(columns=["id", "department", "praise"])

# セッション初期化
if 'user_authenticated' not in st.session_state:
    st.session_state['user_authenticated'] = False
if 'admin_authenticated' not in st.session_state:
    st.session_state['admin_authenticated'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = ''
if 'user_department' not in st.session_state:
    st.session_state['user_department'] = ''

st.title("業務改善提案制度")

# ログアウト
if st.session_state['user_authenticated'] or st.session_state['admin_authenticated']:
    if st.button("🔓 ログアウト"):
        st.session_state['user_authenticated'] = False
        st.session_state['admin_authenticated'] = False
        st.session_state['user_id'] = ''
        st.session_state['user_department'] = ''
        st.session_state['page'] = 'login'
        st.success("ログアウトしました")

# ログイン画面
if not (st.session_state['user_authenticated'] or st.session_state['admin_authenticated']):
    with st.form("login_form"):
        st.subheader("ログイン / 新規登録 / 管理者ログイン")
        login_type = st.radio("選択してください", ["ログイン", "新規登録", "管理者ログイン"])
        user_id = st.text_input("ID")
        user_password = st.text_input("パスワード", type='password')
        department = st.selectbox("所属部署を選んでください", ["営業部", "管理課", "仕上製本課", "印刷課", "企画デザイン課", "総務課"])

        if st.form_submit_button("実行"):
            if login_type == "ログイン":
                user_row = user_credentials_df[(user_credentials_df["id"] == user_id) &
                                               (user_credentials_df["password"] == user_password) &
                                               (user_credentials_df["department"] == department)]
                if not user_row.empty:
                    st.session_state['user_authenticated'] = True
                    st.session_state['user_id'] = user_id
                    st.session_state['user_department'] = department
                    st.session_state['page'] = 'post'
                    st.success("ログイン成功")
                else:
                    st.error("ログイン情報が間違っています")
            elif login_type == "新規登録":
                if user_id in user_credentials_df['id'].values:
                    st.warning("このIDは既に使われています")
                else:
                    new_user = pd.DataFrame([[user_id, user_password, department]], columns=["id", "password", "department"])
                    user_credentials_df = pd.concat([user_credentials_df, new_user], ignore_index=True)
                    user_credentials_df.to_csv(USER_CREDENTIALS_FILE, index=False)
                    st.success("登録完了！ログインしてください。")
            elif login_type == "管理者ログイン":
                if user_id == "管理者" and user_password == "000000" and department == "企画デザイン課":
                    st.session_state['admin_authenticated'] = True
                    st.session_state['user_id'] = user_id
                    st.session_state['user_department'] = department
                    st.success("管理者ログイン成功")
                else:
                    st.error("管理者情報が正しくありません")

# 投稿・投票ページ
if st.session_state['user_authenticated'] or st.session_state['admin_authenticated']:
    st.subheader("投稿ページ")
    months = ["2025年4月", "2025年5月", "2025年6月", "2025年7月", "2025年8月"]
    selected_month = st.selectbox("実施月を選んでください", months)

    menu = st.radio("操作を選んでください", ["作業効率を高めるための提案", 
                                              "利益向上に関する提案", 
                                              "お客様の役に立つための提案", 
                                              "社内の連携や、その他の提案", 
                                              "改善提案に投票", "自分を褒めよう", "結果を見る"])

    if menu in ["作業効率を高めるための提案", "利益向上に関する提案", "お客様の役に立つための提案", "社内の連携や、その他の提案"]:
        category = menu
        existing_proposal = df[(df["month"] == selected_month) & (df["category"] == category) & (df["id"] == st.session_state['user_id'])]
        if not existing_proposal.empty:
            st.write(f"現在の提案内容：{existing_proposal.iloc[0]['suggestion']}")
            new_suggestion = st.text_area("新しい提案を入力：", value=existing_proposal.iloc[0]['suggestion'])
            if st.button("修正する"):
                df.at[existing_proposal.index[0], "suggestion"] = new_suggestion
                df.at[existing_proposal.index[0], "votes"] = 0
                df.to_csv(FILENAME, index=False)
                st.success(f"{category} の提案を修正しました！")
        else:
            new_suggestion = st.text_area(f"{category} の提案を入力してください：")
            if st.button("投稿する"):
                if new_suggestion:
                    new_row = pd.DataFrame([[st.session_state['user_id'], st.session_state['user_department'], selected_month, category, new_suggestion, 0]],
                                           columns=["id", "department", "month", "category", "suggestion", "votes"])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(FILENAME, index=False)
                    st.success(f"{category} の改善提案を投稿しました！")
                else:
                    st.warning("改善提案を入力してください！")

    elif menu == "改善提案に投票":
        st.subheader("改善提案一覧")
        month_df = df[df["month"] == selected_month]
        if month_df.empty:
            st.warning(f"{selected_month}の改善提案はまだありません。")
        else:
            user_votes_count_row = votes_count_df[votes_count_df["id"] == st.session_state['user_id']]
            if user_votes_count_row.empty:
                user_votes_count = 0
                votes_count_df = pd.concat([votes_count_df, pd.DataFrame([[st.session_state['user_id'], 0]], columns=["id", "votes_count"])], ignore_index=True)
            else:
                user_votes_count = int(user_votes_count_row.iloc[0]["votes_count"])

            for idx, row in month_df.iterrows():
                st.write(f"📌 {row['suggestion']}（投票数: {row['votes']}）【{row['category']}】")
                col1, col2 = st.columns(2)
                with col1:
                    if user_votes_count < 3:
                        if st.button(f"👍 投票する", key=f"vote_{idx}"):
                            if row['id'] != st.session_state['user_id']:
                                df.at[idx, "votes"] += 1
                                votes_count_df.loc[votes_count_df["id"] == st.session_state['user_id'], "votes_count"] += 1
                                df.to_csv(FILENAME, index=False)
                                votes_count_df.to_csv(VOTES_COUNT_FILE, index=False)
                                st.success("投票しました！")
                            else:
                                st.warning("自分の提案には投票できません！")
                with col2:
                    if st.session_state['admin_authenticated']:
                        if st.button(f"🗑️ 削除する", key=f"delete_{idx}"):
                            df = df.drop(idx)
                            df.to_csv(FILENAME, index=False)
                            st.success("提案を削除しました！")
                            st.experimental_rerun()

            if user_votes_count >= 3:
                st.warning("あなたはすでに3回投票しました。")
                if st.button("🔄 投票をやり直す"):
                    votes_count_df.loc[votes_count_df["id"] == st.session_state['user_id'], "votes_count"] = 0
                    votes_count_df.to_csv(VOTES_COUNT_FILE, index=False)
                    st.success("投票回数をリセットしました。再度投票できます。")

    elif menu == "結果を見る":
        st.subheader("📊 改善提案の結果")
        month_df = df[df["month"] == selected_month]
        if not month_df.empty:
            sorted_df = month_df.sort_values("votes", ascending=False)
            result_df = sorted_df[["category", "suggestion", "votes"]]
            st.dataframe(result_df)
            if st.session_state['admin_authenticated']:
                st.download_button("📥 改善提案の投票集計データをExcel形式でダウンロード",
                                   data=sorted_df[["id", "department", "category", "suggestion", "votes"]].to_csv(index=False),
                                   file_name=f"improvement_proposals_votes_{selected_month}.csv",
                                   mime="text/csv")
            else:
                st.warning("管理者のみダウンロードできます。")

    elif menu == "自分を褒めよう":
        st.subheader("自分を褒めよう！")
        praise = st.text_area("自分を褒める内容を入力してください：")
        existing_praise = praises_df[praises_df["id"] == st.session_state['user_id']]
        if not existing_praise.empty:
            st.write(f"現在の褒め内容：{existing_praise.iloc[0]['praise']}")
            if st.button("修正する"):
                praises_df.at[existing_praise.index[0], "praise"] = praise
                praises_df.to_csv(PRAISES_FILE, index=False)
                st.success("褒め内容を修正しました！")
        else:
            if st.button("投稿する"):
                praises_df = pd.concat([praises_df, pd.DataFrame([[st.session_state['user_id'], st.session_state['user_department'], praise]], columns=["id", "department", "praise"])], ignore_index=True)
                praises_df.to_csv(PRAISES_FILE, index=False)
                st.success("褒め内容を投稿しました！")

        if st.session_state['admin_authenticated']:
            st.download_button("📥 自分を褒めようの集計データをExcel形式でダウンロード",
                               data=praises_df.to_csv(index=False),
                               file_name=f"praises_{selected_month}.csv",
                               mime="text/csv")
