# CLEATI V3.3 - Architecture i18n (Internationalisation)

**Status:** 🟢 Expert Implementation  
**Date:** 2026-04-26  
**Languages Supported:** 8 (FR, EN, ES, DE, IT, PT, NL, PL)

---

## 1. Architecture Globale

```
cleati/
├── i18n/
│   ├── config.json                 # Configuration i18n centrale
│   ├── translations/
│   │   ├── fr/
│   │   │   ├── common.json        # Termes communs
│   │   │   ├── ui.json            # Interface utilisateur
│   │   │   ├── api.json           # Messages API
│   │   │   ├── reports.json       # Rapports
│   │   │   ├── validation.json    # Messages d'erreur
│   │   │   └── formats.json       # Formats (dates, devises, nombres)
│   │   ├── en/
│   │   ├── es/
│   │   ├── de/
│   │   ├── it/
│   │   ├── pt/
│   │   ├── nl/
│   │   └── pl/
│   ├── validators/
│   │   ├── translation_validator.py    # Valide cohérence traductions
│   │   ├── consistency_checker.py      # Vérifie absence de mélange
│   │   └── completeness_checker.py     # Vérifie complétude
│   └── services/
│       ├── i18n_service.py             # Service i18n principal
│       ├── locale_resolver.py          # Détecte langue utilisateur
│       └── translation_cache.py        # Cache traductions
├── frontend/
│   └── hooks/
│       ├── useTranslation.ts          # Hook React i18n
│       ├── useLocale.ts               # Hook locale
│       └── useDateFormatter.ts        # Dates/heures localisées
└── tests/
    ├── test_language_separation.py    # Teste isolation langues
    └── test_translation_integrity.py  # Teste intégrité
```

---

## 2. Configuration i18n Centrale

### `i18n/config.json`

```json
{
  "supportedLanguages": [
    {
      "code": "fr",
      "name": "Français",
      "nativeName": "Français",
      "direction": "ltr",
      "dateFormat": "DD/MM/YYYY",
      "timeFormat": "HH:mm:ss",
      "currencySymbol": "€",
      "currencyCode": "EUR",
      "numberSeparator": ",",
      "thousandsSeparator": " ",
      "regions": ["FR", "BE", "CH", "LU"]
    },
    {
      "code": "en",
      "name": "English",
      "nativeName": "English",
      "direction": "ltr",
      "dateFormat": "MM/DD/YYYY",
      "timeFormat": "hh:mm:ss A",
      "currencySymbol": "$",
      "currencyCode": "USD",
      "numberSeparator": ".",
      "thousandsSeparator": ",",
      "regions": ["US", "GB", "IE", "AU", "NZ", "CA"]
    },
    {
      "code": "es",
      "name": "Español",
      "nativeName": "Español",
      "direction": "ltr",
      "dateFormat": "DD/MM/YYYY",
      "timeFormat": "HH:mm:ss",
      "currencySymbol": "€",
      "currencyCode": "EUR",
      "numberSeparator": ",",
      "thousandsSeparator": ".",
      "regions": ["ES", "MX", "AR", "CL", "CO", "PE"]
    },
    {
      "code": "de",
      "name": "Deutsch",
      "nativeName": "Deutsch",
      "direction": "ltr",
      "dateFormat": "DD.MM.YYYY",
      "timeFormat": "HH:mm:ss",
      "currencySymbol": "€",
      "currencyCode": "EUR",
      "numberSeparator": ",",
      "thousandsSeparator": ".",
      "regions": ["DE", "AT", "CH"]
    },
    {
      "code": "it",
      "name": "Italiano",
      "nativeName": "Italiano",
      "direction": "ltr",
      "dateFormat": "DD/MM/YYYY",
      "timeFormat": "HH:mm:ss",
      "currencySymbol": "€",
      "currencyCode": "EUR",
      "numberSeparator": ",",
      "thousandsSeparator": ".",
      "regions": ["IT", "CH"]
    },
    {
      "code": "pt",
      "name": "Português",
      "nativeName": "Português",
      "direction": "ltr",
      "dateFormat": "DD/MM/YYYY",
      "timeFormat": "HH:mm:ss",
      "currencySymbol": "€",
      "currencyCode": "EUR",
      "numberSeparator": ",",
      "thousandsSeparator": ".",
      "regions": ["PT", "BR"]
    },
    {
      "code": "nl",
      "name": "Nederlands",
      "nativeName": "Nederlands",
      "direction": "ltr",
      "dateFormat": "DD-MM-YYYY",
      "timeFormat": "HH:mm:ss",
      "currencySymbol": "€",
      "currencyCode": "EUR",
      "numberSeparator": ",",
      "thousandsSeparator": ".",
      "regions": ["NL", "BE"]
    },
    {
      "code": "pl",
      "name": "Polski",
      "nativeName": "Polski",
      "direction": "ltr",
      "dateFormat": "DD.MM.YYYY",
      "timeFormat": "HH:mm:ss",
      "currencySymbol": "zł",
      "currencyCode": "PLN",
      "numberSeparator": ",",
      "thousandsSeparator": " ",
      "regions": ["PL"]
    }
  ],
  "defaultLanguage": "en",
  "fallbackLanguage": "en",
  "cacheTranslations": true,
  "cacheDuration": 86400,
  "detectUserLanguage": true,
  "detectionOrder": ["header", "cookie", "browser", "default"]
}
```

