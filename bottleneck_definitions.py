"""
Bottleneck definitions - all 32 bottlenecks across 8 challenges.
Used by PreFilter for embedding-based similarity matching.
"""


BOTTLENECK_DATA = {
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
                    'description': 'Whilst approved policies may state desired policy actions to achieve outcomes, neither politicians nor technocrats may be committed to driving the required action, especially when this may require disrupting the status quo and/or changes in resource deployment and actions which adversely affect some stakeholders.',
                    'extended_definition': ''
                },
                {
                    'id': '1.2',
                    'name': 'Inadequately broad-based stakeholder involvement, understanding and support for policy action and associated resource mobilization and use',
                    'description': 'Policy discussions and decisions happen within a narrow group of actors, with no meaningful involvement of relevant stakeholders inside or outside the public sector, including service providers and beneficiaries. This limits the political acceptability of government policies, and the overall commitment to their implementation. It can also result in a disconnect between policies and actual needs and demand for them.',
                    'extended_definition': ''
                },
            ]
        },
        2: {
            'name': 'Incoherence between policy goals, context and available resources',
            'description': (
                "Policies proliferate, are poorly coordinated, inconsistent, aspirational, and unaffordable, "
                "without taking into account fiscal reality, costs, or organizational capability."
            ),
            'bottlenecks': [
                {
                    'id': '2.1',
                    'name': 'Fragmented, inconsistent and uncoordinated policies across or within sectors',
                    'description': 'Different government policies, both sectoral and cross-sectoral, tend to proliferate, be poorly coordinated and be inconsistent with each other as they are designed by different stakeholders without taking into account constraints and/or complementarities that exist due to other government policies and commitments. This can be due to bureaucratic silos, management incentives or external donor support, and results in policies that are inconsistent and difficult to implement, or in unnecessary duplications and overlaps.',
                    'extended_definition': """Fragmentation manifests both within and across sectors when policy design does not consider interdependencies, complementarities, or broader strategic frameworks. Examples include:
- Malawi: Donor funding locked into vertical disease-specific programs despite national Health Benefits Package consensus
- Kenya: Overlapping youth skills initiatives creating inefficiencies and blurred accountability
- Pakistan energy: Renewable energy policies developed in isolation from National Power Policy frameworks
- Indonesia: Infrastructure investments in education outpaced teaching quality reforms
- Ghana: Agricultural strategies disconnected from climate goals
- Liberia: Unbalanced funding across education levels despite universal basic education endorsement
- Vietnam: Solar feed-in tariffs without parallel transmission infrastructure investment created bottlenecks
- Kenya: Power generation capacity tripled but poor alignment with demand led to stranded assets"""
                },
                {
                    'id': '2.2',
                    'name': 'Public policies are not prioritized and are unaffordable given their cost and fiscal reality',
                    'description': 'Policy objectives are often aspirational and poorly prioritized. They do not take into account financial affordability and are not based on accurate and reliable costing. Delivery models, which often involve direct public delivery, crowd out potentially more cost-effective alternative models. Policies and strategies do not take into account medium- and long-term resource availability. This disconnect with fiscal reality undermines governments\' capacity to deliver on policy objectives individually and collectively.',
                    'extended_definition': ''
                },
                {
                    'id': '2.3',
                    'name': 'Policies are poorly designed do not take into account context, including the available organizational capability to achieve goals',
                    'description': 'Policies may not consider or elaborate how they will be implemented and a take into account existing available and required capabilities (including skills, systems and institutions etc.), interests (of politicians, the private sector, and citizens) and behavioral norms (culture, society). This means that they cannot be implemented as intended and objectives cannot be achieved.',
                    'extended_definition': ''
                },
            ]
        },
        3: {
            'name': 'Unsustainable fiscal situation of governments and organizations',
            'description': (
                "Short-term perspectives, biased forecasting, weak debt management, budget rigidity, and financial "
                "unviability of providers undermine fiscal sustainability and reduce fiscal space."
            ),
            'bottlenecks': [
                {
                    'id': '3.1',
                    'name': 'Short term incentives and perspectives leads to a failure to manage trade offstradeoffs and pro-cyclical spending which forces deep cuts during downturns',
                    'description': 'The lack of a medium- to long-term focus in fiscal policy formulation means governments fail to prioritize and manage trade-offs over time, and subsequently react to shocks in pro-cyclical ways, raising spending (or cutting taxes) during good times and having to reduce spending (or raise taxes) drastically during economic downturns. This in turn undermines governments\' capacity to deliver on policy objectives.',
                    'extended_definition': ''
                },
                {
                    'id': '3.2',
                    'name': 'Biased or inaccurate fiscal forecasting and unpredictable, volatile resource flows result in budgets being under-funded',
                    'description': 'Fiscal projections tend to be overly optimistic as they are based on weak models, unrealistic assumptions, insufficient data and/or are influenced by political interests, resulting in overestimating growth rates and revenues. Revenues also tend to be volatile, which coupled with weaknesses in within-year cash planning leads to a chronic shortage of financial resources to adequately fund expenditure',
                    'extended_definition': ''
                },
                {
                    'id': '3.3',
                    'name': 'Un-strategic, ad hoc and supply driven debt management undermines fiscal consolidation and reduces fiscal space',
                    'description': 'Debt management is not approached strategically, with limited efforts to link borrowing to funding government priorities and actively seeking out the best financing opportunities. Borrowing is often driven by short-term and political considerations, locking governments into higher-cost financing that puts fiscal sustainability at risk.',
                    'extended_definition': ''
                },
                {
                    'id': '3.4',
                    'name': 'Pre-existing earmarks and spending commitments create budget rigidity and limit options for fiscal consolidation and/or increasing fiscal space',
                    'description': 'Spending related to various types of entitlements, earmarking and mandatory servicing of debt obligations limit governments\' options in terms of both reducing spending when needed, of creating space for new spending to fund policy priorities, and of reallocating resources to enhance development impact.',
                    'extended_definition': ''
                },
                {
                    'id': '3.5',
                    'name': 'Financial unviability of providers and utilities',
                    'description': 'Utilities and frontline providers are financially unviable as a result of weak regulatory oversight, inadequate fiscal incentives and cost recovery and unreliable public revenues.',
                    'extended_definition': ''
                },
            ]
        },
        4: {
            'name': 'Inadequate and inequitable resources mobilized and deployed',
            'description': (
                "Insufficient and unstable revenue mobilization, costly financing, incremental budgeting disconnected "
                "from priorities, and inequitable resource deployment undermine effective public spending."
            ),
            'bottlenecks': [
                {
                    'id': '4.1',
                    'name': 'Domestic revenue policies generate insufficient and unstable resources - in an inequitable manner- to achieve policy goals given fiscal reality',
                    'description': 'In many countries, per capita GDP is low and, due to economic structure (large informal sectors, etc.) and weak capacities, governments only collect a limited share of GDP (10-15 percent) in revenues. This limits their fiscal capacity and fiscal space, constraining spending on priority policies aimed at achieving development outcomes. Studies on the financing gap for SDG achievement have shown this clearly. Further, many countries fail to collect taxes in a sustainable manner and thus have to resort to frequent and piecemeal adjustments to either tax rates or bases.',
                    'extended_definition': ''
                },
                {
                    'id': '4.2',
                    'name': 'Inadequate or costly financing mobilized for investment and service delivery',
                    'description': 'Financing available for funding investment, regulation and service delivery is costly, misaligned with policy priorities, and/or potentially distortionary reducing the impact of public spending.',
                    'extended_definition': ''
                },
                {
                    'id': '4.3',
                    'name': 'Resource raising and deployment is often incremental and disconnected from public policy priorities and delivery mechanisms',
                    'description': 'Budgets are formulated in an incremental manner and not through a process of strategic prioritization, due to the lack of clear linkages between revenue collection, planning and budgeting, a lack of credibly costed sector policies and strategies, and reluctance to move from the status quo.',
                    'extended_definition': ''
                },
                {
                    'id': '4.4',
                    'name': 'Resource deployment is not informed by demand for, the costs of, or performance in achieving public policy objectives',
                    'description': 'The allocation of financial resources in the budget process is not based on a clear assessment of the actual needs, costs of and performance in achieving policy objectives, undermining strategic resource allocation. .',
                    'extended_definition': ''
                },
                {
                    'id': '4.5',
                    'name': 'Unequal and inequitable resource deployment for delivery across geographies and groups and levels of government',
                    'description': 'Resource allocation and distribution does not take existing inequities in socioeconomic status into account (e.g. geographic, income, gender, etc.) or in access to benefits and services, limiting the effectiveness of public spending in addressing such inequities and broader policy objectives.',
                    'extended_definition': ''
                },
            ]
        },
        5: {
            'name': 'Unreliable, delayed and fragmented funding for delivery',
            'description': (
                "Multiple disconnected funding channels, incoherent intergovernmental financing, and shortfalls/delays "
                "in funding undermine effective resource deployment and service delivery."
            ),
            'bottlenecks': [
                {
                    'id': '5.1',
                    'name': 'Ad hoc, political and fragmented funding channels contribute to ineffective and inefficient delivery',
                    'description': 'Governments and public sector entities often rely on multiple and disconnected funding mechanisms to deploy financial resources and reach intended beneficiaries (these can be related to political interference, donor procedures, etc.), generating uncertainty and inefficiency.',
                    'extended_definition': """Funding for service delivery and projects is fragmented due to different funding sources/channels:
                    - Budget general funds from different ministries/agencies
                    - Earmarked funds from transfers from other governments, institutions, organizations
                    - Earmarked government revenues
                    - Donor funding with parallel systems

                    Multiple funding channels are challenging especially without integrated planning and management. Different management stages, procedures, non-consolidated information, and varying discretion levels create:
                    - Difficulty in rational policy planning due to uncertainty and unpredictability
                    - Costly administration
                    - Higher corruption and diversion risks

                    Political discretion creates obstacles to planning/execution:
                    - Changing priorities and biases toward new projects
                    - Reduced predictability of funding
                    - Start-stop patterns in project execution

                    Examples:
                    - Ethiopia: >50% donor funding through parallel systems
                    - Uganda & Indonesia: Multiple fragmented financing sources challenged local government planning
                    - Rwanda: Gender-based violence policies managed by 4+ ministries with donor funding
                    - Nigeria: Health financing highly fragmented across federal/state levels with multiple pools"""
                },
                {
                    'id': '5.2',
                    'name': 'Intergovernmental financing systems for delivery are often incoherent, bypassed and uncoordinated between levels of government',
                    'description': 'Intergovernmental revenue assignments and intergovernmental transfer systems are often ad hoc, have conflicting policy objectives, not based on clear functional assignments and associated expenditure and infrastructure needs, undermining the effective mobilization, deployment and use of public resources across levels of government and sectors.',
                    'extended_definition': ''
                },
                {
                    'id': '5.3',
                    'name': 'Shortfalls, delays and diversion of funding for delivery',
                    'description': 'Weak, ad hoc systems, bureaucratic procedures and political interference cause shortfalls in financial resources, their diversion from their intended purpose and delays in them getting to delivery units when needed.',
                    'extended_definition': ''
                },
            ]
        },
        6: {
            'name': 'Inefficient deployment and management of resources and inputs',
            'description': (
                "High overheads, poor investment management, inefficient human resource deployment, limited operational "
                "funding, procurement delays, and weak multi-level coordination undermine effective resource use."
            ),
            'bottlenecks': [
                {
                    'id': '6.1',
                    'name': 'Resource deployment is inefficient due to high overheads and unbalanced allocations to delivery inputs and sectoral programs',
                    'description': 'There is limited understanding of where major inefficiencies lie in different sectors and/or the causes of those inefficiencies. There may be high administrative overheads. There may be investment in high cost interventions relative to cost effective ones. Wages make up a large and increasing share of sector expenditure, squeezing out non-wage spending critical for regulation and delivery. Large subsides for SOEs absorb increasing shares of spending.',
                    'extended_definition': ''
                },
                {
                    'id': '6.2',
                    'name': 'Inefficient public investment decisions and management of assets',
                    'description': 'There may be a lack of complete, consistent, and up to date information on the status of ongoing, proposed, and stalled/delayed public investment projects. New projects may be included in the budget before existing projects are completed as political incentives push towards announcements of new projects. There may be a proliferation of small and non-strategic projects means that the overall capital portfolio is not aligned with national development priorities. Multi-year commitments to capital spending are not factored into the medium-term budget plan, leading to under-budgeting for capital. Public sector assets may not be properly maintained with new investment prioritized over maintaining existing ones.',
                    'extended_definition': ''
                },
                {
                    'id': '6.3',
                    'name': 'High cost, inefficient deployment, poor motivation and inadequate skills of frontline and other staff',
                    'description': 'Human resources may be of relatively high cost, as their may be a public sector wage premium. Human resources may not be deployed according to need and skills, and are often not qualified enough and not provided with adequate incentives (pay, working conditions, support, training, etc.) and motivated to do their job effectively.',
                    'extended_definition': ''
                },
                {
                    'id': '6.4',
                    'name': 'Limited availability of operational funding to regulate and run services and maintain infrastructure and other assets',
                    'description': 'Payment of wages and salaries eats up a large share of public resources, constraining spending on goods & services and other important operational expenses, and on capital expenditure, rendering government interventions less effective.',
                    'extended_definition': ''
                },
                {
                    'id': '6.5',
                    'name': 'Delays in and inflated cost of procurement for infrastructure and operational inputs',
                    'description': 'Procurement systems are weak, generating unnecessary delays and inflated costs in the acquisition of important operational inputs and infrastructure projects. This results in low quality and costly infrastructure, lack of inputs necessary for service delivery, etc.',
                    'extended_definition': ''
                },
                {
                    'id': '6.6',
                    'name': 'The arrangements for managing resources at the point of delivery is ineffective, especially in multi-level government contexts',
                    'description': 'The processes for managing and monitoring resources at central, subnational and frontline providers is often misaligned with multi level governance arrangements and available capacity. There is often a lack of coordination between sub-national and national budgeting processes results in incoherence in the deployment and use of resources as a whole. They may be similarly weak management and poor coordination across different types of organization - public sector, SOEs and the private sector. These challenges may be different for different types of input - human resources, operational inputs and infrastructure.',
                    'extended_definition': ''
                },
            ]
        },
        7: {
            'name': 'Resource management and oversight institutions discourage performance',
            'description': (
                "Strict controls limit autonomy, weak enforcement undermines compliance, tax administration is weak, "
                "fiscal governance is inadequate, and transparency/accountability mechanisms are insufficient."
            ),
            'bottlenecks': [
                {
                    'id': '7.1',
                    'name': 'The design of regulatory, incentive, control and management systems limits autonomy and discourages performance',
                    'description': 'Strict controls may limit flexibility to manage resources in line with needs, leading to ineffective spending and undermining performance. Taxation, tax expenditure, financing, regulation and incentive schemes are not focused on, inadequate and inconsistent with influencing behavior, investment and action.',
                    'extended_definition': ''
                },
                {
                    'id': '7.2',
                    'name': 'Non-compliance and weak enforcement of regulatory, PFM and public sector management systems undermines performance and accountability',
                    'description': 'Public sector systems, processes and procedures are not consistently utilized and followed by users or public sector workers due to user unfriendly design, inadequate skills, and weak incentives and enforcement, opening the way for inefficiencies, resource misuse and corrupt behavior.',
                    'extended_definition': ''
                },
                {
                    'id': '7.3',
                    'name': 'Weakness in tax compliance administration leads to inefficient or inequitable revenue collection and inefficient revenue management',
                    'description': 'Weaknesses in tax compliance administration undermine the fairness and efficiency of revenue collection. When tax laws are poorly enforced or compliance systems are weak, taxpayers may avoid or evade taxes, shifting the burden onto more compliant individuals and businesses. This not only reduces overall revenue but also erodes trust in the tax system. Inefficient revenue management undermines the governments ability to effectively forecast tax revenues, adequately account for tax revenues and maintain a VAT refund process.',
                    'extended_definition': ''
                },
                {
                    'id': '7.4',
                    'name': 'Weaknesses in fiscal governance undermine public and private investment and action',
                    'description': 'Weaknesses in macro-fiscal discipline, procurement, financial reporting and/or audit undermines government\'s ability to implement public sector programs and mobilize private finance for public and private investment and action.',
                    'extended_definition': ''
                },
                {
                    'id': '7.5',
                    'name': 'Inadequate transparency, oversight, monitoring, evaluation and accountability for resources and performance',
                    'description': 'Monitoring and evaluation systems are not well developed or functioning effectively. The internal audit, external audit and parliamentary oversight functions do not provide adequate accountability for both resource use and performance. There maybe inadequate transparency and/or involvement of beneficiaries in the monitoring and use of funds and service delivery. Weaknesses in accountability and transparency frameworks undermine public confidence in the integrity of the tax administration, impacting upon tax morale.',
                    'extended_definition': ''
                },
            ]
        },
        8: {
            'name': 'Inadequate use of sector and financial data in decision making and accountability',
            'description': (
                "Available information is not effectively used for decision making, and data systems have gaps, "
                "poor quality, and are fragmented without interoperability."
            ),
            'bottlenecks': [
                {
                    'id': '8.1',
                    'name': 'Available financial and non-financial information not used for decision making, management and accountability',
                    'description': 'Governments collect lots of information, both financial and non-financial, across many sectors and policy areas. Such information, however, is not effectively used and analyzed to support decision making processes, limiting the evidence on which policy formulation and implementation are based.',
                    'extended_definition': ''
                },
                {
                    'id': '8.2',
                    'name': 'Data systems have gaps and poor quality information, are fragmented and do not interoperate',
                    'description': 'Different types of data systems for managing different kinds of government information (central, local, sectoral, financial, performance, etc.) have gaps and poor quality information, are set up and managed in an uncoordinated way, and are not integrated in ways that could support better informed decision making.',
                    'extended_definition': ''
                },
            ]
        },
    }
}


def load_bottleneck_definition(bottleneck_id: str) -> dict:
    challenge_id = int(bottleneck_id.split('.')[0])
    challenge = BOTTLENECK_DATA['challenges'][challenge_id]

    for bn in challenge['bottlenecks']:
        if bn['id'] == bottleneck_id:
            return {
                'id': bn['id'],
                'name': bn['name'],
                'description': bn['description'],
                'extended_definition': bn.get('extended_definition', ''),
                'challenge_name': challenge['name'],
                'challenge_description': challenge['description']
            }
    raise ValueError(f"Bottleneck {bottleneck_id} not found")
