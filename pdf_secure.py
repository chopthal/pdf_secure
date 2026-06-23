import os
import platform
import sys
import threading

from core.password import PdfPasswordValidationError, validate_pdf_password
from core.watermark import add_watermark

# --- GUI 인터페이스 ---
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# macOS에서 발생하는 시스템 경고 메시지 억제
if platform.system() == 'Darwin':  # macOS
    # Input Method Kit 관련 경고 억제를 위한 환경 변수 설정
    os.environ.setdefault('NSUnbufferedIO', 'YES')
    
    # stderr 필터링을 위한 클래스 정의 (시스템 경고만 억제)
    class StderrFilter:
        """macOS 시스템 경고 메시지를 필터링하는 클래스"""
        def __init__(self, original_stderr):
            self.original_stderr = original_stderr
            self.filter_keywords = [
                'IMKClient',
                'IMKInputSession',
                'NSOpenPanel',
                'TSM AdjustCapsLockLED',
                'mach port for IMKCFRunLoopWakeUpReliable'
            ]
        
        def write(self, message):
            # 필터링할 키워드가 포함된 메시지는 무시
            if any(keyword in message for keyword in self.filter_keywords):
                return
            # 실제 에러는 그대로 출력
            self.original_stderr.write(message)
        
        def flush(self):
            self.original_stderr.flush()
    
    # stderr를 필터링된 버전으로 교체
    sys.stderr = StderrFilter(sys.stderr)

class PDFSecureGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 보안 처리 시스템")
        self.root.geometry("650x680")
        self.root.resizable(False, False)
        
        # 변수 초기화
        self.input_file = tk.StringVar()
        self.buyer_name = tk.StringVar()
        self.buyer_phone = tk.StringVar()
        self.pdf_password = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="준비")
        
        self.setup_ui()
    
    def setup_ui(self):
        # 제목
        title_label = tk.Label(self.root, text="PDF 보안 처리 시스템", 
                              font=("맑은 고딕", 20, "bold"))
        title_label.pack(pady=15)
        
        # 파일 선택 프레임
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=15, padx=30, fill=tk.X)
        
        tk.Label(file_frame, text="원본 PDF 파일:", font=("맑은 고딕", 13)).pack(anchor=tk.W)
        
        file_select_frame = tk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=8)
        
        self.file_entry = tk.Entry(file_select_frame, textvariable=self.input_file, 
                                   font=("맑은 고딕", 11), state='readonly')
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        tk.Button(file_select_frame, text="파일 선택", command=self.select_file,
                 font=("맑은 고딕", 11)).pack(side=tk.LEFT)
        
        # 구매자 정보 입력 프레임
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=15, padx=30, fill=tk.X)
        
        tk.Label(info_frame, text="구매자 정보", font=("맑은 고딕", 13, "bold")).pack(anchor=tk.W, pady=(0, 8))
        
        # 이름 입력
        name_frame = tk.Frame(info_frame)
        name_frame.pack(fill=tk.X, pady=8)
        tk.Label(name_frame, text="이름:", font=("맑은 고딕", 13), width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.name_entry = tk.Entry(name_frame, textvariable=self.buyer_name, font=("맑은 고딕", 13))
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # macOS 한글 입력 문제 해결: 포커스를 잃을 때 조합 완료
        if platform.system() == 'Darwin':
            self.name_entry.bind('<FocusOut>', self._fix_korean_input)
            self.name_entry.bind('<Return>', lambda e: self.phone_entry.focus())
            self.name_entry.bind('<Tab>', lambda e: self.phone_entry.focus())
        
        # 연락처 입력
        phone_frame = tk.Frame(info_frame)
        phone_frame.pack(fill=tk.X, pady=8)
        tk.Label(phone_frame, text="연락처:", font=("맑은 고딕", 13), width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.phone_entry = tk.Entry(phone_frame, textvariable=self.buyer_phone, font=("맑은 고딕", 13))
        self.phone_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # macOS 한글 입력 문제 해결: 포커스를 잃을 때 조합 완료
        if platform.system() == 'Darwin':
            self.phone_entry.bind('<FocusOut>', self._fix_korean_input)
            self.phone_entry.bind('<Return>', lambda e: self.password_entry.focus())
            self.phone_entry.bind('<Tab>', lambda e: self.password_entry.focus())
        
        # 비밀번호 입력
        password_frame = tk.Frame(info_frame)
        password_frame.pack(fill=tk.X, pady=8)
        tk.Label(password_frame, text="비밀번호:", font=("맑은 고딕", 13), width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.password_entry = tk.Entry(password_frame, textvariable=self.pdf_password, 
                                  font=("맑은 고딕", 13))
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # macOS 한글 입력 문제 해결: 포커스를 잃을 때 조합 완료
        if platform.system() == 'Darwin':
            self.password_entry.bind('<FocusOut>', self._fix_korean_input)
            self.password_entry.bind('<Return>', lambda e: self.start_processing())
        
        # 미리보기 프레임
        preview_frame = tk.Frame(info_frame)
        preview_frame.pack(fill=tk.X, pady=(12, 8))
        tk.Label(preview_frame, text="미리보기:", font=("맑은 고딕", 11, "bold"), 
                anchor=tk.W).pack(anchor=tk.W, pady=(0, 5))
        self.preview_label = tk.Label(preview_frame, text="", 
                                     font=("맑은 고딕", 11), 
                                     fg="#666666", anchor=tk.W, 
                                     wraplength=590, justify=tk.LEFT)
        self.preview_label.pack(fill=tk.X, anchor=tk.W)
        
        # 이름과 연락처 변경 시 미리보기 업데이트
        self.buyer_name.trace_add("write", lambda *args: self.update_preview())
        self.buyer_phone.trace_add("write", lambda *args: self.update_preview())
        
        # 진행 상황 프레임
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=15, padx=30, fill=tk.X)
        
        self.status_label = tk.Label(progress_frame, textvariable=self.status_var, 
                                     font=("맑은 고딕", 11), anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(0, 8))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=590)
        self.progress_bar.pack(fill=tk.X)
        
        # 처리 버튼
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=25)
        
        self.process_button = tk.Button(button_frame, text="처리 시작", 
                                       command=self.start_processing,
                                       font=("맑은 고딕", 13, "bold"),
                                       bg="#4CAF50", fg="white", 
                                       width=18, height=2)
        self.process_button.pack()
    
    def _fix_korean_input(self, event):
        """
        macOS에서 한글 입력 시 포커스 이동으로 인한 문제 해결
        포커스를 잃을 때 한글 조합을 강제로 완료시킴
        """
        widget = event.widget
        # 약간의 지연을 두고 텍스트를 다시 설정하여 조합 완료
        # macOS IME가 조합 중인 상태를 완료하도록 함
        def complete_composition():
            current_text = widget.get()
            # 텍스트를 다시 설정하여 조합 완료
            widget.delete(0, tk.END)
            widget.insert(0, current_text)
            # StringVar 업데이트 (이미 연결되어 있으므로 자동 반영)
        
        # 50ms 지연 후 실행 (IME 조합 완료 대기)
        widget.after(50, complete_composition)
    
    def select_file(self):
        filename = filedialog.askopenfilename(
            title="PDF 파일 선택",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
    
    def update_preview(self):
        """이름과 연락처 입력에 따라 미리보기 업데이트"""
        name = self.buyer_name.get().strip()
        phone = self.buyer_phone.get().strip()
        
        if name and phone:
            preview_text = f"이 책은 {name} ({phone}) 님이 구매하신 전자책입니다."
            self.preview_label.config(text=preview_text, fg="#333333")
        elif name or phone:
            # 하나만 입력된 경우
            if name:
                preview_text = f"이 책은 {name} ( ) 님이 구매하신 전자책입니다."
            else:
                preview_text = f"이 책은  ({phone}) 님이 구매하신 전자책입니다."
            self.preview_label.config(text=preview_text, fg="#999999")
        else:
            # 둘 다 비어있는 경우
            self.preview_label.config(text="", fg="#666666")
    
    def validate_inputs(self):
        if not self.input_file.get():
            messagebox.showerror("오류", "PDF 파일을 선택해주세요.")
            return False
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("오류", "선택한 파일이 존재하지 않습니다.")
            return False
        if not self.buyer_name.get().strip():
            messagebox.showerror("오류", "구매자 이름을 입력해주세요.")
            return False
        if not self.buyer_phone.get().strip():
            messagebox.showerror("오류", "연락처를 입력해주세요.")
            return False
        if not self.pdf_password.get().strip():
            messagebox.showerror("오류", "비밀번호를 입력해주세요.")
            return False
        try:
            validate_pdf_password(self.pdf_password.get())
        except PdfPasswordValidationError as exc:
            messagebox.showerror("오류", str(exc))
            return False
        return True
    
    def progress_callback(self, current, total, message):
        """진행 상황 업데이트 콜백"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def process_pdf(self):
        """PDF 처리 작업 (별도 스레드에서 실행)"""
        try:
            input_path = self.input_file.get()
            buyer_name = self.buyer_name.get().strip()
            buyer_phone = self.buyer_phone.get().strip()
            pdf_password = self.pdf_password.get().strip()
            
            # 출력 파일명 생성
            input_dir = os.path.dirname(input_path)
            input_basename = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{input_basename}_{buyer_name}.pdf"
            output_path = os.path.join(input_dir, output_filename)
            
            # 워터마크 텍스트 생성
            watermark_text = f"이 책은 {buyer_name} ({buyer_phone}) 님이 구매하신 전자책입니다."
            
            # PDF 처리
            success = add_watermark(
                input_path, 
                output_path, 
                watermark_text, 
                password=pdf_password,
                buyer_name=buyer_name,
                buyer_phone=buyer_phone,
                progress_callback=self.progress_callback
            )
            
            if success:
                messagebox.showinfo("완료", 
                                  f"파일이 생성되었습니다!\n\n"
                                  f"파일: {output_filename}\n"
                                  f"비밀번호: {pdf_password}")
                # 초기화
                self.progress_var.set(0)
                self.status_var.set("준비")
                self.process_button.config(state=tk.NORMAL)
            else:
                messagebox.showerror("오류", "PDF 처리 중 오류가 발생했습니다.")
                self.process_button.config(state=tk.NORMAL)
                
        except Exception as e:
            messagebox.showerror("오류", f"처리 중 오류가 발생했습니다:\n{str(e)}")
            self.progress_var.set(0)
            self.status_var.set("오류 발생")
            self.process_button.config(state=tk.NORMAL)
    
    def start_processing(self):
        """처리 시작"""
        if not self.validate_inputs():
            return
        
        # 버튼 비활성화
        self.process_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("처리 시작...")
        
        # 별도 스레드에서 처리 (GUI 블로킹 방지)
        thread = threading.Thread(target=self.process_pdf, daemon=True)
        thread.start()

# --- 실행부 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSecureGUI(root)
    root.mainloop()