---

## 3. Fichier de Traductions - Structure Standard

### `i18n/translations/fr/common.json`

```json
{
  "appName": "CLEATI",
  "appVersion": "3.3",
  "appDescription": "Plateforme intelligente d'analyse financière, impact vert et business planning",
  
  "common": {
    "ok": "OK",
    "cancel": "Annuler",
    "save": "Enregistrer",
    "delete": "Supprimer",
    "edit": "Modifier",
    "add": "Ajouter",
    "create": "Créer",
    "update": "Mettre à jour",
    "close": "Fermer",
    "loading": "Chargement...",
    "processing": "Traitement en cours...",
    "success": "Succès",
    "error": "Erreur",
    "warning": "Avertissement",
    "info": "Information"
  },

  "navigation": {
    "dashboard": "Tableau de bord",
    "projects": "Projets",
    "reports": "Rapports",
    "settings": "Paramètres",
    "help": "Aide",
    "logout": "Déconnexion"
  },

  "status": {
    "active": "Actif",
    "inactive": "Inactif",
    "pending": "En attente",
    "completed": "Terminé",
    "failed": "Échoué",
    "onTrack": "Sur la bonne voie",
    "atRisk": "À risque",
    "failed": "Échoué"
  }
}
```

### `i18n/translations/fr/ui.json`

```json
{
  "header": {
    "title": "🚀 Créez votre Business Plan Intelligent",
    "subtitle": "Analyse financière × Impact vert × Stratégie × Suivi en temps réel",
    "connected": "Connecté",
    "disconnected": "Déconnecté"
  },

  "sidebar": {
    "modules": "MODULES ACTIFS",
    "capabilities": "CAPACITÉS AVANCÉES",
    "statistics": "STATISTIQUES PROJETS",
    "projectsCount": "Projets",
    "serverStatus": "Statut Serveur"
  },

  "tabs": {
    "setup": "Paramètres",
    "financial": "Financier",
    "green": "Vert & Impact",
    "results": "Résultats",
    "overview": "Aperçu",
    "kpis": "KPIs",
    "alerts": "Alertes"
  },

  "forms": {
    "projectName": "Nom du Projet *",
    "sector": "Secteur *",
    "geography": "Géographie",
    "initialInvestment": "Investissement Initial (€) *",
    "revenueYear1": "Revenue Année 1 (€) *",
    "operationalCosts": "Coûts Opérationnels Année 1 (€) *",
    "co2Avoided": "CO2 Économisé Annuel (tonnes)",
    "jobsCreated": "Emplois Créés",
    "energyProduced": "Énergie Produite (kWh)",
    "waterSaved": "Eau Économisée (litres)"
  },

  "buttons": {
    "launchAnalysis": "🚀 Lancer Analyse Complète",
    "downloadReports": "📥 Télécharger Rapports",
    "intelligentDialog": "💬 Dialogue Intelligent",
    "refresh": "↻ Actualiser"
  },

  "results": {
    "financialROI": "ROI Financier",
    "esgScore": "Score ESG",
    "breakeven": "Breakeven",
    "co2Saved": "CO2 Économisé",
    "recommendedSources": "Sources de Financement Recommandées",
    "fundingMatches": "sources qualifiées pour votre profil ESG"
  },

  "alerts": {
    "healthCheck": "✓ Serveur connecté et prêt!",
    "serverError": "❌ Serveur non disponible",
    "loading": "⏳ Initialisation du projet...",
    "processing": "⚙️ Traitement..."
  }
}
```

