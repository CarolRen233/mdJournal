import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date
import pathlib
import frontmatter
import logging
from config import BASE_DIR

# 尝试导入tkcalendar，如果不可用则使用备用方案
try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False

# Constants
EMOTIONS = ["开心😊", "幸福🥰", "兴奋🤩", "自豪😎", "平静😐", "痛苦😫", "悲伤☹️", "疲惫😭", "生病😷", "气愤😡", "成就🥂", "心流🧘"]
APPETITES = ["食欲稳定🥗", "想吃辣的🌶", "想吃碳水🍜"]
CONFIDENCES = ["自信满满", "自我怀疑"]

# 为每个情绪选项定义颜色
EMOTION_COLORS = {
    "开心😊": "#FFD700",      # 金色
    "幸福🥰": "#FF69B4",      # 粉红色
    "兴奋🤩": "#FF4500",      # 橙红色
    "自豪😎": "#4169E1",      # 皇家蓝
    "平静😐": "#87CEEB",      # 天蓝色
    "痛苦😫": "#8B4513",      # 棕色
    "悲伤☹️": "#4682B4",      # 钢蓝色
    "疲惫😭": "#708090",      # 灰石色
    "生病😷": "#98FB98",      # 淡绿色
    "气愤😡": "#DC143C",      # 深红色
    "成就🥂": "#FFD700",      # 金色
    "心流🧘": "#9370DB"       # 中紫色
}

# 为每个食欲选项定义颜色
APPETITE_COLORS = {
    "食欲稳定🥗": "#90EE90",  # 浅绿色
    "想吃辣的🌶": "#FF6347",  # 番茄红
    "想吃碳水🍜": "#FFA500"   # 橙色
}

# 为每个自信选项定义颜色
CONFIDENCE_COLORS = {
    "自信满满": "#32CD32",    # 酸橙绿
    "自我怀疑": "#FFB6C1"     # 浅粉色
}

# Ensure the base directory exists
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=BASE_DIR / "diary_app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def write_frontmatter_file(filename, meta, body):
    """写入带 frontmatter 的 markdown 文件"""
    # 手动构建 frontmatter 格式
    frontmatter_content = "---\n"
    for key, value in meta.items():
        if value is not None:
            # 如果值包含特殊字符，用引号包裹
            if isinstance(value, str) and (':' in value or '"' in value or "'" in value):
                value = f'"{value}"'
            frontmatter_content += f"{key}: {value}\n"
    frontmatter_content += "---\n\n"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(frontmatter_content + body)

def save_diary(location, emotion, appetite, confidence, diary_text, selected_date):
    """保存日记到指定日期"""
    # 如果selected_date是date对象，转换为datetime
    if isinstance(selected_date, date):
        selected_date = datetime.combine(selected_date, datetime.min.time())
    
    filename = BASE_DIR / f"{selected_date.strftime('%Y%m%d')}.md"

    if filename.exists():
        if not messagebox.askyesno("覆盖确认", f"文件 {filename.name} 已存在，是否覆盖？"):
            return

    meta = {
        "Date": selected_date.isoformat(),
        "Location": location,
        "Emotion": emotion,
        "Confidence": confidence,
        "Appetite": appetite
    }

    body = diary_text

    write_frontmatter_file(filename, meta, body)

    messagebox.showinfo("成功", f"日记已保存到 {filename}")

def create_rounded_button(parent, text, command, bg_color="#4A154B", fg_color="white", width=15):
    """创建圆角按钮（Slack风格）"""
    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg_color,
        fg=fg_color,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        bd=0,
        padx=20,
        pady=10,
        cursor="hand2",
        width=width,
        activebackground="#350D36",
        activeforeground="white"
    )
    return button

