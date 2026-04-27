"""
I18n Integration for Reports Generator
Adds language support to report generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class I18nReportsGenerator:
    """
    Language-aware reports generator wrapper.
    Wraps the base ReportGenerator to add i18n support.
    """

    def __init__(self, i18n_service, base_generator):
        """
        Initialize I18n reports generator.

        Args:
            i18n_service: I18nService instance
            base_generator: Base ReportGenerator instance
        """
        self.i18n = i18n_service
        self.generator = base_generator
        self.current_language = i18n_service.current_language

    def generate_all_formats(
        self,
        unified_data: Dict[str, Any],
        formats: List[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, bytes]:
        """
        Generate reports in all requested formats with i18n support.

        Args:
            unified_data: Complete project data
            formats: List of formats ('pdf', 'excel', 'word')
            language: Target language code

        Returns:
            Dict with format -> binary content
        """
        if language:
            self.i18n.set_language(language)

        if formats is None:
            formats = ['pdf', 'excel', 'word']

        reports = {}

        if 'pdf' in formats:
            reports['pdf'] = self.generate_pdf_report(unified_data)
        if 'excel' in formats:
            reports['excel'] = self.generate_excel_report(unified_data)
        if 'word' in formats:
            reports['word'] = self.generate_word_report(unified_data)

        return reports

    def generate_pdf_report(self, unified_data: Dict[str, Any]) -> bytes:
        """
        Generate localized PDF report.

        Args:
            unified_data: Project data

        Returns:
            PDF content as bytes
        """
        project_id = unified_data.get("project_id", "Unknown")
        metadata = unified_data.get("metadata", {})
        project_name = metadata.get("project_name", "Project")

        # Get localized strings
        report_title = self._t('report_title', 'reports')
        exec_summary = self._t('executive_summary', 'reports')
        project_overview = self._t('project_overview', 'reports')
        financial_analysis = self._t('financial_analysis', 'reports')
        green_impact = self._t('green_impact', 'reports')
        business_plan = self._t('business_plan', 'reports')
        monitoring = self._t('monitoring_evaluation', 'reports')
        recommendations = self._t('recommendations', 'reports')
        appendix = self._t('appendix', 'reports')
        generated_on = self._t('generated_on', 'reports')
        page = self._t('page', 'reports')

        # Format timestamp using locale
        formatted_date = self.i18n.format_date(datetime.now(), 'long')

        # Build localized PDF content
        pdf_content = f"""
        ╔════════════════════════════════════════════════════════════════════════════════════╗
        ║                         CLEATI V3.3 - {report_title.upper()}                       ║
        ║                    Intelligent Business Planning Platform                         ║
        ╚════════════════════════════════════════════════════════════════════════════════════╝

        PROJECT: {project_name}
        PROJECT ID: {project_id}
        {generated_on}: {formatted_date}
        STATUS: ✅ READY FOR STAKEHOLDERS

        ════════════════════════════════════════════════════════════════════════════════════════

        📖 TABLE OF CONTENTS

        1. {exec_summary.upper()}
        2. {financial_analysis.upper()}
        3. {green_impact.upper()}
        4. {business_plan.upper()}
        5. {monitoring.upper()}
        6. {recommendations.upper()}
        7. {appendix.upper()}
        """

        # Add financial analysis section
        financial_data = unified_data.get('financial_data', {})
        if financial_data:
            pdf_content += f"""

        ════════════════════════════════════════════════════════════════════════════════════════

        🏦 {financial_analysis.upper()}

        """
            for key, value in financial_data.items():
                label = self._t(key, 'financial')
                formatted_value = self.i18n.format_currency(value)
                pdf_content += f"        {label}: {formatted_value}\n"

        # Add green metrics section
        green_metrics = unified_data.get('green_metrics', {})
        if green_metrics:
            pdf_content += f"""

        ════════════════════════════════════════════════════════════════════════════════════════

        🌱 {green_impact.upper()}

        """
            for key, value in green_metrics.items():
                label = self._t(key, 'green')
                formatted_value = self.i18n.format_number(value, 2)
                pdf_content += f"        {label}: {formatted_value}\n"

        return pdf_content.encode('utf-8')

    def generate_excel_report(self, unified_data: Dict[str, Any]) -> bytes:
        """
        Generate localized Excel report.

        Args:
            unified_data: Project data

        Returns:
            Excel content as bytes
        """
        # This would use openpyxl in production
        # For now, return placeholder
        project_name = unified_data.get("metadata", {}).get("project_name", "Project")
        excel_content = f"Excel Report for {project_name}"
        return excel_content.encode('utf-8')

    def generate_word_report(self, unified_data: Dict[str, Any]) -> bytes:
        """
        Generate localized Word report.

        Args:
            unified_data: Project data

        Returns:
            Word content as bytes
        """
        # This would use python-docx in production
        # For now, return placeholder
        project_name = unified_data.get("metadata", {}).get("project_name", "Project")
        word_content = f"Word Report for {project_name}"
        return word_content.encode('utf-8')

    def _t(self, key: str, namespace: str = 'common') -> str:
        """
        Internal translation helper.

        Args:
            key: Translation key
            namespace: Translation namespace

        Returns:
            Translated string
        """
        return self.i18n.translate(key, namespace)

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of languages for report generation.

        Returns:
            List of supported languages
        """
        return self.i18n.get_supported_languages()

    def validate_language(self, language: str) -> bool:
        """
        Validate that language is supported.

        Args:
            language: Language code

        Returns:
            True if language is supported
        """
        return self.i18n.set_language(language)


