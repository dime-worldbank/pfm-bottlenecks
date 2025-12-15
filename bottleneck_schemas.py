# Databricks notebook source
"""
Validation schemas for bottlenecks.
Each schema defines strong/moderate cues, hard negatives, and acceptance rules.
"""

from typing import List, Dict, Any

# COMMAND ----------

SCHEMA_2_1 = {
    "strong_cues": [
        "conflicting_or_overlapping_policies",
        "parallel_strategies_or_plans",
        "uncoordinated_programs_same_objective",
        "misaligned_targets_across_policies",
        "policy_frameworks_ignore_interdependencies"
    ],

    "moderate_cues": [
        "explicit_policy_terms_present",
        "cross_sector_interface_ignored",
        "causal_link_stated",
        "concrete_consequence_present",
        "sufficient_specificity"
    ],

    "hard_negatives": [
        "macro_institutional_fragmentation",
        "intergovernmental_financing_issues",
        "data_mis_fragmentation",
        "policy_vacuum_not_fragmentation",
        "operational_coordination_only",
        "generic_vague_statements"
    ],

    "failure_types": [
        "inefficiency_or_duplication",
        "stranded_assets_or_bottlenecks",
        "market_distortions",
        "missed_synergies_or_poor_outcomes",
        "higher_costs_or_waste"
    ],

    "acceptance_rule": "strong >= 1 OR moderate >= 2",
    "use_reflection": False,

    "scope_lock": """Treat fragmentation as policy-level coordination failures where multiple policies/strategies/plans are conflicting, duplicative, or operate in silos.
Sectoral policy overlaps qualify. Macro-institutional fragmentation (MoF/Treasury/DMO/Central Bank), intergovernmental financing, and data systems are outside scope."""
}


# COMMAND ----------


SCHEMA_6_1 = {
    "strong_cues": [
        "off_budget",
        "parallel_systems",
        "separate_administration",
        "different_rules_processes_across_streams",
        "political_ad_hoc_allocation",
        "mid_year_approval_outside_cycle",
        "block_allocation_outside_process",
        "multiple_financing_pools_different_agencies"
    ],

    "moderate_cues": [
        "earmarked_or_tied_grants",
        "vertical_fragmentation_intergovernmental",
        "procedural_divergence_reporting_procurement_ifmis",
        "pooled_fund_dissolved_or_bypass",
        "volatility_revealing_fragmentation"
    ],

    "hard_negatives": [
        "wage_bill_personnel_on_budget",
        "generic_program_budget_structure",
        "capacity_procurement_without_alternate_channels",
        "revenue_politics_without_offbudget",
        "donor_dependence_without_parallel"
    ],

    "failure_types": [
        "inefficiency_higher_admin_costs",
        "unpredictability_funding_volatility",
        "coordination_failure_duplication_underutilization_competition",
        "delays_start_stop",
        "arrears_or_cash_shortfalls",
        "corruption_or_leakage_risk"
    ],

    "acceptance_rule": "strong >= 1 OR moderate >= 2",
    "use_reflection": False,

    "scope_lock": """Treat fragmentation strictly as funding/financial-management channel fragmentation.
Program/administrative separation is irrelevant unless it creates distinct funding flow or parallel financial control stream."""
}

# COMMAND ----------

BOTTLENECK_SCHEMAS = {
    "2.1": SCHEMA_2_1,
    "6.1": SCHEMA_6_1,
}


def get_schema(bottleneck_id: str) -> Dict[str, Any]:
    if bottleneck_id not in BOTTLENECK_SCHEMAS:
        raise ValueError(f"No schema for {bottleneck_id}. Available: {list(BOTTLENECK_SCHEMAS.keys())}")
    return BOTTLENECK_SCHEMAS[bottleneck_id]
