
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
from pathlib import Path


# ---------- 파일 기능 ----------

# 현재 파일 이름을 프로그램 창 제목에 표시
def update_title():
    name = Path(current_file).name if current_file else "제목 없음"
    root.title(f"{name} - 수업용 메모장")


# 파일 저장
def save_file():
    global current_file

    path = current_file or filedialog.asksaveasfilename(
        parent=root,
        title="저장",
        defaultextension=".txt",
        filetypes=[
            ("텍스트 파일", "*.txt"),
            ("모든 파일", "*.*")
        ]
    )

    if not path:
        return False

    try:
        Path(path).write_text(
            text.get("1.0", "end-1c"),
            encoding="utf-8"
        )

    except (OSError, UnicodeError) as error:
        messagebox.showerror(
            "저장 오류",
            str(error),
            parent=root
        )
        return False

    current_file = path
    text.edit_modified(False)
    update_title()

    return True


# 새 파일, 파일 열기, 종료 전에 저장 여부 확인
def confirm_save():
    if not text.edit_modified():
        return True

    answer = messagebox.askyesnocancel(
        "저장 확인",
        "변경한 내용을 저장하시겠습니까?",
        parent=root
    )

    if answer is None:
        return False

    return save_file() if answer else True


# 새 파일 만들기
def new_file():
    global current_file

    if not confirm_save():
        return

    text.delete("1.0", tk.END)
    text.edit_modified(False)

    current_file = None

    update_title()
    text.focus_set()


# 파일 열기
def open_file():
    global current_file

    if not confirm_save():
        return

    path = filedialog.askopenfilename(
        parent=root,
        title="열기",
        filetypes=[
            ("텍스트 파일", "*.txt"),
            ("모든 파일", "*.*")
        ]
    )

    if not path:
        return

    try:
        content = Path(path).read_text(
            encoding="utf-8-sig"
        )

    except (OSError, UnicodeError) as error:
        messagebox.showerror(
            "열기 오류",
            f"UTF-8 텍스트 파일을 선택해 주세요.\n{error}",
            parent=root
        )
        return

    text.delete("1.0", tk.END)
    text.insert("1.0", content)
    text.edit_modified(False)

    current_file = path

    update_title()
    text.focus_set()


# 프로그램 종료
def exit_program():
    if confirm_save():
        root.destroy()


# ---------- 편집 기능 ----------

# 잘라내기
def cut_text():
    text.focus_set()
    text.event_generate("<<Cut>>")


# 복사
def copy_text():
    text.focus_set()
    text.event_generate("<<Copy>>")


# 붙여넣기
def paste_text():
    text.focus_set()
    text.event_generate("<<Paste>>")


# ---------- 찾기 및 바꾸기 기능 ----------

