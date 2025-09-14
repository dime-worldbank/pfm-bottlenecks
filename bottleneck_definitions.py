"""
Bottleneck definitions - all 28 bottlenecks across 9 challenges.
Clean, structured definition without CSV reading.
"""

from typing import Dict, List


def load_bottlenecks() -> Dict:
    """
    Return all bottleneck definitions in a clean, structured format.

    Returns:
        Dictionary with 'challenges' containing all 9 challenges and their bottlenecks
    """

# bottleneck_definitions.py
# ...keep your existing imports...

from typing import Dict, List

def load_bottlenecks() -> Dict:
    """
    Return all bottleneck definitions in a clean, structured format.
    """
    data = {
        'challenges': {
            1: {
                'name': 'Insufficient Stakeholder Commitment to Policy Action',
                'description': (
                    "Approved policies are not translated into action due to weak political/technical commitment, "
                    "reversals, lack of follow-through, narrow buy-in, or unwillingness to reallocate resources."
                ),
                'bottlenecks': [
                    {
                        'id': '1.1',
                        'name': 'Inadequate commitment of political and technical leadership to policy action and associated resource mobilization and use within or across sectors',
                        'description': 'Whist approved policies may state desired policy actions to achieve outcomes, neither politicians nor technocrats may be committed to driving the required action when this may require disrupting the status quo an/or changes in resource deployment and actions which adversely affect some stakeholders.'},
                    {
                        'id': '1.2','name': 'Inadequately broad-based stakeholder involvement, understanding and support for policy action and associated resource mobilization and use',
                        'description': 'Policy discussions and decisions happen within a narrow group of actors, with no significant involvement of relevant stakeholders, including service providers and beneficiaries. This limits the political acceptability of government policies, and the overall commitment to their implementation. It can also result in a disconnect between policies and actual demand for them.'},
                        ]
                        },
            2: {
                'name': 'Incoherence and fragmentation of policy',
                'description':
                    "Policies are inconsistent, overlapping or contradictory across/within sectors due to siloed design, weak coordination, and duplicative mandates—making implementation difficult.",
                'bottlenecks': [
                    {
                        'id': '2.1',
                        'name': 'Fragmented, inconsistent and uncoordinated policies across or within sectors',
                        'description': 'Different government policies, both sectoral and cross-sectoral, are designed without taking into account the constraints and/or complementarities that exist due to other government policies and commitments. This can be due to bureaucratic silos, management incentives or external donor support, and results in policies that are inconsistent and difficult to implement, or in unnecessary duplications and overlaps.'},
                        ]
                        },
            3: {
                'name': 'Inadequate Revenue Mobilization and Management',
                'description': (
                    "Public revenues are insufficient or poorly managed, and fiscal policy is weakly aligned to stated outcomes; "
                    "issues include low tax effort, leakages, weak pooling/transfers, and misaligned incentives."
                ),
                'bottlenecks': [
                    {
                        'id': '3.1',
                        'name': 'Insufficient revenue mobilization',
                        'description': 'Insufficient revenue mobilization efforts relative to the potential of the economy. Government revenues to fund public goods and services are often not adequate, and revenue mobilization efforts are hampered by weak systems, avoidance and inadequate governance.'},
                    {
                        'id': '3.2',
                        'name': 'Inefficient government transfer and resource pooling systems',
                        'description': 'When resources cannot be adequately pooled, it remains difficult to equitably redistribute, and to reduce disparities within and across administrative units. This can drive further fragmentation and affect equity.'},
                    {
                        'id': '3.3',
                        'name': 'Fiscal policy not aligned with desired development outcomes',
                        'description': 'Fiscal policies that are not strongly aligned with stated political or developmental priorities. Fiscal policies may not be clearly linked to desired political or developmental outcomes, resulting in limited efficient use of government resources, and creating missed opportunities for achieving targets.'},
                        ]
                        },
            4: {
                'name': 'Insufficiencies in spending execution',
                'description': (
                    "Spending fails at execution due to rigid structures, poor performance/accountability, and weak monitoring—"
                    "hindering timely, effective implementation and course correction."
                ),
                'bottlenecks': [
                    {
                        'id': '4.1',
                        'name': 'Institutional structures and management practices that are inflexible',
                        'description': 'In many settings, institutional structures and arrangements for public service provision are guided by rigid government policies and norms, that prevent officials and administrators from organizing their institutions and work flows in ways that will achieve the most impact with the resources they have available.'},
                    {
                        'id': '4.2',
                        'name': 'Weak staff performance management, accountability systems and enforcement',
                        'description': 'Individual staff performance standards, monitoring and consequences are not adequate. Staff members in public sector posts may not have clear performance standards and expectations, which makes it difficult to drive performance and hold individuals accountable for results.'},
                    {
                        'id': '4.3',
                        'name': 'Inadequate tools to monitor ongoing implementation at all levels',
                        'description': 'The lack of consistent, comprehensive data on results and expenditure hampers decision-making and course correction during implementation. In many settings, information systems are fragmented, indicator frameworks are misaligned, and data systems may not be digital or interoperable. This prevents managers and policy-makers from having a clear view of which policies are working and which are not.'},
                        ]
                        },
            5: {
                'name': 'Inadequate Budget Allocation and Management',
                'description': (
                    "Budgets are misaligned with needs, releases are unpredictable, and virement/line-item rigidity limits within-year "
                    "adjustment; planning and presentation are weak."
                ),
                'bottlenecks': [
                    {
                        'id': '5.1',
                        'name': 'Inadequate budget allocations and/or misalignment of funding flows with financing needs',
                        'description': 'In many settings, there is no clear strategic vision from government on how to target limited resources to achieve maximum impact, and there is no process to adequately channel funds to the most impactful areas. Resource allocation may be governed by ad hoc processes, rather than by an effort to align allocations with priority needs.'},
                    {
                        'id': '5.2',
                        'name': 'Unpredictable funding flows',
                        'description': 'In many settings, approved budgets do not adequately and predictably flow down to sub-national levels and frontline service provider units, making it difficult for these units to plan and implement development priorities.'},
                    {
                        'id': '5.3',
                        'name': 'Inflexible budget policies and procedures',
                        'description': 'Inflexible budget categories may not align with actual implementation priorities. When budgetary allocations in approved budgets are rigid, within year course corrections become difficult, and inefficiencies may persist.'},
                ]
            },
            6: {
                'name': 'Fragmented and uncoordinated deployment of development resources',
                'description': (
                    "Resources flow through multiple uncoordinated channels (on/off-treasury) with different systems/standards, "
                    "creating duplication, parallel structures, and blurred accountability."
                ),
                'bottlenecks': [
                    {
                        'id': '6.1',
                        'name': 'On-treasury resources deployed through non-coordinated channels and insufficiently harmonised systems and standards',
                        'description': 'Multiple government departments, programs, and initiatives may be providing resources for similar objectives, but using different channels, systems, standards, and approaches. This duplication of efforts can create inefficiencies and confusion at service delivery levels.'},
                    {
                        'id': '6.2',
                        'name': 'Lack of coordination of off-treasury development resources with government systems',
                        'description': 'Off-treasury resources including donor funding, loans and technical assistance often deployed through parallel, non-government channels with insufficient coordination with the national government. This creates duplication of efforts, inefficiencies in resource use, and can undermine government systems.'},
                ]
            },
            7: {
                'name': 'Procurement inefficiencies',
                'description': (
                    "Procurement is slow or distorted—multi-layer approvals, re-tendering, and weak/anticompetitive markets "
                    "inflate costs and delay delivery."
                ),
                'bottlenecks': [
                    {
                        'id': '7.1',
                        'name': 'Procurement delays and inefficiencies',
                        'description': 'Excessive and bureaucratic procurement requirements and approval processes can delay implementation of policies. This can also be driven by concerns about inadvertently not complying with the rules, without adequate flexibility to consider the urgency of the need and the nature of the goods and services being procured.'},
                    {
                        'id': '7.2',
                        'name': 'Poor market management of strategic commodities',
                        'description': 'Strategic commodities, such as certain medicines, fertilizers and seeds may be managed in inefficient ways due to the lack of a competitive and adequately structured market, leading to higher prices, lower quality of products, and/or other inefficiencies. This can also include strategic commodities and services being overpriced and inflated due to collusion of suppliers or inadequate procurement capacity within government.'},
                ]
            },
            8: {
                'name': 'Inefficiencies in frontline delivery',
                'description': (
                    "Service delivery suffers from staff shortages/skill-mix gaps, infrastructure deficits, stockouts, weak outreach "
                    "mechanisms, and poor quality standards/supervision."
                ),
                'bottlenecks': [
                    {
                        'id': '8.1',
                        'name': 'Inadequate quantity and skill mix of human resources',
                        'description': 'In many settings, the public sector workforce numbers are inadequate to deliver the scope of expected services. This can be due to insufficient hiring, high turnover, an inability to attract high caliber staff, as well as poor distribution across geographies and administrative units. Additionally, the skill mix within the workforce may not be aligned to service delivery needs.'},
                    {
                        'id': '8.2',
                        'name': 'Inadequate infrastructure',
                        'description': 'Inadequate physical infrastructure at frontline service delivery units, including buildings, equipment, utilities, and digital infrastructure for service provision. Without adequate infrastructure in place, even the most dedicated service delivery workforce would struggle to achieve the desired outcomes.'},
                    {
                        'id': '8.3',
                        'name': 'Supply shortages and stockouts of essential commodities',
                        'description': 'Essential commodities being unavailable at service delivery units when required. Causes can include inadequate quantification and forecasting, insufficient funding, and other supply chain bottlenecks.'},
                    {
                        'id': '8.4',
                        'name': 'Inadequate delivery mechanisms for reaching beneficiaries',
                        'description': 'Inadequate channels and approaches to reach and deliver to targeted beneficiaries. This can be driven by several supply side factors, such as insufficient outreach mechanisms in communities, unaffordable service delivery models, limited community health infrastructure. Or, it could be driven by demand side factors such as low demand for services from beneficiaries.'},
                    {
                        'id': '8.5',
                        'name': 'Poor standards and poor quality of services',
                        'description': 'Frontline staff may deliver sub-standard services due to insufficient skills and competencies, which have a detrimental effect on the achievement of development outcomes. This can be driven by weak accreditation and supervision systems, inadequate and insufficient training programs, and limited accountability for quality.'},
                ]
            },
            9: {
                'name': 'Structural or Contextual Barriers',
                'description': (
                    "Exogenous constraints—geography, socio-cultural norms, poverty, conflict/instability, disasters, migration—"
                    "that limit access or the feasibility of service delivery."
                ),
                'bottlenecks': [
                    {
                        'id': '9.1',
                        'name': 'Geographic barriers',
                        'description': 'Natural or physical geography creates difficulties in reaching populations with services. This includes populations living in remote, mountainous, or island regions, where the cost and complexity of service provision is significantly higher.'},
                    {
                        'id': '9.2',
                        'name': 'Socio-cultural barriers',
                        'description': 'Cultural, social or religious norms and practices that limit access to or utilization of government services by certain population groups. This can include gender-based discrimination, caste systems, or religious beliefs that prevent certain groups from accessing services.'},
                    {
                        'id': '9.3',
                        'name': 'Economic barriers (poverty)',
                        'description': 'Economic constraints that prevent populations from accessing services, even when they are available. This includes both direct costs (fees, transportation) and indirect costs (lost wages, opportunity costs) that make services unaffordable for poor populations.'},
                    {
                        'id': '9.4',
                        'name': 'Governance challenges (conflict, instability)',
                        'description': 'Political instability, conflict, or weak governance structures that prevent effective service delivery. This includes areas affected by war, insurgency, or where government authority is contested or absent.'},
                    {
                        'id': '9.5',
                        'name': 'Environmental challenges (natural disasters)',
                        'description': 'Environmental factors and natural disasters that disrupt service delivery systems. This includes floods, droughts, earthquakes, and other natural disasters that damage infrastructure and displace populations.'},
                    {
                        'id': '9.6',
                        'name': 'Demographic changes (urbanization, migration)',
                        'description': 'Rapid demographic shifts that strain existing service delivery systems. This includes rapid urbanization, large-scale migration, or refugee influxes that overwhelm existing infrastructure and services.'},
                ]
            },
        }
    }
    return data

