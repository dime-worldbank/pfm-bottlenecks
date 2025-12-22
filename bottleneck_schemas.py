# Databricks notebook source
"""
Validation schemas for bottlenecks.
Each schema defines strong/moderate cues, hard negatives, and acceptance rules.
"""

from typing import List, Dict, Any

# COMMAND ----------

SCHEMA_1_1 = [
    {
        "subschema": "Reform Not Followed Through",
        
        "strong_cues": [
            "reform_not_followed_through_with_leadership_attribution",
            "cause_of_inaction_explicit_with_named_actor",
        ],
        
        "moderate_cues": [
            "mentions_approved_reform",
            "reform_tied_to_government_commitment",
            "actor_named_or_identifiable",
            "alternative_explanations_ruled_out",
        ],
        
        "hard_negatives": [
            "too_vague_or_generic",
            "uses_conditional_language",
            "capacity_or_resource_constraint_only",
            "external_factors_blamed",
        ],
        
        "failure_types": [
            "reform_stalled_or_abandoned",
            "policy_not_operationalized",
            "implementation_gap",
        ],
        
        "acceptance_rule": "strong >= 1 OR moderate >= 4",
        "use_reflection": False,
        
        "scope_lock": """This subschema captures cases where approved reforms were not followed through 
due to lack of political will or leadership commitment. The failure must be explicitly attributed 
to leadership inaction, not capacity constraints or external factors."""
    },
    {
        "subschema": "Political Resistance",
        
        "strong_cues": [
            "political_resistance_due_to_political_cost",
            "reform_blocked_by_political_actors",
        ],
        
        "moderate_cues": [
            "mentions_approved_reform",
            "political_resistance_described",
            "actor_named_or_identifiable",
        ],
        
        "hard_negatives": [
            "too_vague_or_generic",
            "uses_conditional_language",
            "technical_disagreement_not_political",
            "resistance_from_external_actors",
        ],
        
        "failure_types": [
            "reform_blocked",
            "reform_diluted",
            "reform_reversed",
        ],
        
        "acceptance_rule": "strong >= 1 OR moderate >= 3",
        "use_reflection": False,
        
        "scope_lock": """This subschema captures political resistance to reforms where actors 
block or undermine reforms due to political costs (loss of patronage, electoral risk, etc.). 
Must name or identify the resisting actor."""
    },
    {
        "subschema": "Interference in Execution",
        
        "strong_cues": [
            "discretionary_interference_in_execution",
            "political_override_of_approved_process",
        ],
        
        "moderate_cues": [
            "mentions_approved_reform",
            "interference_in_execution",
            "actor_named_or_identifiable",
        ],
        
        "hard_negatives": [
            "too_vague_or_generic",
            "uses_conditional_language",
            "procedural_delay_not_interference",
            "legitimate_policy_adjustment",
        ],
        
        "failure_types": [
            "execution_derailed",
            "process_subverted",
            "rules_selectively_applied",
        ],
        
        "acceptance_rule": "strong >= 1 OR moderate >= 3",
        "use_reflection": False,
        
        "scope_lock": """This subschema captures discretionary interference in reform execution 
where political actors override or subvert approved processes. The interference must be 
discretionary (not rule-based) and actor must be identifiable."""
    },
    {
        "subschema": "Failure to Prioritize",
        
        "strong_cues": [
            "leadership_failure_to_prioritize_with_explicit_cause",
            "avoidance_of_difficult_tradeoffs",
        ],
        
        "moderate_cues": [
            "mentions_approved_reform",
            "failure_to_prioritize_resources",
            "followthrough_failure_attributed_to_leadership",
            "actor_named_or_identifiable",
            "alternative_explanations_ruled_out",
        ],
        
        "hard_negatives": [
            "too_vague_or_generic",
            "uses_conditional_language",
            "resource_scarcity_genuine",
            "competing_priorities_legitimate",
        ],
        
        "failure_types": [
            "reform_deprioritized",
            "resources_not_allocated",
            "attention_diverted",
        ],
        
        "acceptance_rule": "strong >= 1 OR moderate >= 3",
        "use_reflection": False,
        
        "scope_lock": """This subschema captures leadership failure to prioritize reforms or 
make difficult tradeoffs. Must show explicit cause of inaction attributed to leadership, 
with alternative explanations ruled out."""
    },
    {
        "subschema": "Passive Commitment Failure",
        
        "strong_cues": [
            "leadership_signals_abandonment",
            "demoralization_linked_to_leadership_passivity",
        ],
        
        "moderate_cues": [
            "demoralization_or_abandonment_described",
            "passive_signals_linked_to_leadership",
            "actor_named_or_identifiable",
        ],
        
        "hard_negatives": [
            "too_vague_or_generic",
            "uses_conditional_language",
            "demoralization_due_to_external_factors",
            "staff_turnover_unrelated_to_leadership",
        ],
        
        "failure_types": [
            "reform_momentum_lost",
            "staff_demoralized",
            "institutional_commitment_eroded",
        ],
        
        "acceptance_rule": "strong >= 1 OR moderate >= 3",
        "use_reflection": False,
        
        "scope_lock": """This subschema captures passive commitment failure where leadership 
signals (through inaction, silence, or deprioritization) lead to demoralization or 
abandonment of reform efforts."""
    },
    {
        "subschema": "Delegated Leadership Failure",
        
        "strong_cues": [
            "central_decision_harmed_implementation_explicitly",
            "top_level_coordination_failure_identified",
        ],
        
        "moderate_cues": [
            "central_decision_harmed_implementation",
            "failure_due_to_top_level_coordination",
            "actor_named_or_identifiable",
        ],
        
        "hard_negatives": [
            "too_vague_or_generic",
            "uses_conditional_language",
            "operational_coordination_failure_only",
            "subnational_coordination_issue",
        ],
        
        "failure_types": [
            "implementation_undermined_by_center",
            "coordination_vacuum",
            "delegated_authority_not_supported",
        ],
        
        "acceptance_rule": "strong >= 1 OR moderate >= 3",
        "use_reflection": False,
        
        "scope_lock": """This subschema captures cases where central/top-level decisions or 
coordination failures harmed implementation. The failure must be at the leadership/center 
level, not operational coordination."""
    },
]

# COMMAND ----------

SCHEMA_2_1 = [
    {
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
]


# COMMAND ----------


SCHEMA_6_1 = [
    {
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
]

# COMMAND ----------

BOTTLENECK_SCHEMAS = {
    "1.1": SCHEMA_1_1,
    "2.1": SCHEMA_2_1,
    "6.1": SCHEMA_6_1,
}


def get_schema(bottleneck_id: str) -> Dict[str, Any]:
    if bottleneck_id not in BOTTLENECK_SCHEMAS:
        raise ValueError(f"No schema for {bottleneck_id}. Available: {list(BOTTLENECK_SCHEMAS.keys())}")
    return BOTTLENECK_SCHEMAS[bottleneck_id]