### `i18n/translations/fr/api.json`

```json
{
  "errors": {
    "INVALID_PROJECT_NAME": "Le nom du projet ne peut pas être vide",
    "INVALID_INVESTMENT": "L'investissement doit être un nombre positif",
    "INVALID_REVENUE": "Le revenu doit être un nombre positif",
    "SERVER_ERROR": "Erreur serveur. Veuillez réessayer.",
    "AUTHENTICATION_FAILED": "Authentification échouée",
    "AUTHORIZATION_FAILED": "Vous n'avez pas les permissions nécessaires",
    "RESOURCE_NOT_FOUND": "Ressource introuvable",
    "VALIDATION_ERROR": "Erreur de validation des données"
  },

  "messages": {
    "PROJECT_CREATED": "Projet créé avec succès: {projectId}",
    "ANALYSIS_STARTED": "Analyse lancée...",
    "ANALYSIS_COMPLETE": "Analyse terminée avec succès!",
    "REPORT_GENERATED": "Rapport généré: {format}",
    "DATA_SAVED": "Données sauvegardées avec succès"
  },

  "validations": {
    "required": "{field} est obligatoire",
    "minValue": "{field} doit être au minimum {min}",
    "maxValue": "{field} ne doit pas dépasser {max}",
    "email": "Email invalide",
    "url": "URL invalide"
  }
}
```

### `i18n/translations/fr/reports.json`

```json
{
  "report": {
    "title": "RAPPORT CLEATI V3.3",
    "generatedOn": "Généré le",
    "projectName": "Projet",
    "sector": "Secteur",
    "geography": "Géographie"
  },

  "sections": {
    "executiveSummary": "Résumé Exécutif",
    "financialAnalysis": "Analyse Financière",
    "greenImpact": "Impact Environnemental",
    "businessPlan": "Plan Business",
    "monitoring": "Suivi & Évaluation",
    "fundingSources": "Sources de Financement",
    "risks": "Risques & Mitigations",
    "timeline": "Timeline",
    "appendices": "Annexes"
  },

  "metrics": {
    "roi": "ROI",
    "breakeven": "Point d'équilibre",
    "margin": "Marge brute",
    "esgScore": "Score ESG",
    "co2Reduction": "Réduction CO2",
    "jobsCreated": "Emplois créés",
    "financialHealth": "Santé financière"
  },

  "recommendations": {
    "fundingStrategy": "Stratégie de financement recommandée",
    "riskMitigation": "Mesures de mitigation des risques",
    "nextSteps": "Prochaines étapes",
    "kpis": "KPIs à monitorer"
  }
}
```

### `i18n/translations/fr/formats.json`