# --- New: challenge-only helpers for the classifier ---

def load_challenge_definitions() -> Dict[int, Dict[str, str]]:
    """
    Returns {id: {"name": str, "description": str}} for the 9 challenges.
    """
    ch = load_bottlenecks()['challenges']
    return {i: {'name': ch[i]['name'], 'description': ch[i].get('description', '')} for i in range(1, 10)}


def format_challenge_definitions() -> str:
    """
    Compact text block you can inject into a prompt.
    """
    defs = load_challenge_definitions()
    lines: List[str] = []
    for i in range(1, 10):
        lines.append(f"{i}. {defs[i]['name']}: {defs[i]['description']}")
    return "\n".join(lines)


__all__ = [
    "load_bottlenecks",
    "load_challenge_definitions",
    "format_challenge_definitions",
]




# Helper constant for quick reference
CHALLENGE_SUMMARY = """
1. Insufficient Stakeholder Commitment to Policy Action (2 bottlenecks)
2. Incoherence and fragmentation of policy (1 bottleneck)
3. Inadequate Revenue Mobilization and Management (3 bottlenecks)
4. Insufficiencies in spending execution (3 bottlenecks)
5. Inadequate Budget Allocation and Management (3 bottlenecks)
6. Fragmented and uncoordinated deployment of development resources (2 bottlenecks)
7. Procurement inefficiencies (2 bottlenecks)
8. Inefficiencies in frontline delivery (5 bottlenecks)
9. Structural or Contextual Barriers (6 bottlenecks)
"""


