# obsidian_daily.py
"""
Obsidian 日记助手
功能：
- 创建/覆盖当天 YYYYMMDD.md（模板 + YAML frontmatter）
- 抽取本地 Outlook 今日日程写入文件
- 扫描目录所有 .md（读取 YAML）生成年度热力图（Emotion/Appetite/Confidence）
"""

import os
import sys
import pathlib
from datetime import datetime, date, time, timedelta
import logging
import frontmatter
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Outlook 用
try:
    import win32com.client
except Exception:
    win32com = None

# GUI 弹窗用于覆盖确认（可回落到命令行）
try:
    import tkinter as tk
    from tkinter import messagebox
    tk_available = True
except Exception:
    tk_available = False

logging.basicConfig(level=logging.INFO)
DEFAULT_DIR = r"D:\jianguo\我的坚果云\obsidian\Personal\2026"
EMOTIONS = ["开心😊","幸福🥰","兴奋🤩","自豪😎","平静😐","痛苦😫","悲伤☹️","疲惫😭","生病😷","气愤😡","成就🥂","心流🧘"]
APPETITES = ["食欲稳定🥗","想吃辣的🌶","想吃碳水🍜"]
CONFIDENCES = ["自信满满","自我怀疑"]

def ask_yes_no(prompt, title="确认"):
    # 先尝试弹窗
    if tk_available:
        root = tk.Tk()
        root.withdraw()
        res = messagebox.askyesno(title, prompt)
        root.destroy()
        return res
    # 回落到控制台
    while True:
        r = input(f"{prompt} (y/n): ").strip().lower()
        if r in ('y','yes'): return True
        if r in ('n','no'): return False

def ensure_dir(path: pathlib.Path):
    if not path.exists():
        logging.info(f"目录 {path} 不存在，尝试创建...")
        try:
            path.mkdir(parents=True, exist_ok=True)
            logging.info("目录创建成功。")
        except Exception as e:
            logging.error(f"无法创建目录：{e}")
            raise

def get_today_filename(base_dir: pathlib.Path, target_date: date):
    name = target_date.strftime("%Y%m%d") + ".md"
    return base_dir / name

def prompt_choice(prompt, options, default_index=0):
    print(f"{prompt}")
    for i, opt in enumerate(options, 1):
        default_mark = " (默认)" if i-1 == default_index else ""
        print(f"  {i}. {opt}{default_mark}")
    while True:
        r = input(f"选择(回车默认 {default_index+1}): ").strip()
        if r == "":
            return options[default_index]
        if r.isdigit():
            idx = int(r)-1
            if 0 <= idx < len(options):
                return options[idx]
        print("请输入有效数字。")

def fetch_outlook_events_for_today():
    events = []
    if win32com is None:
        logging.warning("pywin32 未安装或不可用，跳过 Outlook 集成。")
        return events
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        ns = outlook.GetNamespace("MAPI")
        calendar = ns.GetDefaultFolder(9)  # olFolderCalendar
        items = calendar.Items
        items.IncludeRecurrences = True
        items.Sort("[Start]")
        today = date.today()
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        # Outlook 的 Restrict 需要特定格式
        restr = "[Start] >= '{}' AND [Start] <= '{}'".format(start.strftime("%m/%d/%Y %I:%M %p"),
                                                             end.strftime("%m/%d/%Y %I:%M %p"))
        restricted = items.Restrict(restr)
        for it in restricted:
            try:
                start_time = it.Start
                end_time = it.End
                subj = str(it.Subject)
                events.append({
                    "subject": subj,
                    "start": start_time,
                    "end": end_time
                })
            except Exception:
                continue
    except Exception as e:
        logging.warning(f"获取 Outlook 日程失败：{e}")
    return events

def write_markdown_file(path: pathlib.Path, meta: dict, body: str):
    post = frontmatter.Post(body, **meta)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
        logging.info(f"写入文件 {path}")
    except Exception as e:
        logging.error(f"写文件失败：{e}")
        raise

def build_template(date_dt: datetime, location, emotion, confidence, appetite, diary_text, exercise_text, events):
    # YAML metadata, 注意 field 名称用简洁 key
    meta = {
        "Appetite": appetite,
        "Confidence": confidence,
        "Date": date_dt.isoformat(sep=' '),
        "Emotion": emotion,
        "Location": location
    }
    lines = []
    lines.append("---")
    for key, value in meta.items():
        # Properly format YAML fields
        if isinstance(value, str) and any(c in value for c in ['\"', ':']):
            value = f'"{value}"'  # Add quotes if special characters exist
        lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")
    lines.append("## 今日日程")
    lines.append("")
    if events:
        for e in events:
            st = e["start"].strftime("%H:%M")
            ed = e["end"].strftime("%H:%M")
            lines.append(f"- {st}-{ed}  {e['subject']}")
    else:
        lines.append("")
    lines.append("")
    lines.append("## 今日随笔")
    lines.append("")
    lines.append(diary_text or "")
    lines.append("")
    lines.append("## 运动情况")
    lines.append("")
    lines.append(exercise_text or "")
    lines.append("")
    content = "\n".join(lines)
    return meta, content