def main():
    root = tk.Tk()
    root.title("日记")
    root.geometry("800x700")
    root.configure(bg="#F8F8F8")
    
    # Slack风格配色
    SLACK_PURPLE = "#4A154B"
    SLACK_PURPLE_DARK = "#350D36"
    SLACK_GREEN = "#2EB67D"
    BG_COLOR = "#F8F8F8"
    CARD_BG = "#FFFFFF"
    TEXT_COLOR = "#1D1C1D"
    BORDER_COLOR = "#E8E8E8"
    
    # 主容器
    main_frame = tk.Frame(root, bg=BG_COLOR, padx=30, pady=30)
    main_frame.pack(fill="both", expand=True)
    
    # 内容卡片容器
    content_frame = tk.Frame(main_frame, bg=BG_COLOR)
    content_frame.pack(fill="both", expand=True)
    
    # 左侧卡片 - 基本信息
    left_card = tk.Frame(
        content_frame,
        bg=CARD_BG,
        relief="flat",
        bd=0,
        padx=25,
        pady=25
    )
    left_card.pack(side="left", fill="both", expand=True, padx=(0, 15))
    
    # 右侧卡片 - 日记内容
    right_card = tk.Frame(
        content_frame,
        bg=CARD_BG,
        relief="flat",
        bd=0,
        padx=25,
        pady=25
    )
    right_card.pack(side="right", fill="both", expand=True, padx=(15, 0))
    
    # 日期选择
    date_label = tk.Label(
        left_card,
        text="📅 选择日期",
        font=("Segoe UI", 11, "bold"),
        bg=CARD_BG,
        fg=TEXT_COLOR,
        anchor="w"
    )
    date_label.pack(fill="x", pady=(0, 8))
    
    if HAS_TKCALENDAR:
        date_entry = DateEntry(
            left_card,
            width=20,
            background=SLACK_PURPLE,
            foreground="white",
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=("Segoe UI", 10)
        )
        date_entry.pack(fill="x", pady=(0, 20))
        
        # 添加日期选择后自动关闭日历的功能
        def close_calendar(event=None):
            """关闭日历下拉框"""
            try:
                # 尝试多种方法关闭日历
                if hasattr(date_entry, '_top_cal'):
                    top_cal = date_entry._top_cal
                    if top_cal and hasattr(top_cal, 'winfo_exists') and top_cal.winfo_exists():
                        top_cal.destroy()
                        date_entry._top_cal = None
                # 尝试通过_calendar属性关闭
                if hasattr(date_entry, '_calendar') and date_entry._calendar:
                    cal = date_entry._calendar
                    if hasattr(cal, 'master'):
                        top = cal.master
                        if top and hasattr(top, 'winfo_exists') and top.winfo_exists():
                            top.destroy()
            except Exception:
                pass
        
        # 绑定日期选择事件 - 当用户选择日期后自动关闭
        def on_date_selected(event=None):
            """日期选择后的回调"""
            # 延迟一点关闭，确保日期已经设置
            root.after(50, close_calendar)
        
        date_entry.bind("<<DateEntrySelected>>", on_date_selected)
    else:
        # 如果tkcalendar不可用，使用简单的日期输入
        date_frame = tk.Frame(left_card, bg=CARD_BG)
        date_frame.pack(fill="x", pady=(0, 20))
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry_widget = tk.Entry(
            date_frame,
            textvariable=date_var,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            bg="white",
            fg=TEXT_COLOR
        )
        date_entry_widget.pack(fill="x")
        date_entry = date_var
    
    # Location
    location_label = tk.Label(
        left_card,
        text="📍 位置",
        font=("Segoe UI", 11, "bold"),
        bg=CARD_BG,
        fg=TEXT_COLOR,
        anchor="w"
    )
    location_label.pack(fill="x", pady=(0, 8))
    
    location_entry = tk.Entry(
        left_card,
        width=30,
        font=("Segoe UI", 10),
        relief="solid",
        bd=1,
        bg="white",
        fg=TEXT_COLOR
    )
    location_entry.insert(0, "东涌镇,中国,广东省,广州市 南沙区")
    location_entry.pack(fill="x", pady=(0, 20))
    
    # Emotion
    emotion_label = tk.Label(
        left_card,
        text="😊 情绪",
        font=("Segoe UI", 11, "bold"),
        bg=CARD_BG,
        fg=TEXT_COLOR,
        anchor="w"
    )
    emotion_label.pack(fill="x", pady=(0, 8))
    
    emotion_var = tk.StringVar(value=EMOTIONS[0])
    emotion_frame = tk.Frame(left_card, bg=CARD_BG)
    emotion_frame.pack(fill="x", pady=(0, 15))
    
    # 创建情绪按钮网格（彩色版本）
    emotion_buttons = []
    for i, emotion in enumerate(EMOTIONS):
        row = i // 3
        col = i % 3
        # 获取该情绪对应的颜色
        emotion_color = EMOTION_COLORS.get(emotion, "#F8F8F8")
        is_selected = emotion_var.get() == emotion
        
        btn = tk.Button(
            emotion_frame,
            text=emotion,
            font=("Segoe UI", 9),
            relief="flat",
            bd=1,
            bg=emotion_color if is_selected else "#F0F0F0",
            fg="white" if is_selected else TEXT_COLOR,
            activebackground=emotion_color,
            activeforeground="white",
            cursor="hand2",
            padx=8,
            pady=6,
            command=lambda e=emotion: emotion_var.set(e)
        )
        btn.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
        emotion_buttons.append(btn)
    
    # 更新按钮样式函数（彩色版本）
    def update_emotion_buttons():
        for btn in emotion_buttons:
            emotion_text = btn.cget("text")
            emotion_color = EMOTION_COLORS.get(emotion_text, "#F8F8F8")
            if emotion_text == emotion_var.get():
                btn.config(bg=emotion_color, fg="white")
            else:
                btn.config(bg="#F0F0F0", fg=TEXT_COLOR)
    
    emotion_var.trace("w", lambda *args: update_emotion_buttons())
    emotion_frame.columnconfigure(0, weight=1)
    emotion_frame.columnconfigure(1, weight=1)
    emotion_frame.columnconfigure(2, weight=1)
    
    # Appetite
    appetite_label = tk.Label(
        left_card,
        text="🍽️ 食欲",
        font=("Segoe UI", 11, "bold"),
        bg=CARD_BG,
        fg=TEXT_COLOR,
        anchor="w"
    )
    appetite_label.pack(fill="x", pady=(0, 8))
    
    appetite_var = tk.StringVar(value=APPETITES[0])
    appetite_frame = tk.Frame(left_card, bg=CARD_BG)
    appetite_frame.pack(fill="x", pady=(0, 15))
    
    appetite_buttons = []
    for i, appetite in enumerate(APPETITES):
        appetite_color = APPETITE_COLORS.get(appetite, SLACK_GREEN)
        is_selected = appetite_var.get() == appetite
        
        btn = tk.Button(
            appetite_frame,
            text=appetite,
            font=("Segoe UI", 9),
            relief="flat",
            bd=1,
            bg=appetite_color if is_selected else "#F0F0F0",
            fg="white" if is_selected else TEXT_COLOR,
            activebackground=appetite_color,
            activeforeground="white",
            cursor="hand2",
            padx=12,
            pady=6,
            command=lambda a=appetite: appetite_var.set(a)
        )
        btn.pack(side="left", padx=4, fill="x", expand=True)
        appetite_buttons.append(btn)
    
    def update_appetite_buttons():
        for btn in appetite_buttons:
            appetite_text = btn.cget("text")
            appetite_color = APPETITE_COLORS.get(appetite_text, SLACK_GREEN)
            if appetite_text == appetite_var.get():
                btn.config(bg=appetite_color, fg="white")
            else:
                btn.config(bg="#F0F0F0", fg=TEXT_COLOR)
    
    appetite_var.trace("w", lambda *args: update_appetite_buttons())
    
    # Confidence
    confidence_label = tk.Label(
        left_card,
        text="💪 自信",
        font=("Segoe UI", 11, "bold"),
        bg=CARD_BG,
        fg=TEXT_COLOR,
        anchor="w"
    )
    confidence_label.pack(fill="x", pady=(0, 8))
    
    confidence_var = tk.StringVar(value=CONFIDENCES[0])
    confidence_frame = tk.Frame(left_card, bg=CARD_BG)
    confidence_frame.pack(fill="x", pady=(0, 20))
    
    confidence_buttons = []
    for i, confidence in enumerate(CONFIDENCES):
        confidence_color = CONFIDENCE_COLORS.get(confidence, SLACK_PURPLE)
        is_selected = confidence_var.get() == confidence
        
        btn = tk.Button(
            confidence_frame,
            text=confidence,
            font=("Segoe UI", 9),
            relief="flat",
            bd=1,
            bg=confidence_color if is_selected else "#F0F0F0",
            fg="white" if is_selected else TEXT_COLOR,
            activebackground=confidence_color,
            activeforeground="white",
            cursor="hand2",
            padx=12,
            pady=6,
            command=lambda c=confidence: confidence_var.set(c)
        )
        btn.pack(side="left", padx=4, fill="x", expand=True)
        confidence_buttons.append(btn)
    
    def update_confidence_buttons():
        for btn in confidence_buttons:
            confidence_text = btn.cget("text")
            confidence_color = CONFIDENCE_COLORS.get(confidence_text, SLACK_PURPLE)
            if confidence_text == confidence_var.get():
                btn.config(bg=confidence_color, fg="white")
            else:
                btn.config(bg="#F0F0F0", fg=TEXT_COLOR)
    
    confidence_var.trace("w", lambda *args: update_confidence_buttons())
    
    # 日记正文
    diary_label = tk.Label(
        right_card,
        text="✍️ 日记正文",
        font=("Segoe UI", 11, "bold"),
        bg=CARD_BG,
        fg=TEXT_COLOR,
        anchor="w"
    )
    diary_label.pack(fill="x", pady=(0, 8))
    
    diary_text = tk.Text(
        right_card,
        width=40,
        height=20,
        font=("Segoe UI", 10),
        relief="solid",
        bd=1,
        bg="white",
        fg=TEXT_COLOR,
        wrap="word",
        padx=10,
        pady=10
    )
    diary_text.pack(fill="both", expand=True, pady=(0, 20))
    
    # 按钮区域
    button_frame = tk.Frame(right_card, bg=CARD_BG)
    button_frame.pack(fill="x")
    
    def get_selected_date():
        """获取选中的日期"""
        try:
            if HAS_TKCALENDAR and hasattr(date_entry, 'get_date'):
                return date_entry.get_date()
            elif isinstance(date_entry, tk.StringVar):
                date_str = date_entry.get()
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                return date.today()
        except Exception as e:
            logging.error(f"Error getting date: {e}")
            return date.today()
    
    save_button = create_rounded_button(
        button_frame,
        "💾 保存日记",
        command=lambda: save_diary(
            location_entry.get(),
            emotion_var.get(),
            appetite_var.get(),
            confidence_var.get(),
            diary_text.get("1.0", "end").strip(),
            get_selected_date()
        ),
        bg_color=SLACK_PURPLE,
        width=18
    )
    save_button.pack(side="left")
    
    root.mainloop()

if __name__ == "__main__":
    main()