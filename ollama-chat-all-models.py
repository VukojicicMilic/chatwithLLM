import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, Menu
import subprocess
import os
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image

def select_model():
    """Display a dropdown menu to select a model from Ollama."""
    def fetch_models():
        try:
            process = subprocess.run(
                ["ollama", "list"],
                text=True,
                capture_output=True
            )
            if process.returncode == 0:
                models = [line.split()[0] for line in process.stdout.strip().split("\n")]
                return models
            else:
                raise Exception(f"Error fetching models: {process.stderr.strip()}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch models: {str(e)}")
            return []

    def on_select_model():
        selected = model_var.get()
        if selected:
            root.destroy()
            main_app(selected)

    root = tk.Tk()
    root.title("Select Ollama Model")
    root.geometry("400x200")

    model_var = tk.StringVar(value="")
    models = fetch_models()

    if not models:
        tk.Label(root, text="No models found. Please check your Ollama setup.").pack(pady=20)
    else:
        tk.Label(root, text="Select a model to use:").pack(pady=10)
        model_menu = tk.OptionMenu(root, model_var, *models)
        model_menu.pack(pady=10)
        tk.Button(root, text="Select", command=on_select_model).pack(pady=10)

    root.mainloop()

def main_app(selected_model):
    class ChatApp:
        def __init__(self, root):
            self.root = root
            self.root.title(f"Chat with {selected_model}")
            self.root.geometry("1280x800")
            self.selected_model = selected_model

            self.chat_history = ""
            self.file_content = ""

            self.menu_bar = Menu(root)
            root.config(menu=self.menu_bar)

            file_menu = Menu(self.menu_bar, tearoff=0)
            file_menu.add_command(label="Upload Text File", command=self.upload_file)
            file_menu.add_command(label="Upload PDF File", command=self.upload_pdf)
            file_menu.add_command(label="Export Conversation (TXT)", command=self.export_conversation_txt)
            file_menu.add_command(label="Export Conversation (PDF)", command=self.export_conversation_pdf)
            file_menu.add_command(label="Exit", command=root.quit)
            self.menu_bar.add_cascade(label="File", menu=file_menu)

            self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Verdana", 12), state='disabled')
            self.chat_display.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

            self.input_frame = tk.Frame(root)
            self.input_frame.pack(fill=tk.X, padx=10, pady=10)

            self.user_input = tk.Entry(self.input_frame, font=("Verdana", 12), width=70)
            self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.user_input.bind("<Return>", lambda event: self.send_message())

            self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message, font=("Verdana", 12))
            self.send_button.pack(side=tk.RIGHT, padx=5)

        def update_chat_display(self, sender, message):
            self.chat_display.config(state='normal')
            tag = "user" if sender == "You" else "model"
            self.chat_display.insert(tk.END, f"{sender}: {message}\n", tag)
            self.chat_display.tag_config("user", foreground="blue")
            self.chat_display.tag_config("model", foreground="red")
            self.chat_display.config(state='disabled')
            self.chat_display.see(tk.END)

        def send_message(self):
            user_message = self.user_input.get()
            if not user_message.strip():
                return

            self.update_chat_display("You", user_message)
            self.user_input.delete(0, tk.END)

            response = self.query_ollama(user_message)
            if response:
                self.update_chat_display("Model", response)

        def query_ollama(self, prompt):
            try:
                input_text = self.file_content + "\n\nUser: " + prompt
                process = subprocess.run(
                    ["ollama", "run", self.selected_model],
                    input=input_text,
                    text=True,
                    capture_output=True
                )
                if process.returncode == 0:
                    return process.stdout.strip()
                else:
                    return f"Error: {process.stderr.strip()}"
            except Exception as e:
                return f"Error: {str(e)}"

        def upload_file(self):
            file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
            if file_path:
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        self.file_content = file.read()
                    messagebox.showinfo("File Uploaded", f"File '{os.path.basename(file_path)}' uploaded successfully.")
                    self.update_chat_display("System", f"File '{os.path.basename(file_path)}' content loaded. You can now chat about it.")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not read file: {str(e)}")

        def upload_pdf(self):
            file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
            if file_path:
                try:
                    pdf_reader = PdfReader(file_path)
                    pdf_text = ""
                    for page in pdf_reader.pages:
                        pdf_text += page.extract_text()

                    if not pdf_text.strip():
                        messagebox.showinfo("OCR Processing", "No text found in PDF. Starting OCR...")
                        pdf_text = self.ocr_pdf(file_path)

                    self.file_content = pdf_text
                    messagebox.showinfo("PDF Uploaded", f"PDF '{os.path.basename(file_path)}' processed successfully.")
                    self.update_chat_display("System", f"PDF '{os.path.basename(file_path)}' content loaded. You can now chat about it.")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not process PDF: {str(e)}")

        def ocr_pdf(self, file_path):
            try:
                images = convert_from_path(file_path)
                ocr_text = ""
                for image in images:
                    ocr_text += pytesseract.image_to_string(image)
                return ocr_text
            except Exception as e:
                raise Exception(f"OCR failed: {str(e)}")

        def export_conversation_txt(self):
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(self.chat_display.get("1.0", tk.END).strip())
                    messagebox.showinfo("Export Successful", f"Conversation saved to '{file_path}'.")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save conversation: {str(e)}")

        def export_conversation_pdf(self):
            txt_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
            if txt_path:
                try:
                    with open(txt_path, "w", encoding="utf-8") as file:
                        file.write(self.chat_display.get("1.0", tk.END).strip())
                    pdf_path = txt_path.replace(".txt", ".pdf")
                    subprocess.run(["pandoc", txt_path, "-o", pdf_path])
                    messagebox.showinfo("Export Successful", f"Conversation saved as PDF: '{pdf_path}'.")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save conversation: {str(e)}")

    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    select_model()