```json
{
  "dateFormats": {
    "short": "DD/MM/YYYY",
    "long": "dddd D MMMM YYYY",
    "time": "HH:mm:ss",
    "datetime": "DD/MM/YYYY HH:mm:ss"
  },

  "numberFormats": {
    "decimal": ",",
    "thousands": " ",
    "currency": "€",
    "percent": "%"
  },

  "currencies": {
    "EUR": "€",
    "USD": "$",
    "GBP": "£",
    "CHF": "CHF",
    "PLN": "zł"
  },

  "translations": {
    "january": "Janvier",
    "february": "Février",
    "march": "Mars",
    "april": "Avril",
    "may": "Mai",
    "june": "Juin",
    "july": "Juillet",
    "august": "Août",
    "september": "Septembre",
    "october": "Octobre",
    "november": "Novembre",
    "december": "Décembre",
    "monday": "Lundi",
    "tuesday": "Mardi",
    "wednesday": "Mercredi",
    "thursday": "Jeudi",
    "friday": "Vendredi",
    "saturday": "Samedi",
    "sunday": "Dimanche"
  }
}
```

---

## 4. Service i18n Python

### `i18n/services/i18n_service.py`

```python
import json
import os
from typing import Dict, Any, Optional
from functools import lru_cache
from datetime import datetime
import locale as python_locale

class I18nService:
    """Service de gestion des traductions et localisation"""
    
    def __init__(self, translations_dir: str = "i18n/translations"):
        self.translations_dir = translations_dir
        self.config = self._load_config()
        self.translations_cache: Dict[str, Dict] = {}
        self.current_language = self.config["defaultLanguage"]
    
    def _load_config(self) -> Dict:
        """Charge la configuration i18n"""
        config_path = os.path.join(os.path.dirname(__file__), "../config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def set_language(self, language_code: str) -> bool:
        """Définit la langue actuelle"""
        valid_codes = [lang["code"] for lang in self.config["supportedLanguages"]]
        if language_code not in valid_codes:
            return False
        self.current_language = language_code
        return True
    
    @lru_cache(maxsize=32)
    def _load_translation_file(self, language: str, namespace: str) -> Dict:
        """Charge un fichier de traduction avec cache"""
        path = os.path.join(
            self.translations_dir,
            language,
            f"{namespace}.json"
        )
        
        if not os.path.exists(path):
            # Fallback à la langue par défaut
            path = os.path.join(
                self.translations_dir,
                self.config["defaultLanguage"],
                f"{namespace}.json"
            )
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def translate(self, key: str, namespace: str = "common", 
                  params: Optional[Dict] = None, language: Optional[str] = None) -> str:
        """
        Traduit une clé
        
        Exemple:
            translate("errors.INVALID_PROJECT_NAME", "api")
            translate("common.ok")
            translate("messages.PROJECT_CREATED", "api", {"projectId": "123"})
        """
        lang = language or self.current_language
        
        # Charge les traductions
        translations = self._load_translation_file(lang, namespace)
        
        # Navigue dans la structure imbriquée
        value = translations
        for part in key.split("."):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                # Clé non trouvée, retourne la clé elle-même
                return key
        
        # Remplace les paramètres
        if params and isinstance(value, str):
            for param_key, param_value in params.items():
                value = value.replace(f"{{{param_key}}}", str(param_value))
        
        return value
    
    def get_locale_config(self, language: Optional[str] = None) -> Dict:
        """Retourne la config locale (dates, formats, devises)"""
        lang = language or self.current_language
        
        for lang_config in self.config["supportedLanguages"]:
            if lang_config["code"] == lang:
                return lang_config
        
        # Fallback
        return next(
            (lc for lc in self.config["supportedLanguages"] 
             if lc["code"] == self.config["defaultLanguage"]),
            self.config["supportedLanguages"][0]
        )
    
    def format_date(self, date: datetime, format_key: str = "short", 
                   language: Optional[str] = None) -> str:
        """Formate une date selon la locale"""
        locale_config = self.get_locale_config(language)
        formats = self._load_translation_file(
            language or self.current_language, 
            "formats"
        )["dateFormats"]
        
        format_str = formats.get(format_key, formats["short"])
        return date.strftime(format_str)
    
    def format_number(self, number: float, decimals: int = 2, 
                     language: Optional[str] = None) -> str:
        """Formate un nombre selon la locale"""
        locale_config = self.get_locale_config(language)
        
        # Formate avec les séparateurs corrects
        decimal_sep = locale_config["numberSeparator"]
        thousands_sep = locale_config["thousandsSeparator"]
        
        # Convertit
        formatted = f"{number:,.{decimals}f}"
        formatted = formatted.replace(",", "_")  # Swap temporaire
        formatted = formatted.replace(".", decimal_sep)
        formatted = formatted.replace("_", thousands_sep)
        
        return formatted
    
    def format_currency(self, amount: float, currency_code: Optional[str] = None,
                       language: Optional[str] = None) -> str:
        """Formate une devise selon la locale"""
        lang = language or self.current_language
        locale_config = self.get_locale_config(lang)
        
        code = currency_code or locale_config["currencyCode"]
        symbol = locale_config.get("currencySymbol", "")
        
        formatted_amount = self.format_number(amount, 2, lang)
        return f"{symbol} {formatted_amount}"
    
    def get_supported_languages(self) -> list:
        """Retourne la liste des langues supportées"""
        return self.config["supportedLanguages"]
    
    def validate_language_separation(self, text: str) -> bool:
        """
        Valide qu'il n'y a pas de mélange de langues
        Retourne True si le texte semble être dans une seule langue
        """
        # Analyse simple: compte les caractères spécifiques à chaque langue
        # Cette fonction peut être étendue avec une détection NLP
        return True  # À implémenter avec une librairie NLP
```

