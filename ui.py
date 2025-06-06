import tkinter as tk

class UI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Transcrição e Tradução em tempo real")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#E6F0FA")

        # Frame principal
        main_frame = tk.Frame(self.root, bg="#E6F0FA")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Frame para controles
        controls_frame = tk.Frame(main_frame, bg="#E6F0FA")
        controls_frame.pack(fill=tk.X, pady=(0, 20))

        # Canvas para o marcador de volume
        self.volume_canvas = tk.Canvas(
            controls_frame,
            width=200,
            height=20,
            bg="#ddd",
            bd=0,
            highlightthickness=0
        )
        self.volume_canvas.pack()
        self.volume_bar = self.volume_canvas.create_rectangle(0, 0, 0, 20, fill="#3498db")

        # Frame para as duas colunas de Transcrição e Tradução
        content_frame = tk.Frame(main_frame, bg="#E6F0FA")
        content_frame.pack(fill=tk.X)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        # Frame da Transcrição
        transcription_frame = tk.Frame(content_frame, bg="#E6F0FA")
        transcription_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        transcription_label = tk.Label(
            transcription_frame,
            text="Transcrição",
            font=("Arial", 12, "bold"),
            bg="#E6F0FA",
            fg="#2C3E50"
        )
        transcription_label.pack()

        self.transcription_text_area = tk.Text(
            transcription_frame,
            font=("Arial", 12, "bold"),
            bg="#fff",
            fg="#353b48",
            wrap=tk.WORD,
            bd=2,
            relief=tk.RIDGE,
            padx=10,
            pady=10,
            highlightthickness=0,
            state=tk.DISABLED,
        )
        self.transcription_text_area.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Frame da Tradução
        translation_frame = tk.Frame(content_frame, bg="#E6F0FA")
        translation_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        translation_label = tk.Label(
            translation_frame,
            text="Tradução",
            font=("Arial", 12, "bold"),
            bg="#E6F0FA",
            fg="#2C3E50"
        )
        translation_label.pack()

        self.translation_text_area = tk.Text(
            translation_frame,
            font=("Arial", 12, "bold"),
            bg="#fff",
            fg="#2F3640",
            wrap=tk.WORD,
            bd=2,
            relief=tk.RIDGE,
            padx=10,
            pady=10,
            highlightthickness=0,
            state=tk.DISABLED
        )
        self.translation_text_area.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def update_volume_bar(self, volume: float):
        volume = max(0.0, min(volume, 1.0))
        max_width = 200
        width = int(volume * max_width)
        self.volume_canvas.coords(self.volume_bar, 0, 0, width, 20)

    def update_transcription(self, text):
        self.transcription_text_area.config(state=tk.NORMAL)
        self.transcription_text_area.delete(1.0, tk.END)
        self.transcription_text_area.insert(tk.END, text)
        self.transcription_text_area.config(state=tk.DISABLED)
        self.transcription_text_area.see(tk.END)

    def update_translation(self, text):
        self.translation_text_area.config(state=tk.NORMAL)
        self.translation_text_area.delete(1.0, tk.END)
        self.translation_text_area.insert(tk.END, text)
        self.translation_text_area.config(state=tk.DISABLED)
        self.translation_text_area.see(tk.END)

    def run(self):
        self.root.mainloop()