def scan_folder_for_metadata(base_dir: pathlib.Path):
    records = []
    for p in base_dir.glob("*.md"):
        try:
            post = frontmatter.load(p)
            # 优先寻找 Date 元数据，回退使用文件名
            d = post.metadata.get("Date")
            if d:
                try:
                    dt = datetime.fromisoformat(d)
                    day = dt.date()
                except Exception:
                    # 如果 Date 是纯日期字符串，尝试 parse
                    try:
                        day = datetime.strptime(d, "%Y-%m-%d").date()
                    except Exception:
                        # fallback filename
                        day = None
            else:
                day = None
            if day is None:
                # 使用文件名 YYYYMMDD.md
                try:
                    stem = p.stem
                    day = datetime.strptime(stem, "%Y%m%d").date()
                except Exception:
                    continue
            records.append({
                "date": day,
                "Emotion": post.metadata.get("Emotion"),
                "Appetite": post.metadata.get("Appetite"),
                "Confidence": post.metadata.get("Confidence")
            })
        except Exception:
            continue
    return records

# heatmap helper
from matplotlib.colors import ListedColormap, BoundaryNorm

def make_category_heatmap(records, year, field, out_path: pathlib.Path):
    # records: list of dict with 'date' and field
    # Build map date->category
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    # map categories to ints
    cats = sorted({r[field] for r in records if r[field]})
    cat_to_int = {c: i for i, c in enumerate(cats)}
    # Prepare canvas
    first_sunday = start_date - timedelta(days=(start_date.weekday() + 1) % 7)
    num_weeks = ((end_date - first_sunday).days // 7) + 1
    mat = np.full((7, num_weeks), np.nan)
    # fill
    for r in records:
        d = r["date"]
        if d.year != year: continue
        week_idx = (d - first_sunday).days // 7
        row = (d.weekday() + 1) % 7  # Sunday=0
        val = r.get(field)
        if val in cat_to_int:
            mat[row, week_idx] = cat_to_int[val]
    # plot
    cmap_colors = plt.get_cmap("tab20").colors
    cmap = ListedColormap(cmap_colors[:max(1, len(cats))])
    norm = BoundaryNorm(np.arange(-0.5, len(cats)+0.5, 1), cmap.N)
    fig, ax = plt.subplots(figsize=(min(18, num_weeks*0.25), 3))
    ax.imshow(mat, cmap=cmap, norm=norm, aspect="auto", interpolation='none')
    ax.set_yticks(range(7))
    ax.set_yticklabels(["Sun","Mon","Tue","Wed","Thu","Fri","Sat"])
    ax.set_xticks([])
    ax.set_title(f"{year} - {field}")
    # legend
    handles = [plt.Rectangle((0,0),1,1, color=cmap(i)) for i in range(len(cats))]
    ax.legend(handles, cats, bbox_to_anchor=(1.01,1), loc='upper left')
    plt.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    logging.info(f"保存热力图 {out_path}")

def generate_all_heatmaps(base_dir: pathlib.Path, year: int):
    records = scan_folder_for_metadata(base_dir)
    if not records:
        logging.info("没有找到元数据记录，跳过热力图。")
        return
    out_dir = base_dir / "heatmaps"
    out_dir.mkdir(exist_ok=True)
    for field in ("Emotion","Appetite","Confidence"):
        out_path = out_dir / f"{year}_{field}.png"
        make_category_heatmap(records, year, field, out_path)
    logging.info("热力图生成完毕，保存在 heatmaps 子目录。")

def main():
    base_dir_input = input(f"日记目录（回车默认 {DEFAULT_DIR}）: ").strip()
    base_dir = pathlib.Path(base_dir_input or DEFAULT_DIR)
    try:
        ensure_dir(base_dir)
    except Exception as e:
        print(f"目录不可用: {e}")
        sys.exit(1)

    today = date.today()
    target_file = get_today_filename(base_dir, today)
    if target_file.exists():
        ok = ask_yes_no(f"文件 {target_file.name} 已存在，是否覆盖？", title="覆盖确认")
        if not ok:
            print("取消操作。")
            return

    # 交互输入
    location = input("Location（回车使用默认 '东涌镇,中国,广东省,广州市 南沙区'）: ").strip() or "东涌镇,中国,广东省,广州市 南沙区"
    emotion = prompt_choice("请选择 Emotion:", EMOTIONS, default_index=0)
    appetite = prompt_choice("请选择 Appetite:", APPETITES, default_index=0)
    confidence = prompt_choice("请选择 Confidence:", CONFIDENCES, default_index=0)
    diary_text = input("请输入今日随笔（回车留空，结束按回车）:\n")
    exercise_text = input("请输入运动情况（回车留空）:\n")

    events = fetch_outlook_events_for_today()
    meta, content = build_template(datetime.now(), location, emotion, confidence, appetite, diary_text, exercise_text, events)
    # frontmatter library will place metadata between --- and ---
    try:
        write_markdown_file(target_file, meta, content)
    except Exception as e:
        print(f"写入失败: {e}")
        return

    # 生成热力图（询问）
    if ask_yes_no("是否生成年度热力图并保存到子目录 heatmaps？"):
        try:
            year = today.year
            generate_all_heatmaps(base_dir, year)
            print("热力图已生成（heatmaps 子目录）。")
        except Exception as e:
            print(f"生成热力图失败: {e}")

if __name__ == "__main__":
    main()