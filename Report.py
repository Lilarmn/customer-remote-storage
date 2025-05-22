import json
import customtkinter as ctk
from customtkinter import filedialog
import jdatetime
from openpyxl import Workbook
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from tkinter import messagebox
import shutil

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")  # Changed to green theme

class WorkReportApp(ctk.CTk):
    def __init__(self , master=None):
        super().__init__()
        self.master = master
        self.title("پنل پیشرفته گزارش کار")
        self.geometry("1400x900")  # Increased window size
        self.data_file = "reports_data.json"
        self.attachments = []
        self.persian_months = [
            "فروردین", "اردیبهشت", "خرداد",
            "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر",
            "دی", "بهمن", "اسفند"
        ]
        
        # Load existing data
        self.reports = self.load_data()
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar frame with filters
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=15, fg_color="#2E4053")
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=10, pady=10)
        
        # Date Input
        self.date_label = ctk.CTkLabel(self.sidebar_frame, text="تاریخ (شمسی):", font=("Tahoma", 14))
        self.date_label.grid(row=0, column=0, padx=20, pady=(30, 0))
        self.date_entry = ctk.CTkEntry(self.sidebar_frame, height=35, font=("Tahoma", 13))
        self.date_entry.grid(row=1, column=0, padx=20, pady=(0, 15))
        self.date_entry.insert(0, jdatetime.datetime.now().strftime("%Y/%m/%d"))
        
        # Filter Section
        self.filter_label = ctk.CTkLabel(self.sidebar_frame, text="فیلتر گزارشات:", font=("Tahoma", 14))
        self.filter_label.grid(row=2, column=0, padx=20, pady=(30, 0))
        
        # Year Filter
        current_jyear = jdatetime.datetime.now().year
        self.year_filter = ctk.CTkOptionMenu(self.sidebar_frame, 
                                           values=[str(y) for y in range(current_jyear-2, current_jyear+1)],
                                           button_color="#239B56",
                                           font=("Tahoma", 13))
        self.year_filter.grid(row=3, column=0, padx=20, pady=(0, 15))
        
        # Month Filter
        self.month_filter = ctk.CTkOptionMenu(self.sidebar_frame, 
                                            values=self.persian_months,
                                            button_color="#239B56",
                                            font=("Tahoma", 13))
        self.month_filter.grid(row=4, column=0, padx=20, pady=(0, 20))
        current_jmonth = jdatetime.datetime.now().month
        self.month_filter.set(self.persian_months[current_jmonth-1])
        
        self.apply_filter_btn = ctk.CTkButton(self.sidebar_frame, text="اعمال فیلتر", 
                                           command=self.load_reports,
                                           font=("Tahoma", 14),
                                           fg_color="#28B463",
                                           hover_color="#239B56")
        self.apply_filter_btn.grid(row=5, column=0, padx=20, pady=(0, 30))

        self.stats_btn = ctk.CTkButton(self.sidebar_frame, 
                                     text="آمار و نمودارها",
                                     command=self.show_statistics,
                                     font=("Tahoma", 14),
                                     fg_color="#8E44AD",
                                     hover_color="#6C3480")
        self.stats_btn.grid(row=8, column=0, padx=20, pady=20)

        back_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="بازگشت",
            command=self.go_back,
            fg_color="transparent",
            font=("Tahoma", 14),
            hover_color="#444444"
        )
        back_btn.grid(row=10, column=0, padx=20, pady=(0, 40))


        # Main Content Area
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Report List
        self.report_list_frame = ctk.CTkScrollableFrame(self.main_frame,
                                                      height=600,
                                                      width=900,
                                                      fg_color="transparent")
        self.report_list_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.report_list_frame.grid_columnconfigure(0, weight=1)

        # Add Report Section
        self.add_report_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        self.add_report_frame.grid(row=1, column=0, sticky="sew", pady=(0, 20))
        
        # Title - Larger entry
        self.title_entry = ctk.CTkEntry(self.add_report_frame, 
                                      placeholder_text="عنوان وظیفه",
                                      height=45,
                                      font=("Tahoma", 15),
                                      corner_radius=10)
        self.title_entry.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        # Description - Larger text area
        self.desc_entry = ctk.CTkTextbox(self.add_report_frame, 
                                        height=150,
                                        font=("Tahoma", 14),
                                        corner_radius=10)
        self.desc_entry.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        
        # Action Buttons
        self.actions_frame = ctk.CTkFrame(self.add_report_frame, fg_color="transparent")
        self.actions_frame.grid(row=2, column=0, sticky="ew")
        
        self.add_attachment_btn = ctk.CTkButton(self.actions_frame, 
                                              text="افزودن فایل ضمیمه",
                                              command=self.add_attachment,
                                              font=("Tahoma", 13),
                                              fg_color="#3498DB",
                                              hover_color="#2980B9")
        self.add_attachment_btn.pack(side="left", padx=5)
        
        self.add_report_btn = ctk.CTkButton(self.actions_frame, 
                                          text="ذخیره گزارش",
                                          command=self.add_report,
                                          font=("Tahoma", 14),
                                          fg_color="#28B463",
                                          hover_color="#239B56")
        self.add_report_btn.pack(side="left", padx=5)
        
        self.export_btn = ctk.CTkButton(self.actions_frame, 
                                      text="خروجی Excel",
                                      command=self.export_to_excel,
                                      font=("Tahoma", 14),
                                      fg_color="#E67E22",
                                      hover_color="#D35400")
        self.export_btn.pack(side="right", padx=5)

        # self.setup_ai_features()

        self.category_keywords = {
            "توسعه": {"برنامه", "کدنویسی", "پیاده‌سازی", "git", "commit"},
            "عیب‌یابی": {"خطا", "باگ", "اشکال", "رفع", "bug"},
            "مستندات": {"مستند", "توضیح", "راهنما", "doc", "wiki"},
            "جلسه": {"ملاقات", "میٹینگ", "هماهنگی", "بحث", "گفتگو"},
            "پشتیبانی": {"مشکل", "سوال", "راهنمایی", "کمک", "پاسخ"}
        }
        
        self.setup_lightweight_categorization()


        self.load_reports()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def add_attachment(self):
        files = filedialog.askopenfilenames()
        if files:
            self.attachments.extend(files)
            messagebox.showinfo("Attachments", f"Added {len(files)} files")

    def add_report(self):
        try:
            report_date = jdatetime.datetime.strptime(self.date_entry.get(), "%Y/%m/%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY/MM/DD")
            return

        report_data = {
            "date": self.date_entry.get(),
            "title": self.title_entry.get(),
            "description": self.desc_entry.get("1.0", "end-1c"),
            "attachments": self.attachments.copy(),
            "category": self.auto_category.cget("text").split(" ")[0]
        }
        
        if not report_data["title"]:
            messagebox.showwarning("Warning", "Please enter a task title")
            return
            
        self.reports.append(report_data)
        self.save_data()  # Save after adding
        self.clear_form()
        self.load_reports()
        messagebox.showinfo("Success", "Report added successfully!")

    def on_closing(self):
        self.save_data()  # Save before closing
        self.destroy()

    def load_reports(self):
    # Clear existing reports
        for widget in self.report_list_frame.winfo_children():
            widget.destroy()
        
        # Filter reports
        selected_year = int(self.year_filter.get())
        selected_month = self.persian_months.index(self.month_filter.get()) + 1
        
        filtered_reports = [
            r for r in self.reports 
            if jdatetime.datetime.strptime(r["date"], "%Y/%m/%d").year == selected_year
            and jdatetime.datetime.strptime(r["date"], "%Y/%m/%d").month == selected_month
        ]
        
        # Display reports with enhanced UI
        if not filtered_reports:
            empty_label = ctk.CTkLabel(self.report_list_frame, 
                                    text="⛔ هیچ گزارشی برای این دوره یافت نشد",
                                    font=("Tahoma", 16),
                                    text_color="#E74C3C")
            empty_label.grid(row=0, column=0, pady=20)
            return
            
        for idx, report in enumerate(filtered_reports):
            report_frame = ctk.CTkFrame(self.report_list_frame,
                                    fg_color="#EBF5FB" if idx%2 == 0 else "#FDFEFE",
                                    corner_radius=15,
                                    border_width=2,
                                    border_color="#3498DB")
            report_frame.grid(row=idx, column=0, sticky="ew", pady=8, padx=5)
            report_frame.grid_columnconfigure(1, weight=1)
            
            # Date with icon
            date_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
            date_frame.pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(date_frame, text="📅", font=("Segoe UI Emoji", 16)).pack()
            ctk.CTkLabel(date_frame, 
                    text=report["date"],
                    font=("Tahoma", 14, "bold"),
                    text_color="#2E86C1").pack()
            
            # Title with styling
            title_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
            title_frame.pack(side="left", padx=15, pady=10, fill="x", expand=True)
            ctk.CTkLabel(title_frame, 
                    text=report["title"],
                    font=("Tahoma", 16, "bold"),
                    text_color="#2C3E50",
                    anchor="w").pack(fill="x")
            
            # Attachments with colored badge
            attachments_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
            attachments_frame.pack(side="right", padx=15)
            ctk.CTkLabel(attachments_frame,
                    text=f"📎 {len(report['attachments'])}",
                    font=("Tahoma", 14),
                    text_color="#3498DB",
                    corner_radius=10,
                    fg_color="#EBF5FB",
                    padx=10).pack(side="left", padx=5)
            
            # View button with hover effect
            view_btn = ctk.CTkButton(report_frame, 
                                text="مشاهده جزئیات",
                                font=("Tahoma", 14),
                                fg_color="#28B463",
                                hover_color="#239B56",
                                corner_radius=8,
                                width=120)
            view_btn.configure(command=lambda r=report: self.show_details(r))
            view_btn.pack(side="right", padx=10)

            cat_label = ctk.CTkLabel(report_frame,
                                   text=report["category"],
                                   fg_color=self.get_category_color(report["category"]),
                                   corner_radius=10,
                                   font=("Tahoma", 12))
            cat_label.pack(side="right", padx=10)

    def download_attachment(self, file_path):
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Original file not found!")
            return
            
        dest_path = filedialog.asksaveasfilename(
            initialfile=os.path.basename(file_path),
            filetypes=[("All Files", "*.*")]
        )
        
        if dest_path:
            try:
                shutil.copy(file_path, dest_path)
                messagebox.showinfo("Success", f"File saved to:\n{dest_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
    
    def export_to_excel(self):
        # Filter reports (modified month handling)
        selected_year = int(self.year_filter.get())
        selected_month = self.persian_months.index(self.month_filter.get()) + 1
        
        filtered_reports = [
            r for r in self.reports 
            if jdatetime.datetime.strptime(r["date"], "%Y/%m/%d").year == selected_year
            and jdatetime.datetime.strptime(r["date"], "%Y/%m/%d").month == selected_month
        ]
        
        if not filtered_reports:
            messagebox.showwarning("Warning", "No reports to export for selected period")
            return
            
        wb = Workbook()
        ws = wb.active
        ws.title = "Work Reports"
        
        headers = ["Date", "Title", "Description", "Attachments"]
        ws.append(headers)
        
        for report in filtered_reports:
            attachments = "\n".join(os.path.basename(f) for f in report["attachments"])
            ws.append([
                report["date"],
                report["title"],
                report["description"],
                attachments
            ])
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        
        if filename:
            wb.save(filename)
            messagebox.showinfo("Success", f"Exported {len(filtered_reports)} reports to {filename}")

    def clear_form(self):
        self.title_entry.delete(0, "end")
        self.desc_entry.delete("1.0", "end")
        self.attachments.clear()

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load data: {str(e)}")
            return []

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.reports, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save data: {str(e)}")
            
    def show_details(self, report):
        detail_win = ctk.CTkToplevel(self)
        detail_win.title("جزئیات گزارش")
        detail_win.geometry("800x600")
        detail_win.grid_columnconfigure(0, weight=1)
        
        # Header Section
        header_frame = ctk.CTkFrame(detail_win, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        # Date with icon
        ctk.CTkLabel(header_frame, 
                    text="📅 " + report["date"],
                    font=("Tahoma", 18, "bold"),
                    text_color="#2E86C1").pack(side="left", padx=10)
        
        # Attachments count badge
        attachments_badge = ctk.CTkLabel(header_frame,
                                        text=f"📁 {len(report['attachments'])} فایل ضمیمه",
                                        font=("Tahoma", 14),
                                        corner_radius=15,
                                        fg_color="#E8F8F5",
                                        text_color="#17A589",
                                        padx=15,
                                        pady=5)
        attachments_badge.pack(side="right", padx=10)

        # Main Content
        main_content = ctk.CTkScrollableFrame(detail_win)
        main_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        main_content.grid_columnconfigure(0, weight=1)

        # Title Section
        title_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=10)
        ctk.CTkLabel(title_frame, 
                    text="عنوان گزارش:",
                    font=("Tahoma", 16, "bold"),
                    text_color="#D0D3D4").pack(anchor="w")
        ctk.CTkLabel(title_frame, 
                    text=report["title"],
                    font=("Tahoma", 16),
                    wraplength=700,
                    anchor="w").pack(anchor="w", fill="x")

        # Separator
        ctk.CTkLabel(main_content, 
                    text="━"*100, 
                    text_color="#D0D3D4").grid(row=1, column=0, pady=15)

        # Description Section
        desc_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        desc_frame.grid(row=2, column=0, sticky="ew", pady=10)
        ctk.CTkLabel(desc_frame, 
                    text="توضیحات کامل:",
                    font=("Tahoma", 16, "bold"),
                    text_color="#D0D3D4").pack(anchor="w")
        desc_text = ctk.CTkTextbox(desc_frame,
                                font=("Tahoma", 14),
                                wrap="word",
                                height=200,
                                fg_color="#FBFCFC",
                                border_width=1,
                                text_color='black',
                                border_color="#D0D3D4")
        desc_text.insert("1.0", report["description"])
        desc_text.configure(state="disabled")
        desc_text.pack(fill="both", expand=True)

        # Attachments Section
        if report["attachments"]:
            ctk.CTkLabel(main_content, 
                        text="فایل های ضمیمه:",
                        font=("Tahoma", 16, "bold"),
                        text_color="#D0D3D4").grid(row=3, column=0, pady=15, sticky="w")
            
            attachments_frame = ctk.CTkScrollableFrame(main_content, height=150)
            attachments_frame.grid(row=4, column=0, sticky="ew", pady=10)
            
            for idx, file_path in enumerate(report["attachments"]):
                file_name = os.path.basename(file_path)
                attachment_row = ctk.CTkFrame(attachments_frame, fg_color="transparent")
                attachment_row.pack(fill="x", pady=5)
                
                # File info
                ctk.CTkLabel(attachment_row,
                            text=f"📄 {file_name}",
                            font=("Tahoma", 14),
                            anchor="w").pack(side="left", padx=10)
                
                # Download button
                ctk.CTkButton(attachment_row,
                            text="دانلود",
                            font=("Tahoma", 12),
                            fg_color="#28B463",
                            hover_color="#239B56",
                            width=80,
                            command=lambda fp=file_path: self.download_attachment(fp)
                            ).pack(side="right", padx=10)
                
                # File size
                try:
                    size = os.path.getsize(file_path)
                    size_mb = f"{size/1024/1024:.2f} MB"
                    ctk.CTkLabel(attachment_row,
                                text=size_mb,
                                font=("Tahoma", 12),
                                text_color="#7F8C8D").pack(side="right", padx=10)
                except:
                    pass

        # Configure window resizing
        detail_win.rowconfigure(1, weight=1)
        detail_win.columnconfigure(0, weight=1)

    def show_statistics(self):
        stats_win = ctk.CTkToplevel(self)
        stats_win.title("آمار و تحلیل پیشرفته")
        stats_win.geometry("1400x1000")
        
        # Create main container
        container = ctk.CTkScrollableFrame(stats_win)
        container.pack(fill="both", expand=True)
        
        try:
            # Convert Jalali dates to Gregorian for analysis
            dates = []
            valid_reports = []
            for report in self.reports:
                try:
                    jdate = jdatetime.datetime.strptime(report['date'], "%Y/%m/%d")
                    gdate = jdate.togregorian()
                    dates.append(gdate)
                    valid_reports.append(report)
                except ValueError:
                    continue

            # Create DataFrame with valid dates
            df = pd.DataFrame({
                'date': dates,
                'title': [r['title'] for r in valid_reports],
                'attachments': [len(r['attachments']) for r in valid_reports]
            })
            
            if df.empty:
                raise ValueError("هیچ گزارشی برای تحلیل وجود ندارد")

            # Section 1: Summary Cards with valid colors
            summary_frame = ctk.CTkFrame(container, fg_color="transparent")
            summary_frame.pack(fill="x", pady=10, padx=10)
            
            # Valid color palette (6-digit hex)
            color_palette = [
                ("#1ABC9C", "#D1F2EB"),  # Teal + light teal
                ("#F1C40F", "#FCF3CF"),  # Yellow + light yellow
                ("#E74C3C", "#FADBD8"),  # Red + light red
                ("#8E44AD", "#E8DAEF")   # Purple + light purple
            ]
            
            cards = [
                ("📊 کل گزارشات", len(df), *color_palette[0]),
                ("📎 کل ضمائم", df['attachments'].sum(), *color_palette[1]),
                ("📅 اولین گزارش", 
                jdatetime.date.fromgregorian(date=df['date'].min()).strftime("%Y/%m/%d"), 
                *color_palette[2]),
                ("📅 آخرین گزارش", 
                jdatetime.date.fromgregorian(date=df['date'].max()).strftime("%Y/%m/%d"), 
                *color_palette[3])
            ]
            
            for text, value, base_color, light_color in cards:
                card = ctk.CTkFrame(summary_frame, 
                                fg_color=light_color,
                                corner_radius=15,
                                border_width=1,
                                border_color=base_color)
                card.pack(side="left", padx=10, pady=10, fill="both", expand=True)
                ctk.CTkLabel(card, 
                        text=text,
                        font=("Tahoma", 14),
                        text_color=base_color).pack(pady=5)
                ctk.CTkLabel(card, 
                        text=str(value),
                        font=("Tahoma", 20, "bold"),
                        text_color=base_color).pack(pady=5)

            # Section 2: Monthly Trends (Jalali)
            monthly_frame = ctk.CTkFrame(container, fg_color="transparent")
            monthly_frame.pack(fill="both", expand=True, pady=10, padx=10)
            
            df['jmonth'] = df['date'].apply(lambda d: jdatetime.date.fromgregorian(date=d).month)
            monthly_counts = df.groupby('jmonth').size()
            
            fig1 = plt.Figure(figsize=(10, 5), dpi=100)
            ax1 = fig1.add_subplot(111)
            monthly_counts.plot(kind='bar', ax=ax1, color='#3498DB')
            ax1.set_title('تعداد گزارشات ماهانه (شمسی)', fontfamily='Tahoma', fontsize=14)
            ax1.set_xticks(range(12))
            ax1.set_xticklabels(self.persian_months, rotation=45)
            ax1.set_ylabel('تعداد گزارشات', fontfamily='Tahoma')
            ax1.grid(axis='y', alpha=0.3)
            
            chart1 = FigureCanvasTkAgg(fig1, monthly_frame)
            chart1.get_tk_widget().pack(fill="both", expand=True)

            # Section 3: Weekly Pattern
            weekday_frame = ctk.CTkFrame(container, fg_color="transparent")
            weekday_frame.pack(fill="both", expand=True, pady=10, padx=10)
            
            persian_weekdays = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
            df['weekday'] = df['date'].dt.weekday  # Monday=0, Sunday=6
            weekday_counts = df.groupby('weekday').size()
            
            fig2 = plt.Figure(figsize=(10, 5), dpi=100)
            ax2 = fig2.add_subplot(111)
            weekday_counts.plot(kind='line', ax=ax2, color='#2ECC71', marker='o', markersize=8)
            ax2.set_title('الگوی گزارشات در روزهای هفته', fontfamily='Tahoma', fontsize=14)
            ax2.set_xticks(range(7))
            ax2.set_xticklabels(persian_weekdays)
            ax2.set_ylabel('تعداد گزارشات', fontfamily='Tahoma')
            ax2.grid(True, alpha=0.3)
            
            chart2 = FigureCanvasTkAgg(fig2, weekday_frame)
            chart2.get_tk_widget().pack(fill="both", expand=True)

            # Section 4: Yearly Comparison
            yearly_frame = ctk.CTKFrame(container, fg_color="transparent")
            yearly_frame.pack(fill="both", expand=True, pady=10, padx=10)
            
            df['jyear'] = df['date'].apply(lambda d: jdatetime.date.fromgregorian(date=d).year)
            yearly_counts = df.groupby('jyear').size()
            
            fig3 = plt.Figure(figsize=(10, 5), dpi=100)
            ax3 = fig3.add_subplot(111)
            yearly_counts.plot(kind='barh', ax=ax3, color='#E67E22')
            ax3.set_title('مقایسه سالانه', fontfamily='Tahoma', fontsize=14)
            ax3.set_xlabel('تعداد گزارشات', fontfamily='Tahoma')
            ax3.grid(axis='x', alpha=0.3)
            
            chart3 = FigureCanvasTkAgg(fig3, yearly_frame)
            chart3.get_tk_widget().pack(fill="both", expand=True)

            # Section 5: Attachments Analysis
            attach_frame = ctk.CTkFrame(container, fg_color="transparent")
            attach_frame.pack(fill="both", expand=True, pady=10, padx=10)
            
            file_types = {}
            for report in valid_reports:
                for file in report['attachments']:
                    ext = os.path.splitext(file)[1].lower() or 'بدون پسوند'
                    file_types[ext] = file_types.get(ext, 0) + 1
                    
            fig4 = plt.Figure(figsize=(10, 5), dpi=100)
            ax4 = fig4.add_subplot(111)
            colors = ['#3498DB', '#2ECC71', '#F1C40F', '#E74C3C', '#9B59B6']
            ax4.pie(file_types.values(), 
                labels=file_types.keys(),
                autopct=lambda p: f'{p:.1f}%\n({int(p/100*sum(file_types.values()))})',
                colors=colors[:len(file_types)],
                textprops={'fontfamily': 'Tahoma'})
            ax4.set_title('توزیع انواع فایل های ضمیمه', fontfamily='Tahoma', fontsize=14)
            
            chart4 = FigureCanvasTkAgg(fig4, attach_frame)
            chart4.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("خطای تحلیل", f"خطا در پردازش داده‌ها:\n{str(e)}")
        
        stats_win.mainloop()

    def go_back(self):
        # Destroy current app window
        self.destroy()
        # Show the parent CompanyList window
        self.master.deiconify()

    def get_category_color(self, category):
        # Color mapping for categories
        colors = {
            "توسعه نرم‌افزار": "#3498DB",
            "جلسه": "#2ECC71",
            "عیب‌یابی": "#E74C3C",
            "تحقیق": "#9B59B6",
            "مستندسازی": "#F1C40F",
            "بررسی کد": "#1ABC9C",
            "پشتیبانی فنی": "#E67E22"
        }
        return colors.get(category, "#95A5A6")

    def setup_lightweight_categorization(self):
        # Category components
        self.category_frame = ctk.CTkFrame(self.sidebar_frame)
        self.category_frame.grid(row=11, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.category_label = ctk.CTkLabel(self.category_frame, text="دسته‌بندی خودکار:")
        self.category_label.pack(side="top", anchor="w")
        
        self.auto_category = ctk.CTkLabel(self.category_frame, 
                                        text="",
                                        text_color="#2ECC71",
                                        font=("Tahoma", 12))
        self.auto_category.pack(pady=5)
        
        # Real-time analysis
        self.desc_entry.bind("<KeyRelease>", self.analyze_description)

    def analyze_description(self, event=None):
        desc = self.desc_entry.get("1.0", "end-1c").lower()
        scores = {cat: 0 for cat in self.category_keywords}
        
        # Simple keyword matching
        for word in desc.split():
            for cat, keywords in self.category_keywords.items():
                if word in keywords:
                    scores[cat] += 1
                    
        # Find best match
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category] / len(desc.split()) if desc else 0
        
        if confidence > 0.1:  # Minimum 10% confidence
            self.auto_category.configure(text=f"{best_category} ({confidence:.0%} اطمینان)")
        else:
            self.auto_category.configure(text="دسته‌بندی نشده")


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("dark-blue")
    app = WorkReportApp()
    app.mainloop()