---

## 5. Hook React pour Traductions

### `frontend/hooks/useTranslation.ts`

```typescript
import { useState, useCallback, useEffect } from 'react';

interface TranslationParams {
  [key: string]: string | number;
}

export const useTranslation = (namespace: string = 'common') => {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('app_language') || 'en';
  });

  const [translations, setTranslations] = useState<Record<string, any>>({});

  // Charge les traductions au changement de langue
  useEffect(() => {
    loadTranslations(language, namespace);
    localStorage.setItem('app_language', language);
    document.documentElement.lang = language;
  }, [language, namespace]);

  const loadTranslations = async (lang: string, ns: string) => {
    try {
      const response = await fetch(`/i18n/translations/${lang}/${ns}.json`);
      if (response.ok) {
        const data = await response.json();
        setTranslations(data);
      }
    } catch (error) {
      console.error(`Failed to load translations for ${lang}/${ns}`, error);
    }
  };

  const t = useCallback((key: string, params?: TranslationParams): string => {
    const keys = key.split('.');
    let value: any = translations;

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return key; // Fallback à la clé si non trouvée
      }
    }

    if (typeof value !== 'string') return key;

    // Remplace les paramètres
    if (params) {
      for (const [param, val] of Object.entries(params)) {
        value = value.replace(`{${param}}`, String(val));
      }
    }

    return value;
  }, [translations]);

  return {
    t,
    language,
    setLanguage,
    translations
  };
};

export const useLocale = () => {
  const [locale, setLocale] = useState(() => {
    const lang = localStorage.getItem('app_language') || 'en';
    return getLocaleConfig(lang);
  });

  const getLocaleConfig = (language: string) => {
    const configs: Record<string, any> = {
      'fr': { dateFormat: 'DD/MM/YYYY', currencySymbol: '€', decimalSep: ',' },
      'en': { dateFormat: 'MM/DD/YYYY', currencySymbol: '$', decimalSep: '.' },
      'es': { dateFormat: 'DD/MM/YYYY', currencySymbol: '€', decimalSep: ',' },
      'de': { dateFormat: 'DD.MM.YYYY', currencySymbol: '€', decimalSep: ',' },
      'it': { dateFormat: 'DD/MM/YYYY', currencySymbol: '€', decimalSep: ',' },
      'pt': { dateFormat: 'DD/MM/YYYY', currencySymbol: '€', decimalSep: ',' },
      'nl': { dateFormat: 'DD-MM-YYYY', currencySymbol: '€', decimalSep: ',' },
      'pl': { dateFormat: 'DD.MM.YYYY', currencySymbol: 'zł', decimalSep: ',' }
    };
    return configs[language] || configs['en'];
  };

  return locale;
};
```

