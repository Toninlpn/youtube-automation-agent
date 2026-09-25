"""Rend les calques texte (sous-titres, accroche, question finale) en PNG 1080x1920."""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

WHITE = (255, 255, 255, 255)
GOLD = (255, 198, 61, 255)
BLACK = (0, 0, 0, 255)

CAPTION_SIZE = 62
CAPTION_Y = 1360
CAPTION_MAX_W = 960
STROKE = 5


def font(size):
    return ImageFont.truetype(FONT_BOLD, size)


def tokenize(text, highlights):
    low = text.lower()
    spans = []
    for h in highlights:
        i = low.find(h.lower())
        while i != -1:
            s = i
            while s > 0 and text[s - 1].isalnum():
                s -= 1
            e = i + len(h)
            while e < len(text) and text[e].isalnum():
                e += 1
            spans.append((s, e))
            i = low.find(h.lower(), e)
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    words = []
    i = 0
    while i < len(text):
        if text[i] == " ":
            i += 1
            continue
        j = i
        while j < len(text) and text[j] != " ":
            j += 1
        hl = any(s <= i and j <= e for s, e in merged)
        words.append((text[i:j], hl))
        i = j
    return words


def wrap(words, fnt, draw, max_w):
    lines, cur, cur_w = [], [], 0
    space = draw.textlength(" ", font=fnt)
    for w, hl in words:
        ww = draw.textlength(w, font=fnt)
        add = ww if not cur else ww + space
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [(w, hl)], ww
        else:
            cur.append((w, hl))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, fnt, y_center, line_h, stroke, space_w):
    total = len(lines) * line_h
    y = y_center - total / 2 + (line_h - fnt.size) / 2
    for line in lines:
        widths = [draw.textlength(w, font=fnt) for w, _ in line]
        total_w = sum(widths) + space_w * (len(line) - 1)
        x = (T.W - total_w) / 2
        for (w, hl), ww in zip(line, widths):
            draw.text((x, y), w, font=fnt, fill=GOLD if hl else WHITE,
                      stroke_width=stroke, stroke_fill=BLACK)
            x += ww + space_w
        y += line_h


def draw_tracked(draw, xy, text, fnt, fill, stroke, stroke_fill, tracking=0.92):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += draw.textlength(ch, font=fnt) * tracking


def text_width_tracked(draw, text, fnt, tracking=0.92):
    return sum(draw.textlength(ch, font=fnt) for ch in text) * tracking


def render_block(lines_spec, out_path, y_center, size, max_w, stroke=STROKE):
    img = Image.new("RGBA", (T.W, T.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if lines_spec and isinstance(lines_spec[0][1], (int, float)):
        fonts = []
        for txt, sz, col in lines_spec:
            s = sz
            while s > 40 and text_width_tracked(d, txt, font(s)) > max_w:
                s -= 2
            fonts.append((txt, font(s), col))
        line_hs = [int(f.size * 1.34) for _, f, _ in fonts]
        total = sum(line_hs)
        y = y_center - total / 2
        for (txt, fnt, col), lh in zip(fonts, line_hs):
            tw = text_width_tracked(d, txt, fnt)
            draw_tracked(d, ((T.W - tw) / 2, y + (lh - fnt.size) / 2), txt, fnt,
                         GOLD if col == "gold" else WHITE, 7, BLACK)
            y += lh
    else:
        fnt = font(size)
        probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        space_w = probe.textlength(" ", font=fnt)
        line_h = int(size * 1.34)
        wrapped = []
        for text, highlights in lines_spec:
            for ln in wrap(tokenize(text, highlights), fnt, probe, max_w):
                wrapped.append(ln)
        draw_lines(d, wrapped, fnt, y_center, line_h, stroke, space_w)

    img.save(out_path)
    return out_path


def main():
    os.makedirs(T.WORK, exist_ok=True)
    wins = T.vo_windows()
    caps = T.caption_windows(wins)

    entries = []
    for i, (s, e, text) in enumerate(caps):
        hl = next(h for k, t, h in T.CAPTIONS if t == text)
        p = os.path.join(T.WORK, "cap_%02d.png" % i)
        render_block([(text, hl)], p, CAPTION_Y, CAPTION_SIZE, CAPTION_MAX_W)
        entries.append({"kind": "cap", "file": p, "start": s, "end": e, "text": text})

    for name, spec in (("hook", T.HOOK_TEXT), ("final", T.FINAL_TEXT)):
        p = os.path.join(T.WORK, "%s.png" % name)
        render_block(spec["lines"], p, spec["y"], 0, T.W - 120)
        entries.append({"kind": name, "file": p, "start": spec["start"], "end": spec["end"],
                        "text": " / ".join(l[0] for l in spec["lines"])})

    entries.sort(key=lambda x: x["start"])
    with open(os.path.join(T.WORK, "texts.json"), "w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=1)
    print("%d calques texte rendus" % len(entries))
    for e in entries:
        print("  %.2f-%.2f  %s" % (e["start"], e["end"], e["text"][:58]))


if __name__ == "__main__":
    main()