CHALLENGE_CUES: Dict[str, List[str]] = {
    "1": ["political will", "leadership commitment", "policy reversal", "ministerial directive", "resistance to reform"],
    "2": ["conflicting policies", "policy overlap", "duplication of mandates", "uncoordinated policies", "bureaucratic silos"],
    "3": ["tax effort", "revenue collection", "tax-to-GDP", "tax compliance", "resource pooling", "fiscal policy alignment"],
    "4": ["rigid structures", "inflexible procedures", "performance management", "accountability systems", "fragmented data systems"],
    "5": ["budget misalignment", "unpredictable funding", "cash ceilings", "rigid budget categories", "within-year reallocations"],
    "6": ["off-budget", "parallel channels", "donor systems", "cash rationing", "mid-year reallocations", "earmarked transfers", "harmonization"],
    "7": ["procurement delays", "no-objection", "bid evaluation", "tender cancellation", "collusion", "market concentration"],
    "8": ["staff shortages", "skill mix", "stockouts", "supply shortages", "inadequate infrastructure", "outreach gaps", "quality standards"],
    "9": ["remote areas", "mountainous", "conflict-affected", "drought", "floods", "poverty", "cultural norms", "migration", "urbanization"],
}

def load_challenge_cues() -> Dict[str, List[str]]:
    return CHALLENGE_CUES
