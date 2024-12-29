import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, Menu
import subprocess
import os
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat with Granite Model")
        self.root.geometry("1024x768")  # Set larger default window size

        self.chat_history = ""  # Store chat history
        self.file_content = ""  # Store uploaded file content

        # Create Menu Bar
        self.menu_bar = Menu(root)
        root.config(menu=self.menu_bar)

        # File Menu
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Upload Text File", command=self.upload_file)
        file_menu.add_command(label="Upload PDF File", command=self.upload_pdf)
        file_menu.add_command(label="Export Conversation", command=self.export_conversation)
        file_menu.add_command(label="Exit", command=root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Copy", command=lambda: root.clipboard_append(self.get_selected_text()))
        edit_menu.add_command(label="Paste", command=lambda: self.user_input.insert(tk.END, root.clipboard_get()))
        edit_menu.add_command(label="Find", command=self.find_text)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Chat Display
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Helvetica", 12), state='disabled')
        self.chat_display.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # User Input Frame
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=10)

        # User Input
        self.user_input = tk.Entry(self.input_frame, font=("Helvetica", 12), width=70)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.user_input.bind("<Return>", lambda event: self.send_message())  # Bind Enter key to send message

        # Send Button
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message, font=("Helvetica", 12))
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

        # Send message to Ollama locally
        response = self.query_ollama(user_message)
        if response:
            self.update_chat_display("Model", response)

    def query_ollama(self, prompt):
        try:
            # Combine file content as context with the user prompt
            input_text = self.file_content + "\n\nUser: " + prompt
            process = subprocess.run(
                ["ollama", "run", "granite3.1-dense:2b"],
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

                # Fallback to OCR if no text is found
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

    def get_selected_text(self):
        try:
            return self.chat_display.selection_get()
        except tk.TclError:
            return ""

    def find_text(self):
        def perform_find():
            self.chat_display.tag_remove("highlight", "1.0", tk.END)
            search_query = find_entry.get()
            if search_query:
                start_pos = "1.0"
                while True:
                    start_pos = self.chat_display.search(search_query, start_pos, stopindex=tk.END)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(search_query)}c"
                    self.chat_display.tag_add("highlight", start_pos, end_pos)
                    self.chat_display.tag_config("highlight", background="yellow")
                    start_pos = end_pos

        find_popup = tk.Toplevel(self.root)
        find_popup.title("Find Text")
        find_popup.geometry("300x100")
        find_label = tk.Label(find_popup, text="Find:")
        find_label.pack(pady=5)
        find_entry = tk.Entry(find_popup, width=30)
        find_entry.pack(pady=5)
        find_button = tk.Button(find_popup, text="Find", command=perform_find)
        find_button.pack(pady=5)

    def export_conversation(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(self.chat_display.get("1.0", tk.END).strip())
                messagebox.showinfo("Export Successful", f"Conversation saved to '{file_path}'.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save conversation: {str(e)}")

# Main Application
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()