def open_find_dialog():

    # 찾기 및 바꾸기 창 생성
    find_window = tk.Toplevel(root)
    find_window.title("찾기 및 바꾸기")
    find_window.geometry("350x200")
    find_window.resizable(False, False)
    find_window.transient(root)

    # 검색어와 변경할 단어를 저장하는 변수
    find_var = tk.StringVar()
    replace_var = tk.StringVar()

    # 검색된 단어의 강조 색상 설정
    text.tag_configure(
        "search_highlight",
        background="yellow",
        foreground="black"
    )

    # 찾을 내용 입력
    tk.Label(
        find_window,
        text="찾을 내용:"
    ).pack(pady=3)

    find_entry = tk.Entry(
        find_window,
        textvariable=find_var,
        width=35
    )
    find_entry.pack()

    # 바꿀 내용 입력
    tk.Label(
        find_window,
        text="바꿀 내용:"
    ).pack(pady=3)

    replace_entry = tk.Entry(
        find_window,
        textvariable=replace_var,
        width=35
    )
    replace_entry.pack()

    # 다음 단어 찾기
    def find_next():

        keyword = find_var.get()

        if not keyword:
            messagebox.showwarning(
                "검색 오류",
                "찾을 내용을 입력하세요.",
                parent=find_window
            )
            return

        # 이전 검색 결과 강조 표시 제거
        text.tag_remove(
            "search_highlight",
            "1.0",
            "end"
        )

        # 현재 커서 위치부터 검색
        start = text.index("insert")
        count = tk.IntVar()

        position = text.search(
            keyword,
            start,
            stopindex="end",
            nocase=True,
            count=count
        )

        # 현재 위치 이후에 검색 결과가 없으면
        # 문서 처음부터 다시 검색
        if not position:
            position = text.search(
                keyword,
                "1.0",
                stopindex="end",
                nocase=True,
                count=count
            )

        if position:
            end = f"{position}+{count.get()}c"

            # 검색된 단어 강조 표시
            text.tag_add(
                "search_highlight",
                position,
                end
            )

            # 검색된 위치로 커서 이동
            text.mark_set("insert", end)
            text.see(position)
            text.focus_set()

        else:
            messagebox.showinfo(
                "검색 결과",
                "검색한 단어가 없습니다.",
                parent=find_window
            )

    # 검색된 단어 하나 바꾸기
    def replace_one():

        keyword = find_var.get()
        replacement = replace_var.get()

        if not keyword:
            messagebox.showwarning(
                "입력 오류",
                "찾을 내용을 입력하세요.",
                parent=find_window
            )
            return

        # 현재 강조 표시된 검색 결과 확인
        ranges = text.tag_ranges("search_highlight")

        if len(ranges) >= 2:
            start, end = ranges[0], ranges[1]
            selected = text.get(start, end)

            # 강조된 단어가 현재 검색어와 일치하는지 확인
            if selected.casefold() == keyword.casefold():

                # 기존 단어 삭제 후 새로운 단어 입력
                text.delete(start, end)
                text.insert(start, replacement)

                # 커서를 변경한 단어 뒤로 이동
                text.mark_set(
                    "insert",
                    f"{start}+{len(replacement)}c"
                )

                # 기존 강조 표시 제거
                text.tag_remove(
                    "search_highlight",
                    "1.0",
                    "end"
                )

                # 다음 검색 결과 찾기
                find_next()
                return

        # 검색 결과가 없으면 다음 단어 검색
        find_next()

    # 문서 전체의 단어 바꾸기
    def replace_all():

        keyword = find_var.get()
        replacement = replace_var.get()

        if not keyword:
            messagebox.showwarning(
                "입력 오류",
                "찾을 내용을 입력하세요.",
                parent=find_window
            )
            return

        count = 0
        start = "1.0"

        # 문서 처음부터 검색 시작
        while True:

            match_count = tk.IntVar()

            position = text.search(
                keyword,
                start,
                stopindex="end",
                nocase=True,
                count=match_count
            )

            # 더 이상 검색 결과가 없으면 종료
            if not position:
                break

            end = f"{position}+{match_count.get()}c"

            # 기존 단어 삭제
            text.delete(position, end)

            # 새로운 단어 입력
            text.insert(position, replacement)

            count += 1

            # 새로 입력한 단어 뒤부터 다음 검색
            start = f"{position}+{len(replacement)}c"

        # 검색 결과 강조 표시 제거
        text.tag_remove(
            "search_highlight",
            "1.0",
            "end"
        )

        # 변경 결과 알림
        messagebox.showinfo(
            "바꾸기 완료",
            f"{count}개의 단어를 변경했습니다.",
            parent=find_window
        )

    # 버튼 영역 생성
    button_frame = tk.Frame(find_window)
    button_frame.pack(pady=12)

    # 다음 찾기 버튼
    tk.Button(
        button_frame,
        text="다음 찾기",
        command=find_next
    ).pack(side="left", padx=3)

    # 바꾸기 버튼
    tk.Button(
        button_frame,
        text="바꾸기",
        command=replace_one
    ).pack(side="left", padx=3)

    # 모두 바꾸기 버튼
    tk.Button(
        button_frame,
        text="모두 바꾸기",
        command=replace_all
    ).pack(side="left", padx=3)

    # Enter 키를 누르면 다음 단어 검색
    find_entry.bind(
        "<Return>",
        lambda event: find_next()
    )

    # 찾기 입력창에 커서 배치
    find_entry.focus_set()

    # 찾기 창이 열려 있는 동안 메인 창 조작 제한
    find_window.grab_set()


