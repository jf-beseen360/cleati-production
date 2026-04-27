"""CLEATI - Professional Reports Generator"""
from enum import Enum

class ReportFormat(Enum):
    PDF = "pdf"
    EXCEL = "xlsx"
    WORD = "docx"

class ReportGenerationManager:
    def __init__(self):
        pass

    def ask_report_format(self):
        return "Quel format désirez-vous? 1=PDF, 2=Excel, 3=Word, 4=Tous"

    def parse_format_choice(self, user_input):
        choice = user_input.strip().lower()
        if choice == "1" or "pdf" in choice:
            return [ReportFormat.PDF]
        elif choice == "2" or "excel" in choice:
            return [ReportFormat.EXCEL]
        elif choice == "3" or "word" in choice:
            return [ReportFormat.WORD]
        elif choice == "4" or "tous" in choice:
            return [ReportFormat.PDF, ReportFormat.EXCEL, ReportFormat.WORD]
        return [ReportFormat.PDF, ReportFormat.EXCEL, ReportFormat.WORD]

    def set_report_format_choice(self, conv_id, choice):
        return self.parse_format_choice(choice)

    def get_download_summary(self, conv_id, formats):
        return f"Formats générés: {', '.join([f.value for f in formats])}"

    class generator:
        @staticmethod
        def generate_pdf(report):
            return b"PDF Report Content"

        @staticmethod
        def generate_excel(report):
            return b"Excel Report Content"

        @staticmethod
        def generate_word(report):
            return b"Word Report Content"
