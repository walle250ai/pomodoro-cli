#!/usr/bin/env python3
import time
import sys
import signal
import os

WORK_MINUTES = 25
REST_MINUTES = 5


class PomodoroTimer:
    def __init__(self):
        self.start_time = None
        self.total_work_seconds = 0
        self.total_rest_seconds = 0
        self.current_session = None
        self.current_seconds = 0

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def clear_line(self):
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        sys.stdout.flush()

    def display_timer(self, session_type, remaining_seconds):
        label = "工作" if session_type == "work" else "休息"
        remaining = self.format_time(remaining_seconds)
        elapsed = self.format_time(self.current_seconds)
        bar_length = 30
        total = WORK_MINUTES * 60 if session_type == "work" else REST_MINUTES * 60
        progress = (self.current_seconds / total) if total > 0 else 0
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        line = f"\r【{label}时间】 {elapsed} / {self.format_time(total)} | 剩余: {remaining} | {bar}"
        sys.stdout.write(line)
        sys.stdout.flush()

    def play_sound(self):
        import subprocess
        import shutil

        if sys.platform == 'win32':
            import winsound
            winsound.Beep(1000, 500)
            winsound.Beep(800, 500)
            winsound.Beep(1000, 500)
        elif sys.platform == 'darwin':
            if shutil.which('afplay'):
                try:
                    for _ in range(3):
                        subprocess.run(
                            ['afplay', '/System/Library/Sounds/Glass.aiff'],
                            check=False,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        time.sleep(0.15)
                    return
                except Exception:
                    pass
        else:
            sound_files = [
                '/usr/share/sounds/alsa/Front_Center.wav',
                '/usr/share/sounds/Yaru/stereo/bell.oga',
                '/usr/share/sounds/purple/alert.wav',
                '/usr/share/sounds/freedesktop/stereo/bell.oga',
            ]

            if shutil.which('paplay'):
                for sound_file in sound_files:
                    if os.path.exists(sound_file):
                        try:
                            for _ in range(3):
                                subprocess.run(
                                    ['paplay', sound_file],
                                    check=False,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL
                                )
                                time.sleep(0.15)
                            return
                        except Exception:
                            continue

            if shutil.which('aplay'):
                for sound_file in sound_files:
                    if os.path.exists(sound_file):
                        try:
                            for _ in range(3):
                                subprocess.run(
                                    ['aplay', '-q', sound_file],
                                    check=False,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL
                                )
                                time.sleep(0.15)
                            return
                        except Exception:
                            continue

            if shutil.which('play'):
                try:
                    for freq in [800, 600, 800]:
                        subprocess.run(
                            ['play', '-n', 'synth', '0.3', 'sine', str(freq), 'vol', '0.3'],
                            check=False,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        time.sleep(0.05)
                    return
                except Exception:
                    pass

        print('\a', end='', flush=True)
        time.sleep(0.1)
        print('\a', end='', flush=True)
        time.sleep(0.1)
        print('\a', end='', flush=True)

    def run_session(self, minutes, session_type):
        self.current_session = session_type
        total_seconds = minutes * 60
        self.current_seconds = 0
        self.start_time = time.time()

        try:
            while self.current_seconds < total_seconds:
                remaining = total_seconds - self.current_seconds
                self.display_timer(session_type, remaining)
                time.sleep(1)
                self.current_seconds += 1

            if session_type == "work":
                self.total_work_seconds += total_seconds
            else:
                self.total_rest_seconds += total_seconds

            self.clear_line()
            label = "工作" if session_type == "work" else "休息"
            print(f"✨ {label}阶段完成！已完成: {self.format_time(total_seconds)}")
            self.play_sound()
            
        except KeyboardInterrupt:
            if self.current_session == "work":
                self.total_work_seconds += self.current_seconds
            else:
                self.total_rest_seconds += self.current_seconds
            raise

    def show_stats(self):
        self.clear_line()
        print("\n" + "=" * 50)
        print("📊 本次专注统计")
        print("=" * 50)
        print(f"工作时间: {self.format_time(self.total_work_seconds)}")
        print(f"休息时间: {self.format_time(self.total_rest_seconds)}")
        print(f"总计时间: {self.format_time(self.total_work_seconds + self.total_rest_seconds)}")
        
        work_minutes = self.total_work_seconds // 60
        work_sessions = work_minutes // WORK_MINUTES
        extra_minutes = work_minutes % WORK_MINUTES
        
        if work_sessions > 0 and extra_minutes > 0:
            print(f"完成番茄钟: {work_sessions} 个完整周期 + {extra_minutes} 分钟")
        elif work_sessions > 0:
            print(f"完成番茄钟: {work_sessions} 个完整周期")
        elif extra_minutes > 0:
            print(f"专注时长: {extra_minutes} 分钟")
        
        print("=" * 50)

    def start(self):
        print("🍅 番茄钟启动！")
        print(f"   工作时间: {WORK_MINUTES} 分钟")
        print(f"   休息时间: {REST_MINUTES} 分钟")
        print("   按 Ctrl+C 中断并查看统计\n")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"\n--- 第 {cycle_count} 轮 ---")
                print(f"开始工作 ({WORK_MINUTES} 分钟)...")
                time.sleep(0.5)
                self.run_session(WORK_MINUTES, "work")
                
                print(f"\n开始休息 ({REST_MINUTES} 分钟)...")
                time.sleep(0.5)
                self.run_session(REST_MINUTES, "rest")
                
        except KeyboardInterrupt:
            self.show_stats()
            print("👋 番茄钟已结束，下次再见！")
            sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal.default_int_handler)
    
    timer = PomodoroTimer()
    timer.start()


if __name__ == "__main__":
    main()