# ---------- 서식 기능 ----------

# 글꼴 크기와 확대 배율 적용
def apply_font():

    actual_size = max(
        1,
        round(base_font_size * zoom_percent / 100)
    )

    display_font.configure(size=actual_size)


# 글꼴 종류와 크기 변경
def change_font():

    dialog = tk.Toplevel(root)
    dialog.title("글꼴")
    dialog.resizable(False, False)
    dialog.transient(root)

    ttk.Label(
        dialog,
        text="글꼴"
    ).grid(
        row=0,
        column=0,
        padx=10,
        pady=10
    )

    # 컴퓨터에 설치된 글꼴 목록 표시
    family_box = ttk.Combobox(
        dialog,
        values=sorted(set(tkfont.families(root))),
        state="readonly",
        width=28
    )

    family_box.set(display_font.actual("family"))

    family_box.grid(
        row=0,
        column=1,
        padx=10,
        pady=10
    )

    ttk.Label(
        dialog,
        text="기본 크기(8~72)"
    ).grid(
        row=1,
        column=0,
        padx=10,
        pady=10
    )

    size_var = tk.StringVar(
        value=str(base_font_size)
    )

    # 글꼴 크기 입력
    ttk.Spinbox(
        dialog,
        from_=8,
        to=72,
        textvariable=size_var,
        width=8
    ).grid(
        row=1,
        column=1,
        padx=10,
        pady=10,
        sticky="w"
    )

    # 선택한 글꼴 적용
    def apply_selection():

        global base_font_size

        try:
            size = int(size_var.get())

            if not 8 <= size <= 72:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "크기 오류",
                "8~72의 정수를 입력해 주세요.",
                parent=dialog
            )
            return

        base_font_size = size

        display_font.configure(
            family=family_box.get()
        )

        apply_font()

        dialog.destroy()
        text.focus_set()

    # 적용 버튼
    ttk.Button(
        dialog,
        text="적용",
        command=apply_selection
    ).grid(
        row=2,
        column=0,
        padx=10,
        pady=10
    )

    # 취소 버튼
    ttk.Button(
        dialog,
        text="취소",
        command=dialog.destroy
    ).grid(
        row=2,
        column=1,
        padx=10,
        pady=10
    )

    dialog.grab_set()


# 자동 줄바꿈 설정
def toggle_wrap():

    text.config(
        wrap="word" if wrap_enabled.get() else "none"
    )


# ---------- 보기 기능 ----------

# 글자 확대
def zoom_in():

    global zoom_percent

    zoom_percent = min(
        300,
        zoom_percent + 10
    )

    apply_font()


# 글자 축소
def zoom_out():

    global zoom_percent

    zoom_percent = max(
        50,
        zoom_percent - 10
    )

    apply_font()


# 확대 배율 초기화
def zoom_reset():

    global zoom_percent

    zoom_percent = 100

    apply_font()


# ---------- 창과 입력 영역 ----------

