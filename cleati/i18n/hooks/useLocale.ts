/**
 * useLocale Hook
 * React hook for accessing locale-specific formatting in components
 */

import { useState, useCallback } from 'react';

interface LocaleConfig {
  locale: string;
  dateFormat: string;
  timeFormat: string;
  numberSeparator: string;
  thousandsSeparator: string;
  currencySymbol: string;
  currencyPosition: string;
  currencyCode: string;
  [key: string]: any;
}

interface UseLocaleReturn {
  locale: LocaleConfig;
  formatDate: (date: Date, formatKey?: string) => string;
  formatNumber: (number: number, decimals?: number) => string;
  formatCurrency: (amount: number, currencyCode?: string) => string;
  language: string;
}

let globalI18n: any = null;

export function setGlobalI18nForLocale(i18nInstance: any) {
  globalI18n = i18nInstance;
}

/**
 * useLocale Hook
 * Provides locale-specific formatting to React components
 *
 * Usage:
 *   const { locale, formatDate, formatNumber, formatCurrency } = useLocale();
 *
 *   // Format date
 *   <span>{formatDate(new Date(), 'long')}</span>
 *
 *   // Format number
 *   <span>{formatNumber(1234.56, 2)}</span>
 *
 *   // Format currency
 *   <span>{formatCurrency(1000.00, 'EUR')}</span>
 */
export function useLocale(): UseLocaleReturn {
  const [, setUpdateTrigger] = useState(0);

  const locale: LocaleConfig = globalI18n?.get_locale_config() || {
    locale: 'en-US',
    dateFormat: 'MM/dd/yyyy',
    timeFormat: 'h:mm a',
    numberSeparator: '.',
    thousandsSeparator: ',',
    currencySymbol: '$',
    currencyPosition: 'before',
    currencyCode: 'USD'
  };

  const formatDate = useCallback((date: Date, formatKey: string = 'short'): string => {
    if (!globalI18n) return date.toISOString();
    return globalI18n.format_date(date, formatKey);
  }, []);

  const formatNumber = useCallback((number: number, decimals: number = 2): string => {
    if (!globalI18n) return number.toFixed(decimals);
    return globalI18n.format_number(number, decimals);
  }, []);

  const formatCurrency = useCallback((amount: number, currencyCode?: string): string => {
    if (!globalI18n) return `$${amount.toFixed(2)}`;
    return globalI18n.format_currency(amount, currencyCode);
  }, []);

  const language = globalI18n?.current_language || 'en';

  return {
    locale,
    formatDate,
    formatNumber,
    formatCurrency,
    language
  };
}

export default useLocale;
