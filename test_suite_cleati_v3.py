"""
CLEATI V3.3 - COMPREHENSIVE TEST SUITE
Tests tous les modules en tant qu'utilisateur gourmand challenging la robustesse
"""

import asyncio
import json
from datetime import datetime
from cleati_orchestrator_v3 import orchestrator

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.tests = []

    def log_test(self, name: str, status: str, details: str = ""):
        self.tests.append({
            "name": name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

        if status == "PASS":
            self.passed += 1
            print(f"✅ {name}")
        elif status == "FAIL":
            self.failed += 1
            print(f"❌ {name}")
            if details:
                print(f"   └─ {details}")
        elif status == "WARN":
            self.warnings += 1
            print(f"⚠️  {name}")
            if details:
                print(f"   └─ {details}")

    def summary(self):
        total = self.passed + self.failed + self.warnings
        print("\n" + "="*70)
        print(f"TEST SUMMARY: {self.passed}/{total} passed, {self.failed} failed, {self.warnings} warnings")
        print("="*70 + "\n")

async def test_1_basic_project_creation():
    """Test 1: Création basique de projet"""
    print("\n[TEST 1] Basic Project Creation")

    results = TestResults()

    # Test 1.1: Créer un projet
    user_data = {
        "user_id": "test_user_001",
        "project_name": "Solar Farm - France",
        "sector": "renewable",
        "geography": "France",
        "type": "business_plan"
    }

    project_id = orchestrator.create_project(user_data)

    if project_id and len(project_id) > 0:
        results.log_test("Create project", "PASS")
    else:
        results.log_test("Create project", "FAIL", "Project ID not generated")

    # Test 1.2: Vérifier que le projet existe
    if project_id in orchestrator.projects:
        results.log_test("Project exists in store", "PASS")
    else:
        results.log_test("Project exists in store", "FAIL")

    # Test 1.3: Vérifier metadata
    if orchestrator.projects[project_id].metadata.get("project_name") == "Solar Farm - France":
        results.log_test("Project metadata correct", "PASS")
    else:
        results.log_test("Project metadata correct", "FAIL")

    results.summary()
    return project_id

async def test_2_financial_analysis():
    """Test 2: Analyse Financière - Scénarios extrêmes"""
    print("\n[TEST 2] Financial Analysis (Extreme Scenarios)")

    results = TestResults()

    # Test 2.1: Scénario FORT (High ROI)
    print("\n  [Scenario: HIGH ROI PROJECT]")
    project_strong = orchestrator.create_project({
        "project_name": "Strong ROI Project",
        "sector": "renewable"
    })

    user_answers_strong = {
        "initial_investment": 100000,
        "annual_revenue_y1": 150000,
        "operational_costs_y1": 40000,
        "sector": "renewable",
        "co2_avoided_annual": 500,
        "jobs_created": 5,
        "energy_produced_kwh": 125000,
        "water_saved": 10000
    }

    result_strong = await orchestrator.process_full_pipeline(project_strong, user_answers_strong)

    if result_strong["status"] == "success":
        results.log_test("Strong scenario - Full pipeline", "PASS")

        financial = result_strong["unified_data"]["financial_data"]
        roi = financial.get("roi_percent", 0)

        if roi > 50:
            results.log_test("Strong ROI calculation (>50%)", "PASS", f"ROI: {roi:.1f}%")
        else:
            results.log_test("Strong ROI calculation", "FAIL", f"Expected >50%, got {roi:.1f}%")

        # Vérifier les projections 5 ans
        if "projections_5_years" in financial:
            projections = financial["projections_5_years"]
            if all(f"y{i}" in projections for i in range(1, 6)):
                results.log_test("5-year projections complete", "PASS")
            else:
                results.log_test("5-year projections", "FAIL", "Missing years")
        else:
            results.log_test("5-year projections", "FAIL", "No projections found")

    else:
        results.log_test("Strong scenario - Full pipeline", "FAIL", result_strong.get("error"))

    # Test 2.2: Scénario FAIBLE (Low/Negative ROI)
    print("\n  [Scenario: NEGATIVE ROI]")
    project_weak = orchestrator.create_project({
        "project_name": "Weak ROI Project",
        "sector": "general"
    })

    user_answers_weak = {
        "initial_investment": 500000,
        "annual_revenue_y1": 50000,
        "operational_costs_y1": 40000,
        "sector": "general",
        "co2_avoided_annual": 50,
        "jobs_created": 1,
        "energy_produced_kwh": 10000,
        "water_saved": 1000
    }

    result_weak = await orchestrator.process_full_pipeline(project_weak, user_answers_weak)

    if result_weak["status"] == "success":
        results.log_test("Weak scenario - Full pipeline", "PASS")

        financial = result_weak["unified_data"]["financial_data"]
        roi = financial.get("roi_percent", 0)
        risks = financial.get("risk_flags", [])

        if roi < 0:
            results.log_test("Negative ROI detection", "PASS", f"ROI: {roi:.1f}%")
        else:
            results.log_test("Negative ROI detection", "WARN", f"ROI: {roi:.1f}% (expected negative)")

        if len(risks) > 0:
            results.log_test("Risk detection", "PASS", f"Found {len(risks)} risks")
        else:
            results.log_test("Risk detection", "WARN", "No risks detected for weak project")

    else:
        results.log_test("Weak scenario - Full pipeline", "FAIL", result_weak.get("error"))

    # Test 2.3: Scénario MODÉRÉ
    print("\n  [Scenario: MODERATE ROI]")
    project_moderate = orchestrator.create_project({
        "project_name": "Moderate ROI Project",
        "sector": "energy"
    })

    user_answers_moderate = {
        "initial_investment": 250000,
        "annual_revenue_y1": 100000,
        "operational_costs_y1": 50000,
        "sector": "energy",
        "co2_avoided_annual": 250,
        "jobs_created": 3,
        "energy_produced_kwh": 60000,
        "water_saved": 5000
    }

    result_moderate = await orchestrator.process_full_pipeline(project_moderate, user_answers_moderate)

    if result_moderate["status"] == "success":
        results.log_test("Moderate scenario - Full pipeline", "PASS")
        roi = result_moderate["unified_data"]["financial_data"].get("roi_percent", 0)
        results.log_test("Moderate ROI range (10-30%)", "PASS" if 10 < roi < 30 else "WARN", f"ROI: {roi:.1f}%")
    else:
        results.log_test("Moderate scenario - Full pipeline", "FAIL")

    results.summary()
    return project_strong, project_weak, project_moderate

async def test_3_green_intelligence():
    """Test 3: Intelligence Verte - ESG et Financement"""
    print("\n[TEST 3] Green Intelligence & Funding Matching")

    results = TestResults()

    # Test 3.1: Projet TRÈS VERT (High ESG)
    print("\n  [Scenario: HIGH ESG PROJECT]")
    project_green = orchestrator.create_project({
        "project_name": "Ultra Green Project",
        "sector": "renewable"
    })

    user_answers_green = {
        "initial_investment": 200000,
        "annual_revenue_y1": 120000,
        "operational_costs_y1": 50000,
        "sector": "renewable",
        "co2_avoided_annual": 1000,  # TRÈS ÉLEVÉ
        "jobs_created": 10,
        "energy_produced_kwh": 250000,
        "water_saved": 50000,
        "revenue_model": "B2B Sustainability Services"
    }

    result_green = await orchestrator.process_full_pipeline(project_green, user_answers_green)

    if result_green["status"] == "success":
        results.log_test("Green project pipeline", "PASS")

        green = result_green["unified_data"]["green_metrics"]
        esg_score = green.get("esg_score", 0)

        if esg_score > 7:
            results.log_test("High ESG score (>7)", "PASS", f"ESG: {esg_score:.2f}")
        else:
            results.log_test("High ESG score", "FAIL", f"ESG: {esg_score:.2f} (expected >7)")

        # Test funding sources
        funding = result_green.get("unified_data", {}).get("funding_sources", [])
        if len(funding) > 2:
            results.log_test(f"Funding sources identified ({len(funding)})", "PASS")

            # Vérifie qu'on a au moins une source "green"
            green_sources = [f for f in funding if "Green" in f.get("name", "")]
            if len(green_sources) > 0:
                results.log_test("Green-specific funding sources", "PASS", f"Found: {', '.join([f['name'] for f in green_sources])}")
            else:
                results.log_test("Green-specific funding sources", "WARN", "No green-specific sources")
        else:
            results.log_test("Funding sources identified", "FAIL", f"Only {len(funding)} sources")

        # Test Dual ROI
        dual_roi = green.get("dual_roi", {})
        fin_roi = dual_roi.get("financial_roi", 0)
        eco_roi = dual_roi.get("ecological_roi", 0)
        combined = dual_roi.get("combined_score", 0)

        if fin_roi > 0 and eco_roi > 0 and combined > 0:
            results.log_test("Dual ROI calculation", "PASS", f"Fin: {fin_roi:.1f}%, Eco: {eco_roi:.1f}%, Combined: {combined:.1f}%")
        else:
            results.log_test("Dual ROI calculation", "FAIL")

    else:
        results.log_test("Green project pipeline", "FAIL", result_green.get("error"))

    # Test 3.2: Projet PEU VERT (Low ESG)
    print("\n  [Scenario: LOW ESG PROJECT]")
    project_brown = orchestrator.create_project({
        "project_name": "Low ESG Project",
        "sector": "general"
    })

    user_answers_brown = {
        "initial_investment": 150000,
        "annual_revenue_y1": 80000,
        "operational_costs_y1": 40000,
        "sector": "general",
        "co2_avoided_annual": 0,  # Pas d'impact vert
        "jobs_created": 0,
        "energy_produced_kwh": 0,
        "water_saved": 0,
        "revenue_model": "Generic Services"
    }

    result_brown = await orchestrator.process_full_pipeline(project_brown, user_answers_brown)

    if result_brown["status"] == "success":
        green = result_brown["unified_data"]["green_metrics"]
        esg_score = green.get("esg_score", 0)

        if esg_score < 4:
            results.log_test("Low ESG detection", "PASS", f"ESG: {esg_score:.2f}")
        else:
            results.log_test("Low ESG detection", "WARN", f"ESG: {esg_score:.2f} (expected <4)")

        # Funding sources should be limited
        funding = result_brown.get("unified_data", {}).get("funding_sources", [])
        if len(funding) < 5:
            results.log_test("Limited green funding (expected)", "PASS", f"{len(funding)} sources")
        else:
            results.log_test("Limited green funding", "WARN", f"{len(funding)} sources offered")

    else:
        results.log_test("Brown project pipeline", "FAIL")

    results.summary()
    return project_green, project_brown

async def test_4_business_plan_generation():
    """Test 4: Génération de Business Plans - Qualité et Complétude"""
    print("\n[TEST 4] Business Plan Generation Quality")

    results = TestResults()

    # Utilise le projet green du test précédent
    project_id = orchestrator.create_project({
        "project_name": "Complete BP Test",
        "sector": "renewable"
    })

    user_answers = {
        "initial_investment": 300000,
        "annual_revenue_y1": 180000,
        "operational_costs_y1": 80000,
        "sector": "renewable",
        "co2_avoided_annual": 600,
        "jobs_created": 8,
        "energy_produced_kwh": 150000,
        "water_saved": 30000,
        "revenue_model": "Installation + Maintenance Services"
    }

    result = await orchestrator.process_full_pipeline(project_id, user_answers)

    if result["status"] == "success":
        bp = result["unified_data"]["business_plan"]

        # Test 4.1: Sections présentes
        required_sections = [
            "executive_summary",
            "market_analysis",
            "revenue_model",
            "financial_strategy",
            "sustainability_section",
            "implementation_roadmap"
        ]

        for section in required_sections:
            if section in bp:
                results.log_test(f"Section '{section}' present", "PASS")
            else:
                results.log_test(f"Section '{section}' present", "FAIL")

        # Test 4.2: Executive Summary contient les points clés
        exec_summary = bp.get("executive_summary", {})
        if "company_mission" in exec_summary and "key_value_proposition" in exec_summary:
            results.log_test("Executive summary quality", "PASS")
        else:
            results.log_test("Executive summary quality", "WARN")

        # Test 4.3: Market Analysis inclut ESG
        market = bp.get("market_analysis", {})
        if "esg_relevance" in market:
            results.log_test("ESG integrated in market analysis", "PASS")
        else:
            results.log_test("ESG integrated in market analysis", "WARN")

        # Test 4.4: Sustainability Section
        sustainability = bp.get("sustainability_section", {})
        if "esg_framework" in sustainability and "compliance" in sustainability:
            results.log_test("Sustainability section complete", "PASS")
        else:
            results.log_test("Sustainability section complete", "FAIL")

        # Test 4.5: Roadmap avec milestones
        roadmap = bp.get("implementation_roadmap", {})
        milestones = roadmap.get("milestones", [])

        if len(milestones) >= 4:
            results.log_test(f"Roadmap milestones ({len(milestones)})", "PASS")
        else:
            results.log_test("Roadmap milestones", "WARN", f"Only {len(milestones)} milestones")

        # Test 4.6: Pages estimées
        pages = bp.get("estimated_pages", 0)
        if 15 <= pages <= 25:
            results.log_test(f"Estimated pages ({pages})", "PASS")
        else:
            results.log_test("Estimated pages", "WARN", f"{pages} pages (expected 15-25)")

    else:
        results.log_test("BP generation", "FAIL", result.get("error"))

    results.summary()
    return project_id

async def test_5_monitoring_evaluation():
    """Test 5: Auto-Génération Plan S&E - Intégrité et Intelligence"""
    print("\n[TEST 5] Monitoring & Evaluation Auto-Generation")

    results = TestResults()

    # Utilise un projet existant
    project_id = orchestrator.create_project({
        "project_name": "M&E Test Project",
        "sector": "renewable"
    })

    user_answers = {
        "initial_investment": 250000,
        "annual_revenue_y1": 150000,
        "operational_costs_y1": 70000,
        "sector": "renewable",
        "co2_avoided_annual": 400,
        "jobs_created": 6,
        "energy_produced_kwh": 100000,
        "water_saved": 20000
    }

    result = await orchestrator.process_full_pipeline(project_id, user_answers)

    if result["status"] == "success":
        monitoring = result["unified_data"]["monitoring_plan"]

        # Test 5.1: KPIs Auto-Générés
        kpis = monitoring.get("kpis", [])

        if len(kpis) > 0:
            results.log_test(f"KPIs auto-generated ({len(kpis)})", "PASS")

            # Vérifiez que chaque KPI est lié à une source
            linked_kpis = [k for k in kpis if "linked_to" in k and k["linked_to"]]
            if len(linked_kpis) == len(kpis):
                results.log_test("All KPIs linked to data sources", "PASS")
            else:
                results.log_test("KPI data linkage", "WARN", f"{len(linked_kpis)}/{len(kpis)} linked")

            # Vérifiez mixte: financial + green
            fin_kpis = [k for k in kpis if "Revenue" in k.get("name", "")]
            green_kpis = [k for k in kpis if "CO2" in k.get("name", "")]

            if len(fin_kpis) > 0 and len(green_kpis) > 0:
                results.log_test("Mixed KPIs (Financial + Green)", "PASS", f"Fin: {len(fin_kpis)}, Green: {len(green_kpis)}")
            else:
                results.log_test("Mixed KPI types", "WARN")

        else:
            results.log_test("KPI generation", "FAIL", "No KPIs generated")

        # Test 5.2: Milestones
        milestones = monitoring.get("milestones", [])
        if len(milestones) > 0:
            results.log_test(f"Milestones auto-generated ({len(milestones)})", "PASS")

            # Vérifiez qu'elles ont des success criteria
            with_criteria = [m for m in milestones if "success_criteria" in m and len(m.get("success_criteria", [])) > 0]
            if len(with_criteria) > 0:
                results.log_test("Milestones with success criteria", "PASS", f"{len(with_criteria)} defined")
            else:
                results.log_test("Milestone criteria", "WARN")

        else:
            results.log_test("Milestone generation", "WARN", "No milestones")

        # Test 5.3: Alerts Intelligentes
        alerts = monitoring.get("alerts", [])
        if len(alerts) > 0:
            results.log_test(f"Intelligent alerts ({len(alerts)})", "PASS")

            # Vérifiez que les alertes ont des chemins d'investigation
            with_paths = [a for a in alerts if "investigation_path" in a and len(a["investigation_path"]) > 0]
            if len(with_paths) == len(alerts):
                results.log_test("All alerts with investigation paths", "PASS")
            else:
                results.log_test("Alert paths", "WARN", f"{len(with_paths)}/{len(alerts)} with paths")

        else:
            results.log_test("Alert generation", "WARN", "No alerts")

        # Test 5.4: Success Criteria
        success_criteria = monitoring.get("success_criteria", {})
        if "financial" in success_criteria and "environmental" in success_criteria:
            results.log_test("Dual success criteria (Financial + Environmental)", "PASS")
        else:
            results.log_test("Success criteria", "FAIL", "Missing criteria types")

        # Test 5.5: Auto-Generated flag
        if monitoring.get("auto_generated") and monitoring.get("generated_from_bp"):
            results.log_test("Plan is auto-generated from BP", "PASS")
        else:
            results.log_test("Auto-generation tracking", "WARN")

    else:
        results.log_test("M&E pipeline", "FAIL", result.get("error"))

    results.summary()
    return project_id

async def test_6_data_integrity():
    """Test 6: Intégrité des Données Inter-Modules"""
    print("\n[TEST 6] Data Integrity & Cross-Module Validation")

    results = TestResults()

    # Crée un projet et lance le pipeline
    project_id = orchestrator.create_project({
        "project_name": "Integrity Test",
        "sector": "renewable"
    })

    user_answers = {
        "initial_investment": 300000,
        "annual_revenue_y1": 200000,
        "operational_costs_y1": 90000,
        "sector": "renewable",
        "co2_avoided_annual": 500,
        "jobs_created": 7,
        "energy_produced_kwh": 125000,
        "water_saved": 25000
    }

    result = await orchestrator.process_full_pipeline(project_id, user_answers)

    if result["status"] == "success":
        integrity = result["integrity_check"]

        # Test 6.1: Intégrité générale
        if integrity.get("is_valid"):
            results.log_test("Data integrity validation", "PASS")
        else:
            results.log_test("Data integrity validation", "FAIL", str(integrity.get("issues", [])))

        issues = integrity.get("issues", [])

        # Count par severity
        errors = len([i for i in issues if i.get("severity") == "ERROR"])
        warnings = len([i for i in issues if i.get("severity") == "WARNING"])
        infos = len([i for i in issues if i.get("severity") == "INFO"])

        results.log_test(f"Integrity report", "PASS", f"Errors: {errors}, Warnings: {warnings}, Infos: {infos}")

        # Test 6.2: Cohérence Revenue (BP vs Financial)
        financial_revenue = result["unified_data"]["financial_data"].get("annual_revenue_y1", 0)
        bp_revenue = result["unified_data"]["business_plan"].get("revenue_model", {}).get("y1", 0)

        if financial_revenue > 0 and bp_revenue > 0:
            variance = abs(financial_revenue - bp_revenue) / financial_revenue
            if variance < 0.05:  # Moins de 5%
                results.log_test("Revenue coherence (BP vs Financial)", "PASS", f"Variance: {variance*100:.1f}%")
            else:
                results.log_test("Revenue coherence", "WARN", f"Variance: {variance*100:.1f}%")
        else:
            results.log_test("Revenue coherence", "WARN", "Missing data")

        # Test 6.3: Green metrics dans Monitoring
        monitoring_kpis = result["unified_data"]["monitoring_plan"].get("kpis", [])
        green_kpis_in_monitoring = [k for k in monitoring_kpis if "CO2" in k.get("name", "")]

        if len(green_kpis_in_monitoring) > 0:
            results.log_test("Green metrics reflected in monitoring", "PASS", f"{len(green_kpis_in_monitoring)} green KPIs")
        else:
            results.log_test("Green metrics in monitoring", "WARN", "No green KPIs in monitoring")

    else:
        results.log_test("Integrity check", "FAIL", result.get("error"))

    results.summary()
    return project_id

async def test_7_event_logging():
    """Test 7: Event Logging et Audit Trail"""
    print("\n[TEST 7] Event Logging & Audit Trail")

    results = TestResults()

    initial_event_count = len(orchestrator.events)

    # Crée un projet qui génère plusieurs événements
    project_id = orchestrator.create_project({"project_name": "Event Test"})

    # Compte les événements
    project_events = [e for e in orchestrator.events if e["project_id"] == project_id]

    if len(project_events) > 0:
        results.log_test(f"Event logging started ({len(project_events)} events)", "PASS")
    else:
        results.log_test("Event logging", "FAIL", "No events recorded")

    # Lance le pipeline
    user_answers = {
        "initial_investment": 200000,
        "annual_revenue_y1": 150000,
        "operational_costs_y1": 70000,
        "sector": "renewable",
        "co2_avoided_annual": 300,
        "jobs_created": 5,
        "energy_produced_kwh": 75000,
        "water_saved": 15000
    }

    result = await orchestrator.process_full_pipeline(project_id, user_answers)

    # Recount
    project_events = [e for e in orchestrator.events if e["project_id"] == project_id]

    expected_event_types = [
        "project_initiated",
        "financial_complete",
        "green_complete",
        "bp_complete",
        "monitoring_complete"
    ]

    event_types_found = set([e["type"] for e in project_events])

    for expected in expected_event_types:
        if expected in event_types_found:
            results.log_test(f"Event '{expected}' logged", "PASS")
        else:
            results.log_test(f"Event '{expected}' logged", "FAIL")

    results.summary()

async def run_all_tests():
    """Lance tous les tests"""
    print("\n" + "="*70)
    print("CLEATI V3.3 - COMPREHENSIVE TEST SUITE")
    print("Challenging robustness as a demanding user")
    print("="*70)

    project_id_1 = await test_1_basic_project_creation()
    projects_financial = await test_2_financial_analysis()
    projects_green = await test_3_green_intelligence()
    project_bp = await test_4_business_plan_generation()
    project_me = await test_5_monitoring_evaluation()
    project_integrity = await test_6_data_integrity()
    await test_7_event_logging()

    # Final Summary
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print(f"Projects created: {len(orchestrator.projects)}")
    print(f"Events logged: {len(orchestrator.events)}")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