if __name__ == "__main__":

    # 메인 프로그램 창 생성
    root = tk.Tk()

    root.geometry("850x550")

    # 현재 파일 경로 초기화
    current_file = None

    # 기본 글꼴 크기
    base_font_size = 12

    # 확대 배율
    zoom_percent = 100

    # 자동 줄바꿈 기본값
    wrap_enabled = tk.BooleanVar(value=True)

    # 기본 글꼴 복사
    display_font = tkfont.nametofont(
        "TkTextFont"
    ).copy()

    display_font.configure(
        size=base_font_size
    )

    # 편집 영역 생성
    editor_frame = tk.Frame(root)

    editor_frame.pack(
        fill=tk.BOTH,
        expand=True
    )

    editor_frame.rowconfigure(
        0,
        weight=1
    )

    editor_frame.columnconfigure(
        0,
        weight=1
    )

    # 글을 입력하는 Text 위젯
    text = tk.Text(
        editor_frame,
        wrap="word",
        font=display_font
    )

    text.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    # 세로 스크롤바
    y_scroll = ttk.Scrollbar(
        editor_frame,
        orient="vertical",
        command=text.yview
    )

    y_scroll.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    # 가로 스크롤바
    x_scroll = ttk.Scrollbar(
        editor_frame,
        orient="horizontal",
        command=text.xview
    )

    x_scroll.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    # 스크롤바와 Text 위젯 연결
    text.configure(
        yscrollcommand=y_scroll.set,
        xscrollcommand=x_scroll.set
    )

    # 처음 실행할 때 수정되지 않은 상태로 설정
    text.edit_modified(False)


    # ---------- 메뉴 구성 ----------

    # 메뉴 바 생성
    menu_bar = tk.Menu(root)

    root.config(
        menu=menu_bar
    )


    # 파일 메뉴
    file_menu = tk.Menu(
        menu_bar,
        tearoff=0
    )

    menu_bar.add_cascade(
        label="파일",
        menu=file_menu
    )

    file_menu.add_command(
        label="새파일",
        command=new_file
    )

    file_menu.add_command(
        label="열기",
        command=open_file
    )

    file_menu.add_command(
        label="저장",
        command=save_file
    )

    file_menu.add_separator()

    file_menu.add_command(
        label="종료",
        command=exit_program
    )


    # 편집 메뉴
    edit_menu = tk.Menu(
        menu_bar,
        tearoff=0
    )

    menu_bar.add_cascade(
        label="편집",
        menu=edit_menu
    )

    edit_menu.add_command(
        label="잘라내기",
        command=cut_text
    )

    edit_menu.add_command(
        label="복사",
        command=copy_text
    )

    edit_menu.add_command(
        label="붙여넣기",
        command=paste_text
    )

    # 찾기 및 바꾸기 메뉴 추가
    edit_menu.add_separator()

    edit_menu.add_command(
        label="찾기 및 바꾸기",
        command=open_find_dialog
    )


    # 서식 메뉴
    format_menu = tk.Menu(
        menu_bar,
        tearoff=0
    )

    menu_bar.add_cascade(
        label="서식",
        menu=format_menu
    )

    format_menu.add_command(
        label="글꼴",
        command=change_font
    )

    format_menu.add_checkbutton(
        label="자동 줄바꿈",
        variable=wrap_enabled,
        command=toggle_wrap
    )


    # 보기 메뉴
    view_menu = tk.Menu(
        menu_bar,
        tearoff=0
    )

    menu_bar.add_cascade(
        label="보기",
        menu=view_menu
    )

    view_menu.add_command(
        label="확대",
        command=zoom_in
    )

    view_menu.add_command(
        label="축소",
        command=zoom_out
    )

    view_menu.add_command(
        label="기본 배율(100%)",
        command=zoom_reset
    )


    # ---------- 창 이벤트 연결 ----------

    # 창 오른쪽 위 X 버튼을 눌렀을 때 종료 함수 실행
    root.protocol(
        "WM_DELETE_WINDOW",
        exit_program
    )


    # ---------- 프로그램 초기 실행 ----------

    # 창 제목 설정
    update_title()

    # 편집창에 커서 배치
    text.focus_set()

    # 프로그램 실행
    root.mainloop()