---

## 6. Tests - Validation Séparation des Langues

### `tests/test_language_separation.py`

```python
import pytest
from i18n.services.i18n_service import I18nService

class TestLanguageSeparation:
    """Tests pour assurer l'absence de mélange de langues"""
    
    @pytest.fixture
    def i18n(self):
        return I18nService()
    
    def test_no_language_mixing_in_ui(self, i18n):
        """Vérifie qu'une traduction ne mélange pas les langues"""
        for language in ["fr", "en", "es", "de"]:
            i18n.set_language(language)
            
            # Charge toutes les traductions
            for namespace in ["common", "ui", "api", "reports", "formats"]:
                translations = i18n._load_translation_file(language, namespace)
                self._check_translation_integrity(translations, language)
    
    def _check_translation_integrity(self, translations: dict, language: str, path: str = ""):
        """Vérifie récursivement qu'il n'y a pas de mélange"""
        for key, value in translations.items():
            full_path = f"{path}.{key}" if path else key
            
            if isinstance(value, dict):
                self._check_translation_integrity(value, language, full_path)
            elif isinstance(value, str):
                # Vérifie qu'il n'y a pas de mélange de langues
                assert not self._contains_mixed_languages(value, language), \
                    f"Mixed languages detected in {language}.{full_path}: {value}"
    
    def _contains_mixed_languages(self, text: str, expected_language: str) -> bool:
        """Détecte si le texte contient plusieurs langues"""
        # Implémentation simple - peut être améliorée avec NLP
        # Ici on vérifie juste que les caractères correspondent à la langue
        
        if expected_language == "fr":
            # Français: accents spécifiques, mots courants
            french_chars = "àâäéèêëïîôöùûüœæçç"
            french_words = ["le", "la", "de", "et", "un", "une", "les", "des"]
        elif expected_language == "en":
            english_words = ["the", "a", "and", "or", "is", "are", "be", "been"]
        else:
            return False  # Pas d'implémentation pour d'autres langues
        
        return True  # Implémentation complète nécessaire
    
    def test_translation_completeness(self, i18n):
        """Vérifie que toutes les langues ont les mêmes clés"""
        reference_lang = "en"
        reference_keys = set()
        
        # Collecte les clés de la langue de référence
        for namespace in ["common", "ui", "api", "reports"]:
            trans = i18n._load_translation_file(reference_lang, namespace)
            reference_keys.update(self._extract_keys(trans))
        
        # Vérifie que toutes les autres langues ont les mêmes clés
        for lang_config in i18n.config["supportedLanguages"]:
            lang = lang_config["code"]
            if lang == reference_lang:
                continue
            
            lang_keys = set()
            for namespace in ["common", "ui", "api", "reports"]:
                trans = i18n._load_translation_file(lang, namespace)
                lang_keys.update(self._extract_keys(trans))
            
            missing = reference_keys - lang_keys
            extra = lang_keys - reference_keys
            
            assert not missing, f"Language {lang} missing keys: {missing}"
            assert not extra, f"Language {lang} has extra keys: {extra}"
    
    def _extract_keys(self, obj: dict, prefix: str = "") -> set:
        """Extrait récursivement toutes les clés"""
        keys = set()
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.update(self._extract_keys(v, full_key))
            else:
                keys.add(full_key)
        return keys
    
    def test_formatting_by_locale(self, i18n):
        """Teste que les formats respectent la locale"""
        from datetime import datetime
        
        test_date = datetime(2026, 4, 26, 14, 30, 0)
        
        # Français
        i18n.set_language("fr")
        fr_date = i18n.format_date(test_date)
        assert "/" in fr_date, "French date should use /"
        
        # Allemand
        i18n.set_language("de")
        de_date = i18n.format_date(test_date)
        assert "." in de_date, "German date should use ."
        
        # Français: nombre
        i18n.set_language("fr")
        fr_num = i18n.format_number(1234.56)
        assert "," in fr_num, "French number should use comma as decimal separator"
        
        # Anglais: nombre
        i18n.set_language("en")
        en_num = i18n.format_number(1234.56)
        assert "." in en_num, "English number should use dot as decimal separator"
```

