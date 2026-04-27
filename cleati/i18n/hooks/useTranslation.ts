/**
 * useTranslation Hook
 * React hook for accessing translation functionality in components
 */

import { useState, useCallback } from 'react';

interface TranslationParams {
  [key: string]: string | number;
}

interface UseTranslationReturn {
  t: (key: string, namespace?: string, params?: TranslationParams) => string;
  language: string;
  setLanguage: (lang: string) => void;
  i18n: any;
}

let globalI18n: any = null;

export function setGlobalI18n(i18nInstance: any) {
  globalI18n = i18nInstance;
}

/**
 * useTranslation Hook
 * Provides translation functionality to React components
 *
 * Usage:
 *   const { t, language, setLanguage } = useTranslation();
 *
 *   // Simple translation
 *   <h1>{t('app_name')}</h1>
 *
 *   // With namespace
 *   <label>{t('project_name', 'ui')}</label>
 *
 *   // With parameters
 *   <p>{t('greeting', 'common', { name: 'John' })}</p>
 */
export function useTranslation(): UseTranslationReturn {
  const [, setUpdateTrigger] = useState(0);

  const t = useCallback((
    key: string,
    namespace: string = 'common',
    params?: TranslationParams
  ): string => {
    if (!globalI18n) {
      console.warn('i18n service not initialized');
      return key;
    }

    return globalI18n.translate(key, namespace, params);
  }, []);

  const language = globalI18n?.current_language || 'en';

  const setLanguage = useCallback((lang: string) => {
    if (!globalI18n) return;

    const success = globalI18n.set_language(lang);
    if (success) {
      // Trigger re-render
      setUpdateTrigger(prev => prev + 1);
    }
  }, []);

  return {
    t,
    language,
    setLanguage,
    i18n: globalI18n
  };
}

export default useTranslation;
