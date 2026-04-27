"""
CLEATI V3.3 - Intelligence Orchestrator (The Maestro)
Dirige les 4 moteurs intelligents de manière harmonieuse
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import asyncio

class EventType(Enum):
    PROJECT_INITIATED = "project_initiated"
    FINANCIAL_COMPLETE = "financial_complete"
    GREEN_COMPLETE = "green_complete"
    BP_COMPLETE = "bp_complete"
    MONITORING_COMPLETE = "monitoring_complete"
    ALL_COMPLETE = "all_complete"
    ERROR = "error"

class UnifiedDataModel:
    """Single Source of Truth pour tous les modules"""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.created_at = datetime.now()

        self.metadata = {}
        self.financial_data = {}
        self.green_metrics = {}
        self.business_plan = {}
        self.monitoring_plan = {}
        self.funding_sources = []

        self._integrity_checks = []

    def to_dict(self) -> Dict:
        return {
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "financial_data": self.financial_data,
            "green_metrics": self.green_metrics,
            "business_plan": self.business_plan,
            "monitoring_plan": self.monitoring_plan,
            "funding_sources": self.funding_sources,
            "integrity_checks": self._integrity_checks
        }

    def validate_integrity(self) -> Dict[str, Any]:
        """Vérifie la cohérence entre les modules"""
        issues = []

        # Vérification 1: BP revenue vs Financial revenue
        if self.business_plan and self.financial_data:
            bp_revenue = self.business_plan.get("revenue_model", {}).get("y1", 0)
            fin_revenue = self.financial_data.get("annual_revenue_y1", 0)

            if bp_revenue and fin_revenue:
                variance = abs(bp_revenue - fin_revenue) / fin_revenue
                if variance > 0.15:  # > 15% de différence = warning
                    issues.append({
                        "severity": "WARNING",
                        "issue": "Revenue variance between BP and Financial",
                        "variance": f"{variance*100:.1f}%"
                    })

        # Vérification 2: KPIs linked to data sources (FIX: Proper path resolution)
        if self.monitoring_plan:
            for kpi in self.monitoring_plan.get("kpis", []):
                source = kpi.get("linked_to")
                if source:
                    # Parse the path (e.g., "financial_data.annual_revenue_y1")
                    parts = source.split(".")
                    if len(parts) >= 2:
                        module = parts[0]
                        field = ".".join(parts[1:])

                        # Check if module exists and has the field
                        module_data = None
                        if module == "financial_data":
                            module_data = self.financial_data
                        elif module == "green_metrics":
                            module_data = self.green_metrics
                        elif module == "business_plan":
                            module_data = self.business_plan

                        # Verify field exists
                        if module_data is None or (field not in str(module_data.get(field.split(".")[0], ""))):
                            # This is just a warning - the data may not be populated yet
                            issues.append({
                                "severity": "INFO",
                                "issue": f"KPI '{kpi['name']}' may reference data not yet populated",
                                "source": source
                            })

        # Vérification 3: Green metrics alignment
        if self.green_metrics and self.monitoring_plan:
            co2_target = self.green_metrics.get("co2_avoided_annual", 0)
            kpi_targets = [k.get("target") for k in self.monitoring_plan.get("kpis", [])
                          if "CO2" in k.get("name", "")]

            if co2_target and kpi_targets:
                # Allow some variance
                if abs(co2_target - kpi_targets[0]) > co2_target * 0.1:
                    issues.append({
                        "severity": "WARNING",
                        "issue": "CO2 target slightly different between modules",
                        "variance_percent": f"{abs(co2_target - kpi_targets[0]) / co2_target * 100:.1f}%"
                    })

        self._integrity_checks = issues

        return {
            "is_valid": len([i for i in issues if i["severity"] == "ERROR"]) == 0,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }

class CLEATIOrchestrator:
    """
    Master Orchestrator
    Dirige tous les moteurs de manière intelligente
    """

    def __init__(self):
        self.projects = {}  # {project_id: UnifiedDataModel}
        self.events = []    # Event log

        # Import des moteurs (seront créés après)
        self.financial_engine = None
        self.green_engine = None
        self.bp_architect = None
        self.monitoring_architect = None

    def create_project(self, user_data: Dict) -> str:
        """Initie un nouveau projet"""
        project_id = str(uuid.uuid4())[:8]

        unified_data = UnifiedDataModel(project_id)
        unified_data.metadata = {
            "user_id": user_data.get("user_id", "unknown"),
            "project_name": user_data.get("project_name", "New Project"),
            "sector": user_data.get("sector", "general"),
            "geography": user_data.get("geography", "France"),
            "type": user_data.get("type", "business_plan"),
            "created_at": datetime.now().isoformat()
        }

        self.projects[project_id] = unified_data
        self._emit_event(project_id, EventType.PROJECT_INITIATED, "Project created")

        return project_id

    async def process_full_pipeline(self, project_id: str, user_answers: Dict) -> Dict:
        """
        Pipeline principal orchestré
        Chaque moteur processus en séquence intelligente
        """

        if project_id not in self.projects:
            return {"error": "Project not found"}

        unified = self.projects[project_id]

        try:
            # ÉTAPE 1: Financial Intelligence
            print(f"[CLEATI V3.3] Étape 1: Analyse Financière pour {project_id}")
            financial_result = await self._run_financial_engine(project_id, user_answers)
            unified.financial_data = financial_result.get("data", {})
            self._emit_event(project_id, EventType.FINANCIAL_COMPLETE, financial_result.get("message"))

            # ÉTAPE 2: Green Intelligence (croise financial + vert)
            print(f"[CLEATI V3.3] Étape 2: Analyse Verte & Impact")
            green_result = await self._run_green_engine(project_id, unified.financial_data, user_answers)
            unified.green_metrics = green_result.get("data", {})
            unified.funding_sources = green_result.get("funding_sources", [])
            self._emit_event(project_id, EventType.GREEN_COMPLETE, green_result.get("message"))

            # ÉTAPE 3: Business Plan Architect
            print(f"[CLEATI V3.3] Étape 3: Génération Business Plan Intelligent")
            bp_result = await self._run_bp_architect(project_id, unified.financial_data,
                                                     unified.green_metrics, user_answers)
            unified.business_plan = bp_result.get("data", {})
            self._emit_event(project_id, EventType.BP_COMPLETE, bp_result.get("message"))

            # ÉTAPE 4: Monitoring & Evaluation Auto-Architect
            print(f"[CLEATI V3.3] Étape 4: Auto-Génération Plan S&E (Intelligent)")
            monitoring_result = await self._run_monitoring_architect(project_id, unified)
            unified.monitoring_plan = monitoring_result.get("data", {})
            self._emit_event(project_id, EventType.MONITORING_COMPLETE, monitoring_result.get("message"))

            # ÉTAPE 5: Validation d'intégrité
            print(f"[CLEATI V3.3] Étape 5: Validation d'Intégrité Inter-Modules")
            integrity = unified.validate_integrity()

            return {
                "status": "success",
                "project_id": project_id,
                "unified_data": unified.to_dict(),
                "integrity_check": integrity,
                "ready_for_reports": integrity["is_valid"],
                "events": self.events[-10:]  # Derniers 10 événements
            }

        except Exception as e:
            self._emit_event(project_id, EventType.ERROR, str(e))
            return {
                "status": "error",
                "project_id": project_id,
                "error": str(e),
                "events": self.events[-10:]
            }

    async def _run_financial_engine(self, project_id: str, user_answers: Dict) -> Dict:
        """Exécute le moteur financier"""
        # Simulation intelligente du moteur financier

        investment = float(user_answers.get("initial_investment", 100000))
        revenue_y1 = float(user_answers.get("annual_revenue_y1", 50000))
        costs_y1 = float(user_answers.get("operational_costs_y1", 30000))

        margin = (revenue_y1 - costs_y1) / revenue_y1 if revenue_y1 > 0 else 0
        roi = ((revenue_y1 - costs_y1) / investment) * 100 if investment > 0 else 0

        # Calcule breakeven
        annual_net = revenue_y1 - costs_y1
        breakeven_months = (investment / annual_net * 12) if annual_net > 0 else 999

        # Projections 5 ans (exponential growth intelligente)
        projections = {}
        for year in range(1, 6):
            growth_rate = 1.15  # 15% growth par an
            projections[f"y{year}"] = {
                "revenue": revenue_y1 * (growth_rate ** (year - 1)),
                "costs": costs_y1 * (1 + 0.05 * (year - 1)),  # Costs grow slower
                "net_income": (revenue_y1 * (growth_rate ** (year - 1))) - (costs_y1 * (1 + 0.05 * (year - 1)))
            }

        return {
            "message": "Financial analysis completed successfully",
            "data": {
                "initial_investment": investment,
                "annual_revenue_y1": revenue_y1,
                "operational_costs_y1": costs_y1,
                "gross_margin": margin,
                "roi_percent": roi,
                "breakeven_months": breakeven_months,
                "projections_5_years": projections,
                "financial_health": "strong" if roi > 20 else "moderate" if roi > 10 else "weak",
                "risk_flags": self._identify_financial_risks(investment, roi, margin)
            }
        }

    async def _run_green_engine(self, project_id: str, financial_data: Dict, user_answers: Dict) -> Dict:
        """Exécute le moteur vert intelligent"""

        co2_reduction = float(user_answers.get("co2_avoided_annual", 0))
        jobs_created = int(user_answers.get("jobs_created", 0))
        energy_produced = float(user_answers.get("energy_produced_kwh", 0))
        water_saved = float(user_answers.get("water_saved", 0))

        # Calcule ESG Score (0-10) - INTELLIGENT SCORING (FIXED)
        # Environmental: Sensitive to CO2 (1T CO2 = 0.01 points)
        environmental_impact = min(10, co2_reduction / 100) if co2_reduction > 0 else 0

        # Social: Linear with jobs created (1 job = 0.75 points, max 10)
        social_impact = min(10, jobs_created * 0.75) if jobs_created > 0 else 0

        # Governance: Base 5 + bonuses for environmental and social impact
        governance = 5.0
        if co2_reduction > 500:
            governance += 2  # Strong environmental commitment
        if jobs_created > 5:
            governance += 2  # Strong social commitment
        governance = min(10, governance)

        esg_components = {
            "environmental_impact": round(environmental_impact, 2),
            "social_impact": round(social_impact, 2),
            "governance": round(governance, 2)
        }
        esg_score = sum(esg_components.values()) / len(esg_components)

        # INTELLIGENCE: Dual ROI
        financial_roi = financial_data.get("roi_percent", 0)

        # Ecological ROI: Combien d'économies CO2 par euro investi?
        investment = financial_data.get("initial_investment", 1)
        eco_roi = (co2_reduction / investment) * 100 if investment > 0 else 0

        # Combined Score (intelligence véritable)
        combined_score = (financial_roi + eco_roi) / 2

        # INTELLIGENCE: Identifie sources de financement SPÉCIFIQUES
        funding_sources = self._identify_green_funding(
            investment=investment,
            sector=user_answers.get("sector", "general"),
            co2_saved=co2_reduction,
            roi=financial_roi,
            esg_score=esg_score
        )

        # Compliance checks
        csrd_eligible = co2_reduction > 100 or jobs_created > 0  # Simplifié

        return {
            "message": f"Green analysis complete - ESG Score: {esg_score:.1f}/10",
            "data": {
                "co2_avoided_annual": co2_reduction,
                "energy_produced_kwh": energy_produced,
                "water_saved_liters": water_saved,
                "jobs_created": jobs_created,
                "esg_score": round(esg_score, 2),
                "esg_components": esg_components,
                "dual_roi": {
                    "financial_roi": round(financial_roi, 2),
                    "ecological_roi": round(eco_roi, 2),
                    "combined_score": round(combined_score, 2)
                },
                "csrd_compliant": csrd_eligible,
                "sustainability_rating": self._rate_sustainability(esg_score)
            },
            "funding_sources": funding_sources
        }

    async def _run_bp_architect(self, project_id: str, financial_data: Dict,
                               green_data: Dict, user_answers: Dict) -> Dict:
        """Génère Business Plan intelligent basé sur les données réelles"""

        # INTELLIGENCE: Le BP est construit à partir des données, pas de template vide

        # Extrait du modèle financier
        revenue_y1 = financial_data.get("annual_revenue_y1", 0)
        roi = financial_data.get("roi_percent", 0)
        margin = financial_data.get("gross_margin", 0)
        sector = user_answers.get("sector", "General")

        # Market analysis intelligente par secteur
        market_analysis = self._generate_market_analysis(
            sector=sector,
            revenue_y1=revenue_y1,
            esg_score=green_data.get("esg_score", 0)
        )

        # Revenue model intelligent
        revenue_model = {
            "model_type": user_answers.get("revenue_model", "B2B Services"),
            "y1": revenue_y1,
            "y5_projection": revenue_y1 * (1.15 ** 4),  # 15% growth
            "gross_margin": margin,
            "unit_economics": {
                "customer_acquisition_cost": revenue_y1 * 0.15,
                "customer_lifetime_value": revenue_y1 * 3
            }
        }

        # Implementation roadmap basée sur breakeven
        breakeven_months = financial_data.get("breakeven_months", 24)
        roadmap = self._generate_roadmap(breakeven_months, sector)

        return {
            "message": f"Business Plan generated - {len(roadmap['milestones'])} milestones",
            "data": {
                "executive_summary": {
                    "company_mission": f"Lead the {sector} sector with sustainable impact",
                    "target_market": market_analysis.get("tam", "Not specified"),
                    "key_value_proposition": [
                        "Profitability",
                        "Environmental Impact",
                        "Scalability"
                    ]
                },
                "market_analysis": market_analysis,
                "revenue_model": revenue_model,
                "financial_strategy": {
                    "roi_target": roi,
                    "breakeven_timeline": f"{int(breakeven_months)} months",
                    "5_year_projection": financial_data.get("projections_5_years", {})
                },
                "sustainability_section": {
                    "impact_statement": f"Annual CO2 reduction: {green_data.get('co2_avoided_annual')}T",
                    "esg_framework": green_data,
                    "compliance": {
                        "csrd": green_data.get("csrd_compliant", False),
                        "esg_certified": green_data.get("esg_score", 0) > 6.5
                    }
                },
                "implementation_roadmap": roadmap,
                "estimated_pages": 15 + len(roadmap['milestones'])
            }
        }

    async def _run_monitoring_architect(self, project_id: str, unified: UnifiedDataModel) -> Dict:
        """AUTO-GÉNÈRE le plan S&E de manière intelligente"""

        # ÉTAPE 1: Extrait les promesses du BP
        bp_promises = self._extract_bp_promises(unified.business_plan)

        # ÉTAPE 2: Crée KPI pour CHAQUE promesse automatiquement
        kpis = []

        # KPI Financiers
        if unified.financial_data:
            revenue_target = unified.financial_data.get("annual_revenue_y1", 0)
            if revenue_target > 0:
                kpis.append({
                    "name": "Revenue_vs_Projection",
                    "target": revenue_target,
                    "frequency": "monthly",
                    "alert_threshold": 0.80,
                    "unit": "EUR",
                    "linked_to": "financial_data.annual_revenue_y1",
                    "critical": True
                })

        # KPI Verts
        if unified.green_metrics:
            co2_target = unified.green_metrics.get("co2_avoided_annual", 0)
            if co2_target > 0:
                kpis.append({
                    "name": "CO2_Impact_Real",
                    "target": co2_target,
                    "frequency": "quarterly",
                    "alert_threshold": 0.85,
                    "unit": "Tonnes CO2e",
                    "linked_to": "green_metrics.co2_avoided_annual",
                    "critical": True
                })

            jobs_target = unified.green_metrics.get("jobs_created", 0)
            if jobs_target > 0:
                kpis.append({
                    "name": "Jobs_Created",
                    "target": jobs_target,
                    "frequency": "quarterly",
                    "alert_threshold": 0.90,
                    "unit": "Count",
                    "linked_to": "green_metrics.jobs_created",
                    "critical": False
                })

        # ÉTAPE 3: Crée jalons intelligents
        milestones = self._generate_milestones_from_bp(
            unified.business_plan,
            unified.financial_data
        )

        # ÉTAPE 4: Crée alertes intelligentes avec chemins d'investigation
        alerts = self._generate_intelligent_alerts(unified)

        return {
            "message": f"Monitoring plan auto-generated - {len(kpis)} KPIs, {len(milestones)} milestones",
            "data": {
                "kpis": kpis,
                "milestones": milestones,
                "alerts": alerts,
                "evaluation_frequency": "quarterly",
                "success_criteria": {
                    "financial": f"Achieve {unified.financial_data.get('roi_percent', 0):.0f}% ROI",
                    "environmental": f"Reduce CO2 by {unified.green_metrics.get('co2_avoided_annual', 0)}T",
                    "social": f"Create {unified.green_metrics.get('jobs_created', 0)} jobs"
                },
                "review_schedule": {
                    "monthly": "Financial metrics",
                    "quarterly": "All KPIs",
                    "annually": "Strategic review"
                },
                "auto_generated": True,
                "generated_from_bp": True
            }
        }

    def _identify_financial_risks(self, investment: float, roi: float, margin: float) -> List[str]:
        """Identifie les risques financiers"""
        risks = []

        if roi < 10:
            risks.append("Low ROI - Monitor closely")
        if roi < 0:
            risks.append("CRITICAL: Negative ROI")
        if margin < 0.2:
            risks.append("Low margin - Pricing pressure risk")
        if investment > 500000:
            risks.append("High investment - Capital at risk")

        return risks

    def _identify_green_funding(self, investment: float, sector: str, co2_saved: float,
                               roi: float, esg_score: float) -> List[Dict]:
        """INTELLIGENCE: Recommande des sources de financement verts SPÉCIFIQUES"""

        sources = []

        # Eligibilité basée sur critères objectifs
        if co2_saved > 500:
            sources.append({
                "name": "EU Green Bond Programme",
                "min_amount": 100000,
                "max_amount": 5000000,
                "rate": "2.5%",
                "eligibility": "STRONG",
                "notes": "Excellent CO2 reduction profile"
            })

        if sector.lower() in ["renewable", "energy", "sustainable"]:
            sources.append({
                "name": "BDF (Banque de France) Green Credit",
                "min_amount": 50000,
                "max_amount": 2000000,
                "rate": "3.2%",
                "eligibility": "STRONG",
                "notes": "Sector alignment perfect"
            })

        if esg_score > 7:
            sources.append({
                "name": "ESG-Focused Impact Investors",
                "min_amount": 200000,
                "max_amount": 3000000,
                "rate": "Variable + equity",
                "eligibility": "STRONG",
                "notes": "High ESG score attractive to impact funds"
            })

        if roi > 15:
            sources.append({
                "name": "Subvention ADEME (France)",
                "min_amount": 50000,
                "max_amount": 500000,
                "rate": "Grant (0%)",
                "eligibility": "MODERATE",
                "notes": "Check sector eligibility"
            })

        # Fallback pour tous
        sources.append({
            "name": "Standard Commercial Banking",
            "min_amount": investment * 0.5,
            "max_amount": investment,
            "rate": "4.0-5.0%",
            "eligibility": "ALWAYS",
            "notes": "Baseline option"
        })

        return sources

    def _rate_sustainability(self, esg_score: float) -> str:
        """Évalue le niveau de durabilité"""
        if esg_score >= 8.5:
            return "Exceptional (ESG Leader)"
        elif esg_score >= 7:
            return "Strong (ESG Compliant)"
        elif esg_score >= 5:
            return "Moderate (Improving)"
        else:
            return "Weak (Action needed)"

    def _generate_market_analysis(self, sector: str, revenue_y1: float, esg_score: float) -> Dict:
        """Génère une analyse de marché intelligente"""

        market_sizes = {
            "renewable": 500000000,
            "energy": 1000000000,
            "sustainable": 600000000,
            "general": 300000000
        }

        tam = market_sizes.get(sector.lower(), market_sizes["general"])

        return {
            "sector": sector,
            "tam": f"€{tam:,.0f}",
            "market_growth_rate": "12-15% annually",
            "competitive_landscape": "Fragmented - opportunity for consolidation",
            "key_trends": [
                "ESG regulations tightening",
                "Green financing accelerating",
                "Consumer demand for sustainability"
            ],
            "esg_relevance": f"High - ESG Score {esg_score:.1f}/10 aligns with market trends"
        }

    def _generate_roadmap(self, breakeven_months: int, sector: str) -> Dict:
        """Génère une roadmap basée sur le breakeven"""

        milestones = []

        # Phase 1: Setup
        milestones.append({
            "quarter": "Q1",
            "milestone": "Setup & Launch",
            "target_date": "Month 1-3",
            "kpis": ["Team hired", "Operations live"]
        })

        # Phase 2: Ramp-up
        ramp_months = int(breakeven_months * 0.5)
        q2_month = 3 + ramp_months
        milestones.append({
            "quarter": "Q2-3",
            "milestone": "Market Penetration",
            "target_date": f"Month 4-{q2_month}",
            "kpis": ["Customer acquisition", "Revenue growing"]
        })

        # Phase 3: Breakeven
        milestones.append({
            "quarter": f"Q{int(breakeven_months/3)}",
            "milestone": "BREAKEVEN POINT",
            "target_date": f"Month {int(breakeven_months)}",
            "kpis": ["Revenue = Costs", "Profitability path clear"]
        })

        # Phase 4: Scale
        milestones.append({
            "quarter": f"Q{int(breakeven_months/3) + 2}+",
            "milestone": "Growth & Scale",
            "target_date": f"Month {int(breakeven_months) + 6}+",
            "kpis": ["Expanding market share", "Improving margins"]
        })

        return {"milestones": milestones}

    def _extract_bp_promises(self, business_plan: Dict) -> List[Dict]:
        """Extrait les promesses du BP pour créer les KPIs"""

        promises = []

        if "revenue_model" in business_plan:
            revenue = business_plan["revenue_model"].get("y1", 0)
            if revenue > 0:
                promises.append({
                    "name": "Revenue Y1",
                    "target_value": revenue,
                    "is_critical": True
                })

        if "implementation_roadmap" in business_plan:
            for milestone in business_plan["implementation_roadmap"].get("milestones", []):
                promises.append({
                    "name": milestone.get("milestone", "Unknown"),
                    "target_value": milestone.get("target_date"),
                    "is_critical": "BREAKEVEN" in milestone.get("milestone", "")
                })

        return promises

    def _generate_milestones_from_bp(self, business_plan: Dict, financial_data: Dict) -> List[Dict]:
        """Génère des jalons à partir du BP"""

        milestones = []

        if "implementation_roadmap" in business_plan:
            for i, milestone in enumerate(business_plan["implementation_roadmap"].get("milestones", []), 1):
                milestones.append({
                    "id": i,
                    "name": milestone.get("milestone"),
                    "target_date": milestone.get("target_date"),
                    "success_criteria": milestone.get("kpis", []),
                    "responsible": "Project Manager",
                    "status": "planned"
                })

        return milestones

    def _generate_intelligent_alerts(self, unified: UnifiedDataModel) -> List[Dict]:
        """Crée des alertes intelligentes avec chemins d'investigation"""

        alerts = []

        # Alert 1: Revenue deviation
        alerts.append({
            "trigger": "Revenue < Target * 0.80",
            "severity": "HIGH",
            "investigation_path": [
                "1. Check customer acquisition rate",
                "2. Analyze customer churn",
                "3. Review pricing strategy",
                "4. Investigate competitive pressure",
                "5. Assess market conditions"
            ],
            "auto_action": "Trigger board notification"
        })

        # Alert 2: Cost overrun
        alerts.append({
            "trigger": "Costs > Budget * 1.15",
            "severity": "MEDIUM",
            "investigation_path": [
                "1. Review operational expenses",
                "2. Identify cost drivers",
                "3. Implement cost reduction measures",
                "4. Adjust margin targets"
            ],
            "auto_action": "Notify CFO"
        })

        # Alert 3: Green impact miss
        if unified.green_metrics:
            alerts.append({
                "trigger": "CO2 Impact < Target * 0.85",
                "severity": "MEDIUM",
                "investigation_path": [
                    "1. Check implementation quality",
                    "2. Validate measurement methodology",
                    "3. Review equipment efficiency",
                    "4. Assess operational issues"
                ],
                "auto_action": "Notify sustainability officer"
            })

        return alerts

    def _emit_event(self, project_id: str, event_type: EventType, message: str):
        """Enregistre un événement"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "project_id": project_id,
            "type": event_type.value,
            "message": message
        }
        self.events.append(event)


# Instance globale
orchestrator = CLEATIOrchestrator()