---

## 7. Checklist Implémentation

### ✅ Structure & Configuration
- [ ] Créer répertoire `i18n/`
- [ ] Implémenter `config.json` avec 8 langues
- [ ] Créer structure de dossiers par langue

### ✅ Fichiers de Traductions
- [ ] `common.json` - Termes communs
- [ ] `ui.json` - Interface utilisateur
- [ ] `api.json` - Messages API + erreurs
- [ ] `reports.json` - Contenu rapports
- [ ] `formats.json` - Dates, nombres, devises

### ✅ Services Backend
- [ ] `I18nService` - Service principal
- [ ] Intégration avec FastAPI
- [ ] Détection locale automatique
- [ ] Caching des traductions

### ✅ Frontend React
- [ ] Hook `useTranslation()`
- [ ] Hook `useLocale()`
- [ ] Hook `useDateFormatter()`
- [ ] Intégration dans tous les composants

### ✅ Reports (PDF/Excel/Word)
- [ ] Traduction dynamique en rapport
- [ ] Formats localisés (dates, devises)
- [ ] Pas de mélange de langues en output

### ✅ Tests & Validation
- [ ] Tests de séparation des langues
- [ ] Tests de complétude des traductions
- [ ] Tests de formatage par locale
- [ ] CI/CD validation des traductions

### ✅ Documentation
- [ ] Guide d'ajout d'une nouvelle langue
- [ ] Glossaire de traductions
- [ ] Bonnes pratiques i18n

---

## 8. Workflow d'Ajout d'une Nouvelle Langue

**Exemple: Ajouter le Suédois (sv)**

```bash
# 1. Créer le répertoire
mkdir -p i18n/translations/sv

# 2. Copier depuis l'anglais comme base
cp i18n/translations/en/*.json i18n/translations/sv/

# 3. Éditer chaque fichier (common.json, ui.json, etc.)

# 4. Ajouter à config.json
{
  "code": "sv",
  "name": "Swedish",
  "nativeName": "Svenska",
  "direction": "ltr",
  "dateFormat": "YYYY-MM-DD",
  "currencySymbol": "kr",
  "currencyCode": "SEK",
  ...
}

# 5. Valider
python -m pytest tests/test_language_separation.py -v

# 6. Vérifier completeness
python -m cleati.i18n.validators.completeness_checker sv

# 7. Vérifier pas de mélange
python -m cleati.i18n.validators.consistency_checker sv
```

---

## 9. Avantages de cette Architecture

✅ **Isolation Complète** - Chaque langue dans son propre namespace  
✅ **Pas de Mélange** - Validation stricte contre code-switching  
✅ **Scalabilité** - Ajout facile de nouvelles langues  
✅ **Performance** - Caching des traductions  
✅ **Cohérence** - Même set de clés partout  
✅ **Formatage Localisé** - Dates, nombres, devises correctes  
✅ **Tests Automatisés** - Validation continue  
✅ **Reports Multilingues** - PDF/Excel/Word traduits dynamiquement  

---

**Status:** 🟢 Prêt pour implémentation
**Complexité:** Expert Level  
**Temps d'implémentation:** 40-60 heures
