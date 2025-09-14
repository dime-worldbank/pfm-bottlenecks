"""
Bottleneck context enhancement - Additional context and nuances for each bottleneck.
This file can be updated with expert insights to improve agent understanding.
"""

from typing import Dict, List, Optional


class BottleneckContext:
    """Enhanced context for bottlenecks including expert insights and nuances."""
    
    @staticmethod
    def get_context(bottleneck_id: str) -> Dict:
        """Get enhanced context for a specific bottleneck."""
        contexts = {
            "1.1": {
                "key_indicators": [
                    "Policy reversals or frequent changes in direction",
                    "Lack of follow-through on announced initiatives",
                    "Resource allocation not matching stated priorities",
                    "Leadership turnover affecting continuity"
                ],
                "common_phrases": [
                    "political will", "commitment gap", "implementation failure",
                    "policy reversal", "lack of follow-through", "empty promises"
                ],
                "nuances": [
                    "Distinguish between technical capacity issues and genuine lack of commitment",
                    "Look for patterns over time, not just single instances",
                    "Consider both political and bureaucratic commitment levels"
                ],
                "false_positive_warnings": [
                    "General complaints about government without specific commitment issues",
                    "Capacity problems that are mistaken for commitment issues",
                    "External constraints being blamed on lack of commitment"
                ],
                "extraction_guidance": """Look for evidence of:
- Political or technical leadership failing to implement approved policies
- Delays, resistance to change, or failure to act
- Refusal to reallocate resources despite stated goals
- Lack of follow-through on commitments
AVOID: General policy descriptions or intentions without evidence of failure"""
            },
            "1.2": {
                "key_indicators": [
                    "Limited consultation processes",
                    "Stakeholder complaints about exclusion",
                    "Policies developed by small groups",
                    "Lack of public awareness about policies"
                ],
                "common_phrases": [
                    "narrow consultation", "limited stakeholder engagement",
                    "top-down approach", "lack of buy-in", "exclusion of beneficiaries"
                ],
                "nuances": [
                    "Differentiate between formal consultation and meaningful engagement",
                    "Consider cultural context of stakeholder engagement",
                    "Look for evidence of actual exclusion, not just complaints"
                ],
                "extraction_guidance": """Look for evidence of:
- Limited or narrow stakeholder consultation
- Exclusion of key groups from policy processes  
- Lack of public awareness or buy-in
- Top-down decision making without engagement
AVOID: General complaints without specific exclusion evidence"""
            },
            "2.1": {
                "key_indicators": [
                    "Multiple agencies doing similar work",
                    "Conflicting policies or regulations",
                    "Duplication of programs or services",
                    "Lack of inter-agency coordination"
                ],
                "common_phrases": [
                    "working in silos", "policy overlap", "duplication of efforts",
                    "conflicting mandates", "uncoordinated approach", "fragmentation"
                ],
                "nuances": [
                    "Some overlap may be intentional for coverage",
                    "Distinguish between poor coordination and deliberate redundancy",
                    "Consider historical/political reasons for fragmentation"
                ],
                "extraction_guidance": """Look for evidence of:
- Multiple agencies doing similar/overlapping work
- Conflicting policies or regulations
- Duplication of programs or services
- Lack of coordination between departments
AVOID: Normal division of responsibilities"""
            },
            "3.1": {
                "key_indicators": [
                    "Low tax-to-GDP ratio",
                    "High levels of tax evasion/avoidance",
                    "Narrow tax base",
                    "Weak tax administration capacity"
                ],
                "common_phrases": [
                    "revenue shortfall", "tax gap", "collection efficiency",
                    "compliance rates", "tax effort", "revenue mobilization"
                ],
                "nuances": [
                    "Consider economic context (informal economy size)",
                    "Distinguish between policy issues and administrative weaknesses",
                    "Account for legitimate exemptions vs. leakages"
                ]
            ,
                "extraction_guidance": """Look for evidence of:
- Low tax collection rates or tax-to-GDP ratios
- High tax evasion or avoidance
- Weak tax administration capacity
- Narrow tax base or excessive exemptions
AVOID: General revenue discussions without specific mobilization issues"""
            },
            "3.2": {
                "key_indicators": [
                    "Fragmented funding pools",
                    "Inequitable resource distribution",
                    "Weak intergovernmental transfer systems",
                    "Earmarking preventing flexible allocation"
                ],
                "common_phrases": [
                    "resource pooling", "fiscal transfers", "equalization",
                    "earmarked funds", "fragmented financing", "vertical imbalance"
                ],
                "nuances": [
                    "Some earmarking may be constitutionally required",
                    "Consider federal vs. unitary system constraints",
                    "Distinguish between design issues and implementation problems"
                ]
            ,
                "extraction_guidance": """Look for evidence of:
- Fragmented funding pools preventing redistribution
- Inequitable resource transfers between regions/sectors
- Excessive earmarking limiting flexibility
- Weak pooling mechanisms
AVOID: Normal budget allocations without pooling issues"""
            },
            "3.3": {
                "key_indicators": [
                    "Budget not reflecting stated priorities",
                    "Pro-cyclical fiscal policies",
                    "Lack of medium-term perspective",
                    "Weak link between planning and budgeting"
                ],
                "common_phrases": [
                    "fiscal policy alignment", "budget priorities", "development outcomes",
                    "pro-cyclical", "planning-budget disconnect", "fiscal strategy"
                ],
                "nuances": [
                    "Consider external constraints on fiscal policy",
                    "Distinguish between political choices and technical issues",
                    "Account for emergency responses vs. systematic misalignment"
                ]
            ,
                "extraction_guidance": """Look for evidence of:
- Budget not matching stated policy priorities
- Fiscal policies undermining development goals
- Lack of link between planning and resource allocation
- Pro-cyclical spending patterns
AVOID: Budget constraints without misalignment evidence"""
            },
            "4.1": {
                "key_indicators": [
                    "Rigid organizational structures",
                    "Inability to reorganize or adapt",
                    "Excessive bureaucratic procedures",
                    "Lack of management autonomy"
                ],
                "common_phrases": [
                    "rigid structures", "bureaucratic inflexibility", "red tape",
                    "management constraints", "organizational rigidity", "process-bound"
                ],
                "nuances": [
                    "Some rigidity may be for accountability purposes",
                    "Consider legal/regulatory constraints",
                    "Distinguish between necessary controls and excessive rigidity"
                ]
            ,
                "extraction_guidance": """Look for evidence of:
- Rigid organizational structures preventing adaptation
- Excessive bureaucratic procedures
- Inability to reorganize or innovate
- Lack of management autonomy or flexibility
AVOID: Normal procedures without evidence of inflexibility"""
            },
            "4.2": {
                "key_indicators": [
                    "Absence of performance standards",
                    "No consequences for poor performance",
                    "Weak supervision and monitoring",
                    "Lack of performance incentives"
                ],
                "common_phrases": [
                    "accountability gap", "performance management", "no consequences",
                    "weak supervision", "lack of standards", "impunity"
                ],
                "nuances": [
                    "Consider civil service protections vs. accountability",
                    "Distinguish between individual and systemic issues",
                    "Account for capacity vs. motivation problems"
                ]
            ,
                "extraction_guidance": """Look for evidence of:
- Absence of performance standards or monitoring
- No consequences for poor performance
- Weak accountability systems
- Lack of supervision or oversight
AVOID: General morale issues without performance management gaps"""
            },
            "4.3": {
                "key_indicators": [
                    "Fragmented information systems",
                    "Lack of real-time data",
                    "Poor data quality or reliability",
                    "No feedback loops for decision-making"
                ],
                "common_phrases": [
                    "monitoring gaps", "data fragmentation", "information silos",
                    "reporting delays", "data quality", "M&E weaknesses"
                ],
                "nuances": [
                    "Consider technical infrastructure limitations",
                    "Distinguish between data availability and use",
                    "Account for capacity constraints in data management"
                ]
            ,
                "extraction_guidance": """Look for evidence of:
- Fragmented or non-existent information systems
- Lack of real-time data for decision making
- Poor data quality or reliability
- No monitoring of implementation progress
AVOID: Minor data issues without systemic monitoring gaps"""
            },
            "5.1": {
                "key_indicators": [
                    "Budget allocations not matching needs",
                    "Historical/incremental budgeting",
                    "Lack of needs assessment",
                    "Political rather than technical allocation"
                ],
                "common_phrases": [
                    "budget misalignment", "allocation inefficiency", "funding gaps",
                    "incremental budgeting", "political budgeting", "needs mismatch"
                ],
                "nuances": [
                    "Consider political economy constraints",
                    "Distinguish between allocation and execution issues",
                    "Account for external funding dependencies"
                ],
                "extraction_guidance": """Look for evidence of:
- Budget allocations not matching actual needs
- Historical/incremental budgeting without analysis
- Political rather than technical allocation decisions
- Lack of needs assessment in budgeting
AVOID: Budget constraints without misallocation evidence"""
            },
            "5.2": {
                "key_indicators": [
                    "Irregular fund releases",
                    "Cash rationing",
                    "Delayed transfers to service units",
                    "Unpredictable budget execution"
                ],
                "common_phrases": [
                    "unpredictable funding", "cash flow problems", "delayed releases",
                    "budget uncertainty", "irregular transfers", "cash rationing"
                ],
                "nuances": [
                    "Consider macroeconomic volatility impacts",
                    "Distinguish between systematic and occasional delays",
                    "Account for seasonal patterns in revenues"
                ],
                "extraction_guidance": """Look for evidence of:
- Irregular or unpredictable fund releases
- Cash rationing or delayed transfers
- Budget execution uncertainty
- Funds not reaching service delivery units
AVOID: One-time delays without systematic unpredictability"""
            },
            "5.3": {
                "key_indicators": [
                    "Rigid line-item budgets",
                    "No virement authority",
                    "Inability to reallocate during execution",
                    "Excessive budget categories"
                ],
                "common_phrases": [
                    "budget rigidity", "line-item constraints", "virement restrictions",
                    "inflexible categories", "reallocation barriers", "budget locks"
                ],
                "nuances": [
                    "Some rigidity ensures legislative oversight",
                    "Consider fraud/corruption prevention measures",
                    "Distinguish between needed flexibility and control"
                ],
                "extraction_guidance": """Look for evidence of:
- Rigid line-item budgets preventing reallocation
- No virement authority during execution
- Excessive budget categories limiting flexibility
- Inability to respond to changing needs
AVOID: Normal budget controls without excessive rigidity"""
            },
            "6.1": {
                "key_indicators": [
                    "Multiple government funding channels",
                    "Different systems and standards",
                    "Duplication at service delivery level",
                    "Lack of coordination mechanisms"
                ],
                "common_phrases": [
                    "parallel channels", "fragmented flows", "duplication",
                    "uncoordinated funding", "multiple systems", "harmonization gaps"
                ],
                "nuances": [
                    "Some separation may be for ring-fencing",
                    "Consider decentralization impacts",
                    "Distinguish between diversity and fragmentation"
                ],
                "extraction_guidance": """Look for evidence of:
- Multiple government funding channels for same purpose
- Different systems and standards across programs
- Duplication and confusion at service delivery level
- Lack of harmonization in government funding
AVOID: Normal program diversity without fragmentation"""
            },
            "6.2": {
                "key_indicators": [
                    "Donor projects outside government systems",
                    "Parallel implementation units",
                    "Off-budget financing",
                    "Lack of aid coordination"
                ],
                "common_phrases": [
                    "off-budget", "parallel systems", "donor fragmentation",
                    "aid coordination", "project implementation units", "bypassing government"
                ],
                "nuances": [
                    "Consider fiduciary risk concerns",
                    "Distinguish between temporary and permanent parallel systems",
                    "Account for capacity substitution vs. building"
                ],
                "extraction_guidance": """Look for evidence of:
- Donor projects bypassing government systems
- Parallel implementation units outside government
- Off-budget aid flows
- Lack of coordination with national systems
AVOID: Normal donor support without parallel structures"""
            },
            "7.1": {
                "key_indicators": [
                    "Lengthy procurement processes",
                    "Multiple approval layers",
                    "Frequent re-tendering",
                    "Procurement bottlenecks delaying implementation"
                ],
                "common_phrases": [
                    "procurement delays", "approval bottlenecks", "re-tendering",
                    "bureaucratic procurement", "slow procurement", "tender failures"
                ],
                "nuances": [
                    "Balance between speed and transparency",
                    "Consider corruption prevention measures",
                    "Distinguish between systematic and case-specific delays"
                ],
                "extraction_guidance": """Look for evidence of:
- Lengthy procurement processes causing delays
- Multiple approval layers slowing procurement
- Frequent re-tendering or bid failures
- Bureaucratic procurement requirements
AVOID: Normal procurement timelines without excessive delays"""
            },
            "7.2": {
                "key_indicators": [
                    "Market concentration/monopolies",
                    "Price inflation for government purchases",
                    "Collusion among suppliers",
                    "Poor quality of procured goods"
                ],
                "common_phrases": [
                    "market concentration", "price inflation", "supplier collusion",
                    "anti-competitive", "market manipulation", "overpricing"
                ],
                "nuances": [
                    "Consider legitimate market constraints",
                    "Distinguish between market failure and corruption",
                    "Account for geographic/infrastructure limitations"
                ],
                "extraction_guidance": """Look for evidence of:
- Market concentration or monopolies in government supply
- Price inflation for government purchases
- Collusion among suppliers
- Poor quality of procured goods/services
AVOID: Normal market competition without manipulation"""
            },
            "8.1": {
                "key_indicators": [
                    "High vacancy rates",
                    "Staff shortages in key positions",
                    "Skills mismatch",
                    "Geographic maldistribution"
                ],
                "common_phrases": [
                    "staff shortages", "vacancy rates", "skills gap",
                    "human resource constraints", "understaffing", "brain drain"
                ],
                "nuances": [
                    "Consider wage competitiveness issues",
                    "Distinguish between absolute shortages and distribution",
                    "Account for political appointments vs. merit"
                ],
                "extraction_guidance": """Look for evidence of:
- High vacancy rates in key positions
- Staff shortages affecting service delivery
- Skills mismatch or inadequate qualifications
- Geographic maldistribution of staff
AVOID: Minor staffing issues without systematic gaps"""
            },
            "8.2": {
                "key_indicators": [
                    "Dilapidated facilities",
                    "Lack of basic equipment",
                    "No utilities (electricity, water)",
                    "Poor ICT infrastructure"
                ],
                "common_phrases": [
                    "infrastructure deficit", "facility conditions", "equipment shortages",
                    "no electricity/water", "ICT gaps", "physical infrastructure"
                ],
                "nuances": [
                    "Consider maintenance vs. new infrastructure",
                    "Distinguish between urban and rural contexts",
                    "Account for climate/geographic challenges"
                ],
                "extraction_guidance": """Look for evidence of:
- Dilapidated or non-functional facilities
- Lack of basic equipment or utilities
- Poor ICT infrastructure
- Infrastructure preventing service delivery
AVOID: Minor maintenance issues without major deficits"""
            },
            "8.3": {
                "key_indicators": [
                    "Frequent stockouts",
                    "Supply chain disruptions",
                    "Poor forecasting/quantification",
                    "Storage and distribution problems"
                ],
                "common_phrases": [
                    "stockouts", "supply shortages", "commodity availability",
                    "supply chain", "distribution problems", "inventory management"
                ],
                "nuances": [
                    "Consider seasonal patterns",
                    "Distinguish between funding and logistics issues",
                    "Account for emergency vs. routine supplies"
                ],
                "extraction_guidance": """Look for evidence of:
- Frequent stockouts of essential supplies
- Supply chain disruptions
- Poor forecasting leading to shortages
- Storage and distribution problems
AVOID: Occasional shortages without systematic issues"""
            },
            "8.4": {
                "key_indicators": [
                    "Limited service coverage",
                    "Accessibility barriers",
                    "Weak outreach mechanisms",
                    "Demand-side constraints"
                ],
                "common_phrases": [
                    "coverage gaps", "access barriers", "outreach limitations",
                    "last mile delivery", "beneficiary reach", "service accessibility"
                ],
                "nuances": [
                    "Consider demand vs. supply issues",
                    "Distinguish between physical and social barriers",
                    "Account for cost and cultural factors"
                ],
                "extraction_guidance": """Look for evidence of:
- Limited service coverage or reach
- Accessibility barriers for beneficiaries
- Weak outreach mechanisms
- Last-mile delivery challenges
AVOID: Normal service limitations without delivery gaps"""
            },
            "8.5": {
                "key_indicators": [
                    "Poor service quality indicators",
                    "Lack of standards/protocols",
                    "Weak supervision systems",
                    "No quality assurance mechanisms"
                ],
                "common_phrases": [
                    "quality gaps", "substandard services", "poor quality",
                    "no standards", "weak supervision", "quality assurance"
                ],
                "nuances": [
                    "Consider measurement challenges",
                    "Distinguish between technical and interpersonal quality",
                    "Account for resource constraints on quality"
                ],
                "extraction_guidance": """Look for evidence of:
- Poor service quality indicators or outcomes
- Lack of standards or protocols
- Weak supervision and quality assurance
- Substandard service delivery
AVOID: Minor quality issues without systematic problems"""
            },
            "9.1": {
                "key_indicators": [
                    "Remote/isolated populations",
                    "Difficult terrain",
                    "High transport costs",
                    "Seasonal accessibility"
                ],
                "common_phrases": [
                    "geographic isolation", "remote areas", "difficult terrain",
                    "accessibility challenges", "distance barriers", "topographic constraints"
                ],
                "nuances": [
                    "Consider cost-effectiveness of reaching remote areas",
                    "Distinguish between permanent and seasonal barriers",
                    "Account for technology solutions potential"
                ],
                "extraction_guidance": """Look for evidence of:
- Geographic isolation preventing service access
- Difficult terrain or remoteness
- High transport costs as barriers
- Seasonal inaccessibility
AVOID: Normal distance without being a significant barrier"""
            },
            "9.2": {
                "key_indicators": [
                    "Cultural barriers to service use",
                    "Gender-based restrictions",
                    "Language barriers",
                    "Social exclusion"
                ],
                "common_phrases": [
                    "cultural barriers", "social norms", "gender discrimination",
                    "social exclusion", "cultural practices", "traditional beliefs"
                ],
                "nuances": [
                    "Respect cultural sensitivity",
                    "Distinguish between preferences and barriers",
                    "Consider intersectionality of barriers"
                ],
                "extraction_guidance": """Look for evidence of:
- Cultural barriers preventing service use
- Gender-based restrictions on access
- Language barriers
- Social exclusion or discrimination
AVOID: Cultural differences without being access barriers"""
            },
            "9.3": {
                "key_indicators": [
                    "Cost barriers to access",
                    "Opportunity costs",
                    "Poverty preventing service use",
                    "Catastrophic expenditures"
                ],
                "common_phrases": [
                    "affordability", "economic barriers", "poverty constraints",
                    "cost barriers", "financial access", "economic exclusion"
                ],
                "nuances": [
                    "Consider direct and indirect costs",
                    "Distinguish between absolute and relative poverty",
                    "Account for coping mechanisms"
                ],
                "extraction_guidance": """Look for evidence of:
- Cost barriers preventing access to services
- Unaffordable user fees or charges
- High opportunity costs of accessing services
- Poverty as a barrier to utilization
AVOID: Normal costs without being prohibitive"""
            },
            "9.4": {
                "key_indicators": [
                    "Conflict-affected areas",
                    "Political instability",
                    "Weak rule of law",
                    "Contested government authority"
                ],
                "common_phrases": [
                    "conflict zones", "instability", "fragile contexts",
                    "weak governance", "security challenges", "state fragility"
                ],
                "nuances": [
                    "Consider varying degrees of fragility",
                    "Distinguish between active conflict and post-conflict",
                    "Account for localized vs. national issues"
                ],
                "extraction_guidance": """Look for evidence of:
- Conflict or instability disrupting services
- Weak governance or rule of law
- Security challenges preventing delivery
- Contested government authority
AVOID: Minor security issues without major disruption"""
            },
            "9.5": {
                "key_indicators": [
                    "Natural disaster impacts",
                    "Climate vulnerability",
                    "Environmental degradation",
                    "Disaster-damaged infrastructure"
                ],
                "common_phrases": [
                    "disaster impact", "climate vulnerability", "environmental challenges",
                    "natural hazards", "disaster risk", "climate change"
                ],
                "nuances": [
                    "Consider frequency and severity",
                    "Distinguish between acute and chronic impacts",
                    "Account for adaptation capacity"
                ],
                "extraction_guidance": """Look for evidence of:
- Natural disasters disrupting services
- Climate impacts on infrastructure/delivery
- Environmental degradation affecting access
- Disaster damage to systems
AVOID: Minor weather events without significant impact"""
            },
            "9.6": {
                "key_indicators": [
                    "Rapid urbanization",
                    "Large-scale migration",
                    "Refugee influxes",
                    "Demographic transitions"
                ],
                "common_phrases": [
                    "urbanization pressure", "migration flows", "demographic change",
                    "population movement", "refugee crisis", "urban sprawl"
                ],
                "nuances": [
                    "Consider planned vs. unplanned changes",
                    "Distinguish between internal and cross-border movement",
                    "Account for temporary vs. permanent shifts"
                ],
                "extraction_guidance": """Look for evidence of:
- Rapid urbanization overwhelming services
- Large-scale migration straining systems
- Demographic shifts exceeding capacity
- Population movements disrupting delivery
AVOID: Normal population changes without strain"""
            }
        }
        
        # Return default context if specific bottleneck not found
        default_context = {
            "key_indicators": [],
            "common_phrases": [],
            "nuances": [],
            "false_positive_warnings": []
        }
        
        return contexts.get(bottleneck_id, default_context)
    
    @staticmethod
    def get_all_contexts() -> Dict:
        """Get all bottleneck contexts."""
        all_contexts = {}
        # Generate for all 28 bottlenecks
        bottleneck_ids = [
            "1.1", "1.2", "2.1", "3.1", "3.2", "3.3", "4.1", "4.2", "4.3",
            "5.1", "5.2", "5.3", "6.1", "6.2", "7.1", "7.2", "8.1", "8.2",
            "8.3", "8.4", "8.5", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6"
        ]
        for bid in bottleneck_ids:
            all_contexts[bid] = BottleneckContext.get_context(bid)
        return all_contexts
    
    @staticmethod
    def format_context_for_prompt(bottleneck_id: str, include_extraction_guidance: bool = False) -> str:
        """Format context as text for inclusion in prompts."""
        context = BottleneckContext.get_context(bottleneck_id)
        
        lines = []
        
        if context.get("key_indicators"):
            lines.append("KEY INDICATORS TO LOOK FOR:")
            for indicator in context["key_indicators"]:
                lines.append(f"  • {indicator}")
        
        if context.get("common_phrases"):
            lines.append("\nCOMMON PHRASES AND TERMINOLOGY:")
            lines.append(", ".join(context["common_phrases"]))
        
        if context.get("nuances"):
            lines.append("\nIMPORTANT NUANCES TO CONSIDER:")
            for nuance in context["nuances"]:
                lines.append(f"  • {nuance}")
        
        if context.get("false_positive_warnings"):
            lines.append("\nCOMMON FALSE POSITIVES TO AVOID:")
            for warning in context["false_positive_warnings"]:
                lines.append(f"  • {warning}")
        
        # Optionally include extraction guidance (not included by default as it's accessed separately)
        if include_extraction_guidance and context.get("extraction_guidance"):
            lines.append("\nEXTRACTION GUIDANCE:")
            lines.append(context["extraction_guidance"])
        
        return "\n".join(lines) if lines else ""