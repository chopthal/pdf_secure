import io
import os
import platform
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter

def get_korean_font():
    """
    운영체제에 따라 한글 폰트를 자동으로 찾아서 등록합니다.
    Windows: 맑은고딕
    macOS: 애플고딕 또는 나눔고딕
    """
    system = platform.system()
    font_name = None
    font_path = None
    
    if system == 'Windows':
        # Windows: 맑은고딕
        possible_paths = [
            'C:/Windows/Fonts/malgun.ttf',
            'C:/Windows/Fonts/gulim.ttc',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                font_path = path
                font_name = 'Malgun' if 'malgun' in path.lower() else 'Gulim'
                break
    elif system == 'Darwin':  # macOS
        # macOS: 애플고딕 또는 나눔고딕
        possible_paths = [
            '/System/Library/Fonts/AppleGothic.ttf',
            '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
            '/Library/Fonts/NanumGothic.ttf',
            os.path.expanduser('~/Library/Fonts/NanumGothic.ttf'),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                font_path = path
                font_name = 'AppleGothic' if 'Apple' in path else 'NanumGothic'
                break
    
    # 폰트 등록 시도
    if font_path and font_name:
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            return font_name
        except Exception as e:
            print(f"폰트 등록 실패 ({font_path}): {e}")
    
    # 폰트를 찾지 못한 경우 기본 폰트 사용 (한글 깨짐 주의)
    print("한글 폰트를 찾을 수 없습니다. 기본 폰트로 진행합니다. (한글이 깨질 수 있습니다)")
    return 'Helvetica'

def add_watermark(input_pdf, output_pdf, watermark_text, password=None, 
                 buyer_name=None, buyer_phone=None, progress_callback=None):
    # 1. 한글 폰트 등록 (크로스 플랫폼 지원)
    font_name = get_korean_font()

    # 2. 워터마크 레이어 생성
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont(font_name, 10) # 폰트 크기 (하단 표기용으로 작게 조정)
    can.setFillColorRGB(0.5, 0.5, 0.5) # 밝은 회색
    can.setFillAlpha(0.6) # 투명도 60% (0.6)
    
    # 워터마크 위치 (왼쪽 하단)
    width, height = A4
    font_size = 10
    can.drawString(30, 30 + font_size * 1.5, watermark_text) # 왼쪽 하단에 배치 (글자 크기 1.5배만큼 위로)
    
    can.save()
    packet.seek(0)
    
    # 3. 원본 PDF와 워터마크 합치기
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(input_pdf)
    output = PdfWriter()
    
    total_pages = len(existing_pdf.pages)
    if progress_callback:
        progress_callback(0, total_pages, "PDF 읽기 완료")

    # 5번째 페이지(인덱스 4)부터 워터마크 적용
    for i in range(total_pages):
        page = existing_pdf.pages[i]
        if i >= 4:  # 5번째 페이지부터 (인덱스는 0부터 시작)
            page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        
        if progress_callback:
            progress_callback(i + 1, total_pages, f"페이지 처리 중: {i + 1}/{total_pages}")

    # 4. 메타데이터 설정 (구매자 정보 추가)
    if buyer_name or buyer_phone:
        if progress_callback:
            progress_callback(total_pages, total_pages, "메타데이터 설정 중...")
        
        # 기존 메타데이터 읽기
        metadata = {}
        if hasattr(existing_pdf, 'metadata') and existing_pdf.metadata:
            metadata = existing_pdf.metadata.copy()
        
        # 구매자 정보로 메타데이터 업데이트
        metadata.update({
            '/Author': '올라',
            '/Subject': f'구매자 정보: {buyer_name or ""} ({buyer_phone or ""})',
            '/Creator': '올라의 꿀수면 프로젝트',
            '/Producer': '',
        })
        
        output.add_metadata(metadata)
    
    # 5. 비밀번호 및 권한 설정 (제공된 경우)
    if password:
        if progress_callback:
            progress_callback(total_pages, total_pages, "비밀번호 및 권한 설정 중...")
        
        # pypdf의 encrypt 메서드는 기본적으로 비밀번호만 받음
        # 권한 설정을 위해서는 암호화 후 권한을 직접 설정해야 함
        # 하지만 pypdf의 최신 버전에서는 권한 설정이 제한적임
        
        # 기본 암호화 적용
        output.encrypt(
            user_password=password,
            owner_password=password,
            use_128bit=True
        )
        
        # 참고: pypdf에서는 권한(복사/인쇄 제한) 설정이 제한적입니다.
        # 완전한 권한 제어를 위해서는 PyPDF2 라이브러리 사용이 필요할 수 있습니다.
        # 현재는 비밀번호 보호만 적용되며, 권한 설정은 PDF 뷰어에 따라 다르게 동작할 수 있습니다.
    
    # 5. 파일 저장
    if progress_callback:
        progress_callback(total_pages, total_pages, "파일 저장 중...")
    with open(output_pdf, "wb") as outputStream:
        output.write(outputStream)
    
    if progress_callback:
        progress_callback(total_pages, total_pages, "완료!")
    
    return True

# --- GUI 인터페이스 ---
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import sys
import os

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
        self.root.geometry("500x520")
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
                              font=("맑은 고딕", 16, "bold"))
        title_label.pack(pady=10)
        
        # 파일 선택 프레임
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(file_frame, text="원본 PDF 파일:", font=("맑은 고딕", 10)).pack(anchor=tk.W)
        
        file_select_frame = tk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=5)
        
        self.file_entry = tk.Entry(file_select_frame, textvariable=self.input_file, 
                                   font=("맑은 고딕", 9), state='readonly')
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(file_select_frame, text="파일 선택", command=self.select_file,
                 font=("맑은 고딕", 9)).pack(side=tk.LEFT)
        
        # 구매자 정보 입력 프레임
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(info_frame, text="구매자 정보", font=("맑은 고딕", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # 이름 입력
        name_frame = tk.Frame(info_frame)
        name_frame.pack(fill=tk.X, pady=5)
        tk.Label(name_frame, text="이름:", font=("맑은 고딕", 9), width=10, anchor=tk.W).pack(side=tk.LEFT)
        tk.Entry(name_frame, textvariable=self.buyer_name, font=("맑은 고딕", 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 연락처 입력
        phone_frame = tk.Frame(info_frame)
        phone_frame.pack(fill=tk.X, pady=5)
        tk.Label(phone_frame, text="연락처:", font=("맑은 고딕", 9), width=10, anchor=tk.W).pack(side=tk.LEFT)
        tk.Entry(phone_frame, textvariable=self.buyer_phone, font=("맑은 고딕", 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # PDF 비밀번호 입력
        password_frame = tk.Frame(info_frame)
        password_frame.pack(fill=tk.X, pady=5)
        tk.Label(password_frame, text="PDF 비밀번호:", font=("맑은 고딕", 9), width=10, anchor=tk.W).pack(side=tk.LEFT)
        password_entry = tk.Entry(password_frame, textvariable=self.pdf_password, 
                                  font=("맑은 고딕", 9))
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 미리보기 프레임
        preview_frame = tk.Frame(info_frame)
        preview_frame.pack(fill=tk.X, pady=(10, 5))
        tk.Label(preview_frame, text="미리보기:", font=("맑은 고딕", 9, "bold"), 
                anchor=tk.W).pack(anchor=tk.W, pady=(0, 3))
        self.preview_label = tk.Label(preview_frame, text="", 
                                     font=("맑은 고딕", 9), 
                                     fg="#666666", anchor=tk.W, 
                                     wraplength=460, justify=tk.LEFT)
        self.preview_label.pack(fill=tk.X, anchor=tk.W)
        
        # 이름과 연락처 변경 시 미리보기 업데이트
        self.buyer_name.trace_add("write", lambda *args: self.update_preview())
        self.buyer_phone.trace_add("write", lambda *args: self.update_preview())
        
        # 진행 상황 프레임
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.status_label = tk.Label(progress_frame, textvariable=self.status_var, 
                                     font=("맑은 고딕", 9), anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=460)
        self.progress_bar.pack(fill=tk.X)
        
        # 처리 버튼
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.process_button = tk.Button(button_frame, text="처리 시작", 
                                       command=self.start_processing,
                                       font=("맑은 고딕", 11, "bold"),
                                       bg="#4CAF50", fg="white", 
                                       width=15, height=2)
        self.process_button.pack()
    
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
            messagebox.showerror("오류", "PDF 비밀번호를 입력해주세요.")
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