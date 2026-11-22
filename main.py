"""A silent, one-minute Python animation about Ocholla James and coding."""

import math
import random
import struct
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import wave
from pathlib import Path

try:
    import winsound
except ImportError:
    winsound = None


WIDTH, HEIGHT = 1280, 720
DURATION = 60
SCORE_FILE = Path(__file__).resolve().parent / "coding_theme.wav"


def make_original_theme(filename):
    """Create an original, upbeat coding theme using Python's standard library."""
    sample_rate = 11025
    beat = 60 / 92
    chords = (
        (130.81, 164.81, 196.00, 261.63),
        (110.00, 130.81, 164.81, 220.00),
        (87.31, 130.81, 174.61, 220.00),
        (98.00, 123.47, 146.83, 196.00),
    )
    roots = (65.41, 55.00, 43.65, 49.00)
    melody = (523.25, 587.33, 659.25, 783.99, 659.25, 587.33, 523.25, 392.00)
    samples = bytearray()
    for sample in range(sample_rate * DURATION):
        seconds = sample / sample_rate
        chord_index = int(seconds / (beat * 8)) % len(chords)
        chord = chords[chord_index]
        beat_number = int(seconds / beat)
        beat_phase = seconds % beat
        pad = sum(math.sin(math.tau * note * seconds) for note in chord) * 0.035
        bass = math.sin(math.tau * roots[chord_index] * seconds) * 0.12
        lead = math.sin(math.tau * melody[beat_number % len(melody)] * seconds) * math.exp(-beat_phase * 3.5) * 0.18
        kick_phase = seconds % (beat * 2)
        kick = math.sin(math.tau * 48 * kick_phase) * math.exp(-kick_phase * 20) * 0.07
        fade = max(0.0, min(1.0, seconds / 1.5, (DURATION - seconds) / 2.0))
        value = max(-1.0, min(1.0, (pad + bass + lead + kick) * fade))
        samples.extend(struct.pack("<h", int(value * 32767 * 0.58)))
    with wave.open(str(filename), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(samples)


class Film:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Code in My Heart | Ocholla James")
        self.root.geometry("1280x720")
        self.root.minsize(960, 600)
        self.root.configure(bg="#070b15")
        self.canvas = tk.Canvas(self.root, bg="#080e1b", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.elapsed = 0.0
        self.finished = False
        self.last_tick = time.monotonic()
        self.paused = False
        self.muted = False
        self.closing = False
        self.score_generating = False
        self.stars = [(random.randint(0, WIDTH), random.randint(35, HEIGHT - 35), random.choice((1, 1, 2))) for _ in range(115)]
        self.root.bind("<space>", self.toggle_pause)
        self.root.bind("<Escape>", self.close)
        self.root.bind("r", self.restart)
        self.root.bind("R", self.restart)
        self.root.bind("m", self.toggle_mute)
        self.root.bind("M", self.toggle_mute)
        self.canvas.bind("<Configure>", self.draw_background)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.draw_background()
        self.root.after(200, self.start_sound)
        self.root.after(200, self.tick)

    def start_sound(self):
        if winsound is None or self.muted or self.closing:
            return
        if SCORE_FILE.exists():
            try:
                winsound.PlaySound(str(SCORE_FILE), winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception:
                pass
        elif not self.score_generating:
            self.score_generating = True
            threading.Thread(target=self.create_and_play_theme, daemon=True).start()

    def create_and_play_theme(self):
        try:
            make_original_theme(SCORE_FILE)
            if not self.muted and not self.closing and winsound is not None:
                winsound.PlaySound(str(SCORE_FILE), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass
        finally:
            self.score_generating = False

    def stop_sound(self):
        if winsound is not None:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass

    def close(self, _event=None):
        self.closing = True
        self.stop_sound()
        self.root.destroy()

    def toggle_pause(self, _event=None):
        self.paused = not self.paused
        self.last_tick = time.monotonic()

    def restart(self, _event=None):
        self.elapsed = 0.0
        self.finished = False
        self.last_tick = time.monotonic()
        self.stop_sound()
        if not self.muted:
            self.start_sound()

    def toggle_mute(self, _event=None):
        self.muted = not self.muted
        if self.muted:
            self.stop_sound()
        else:
            self.start_sound()

    def draw_background(self, _event=None):
        self.canvas.delete("background")
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        bands = 70
        top = (7, 12, 24)
        bottom = (20, 24, 48)
        for band in range(bands):
            ratio = band / max(bands - 1, 1)
            color = "#%02x%02x%02x" % tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
            x1 = width * band / bands
            x2 = width * (band + 1) / bands + 1
            self.canvas.create_rectangle(x1, 0, x2, height, fill=color, outline="", tags="background")
        scale = min(width / WIDTH, height / HEIGHT)
        ox = (width - WIDTH * scale) / 2
        oy = (height - HEIGHT * scale) / 2
        for x, y, size in self.stars:
            self.canvas.create_oval(ox + x * scale, oy + y * scale, ox + (x + size) * scale,
                                    oy + (y + size) * scale, fill="#7895b5", outline="", tags="background")
        for y in (48, HEIGHT - 48):
            self.canvas.create_rectangle(0, oy + y * scale, width, oy + (y + 1) * scale,
                                         fill="#59657b", outline="", tags="background")

    def transform(self):
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        scale = min(width / WIDTH, height / HEIGHT)
        offset_x = (width - WIDTH * scale) / 2
        offset_y = (height - HEIGHT * scale) / 2
        return scale, offset_x, offset_y

    def point(self, x, y, scale, ox, oy):
        return ox + x * scale, oy + y * scale

    def text(self, x, y, value, size, color, scale, ox, oy, bold=False, anchor="center", family="Segoe UI"):
        px, py = self.point(x, y, scale, ox, oy)
        self.canvas.create_text(px + 2 * scale, py + 3 * scale, text=value,
                                fill="#03060c", font=(family, max(8, int(size * scale)), "bold" if bold else "normal"),
                                anchor=anchor, tags="frame")
        self.canvas.create_text(px, py, text=value,
                                fill=color, font=(family, max(8, int(size * scale)), "bold" if bold else "normal"),
                                anchor=anchor, tags="frame")

    def caption(self, main, sub, scale, ox, oy):
        self.text(WIDTH / 2, 565, main, 28, "#f4f6fc", scale, ox, oy, bold=True)
        self.text(WIDTH / 2, 607, sub, 17, "#a9b7ce", scale, ox, oy)

    def flower(self, cx, cy, bloom, scale, ox, oy, size=1.0):
        center_x, center_y = self.point(cx, cy, scale, ox, oy)
        colors = ("#ff80b5", "#f777a9", "#ff9ac5", "#ee72a5", "#ff8abb", "#f77eae", "#ff9ac5", "#f46d9b")
        for index, color in enumerate(colors):
            progress = max(0.0, min(1.0, (bloom - index * 0.055) / 0.68))
            ease = progress * progress * (3 - 2 * progress)
            angle = index * math.pi / 4 + math.sin(self.elapsed * 0.42 + index) * 0.025
            shape = ((0, 0), (18, -12), (42, -18), (70, -12), (82, 0), (70, 12), (42, 18), (18, 12))
            coords = []
            for x, y in shape:
                x *= ease * size * scale
                y *= ease * size * scale
                coords.extend((center_x + x * math.cos(angle) - y * math.sin(angle),
                               center_y + x * math.sin(angle) + y * math.cos(angle)))
            if progress > 0:
                self.canvas.create_polygon(*coords, fill=color, outline="#ffd6e8", width=max(1, int(1.4 * scale)), tags="frame")
        core = max(1, int(15 * min(1, bloom) * size * scale))
        self.canvas.create_oval(center_x-core, center_y-core, center_x+core, center_y+core,
                                fill="#ffd978", outline="#fff4bf", width=max(1, int(2 * scale)), tags="frame")
        rng = random.Random(17)
        for index in range(32):
            theta = index * math.tau / 32 + self.elapsed * 0.38
            radius = (52 + 22 * math.sin(self.elapsed * 1.8 + index)) * max(0.2, min(1, bloom)) * size * scale
            x = center_x + math.cos(theta) * radius
            y = center_y + math.sin(theta) * radius * 0.72 + math.sin(self.elapsed * 2 + index) * 3 * scale
            dot = rng.choice((2, 3, 4)) * scale
            color = rng.choice(("#fff2a6", "#aaf7eb", "#ffe3f0", "#f3c8ff"))
            self.canvas.create_oval(x-dot, y-dot, x+dot, y+dot, fill=color, outline="", tags="frame")

    def assemble_words(self, value, center_x, target_y, progress, size, scale, ox, oy):
        """Fly each title character out from the flower with a tiny glitter trail."""
        font_size = max(10, int(size * scale))
        font = tkfont.Font(self.root, family="Segoe UI", size=font_size, weight="bold")
        widths = [font.measure(char) for char in value]
        cursor = center_x * scale - sum(widths) / 2
        target_xs = []
        for char_width in widths:
            target_xs.append(cursor + char_width / 2)
            cursor += char_width
        _, target_py = self.point(center_x, target_y, scale, ox, oy)
        for index, (char, target_px) in enumerate(zip(value, target_xs)):
            arrival = max(0.0, min(1.0, (progress - index * 0.035) / 0.68))
            ease = arrival * arrival * (3 - 2 * arrival)
            angle = index * 2.38 + 0.8
            start_px, start_py = self.point(640, 278, scale, ox, oy)
            start_px += math.cos(angle) * (40 + index * 5) * scale
            start_py += math.sin(angle) * 115 * scale
            px = start_px + (target_px - start_px) * ease
            py = start_py + (target_py - start_py) * ease
            if char != " ":
                self.canvas.create_text(px+2*scale, py+3*scale, text=char, fill="#163448",
                                        font=font, tags="frame")
                color = "#a8f2e3" if index % 3 == 1 else "#fff7f4"
                self.canvas.create_text(px, py, text=char, fill=color, font=font, tags="frame")
                if 0 < arrival < 1:
                    glow = 3 * scale
                    self.canvas.create_line(px-glow, py, px+glow, py, fill="#fff0a5", width=max(1, int(scale)), tags="frame")
                    self.canvas.create_line(px, py-glow, px, py+glow, fill="#fff0a5", width=max(1, int(scale)), tags="frame")

    def draw_dust(self, scale, ox, oy):
        for index in range(30):
            x = (index * 131 + self.elapsed * (15 + index % 7)) % WIDTH
            y = (index * 67 + 35 * math.sin(self.elapsed * 0.5 + index)) % HEIGHT
            px, py = self.point(x, y, scale, ox, oy)
            radius = (1.2 + (index % 3) * 0.5) * scale
            color = "#7297bd" if index % 2 else "#e9d6ad"
            self.canvas.create_oval(px-radius, py-radius, px+radius, py+radius,
                                    fill=color, outline="", tags="frame")

    def type_line(self, value, x, y, progress, size, color, scale, ox, oy, bold=False):
        count = max(0, min(len(value), int(len(value) * progress)))
        shown = value[:count]
        if progress < 1 and int(self.elapsed * 5) % 2 == 0:
            shown += "|"
        self.text(x, y, shown, size, color, scale, ox, oy, bold=bold)

    def draw_code_panel(self, progress, scale, ox, oy):
        x1, y1 = self.point(235, 190, scale, ox, oy)
        x2, y2 = self.point(1045, 470, scale, ox, oy)
        radius = 16 * scale
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#111a2b", outline="#35445d", width=2, tags="frame")
        self.canvas.create_oval(x1+14*scale, y1+15*scale, x1+24*scale, y1+25*scale, fill="#ff6f78", outline="", tags="frame")
        self.canvas.create_oval(x1+34*scale, y1+15*scale, x1+44*scale, y1+25*scale, fill="#f5c05e", outline="", tags="frame")
        self.canvas.create_oval(x1+54*scale, y1+15*scale, x1+64*scale, y1+25*scale, fill="#69d7a4", outline="", tags="frame")
        lines = [
            ("# Turning an idea into something useful", "#7e91ac"),
            ('name = "Ocholla James"', "#f4d28a"),
            ('university = "Kisii University"', "#f4d28a"),
            ('skill = "Python"', "#f4d28a"),
            ("while learning:", "#94bfff"),
            ("    build_with_purpose()", "#9ee8ca"),
        ]
        for index, (line, color) in enumerate(lines):
            reveal = max(0.0, min(1.0, (progress - index * 0.15) / 0.36))
            visible = line[:int(len(line) * reveal)]
            if visible:
                px, py = self.point(270, 245 + index * 34, scale, ox, oy)
                self.canvas.create_text(px, py, text=visible, fill=color,
                                        font=("Consolas", max(9, int(20 * scale))), anchor="w", tags="frame")

    def tick(self):
        now = time.monotonic()
        if not self.paused:
            self.elapsed += now - self.last_tick
        self.last_tick = now
        if self.elapsed >= DURATION and not self.finished:
            self.elapsed = float(DURATION)
            self.finished = True
            self.stop_sound()

        self.canvas.delete("frame")
        scale, ox, oy = self.transform()
        t = self.elapsed

        if t < 8:
            self.flower(640, 285, min(1, t / 4), scale, ox, oy, 1.05)
            self.assemble_words("LOVE CODING", WIDTH/2, 470, max(0, (t-0.5)/2.8), 58, scale, ox, oy)
            self.text(WIDTH/2, 535, "I start with a dream, one line at a time.", 20, "#aee9df", scale, ox, oy)
        elif t < 18:
            local = t - 8
            self.flower(1000, 340, 1, scale, ox, oy, 0.7)
            self.type_line("OCHOLLA JAMES", 305, 250, local/1.8, 53, "#ffffff", scale, ox, oy, True)
            self.type_line("Kisii University", 310, 335, (local-1)/1.8, 27, "#aee9df", scale, ox, oy, True)
            self.type_line("Computer Science Student", 310, 390, (local-2)/1.8, 23, "#c5d3e5", scale, ox, oy)
            self.type_line("Python Programmer", 310, 435, (local-3)/1.8, 23, "#c5d3e5", scale, ox, oy)
        elif t < 34:
            local = t - 18
            self.text(WIDTH/2, 130, "I LOVE BUILDING WITH PYTHON", 32, "#eaf0fb", scale, ox, oy, True)
            self.draw_code_panel(local / 8, scale, ox, oy)
            self.text(WIDTH/2, 525, "I build what I imagine; I make ideas shine.", 21, "#aee9df", scale, ox, oy)
        elif t < 46:
            local = t - 34
            self.text(WIDTH/2, 175, "LEARNING THROUGH EVERY CHALLENGE", 30, "#ffffff", scale, ox, oy, True)
            if local < 5:
                self.text(WIDTH/2, 300, "NameError: idea_not_yet_finished", 24, "#ff8991", scale, ox, oy, family="Consolas")
                self.text(WIDTH/2, 365, "When errors appear, I try once more.", 22, "#d3daea", scale, ox, oy)
            else:
                self.text(WIDTH/2, 300, "BUG FIXED  |  LESSON LEARNED", 26, "#8de1bd", scale, ox, oy, True)
                self.text(WIDTH/2, 365, "Each lesson helps my skills grow.", 22, "#d3daea", scale, ox, oy)
            self.flower(640, 495, min(1, local/4), scale, ox, oy, 0.52)
        elif t < 54:
            local = t - 46
            self.text(WIDTH/2, 155, "BUILD WITH PURPOSE", 42, "#ffffff", scale, ox, oy, True)
            self.flower(640, 355, 1, scale, ox, oy, 0.72)
            labels = (("IDEA", 290), ("PYTHON", 640), ("USEFUL TOOLS", 990))
            for index, (label, x) in enumerate(labels):
                appear = max(0, min(1, (local - index * 1.3) / 1.2))
                if appear:
                    color = ("#ffc979", "#85e4d4", "#f4f4ff")[index]
                    self.text(x, 535, label, 21, color, scale, ox, oy, True)
                    radius = (32 + 8 * math.sin(t * 3 + index)) * scale
                    px, py = self.point(x, 450, scale, ox, oy)
                    self.canvas.create_oval(px-radius, py-radius, px+radius, py+radius,
                                            outline=color, width=max(1, int(2*scale)), tags="frame")
        else:
            local = t - 54
            self.flower(640, 235, 1, scale, ox, oy, 0.62)
            self.type_line("LOVE CODING", WIDTH/2, 395, local/1.4, 43, "#ffffff", scale, ox, oy, True)
            self.text(WIDTH/2, 455, "OCHOLLA JAMES  |  KISII UNIVERSITY", 19, "#aee9df", scale, ox, oy, True)
            self.text(WIDTH/2, 491, "Computer Science Student  |  Python Programmer", 17, "#bac6d9", scale, ox, oy)
            self.text(WIDTH/2, 550, "I learn, I build, I solve real problems.", 17, "#aee9df", scale, ox, oy, True)

        self.draw_dust(scale, ox, oy)
        if self.paused:
            self.text(WIDTH/2, HEIGHT/2, "PAUSED  |  PRESS SPACE TO CONTINUE", 20, "#ffffff", scale, ox, oy, True)
        self.text(WIDTH/2, HEIGHT-20, "SPACE  PAUSE     R  RESTART     M  MUSIC     ESC  EXIT", 11, "#9aaac0", scale, ox, oy)
        self.root.after(33, self.tick)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Film().run()