class ReportLocalizationHelper:
    """Helper class for localizing report content."""

    def __init__(self, i18n_service):
        self.i18n = i18n_service

    def localize_section(self, section_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Localize a report section.

        Args:
            section_key: Section translation key
            data: Section data

        Returns:
            Localized section
        """
        localized = {
            'title': self.i18n.translate(section_key, 'reports'),
            'data': {}
        }

        for key, value in data.items():
            # Try to translate the key
            translated_key = self.i18n.translate(key, 'common')

            # Format the value based on type
            if isinstance(value, float):
                if 'currency' in key or 'cost' in key or 'price' in key:
                    formatted_value = self.i18n.format_currency(value)
                else:
                    formatted_value = self.i18n.format_number(value, 2)
            elif isinstance(value, int):
                formatted_value = self.i18n.format_number(value, 0)
            elif isinstance(value, dict) and 'year' in value:
                formatted_value = self.i18n.format_date(
                    value.get('date', datetime.now()),
                    'short'
                )
            else:
                formatted_value = str(value)

            localized['data'][translated_key] = formatted_value

        return localized

    def localize_table(self, table_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Localize table headers and data.

        Args:
            table_data: Table data with headers and rows

        Returns:
            Localized table
        """
        localized_table = []

        for row in table_data:
            localized_row = {}
            for key, value in row.items():
                # Translate header
                translated_key = self.i18n.translate(key, 'common')

                # Format value
                if isinstance(value, float):
                    formatted_value = self.i18n.format_number(value, 2)
                elif isinstance(value, int):
                    formatted_value = self.i18n.format_number(value, 0)
                else:
                    formatted_value = str(value)

                localized_row[translated_key] = formatted_value

            localized_table.append(localized_row)

        return localized_table

    def localize_date(self, date: datetime, format_key: str = 'short') -> str:
        """
        Localize a date.

        Args:
            date: Date to localize
            format_key: Format key

        Returns:
            Localized date string
        """
        return self.i18n.format_date(date, format_key)

    def localize_number(self, number: float, decimals: int = 2) -> str:
        """
        Localize a number.

        Args:
            number: Number to localize
            decimals: Decimal places

        Returns:
            Localized number string
        """
        return self.i18n.format_number(number, decimals)

    def localize_currency(self, amount: float, currency_code: str = None) -> str:
        """
        Localize currency.

        Args:
            amount: Amount to localize
            currency_code: Currency code

        Returns:
            Localized currency string
        """
        return self.i18n.format_currency(amount, currency_code)
