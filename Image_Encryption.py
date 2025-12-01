import os
from tkinter import Tk, StringVar, END
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image


# ---------- Core Image Logic (XOR + Pixel Swapping) ----------

def transform_image(input_path: str, output_path: str, key: int) -> None:
    """
    Transform image using:
    1) XOR on each RGB channel with the key
    2) Swapping pixel positions in each row based on the key

    This function is its own inverse.
    Calling it twice with the same key restores the original image.
    So it can be used for both encryption and decryption.
    """
    img = Image.open(input_path).convert("RGB")
    width, height = img.size
    pixels = img.load()

    key = key % 256  # keep key in byte range

    # 1) Color transform: XOR each channel with key
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            r ^= key
            g ^= key
            b ^= key

            pixels[x, y] = (r, g, b)

    # 2) Position transform: swap some pixel pairs in each row
    for y in range(height):
        for x in range(width // 2):
            if (x + y + key) % 2 == 0:
                x2 = width - 1 - x
                p1 = pixels[x, y]
                p2 = pixels[x2, y]
                pixels[x, y], pixels[x2, y] = p2, p1

    img.save(output_path)


# ---------- GUI App ----------

class ImageEncryptionApp:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Image Encryption Tool")
        self.root.geometry("650x350")
        self.root.resizable(False, False)

        # Set overall style
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Colors
        bg_color = "#0f172a"      # dark navy
        card_color = "#1f2937"   # slate
        accent_color = "#38bdf8" # sky blue
        text_color = "#e5e7eb"   # light gray

        self.root.configure(bg=bg_color)
        self.style.configure("TLabel", background=card_color, foreground=text_color, font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"))
        self.style.configure("Accent.TButton", background=accent_color, foreground="#020617")
        self.style.map("Accent.TButton",
                       background=[("active", "#0ea5e9")])

        # Variables
        self.image_path = StringVar()
        self.key_value = StringVar()
        self.mode = StringVar(value="encrypt")
        self.status_text = StringVar(value="© Gokul.")

        # Main container (card)
        card = ttk.Frame(self.root, padding=20, style="Card.TFrame")
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Custom style for card
        self.style.configure("Card.TFrame", background=card_color, relief="flat")

        # Title
        title_label = ttk.Label(
            card,
            text="Image Encryption Tool GUI",
            font=("Segoe UI Semibold", 18)
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="w")

        subtitle_label = ttk.Label(
            card,
            text="Pixel manipulation using XOR + position swapping\nUse the same key for encryption and decryption.",
            font=("Segoe UI", 9)
        )
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 15), sticky="w")

        # Image path row
        ttk.Label(card, text="Image File:").grid(row=2, column=0, sticky="w")

        self.entry_path = ttk.Entry(card, textvariable=self.image_path, width=45)
        self.entry_path.grid(row=2, column=1, padx=(8, 8), pady=5, sticky="w")

        browse_btn = ttk.Button(card, text="Browse", command=self.browse_file)
        browse_btn.grid(row=2, column=2, pady=5, sticky="e")

        # Key row
        ttk.Label(card, text="Key (Digit):").grid(row=3, column=0, sticky="w", pady=(10, 5))

        self.entry_key = ttk.Entry(card, textvariable=self.key_value, width=15)
        self.entry_key.grid(row=3, column=1, sticky="w", pady=(10, 5))

        # Buttons row
        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.grid(row=4, column=0, columnspan=3, pady=(20, 10))

        encrypt_btn = ttk.Button(
            btn_frame,
            text="Encrypt",
            style="Accent.TButton",
            command=self.encrypt_action,
            width=14
        )
        encrypt_btn.grid(row=0, column=0, padx=10)

        decrypt_btn = ttk.Button(
            btn_frame,
            text="Decrypt",
            command=self.decrypt_action,
            width=14
        )
        decrypt_btn.grid(row=0, column=1, padx=10)

        # Status bar
        status_label = ttk.Label(
            card,
            textvariable=self.status_text,
            font=("Segoe UI", 9)
        )
        status_label.grid(row=5, column=0, columnspan=3, pady=(10, 0), sticky="w")

    # ---------- GUI Callbacks ----------

    def browse_file(self):
        filetypes = [("Image Files", "*.png *.jpg *.jpeg *.bmp"), ("All Files", "*.*")]
        filename = filedialog.askopenfilename(title="Select Image", filetypes=filetypes)
        if filename:
            self.image_path.set(filename)
            self.status_text.set("Selected image: " + os.path.basename(filename))

    def validate_inputs(self):
        path = self.image_path.get().strip()
        key_str = self.key_value.get().strip()

        if not path:
            messagebox.showerror("Error", "Please select an image file.")
            return None, None

        if not os.path.isfile(path):
            messagebox.showerror("Error", "File not found. Please check the path.")
            return None, None

        if not key_str:
            messagebox.showerror("Error", "Please enter a numeric key.")
            return None, None

        if not key_str.lstrip("-").isdigit():
            messagebox.showerror("Error", "Key must be a valid integer.")
            return None, None

        key = int(key_str)
        return path, key

    def encrypt_action(self):
        path, key = self.validate_inputs()
        if path is None:
            return

        base, ext = os.path.splitext(path)
        output_path = base + "_encrypted" + ext

        try:
            transform_image(path, output_path, key)
            self.status_text.set(f"Encrypted image saved as: {os.path.basename(output_path)}")
            messagebox.showinfo("Success", f"Image encrypted and saved as:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed:\n{e}")

    def decrypt_action(self):
        path, key = self.validate_inputs()
        if path is None:
            return

        base, ext = os.path.splitext(path)
        output_path = base + "_decrypted" + ext

        try:
            transform_image(path, output_path, key)
            self.status_text.set(f"Decrypted image saved as: {os.path.basename(output_path)}")
            messagebox.showinfo("Success", f"Image decrypted and saved as:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed:\n{e}")


def main():
    root = Tk()
    app = ImageEncryptionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
