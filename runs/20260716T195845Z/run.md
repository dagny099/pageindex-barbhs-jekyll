# Retrieval run 20260716T195845Z

- Indexes: `IDX-D-gdpr`, `IDX-PDF-textheadings-gdpr`, `IDX-C0-gdpr`
- Retrievers: `gpt-4o-2024-11-20`
- Corpus: `gdpr-md-v1 (workspace/gdpr.md, pinned by sha256)` (`8557dfa77426…`)
- Repo commit: `d17398567c`  ·  questions: 24

## Comparison — means across questions

| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|---|
| `IDX-D-gdpr` | `gpt-4o-2024-11-20` | 24 | 3.9 | 2853.0 | 1574.1 | 10102 | 0.6661 | 7.3 |
| `IDX-PDF-textheadings-gdpr` | `gpt-4o-2024-11-20` | 24 | 3.9 | 2891.0 | 1347.8 | 9973 | 0.6551 | 7.4 |
| `IDX-C0-gdpr` | `gpt-4o-2024-11-20` | 24 | 3.8 | 15272.0 | 1413.6 | 35233 | 2.1707 | 7.5 |

## Per-question detail (question, expected evidence, ground truth, answer)
*Everything needed to score each answer is inline below — no cross-referencing.*

### [IDX-D-gdpr | gpt-4o-2024-11-20] GA1 — single-hop-lookup

**Q:** If a company breaks the data protection rules, how large a fine can it face at most, and what sorts of violations carry the steepest penalties?

metrics: tools=3 · struct_tok=2853 · content_tok=1275 · total_tok=9451 · $0.026 · 8.85s
fetched line ranges: `1772-1822`

**Answer:**

A company that violates data protection rules under the GDPR may face administrative fines categorized as follows:

1. **Up to €10 million or 2% of annual global turnover** (whichever is higher) for breaches such as:
   - Obligations of controllers or processors (e.g., related to data protection by design, security measures, or impact assessments) under Articles 8, 11, 25–39, and 42–43.
   - Breaches by certification bodies or monitoring bodies.

2. **Up to €20 million or 4% of annual global turnover** (whichever is higher) for more severe breaches, including:
   - Violations of the basic principles of processing (e.g., obtaining proper consent) under Articles 5-9.
   - Breaches of data subjects' rights under Articles 12–22.
   - Non-compliance with orders from supervisory authorities or violations related to cross-border data transfers under Articles 44–49.

The steepest penalties are reserved for intentional or negligent violations of fundamental principles like lawful data processing and respecting data subjects' rights, as well as for failing to comply with supervisory authority orders.

The fines are designed to be effective, proportional, and dissuasive, and Member States may also impose additional penalties for cases not covered. (Sources: Articles 83 and 84)

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GA2 — single-hop-lookup

**Q:** If a company suffers a personal data breach, how quickly must it tell the regulator, and what does it have to include if it reports later than that?

metrics: tools=3 · struct_tok=2853 · content_tok=361 · total_tok=8347 · $0.0218 · 7.14s
fetched line ranges: `962`

**Answer:**

If a company suffers a personal data breach, it must notify the supervisory authority without undue delay and, where feasible, within 72 hours after becoming aware of it, unless the breach is unlikely to result in a risk to the rights and freedoms of individuals. If the notification is made after 72 hours, it must include reasons for the delay.

Reference: **Article 33 — Notification of a personal data breach to the supervisory authority**.

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GA3 — single-hop-lookup

**Q:** What counts as 'personal data' under the GDPR, and what makes a person 'identifiable'?

metrics: tools=3 · struct_tok=2853 · content_tok=1696 · total_tok=9676 · $0.0254 · 5.23s
fetched line ranges: `405`

**Answer:**

According to **Article 4 — Definitions** of the GDPR:

1. **Personal data** is defined as any information relating to an identified or identifiable natural person (referred to as the "data subject"). A person is considered **identifiable** if they can be identified, directly or indirectly, through:
   - An **identifier** (e.g., name, identification number, location data, online identifier).
   - One or more factors specific to their **physical, physiological, genetic, mental, economic, cultural, or social identity**.

For further details, please see the section titled "Article 4 — Definitions."

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GA4 — single-hop-lookup

**Q:** How old does a child have to be to agree on their own to an online service, and how much are individual countries allowed to lower that age?

metrics: tools=3 · struct_tok=2853 · content_tok=220 · total_tok=8182 · $0.0213 · 4.09s
fetched line ranges: `537`

**Answer:**

A child must be at least **16 years old** to consent on their own to online services under Article 8 of the GDPR. However, individual Member States can lower this age, but not below **13 years**. 

This information is from **Article 8 — Conditions applicable to child's consent in relation to information society services**.

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GB1 — multi-hop-synthesis

**Q:** When is a company required to carry out a data protection impact assessment, and what must it do if that assessment shows a high risk it cannot reduce?

metrics: tools=4 · struct_tok=2853 · content_tok=1316 · total_tok=9518 · $0.0263 · 6.6s
fetched line ranges: `1022`, `994`

**Answer:**

A company is required to carry out a data protection impact assessment (DPIA) under Article 35 of the GDPR when a type of data processing, particularly involving new technologies, is likely to result in a high risk to the rights and freedoms of individuals. Specifically, this applies to cases such as:

- Systematic evaluations of personal aspects based on automated processing (including profiling) that have legal or significant effects on individuals.
- Large-scale processing of special categories of data (e.g., sensitive data or data on criminal convictions/offenses).
- Systematic large-scale monitoring of publicly accessible areas.

The assessment must include a description of the intended processing operations, their purposes, necessity, proportionality, associated risks, and the measures to address those risks (e.g., security safeguards).

If the DPIA indicates a high risk that cannot be sufficiently mitigated, the company (controller) must consult the supervisory authority before proceeding with the processing under Article 36. The authority then provides advice and, if necessary, prevents the processing if it infringes the GDPR. The supervisory authority may take up to 8 weeks to respond (extendable by 6 additional weeks if needed).

References:
- **Article 35 — Data protection impact assessment**
- **Article 36 — Prior consultation**

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GB2 — multi-hop-synthesis

**Q:** Health data and similar sensitive information get special treatment. How does the GDPR's default stance on processing sensitive data differ from its default stance on ordinary personal data, and give two grounds that allow sensitive data to be processed anyway.

metrics: tools=3 · struct_tok=2853 · content_tok=824 · total_tok=8956 · $0.0241 · 6.21s
fetched line ranges: `544`

**Answer:**

The GDPR's default stance on processing sensitive data, such as health data or data revealing racial or ethnic origin, is stricter than its treatment of ordinary personal data. By default, processing sensitive data is prohibited under **Article 9(1)**.

However, exceptions allow the processing of sensitive data under specific conditions, two of which include:

1. **Explicit Consent**: The data subject has given explicit consent for specific purposes, provided exceptions under Union or Member State law do not prohibit this ([Article 9(2)(a)]).

2. **Vital Interests**: Processing is necessary to protect the vital interests of the data subject or another person when the data subject is physically or legally incapable of giving consent ([Article 9(2)(c)]).

These safeguards reflect the importance of protecting sensitive information. For more details, refer to **Article 9 — Processing of special categories of personal data**.

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GB3 — multi-hop-synthesis

**Q:** After a data breach, how do the rules for notifying the regulator differ from the rules for notifying the affected individuals — in when each is required, how fast, and when you don't have to tell the individuals at all?

metrics: tools=4 · struct_tok=2853 · content_tok=1086 · total_tok=9576 · $0.0281 · 6.37s
fetched line ranges: `978-991`, `962-978`

**Answer:**

### Rules for Notifying the Regulator (Supervisory Authority) vs. Affected Individuals (Data Subjects)

#### Notification to the Supervisory Authority (Regulator)
1. **When Required**: A data breach must be reported to the supervisory authority when it poses any risk to the rights and freedoms of natural persons. Notification is not required if the risk is unlikely.
2. **Timeline**: Notification must occur **without undue delay** and, where feasible, no later than **72 hours** after becoming aware of the breach.
3. **Content of Notification**: The notification must include:
   - Nature of the data breach (categories and numbers of data subjects and records affected).
   - Contact information for follow-up.
   - Likely consequences of the breach.
   - Measures taken or proposed to mitigate the breach (Article 33).

#### Notification to Affected Individuals (Data Subjects)
1. **When Required**: Communication with individuals is required only when the breach is **likely to result in a high risk** to their rights and freedoms.
2. **Timeline**: Must occur **without undue delay**.
3. **Exemptions from Notification**:
   - Where effective technical and organizational measures (e.g., encryption) were in place, rendering the data unintelligible to unauthorized persons.
   - When subsequent actions reduce risks such that they are no longer likely to materialize.
   - If individual notification would involve **disproportionate effort**, in which case a public communication or equivalent method is used (Article 34).
4. **Content of Notification**: Must describe the nature of the breach in plain language and detail the consequences, mitigation measures, and where further assistance or information can be obtained (Article 34).

#### Differences in Requirements
- **Threshold for Notification**: Supervisory authority notification is required for any risk, while data subjects are only notified for high-risk breaches.
- **Exemptions for Individuals**: Controllers may avoid notifying individuals if specific mitigations (encryption or actions reducing risk) are in place or if it involves disproportionate effort.

### Sources Consulted
- [Article 33 — Notification of a personal data breach to the supervisory authority](functions.get_page_content, 962-978)
- [Article 34 — Communication of a personal data breach to the data subject](functions.get_page_content, 978-991)

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GB4 — multi-hop-synthesis

**Q:** When is a company required to appoint a Data Protection Officer, and what job protections and reporting line does that officer have?

metrics: tools=4 · struct_tok=2853 · content_tok=674 · total_tok=8881 · $0.0248 · 6.46s
fetched line ranges: `1061-1069`, `1045-1060`

**Answer:**

A company is required to appoint a Data Protection Officer (DPO) in the following situations, as outlined in **Article 37** of the General Data Protection Regulation (GDPR):

1. **Public Authorities or Bodies**: When processing is carried out by a public authority or body, except for courts acting in their judicial capacity.
2. **Large-Scale Monitoring**: When the core activities of the company involve regular and systematic monitoring of data subjects on a large scale.
3. **Large-Scale Processing of Special Data**: When the core activities involve large-scale processing of special categories of data (e.g., health data) or personal data relating to criminal convictions and offenses.

### Job Protections and Reporting Line
As stipulated in **Article 38**:
- The DPO must be involved in all issues related to data protection in a timely and proper manner.
- The organization must provide necessary resources and access to data to enable the DPO to perform their tasks effectively.
- The DPO must not receive instructions on performing tasks, nor can they be dismissed or penalized for executing their responsibilities.
- The DPO reports directly to the highest management level.
- Although the DPO may hold additional responsibilities in the organization, these must not create a conflict of interest.

These provisions ensure the DPO's independence and authority within the organization.

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GB5 — multi-hop-synthesis

**Q:** If a country has not been officially recognised as offering adequate data protection, how can a company still lawfully send personal data there, and what last-resort option remains if none of those tools are available?

metrics: tools=4 · struct_tok=2853 · content_tok=2430 · total_tok=10734 · $0.0297 · 7.56s
fetched line ranges: `1272-1296`, `1185-1204`

**Answer:**

If a country has not been officially recognized as providing adequate data protection, a company can still lawfully transfer personal data to that country under specific conditions:

1. **Using appropriate safeguards**: According to **Article 46**, personal data can be transferred if appropriate safeguards are in place. These safeguards may include:
   - Binding corporate rules (BCRs)
   - Standard data protection clauses adopted by the European Commission or a supervising authority
   - Approved codes of conduct or certification mechanisms accompanied by enforceable commitments (e.g., applying data subjects' rights).

2. **Derogations for specific situations**: Under **Article 49**, transfers may proceed in the absence of adequate safeguards or decisions if:
   - The data subject gives explicit consent after being informed of risks.
   - The transfer is necessary for contractual reasons, public interest, litigation, or vital interests.
   - The transfer is made from public registers under specific conditions.

3. **Last-resort option**: If both the safeguards and derogations are unavailable, a transfer may be allowed under **Article 49(1)(second subparagraph)** for compelling legitimate interests, subject to strict conditions:
   - The transfer must not be repetitive.
   - It must involve limited data subjects and be necessary for overriding interests.
   - The controller must assess the circumstances, implement safeguards, notify the supervisory authority, and inform data subjects about the transfer.

These measures collectively provide companies with ways to address international data transfers while respecting compliance obligations.

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GB6 — multi-hop-synthesis

**Q:** Someone who previously agreed to let a company use their data changes their mind and withdraws that agreement. What does the GDPR require about how withdrawal works, and can the person then demand their data be deleted — on what basis?

metrics: tools=4 · struct_tok=2853 · content_tok=1320 · total_tok=9549 · $0.0261 · 4.92s
fetched line ranges: `530-537`, `714-742`

**Answer:**

Under the GDPR:

1. **Withdrawing Consent**: Article 7(3) states that any individual who has given consent for their data to be processed has the right to withdraw that consent at any time. The withdrawal process must be as easy as giving consent, and individuals must be informed about this right before giving their consent. Withdrawal does not affect the lawfulness of processing that occurred while the consent was valid.

2. **Demand for Data Deletion**: After withdrawing consent, a person can demand that the data be deleted under the "right to erasure" (Article 17). This right applies where consent was the legal basis for processing, and no other legal grounds for processing the data exist (Article 17(1)(b)). However, certain exceptions (Article 17(3)) apply, such as compliance with legal obligations or for the establishment, exercise, or defense of legal claims, among others.

Relevant sections: 
- **Article 7 — Conditions for consent**
- **Article 17 — Right to erasure (‘right to be forgotten’)**

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GC1 — cross-reference-resolution

**Q:** If a person objects to a company continuing to use their personal data, on what basis can they object, and when can the company refuse to stop despite the objection?

metrics: tools=4 · struct_tok=2853 · content_tok=869 · total_tok=9146 · $0.0258 · 10.47s
fetched line ranges: `774`, `799`

**Answer:**

A person can object to the use of their personal data based on **Article 21 (Right to object)** of the GDPR. They have the right to object to processing in the following cases:

1. **Processing based on legitimate interests or public interest** (Article 6(1)(e) or (f)): A person can object on grounds relating to their specific situation. In such cases, the company must stop processing the data unless it demonstrates compelling legitimate grounds that override the individual's interests, rights, and freedoms, or if the processing is necessary for legal claims.

2. **Direct marketing purposes**: A person has an absolute right to object at any time. If they object, the company must stop processing their personal data for such purposes immediately.

3. **Research or statistical purposes**: A person can object if their situation justifies it unless the processing is essential for a task carried out in the public interest.

However, under **Article 23 (Restrictions)**, the company can refuse to stop processing if restrictions are imposed by **Union or Member State law** as a necessary measure in a democratic society for objectives, such as:
- Safeguarding national security, public security, or defense.
- Preventing, investigating, or prosecuting criminal offenses.
- Protecting important public (economic, financial) interests, public health, or social security.
- Ensuring judicial independence or regulating ethics in professions.

These restrictions must respect the essence of fundamental rights and freedoms, and their scope should be clearly defined. 

(Cited Articles: 21 — Right to object; 23 — Restrictions)

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GC2 — cross-reference-resolution

**Q:** Can a company make fully automated decisions about a person using sensitive data such as health information? If it is ever allowed, under what two conditions, and what safeguard must be in place?

metrics: tools=4 · struct_tok=2853 · content_tok=1115 · total_tok=13034 · $0.0347 · 7.01s
fetched line ranges: `783`, `544`

**Answer:**

A company can make fully automated decisions involving sensitive data such as health information, but only under specific conditions:

1. **Conditions**: 
   - The decision must meet one of the following criteria (as per Article 22(2)):
     - **Necessary for a contract** between the individual and the data controller (e.g., determining eligibility for a service).
     - **Based on explicit consent** of the individual.
     - **Authorized by law**, provided the law includes measures to safeguard the individual's rights, freedoms, and legitimate interests.

2. **Safeguard Requirement**:
   - Where decisions are based on sensitive data like health information (per Article 22(4) and Article 9(2)), safeguards must include **specific protective measures** for safeguarding the rights and interests of the data subject. This includes, at a minimum, the ability for the subject to:
     - Obtain human intervention.
     - Express their point of view.
     - Contest the decision.

Cited sections: Article 22 (Automated individual decision-making) and Article 9 (Processing special categories of personal data).

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GC3 — cross-reference-resolution

**Q:** A multinational wants to move personal data between its own entities in different countries using 'binding corporate rules.' What conditions must those binding corporate rules satisfy to be valid?

metrics: tools=3 · struct_tok=2853 · content_tok=941 · total_tok=9266 · $0.0266 · 10.72s
fetched line ranges: `1228`

**Answer:**

For binding corporate rules (BCRs) to be valid under Article 47 of the GDPR, they must satisfy the following conditions:

1. **General Requirements (Paragraph 1):**
   - **Legally Binding:** The rules must be legally binding and applicable internally and externally across all members of the group and their employees.
   - **Enforcement of Rights:** The rules must confer enforceable rights on data subjects regarding the processing of their personal data.
   - **Compliance with Paragraph 2:** The BCRs must fulfill the specific requirements outlined in Paragraph 2.

2. **Specific Requirements (Paragraph 2):**
   The BCRs must include:
   - Structure and contact details of the group and its members.
   - Nature of data transfers, including types of data, processing purposes, affected data subjects, and the third countries involved.
   - Legally binding nature both internally and externally.
   - Application of core data protection principles (e.g., purpose limitation, data minimization, and security measures) and rules for onward transfers.
   - Data subjects' rights (e.g., to lodge complaints, seek redress, and obtain compensation for breaches).
   - Acceptance of liability by entities in the EU for breaches by non-EU group members, with conditions for exemption.
   - Procedures for data subjects to access information about the BCRs.
   - Oversight mechanisms, including the role of a data protection officer or compliance entity, compliance verification processes, and audits.
   - Mechanisms for reporting and recording rule changes to supervisory authorities.
   - Cooperation mechanisms with supervisory authorities.
   - Mechanisms to report legal requirements in third countries that conflict with the BCRs and may undermine guarantees.
   - Data protection training for relevant personnel.

3. **Implementation Mechanisms (Paragraph 3):**
   The European Commission may establish formats and procedures for the exchange of BCR-related information between controllers, processors, and supervisory authorities.

These requirements ensure that multinational groups transfer personal data safely and comply with data protection standards. [Source: Article 47 — Binding corporate rules]

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GC4 — cross-reference-resolution

**Q:** The right to have your data erased does not apply when the data is needed for certain public-health purposes. What kinds of health-related processing fall under that exception?

metrics: tools=3 · struct_tok=2853 · content_tok=850 · total_tok=8888 · $0.0235 · 6.02s
fetched line ranges: `714-742`

**Answer:**

The exception to the right to have personal data erased for public health purposes applies to processing that is necessary:

- **"For reasons of public interest in the area of public health"** according to points (h) and (i) of Article 9(2), as well as Article 9(3).

These provisions highlight purposes such as protecting against serious cross-border health threats or ensuring high standards of quality and safety in health care and medicinal products or devices. The processing must comply with conditions and safeguards outlined in the GDPR.

This is specified in **Article 17(3)(c)** of the GDPR under the "Right to Erasure" section.

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GC5 — cross-reference-resolution

**Q:** If a company ignores a formal order from the data protection regulator, which level of fine does it face, and name three of the corrective powers the regulator can use.

metrics: tools=4 · struct_tok=2853 · content_tok=2335 · total_tok=10450 · $0.0278 · 6.96s
fetched line ranges: `1431-1492`, `1772-1822`

**Answer:**

If a company ignores a formal order from the data protection regulator under GDPR, it faces an administrative fine of up to **€20,000,000** or **4% of the total worldwide annual turnover of the preceding financial year**, whichever is higher (Article 83, paragraph 6).

Three corrective powers the regulator can use include (Article 58, paragraph 2):
1. **Order the rectification or erasure of personal data**, or restrict processing.
2. **Impose a temporary or definitive limitation**, such as a complete ban on processing.
3. **Suspend data flows** to a recipient in a third country or international organization.

These measures aim to ensure compliance and protect data subject rights.

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GD1 — scattered-enumeration

**Q:** What rights does the GDPR give individuals over their own personal data? List them.

metrics: tools=4 · struct_tok=2853 · content_tok=2441 · total_tok=10666 · $0.0297 · 6.87s
fetched line ranges: `684`, `710,714,742,760,774,783`

**Answer:**

The GDPR grants individuals (data subjects) the following rights over their personal data:

1. **Right to Access**: Individuals can confirm whether their data is being processed and access their personal data along with detailed information about its processing (Article 15).
2. **Right to Rectification**: Individuals can request the correction of inaccurate personal data and the completion of incomplete data (Article 16).
3. **Right to Erasure ('Right to be Forgotten')**: Individuals can request the deletion of their personal data under certain conditions (e.g., data is no longer necessary for its original purpose, or consent is withdrawn) (Article 17).
4. **Right to Restriction of Processing**: Individuals can request that the processing of their data be limited under specified circumstances (e.g., contesting its accuracy or unlawful processing) (Article 18).
5. **Right to Data Portability**: Individuals can receive their personal data in a structured, commonly used, machine-readable format and transfer it to another data controller (Article 20).
6. **Right to Object**: Individuals can object to processing based on legitimate interests, public interest tasks, or direct marketing purposes (Article 21).
7. **Rights Related to Automated Decision-Making and Profiling**: Individuals have the right not to be subject to decisions made solely on automated processing, including profiling, that produce significant effects (Article 22).

These rights are part of Chapter III of the GDPR. Each specific right provides detailed conditions and limitations to balance the interests of data subjects, controllers, and the public.

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GD2 — scattered-enumeration

**Q:** What documentation and record-keeping must a company maintain to show it complies with the GDPR — from the overarching duty to demonstrate compliance down to specific records of processing activities and of breaches?

metrics: tools=5 · struct_tok=2853 · content_tok=4484 · total_tok=13082 · $0.0378 · 10.66s
fetched line ranges: `910-940`, `962-978`, `840-947`

**Answer:**

Under the GDPR, companies must maintain specific documentation and records to demonstrate compliance. Key requirements include:

### 1. **General Duty to Demonstrate Compliance**
- **Responsibility of the Controller (Article 24):** Controllers must implement technical and organizational measures to ensure and demonstrate compliance with the GDPR. This can include adhering to approved codes of conduct or certification mechanisms where applicable.

### 2. **Records of Processing Activities**
- **For Controllers (Article 30(1)):** Must maintain records detailing:
  - Name and contact details of the controller, joint controllers, representative, and data protection officer.
  - Purposes of processing.
  - Categories of data subjects and personal data.
  - Categories of data recipients, including third country or international organizations.
  - Transfers of personal data and safeguards (where applicable).
  - Time limits for erasure of data (if possible).
  - General description of technical and organizational security measures.

- **For Processors (Article 30(2)):** Must maintain records that include:
  - Name and contact details of processors, controllers they act for, and the data protection officer.
  - Categories of processing carried out on behalf of controllers.
  - Data transfers (if applicable) with safeguards.
  - Description of technical and organizational security measures.

- Both sets of records must be in writing (electronic format is acceptable) and be made available to supervisory authorities upon request (Article 30(3-4)).

- **Exemptions:** Organizations with fewer than 250 employees are exempt unless the processing involves risks to data subjects, is not occasional, or involves sensitive data (Article 30(5)).

### 3. **Records of Data Breaches**
- **Notification of Personal Data Breaches (Articles 33-34):**
  - Controllers must notify the supervisory authority of personal data breaches within 72 hours, unless the breach is unlikely to pose a risk to data subjects. Notifications must include:
    - Breach nature and affected individuals.
    - Contact information for further details.
    - Likely consequences of the breach.
    - Measures taken to mitigate risks.
  - Breaches must be documented, stating the facts, impacts, and mitigation actions, enabling the supervisory authority to verify compliance (Article 33(5)).

- **High Risk Breach Communication (Article 34):** If a breach poses high risk to individuals, controllers must inform data subjects unless effective protection measures (e.g., encryption) mitigate the risk or informing them would require disproportionate effort.

### 4. **Cooperation with Supervisory Authorities**
- Controllers, processors, and their representatives are required to cooperate with supervisory authorities to fulfill GDPR obligations (Article 31).

These documentation and record-keeping standards ensure accountability and preparedness in case of supervisory authority inspections or inquiries. (References: Articles 24, 30-34).

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GD3 — scattered-enumeration

**Q:** If someone believes their data protection rights have been violated, what avenues of complaint and legal action can they pursue, and can they obtain compensation?

metrics: tools=4 · struct_tok=2853 · content_tok=2791 · total_tok=11336 · $0.0334 · 11.19s
fetched line ranges: `1735-1763`, `1763-1772`

**Answer:**

If someone believes their data protection rights under the GDPR have been violated, they have the following avenues for complaint and legal action:

### 1. **Complaining to a Supervisory Authority**
   - **Right to Lodge a Complaint (Article 77):** Data subjects can file a complaint with a supervisory authority, especially in the EU Member State of their habitual residence, workplace, or where the alleged infringement occurred. This process allows the individual to report violations of the GDPR's provisions.
   - The supervisory authority is obligated to inform the complainant about the progress and outcome of the complaint, including the possibility of pursuing a judicial remedy under Article 78.

### 2. **Judicial Remedies**
   - **Against Supervisory Authorities (Article 78):** Data subjects can seek judicial remedies if:
     - A supervisory authority issues a legally binding decision affecting them.
     - The supervisory authority fails to handle their complaint or provide a response within three months.
     - Such cases can only be brought in the Member State where the supervisory authority is located.
   - **Against Controllers or Processors (Article 79):** If a controller or processor violates GDPR rights (e.g., through improper data processing), individuals have the right to pursue judicial proceedings directly against the entity. These proceedings can take place either in the jurisdiction of the entity’s establishment or the data subject’s habitual residence.

### 3. **Representation**
   - **Representation by Advocacy Groups (Article 80):** Affected individuals can mandate non-profit organizations or associations to:
     - File complaints on their behalf.
     - Seek compensation or enforce other GDPR-provided rights, if permitted under national law.
   - Additionally, groups may independently initiate complaints in cases of infringement, even without a direct mandate from data subjects.

### 4. **Right to Compensation (Article 82)**
   - **Damages:** Individuals suffering **material** or **non-material damage** due to GDPR violations can claim compensation from the responsible data controller or processor.
   - **Liability:** Controllers and processors are liable unless they prove they were not responsible for the events causing the damage. If multiple parties are involved, they may be jointly liable to ensure effective compensation.
   - **Court Cases:** Compensation claims must be filed in courts authorized under national jurisdiction principles, as outlined in Article 79(2).

### 5. **Administrative Penalties (Article 83)**
   - Supervisory authorities may impose fines for GDPR infringements, with amounts ranging up to:
     - €10 million or 2% of worldwide annual turnover for certain conditions.
     - €20 million or 4% of the worldwide annual turnover for more serious breaches.
   - Fines aim to be effective, proportionate, and dissuasive.

These measures ensure individuals have multiple pathways to protect their rights. Key articles include **Articles 77-80, 82, and 83** of the GDPR.

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GD4 — scattered-enumeration

**Q:** The GDPR encourages voluntary codes of conduct and certification schemes. What are these mechanisms, and who checks that organisations actually comply with each of them?

metrics: tools=6 · struct_tok=2853 · content_tok=2841 · total_tok=11226 · $0.0316 · 8.18s
fetched line ranges: `1124`, `1141`, `1088`, `1152`

**Answer:**

The GDPR promotes voluntary **codes of conduct** and **certification schemes** to ensure compliance with its provisions. These mechanisms are intended to provide specific guidance for applying the regulation and to create frameworks for verifying compliance. Here's a summary of what they entail and the compliance checks associated with each:

1. **Codes of Conduct (Article 40)**  
   - Associations or industry bodies may develop codes of conduct to detail how to apply the GDPR to specific sectors.
   - These codes may cover areas like fair processing, data breaches, pseudonymisation, and data subject rights.
   - These codes are monitored by independent bodies accredited by supervisory authorities, as detailed in **Article 41**. These bodies:
     - Must demonstrate independence and expertise.
     - Are responsible for handling complaints, monitoring adherence, and, if necessary, suspending or excluding non-compliant organizations.
     - Report to supervisory authorities, which retain the power to revoke the monitoring body's accreditation if its conditions are no longer met.

2. **Certification Mechanisms (Article 42)**  
   - These mechanisms (e.g., seals or marks) demonstrate compliance with GDPR requirements and are voluntary.
   - Certifications are issued by certification bodies or supervisory authorities based on approved criteria.
   - Certification bodies, as outlined in **Article 43**, must demonstrate independence, expertise, and procedural integrity. They are accredited by national authorities or supervisory bodies and provide reasons for issuing or withdrawing certifications.
   - Certifications are valid for up to three years and can be revoked if requirements are no longer met.

In summary:
- Codes of conduct are monitored by accredited bodies and supervisory authorities (Article 41).
- Certification compliance is verified by certification bodies or supervisory authorities (Article 43).

Relevant sections: **Article 40, Article 41, Article 42, and Article 43.**

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GD5 — scattered-enumeration

**Q:** When a company collects someone's personal data, what must it tell that person, and how do those obligations differ depending on whether the data was collected directly from the person or obtained from somewhere else?

metrics: tools=4 · struct_tok=2853 · content_tok=1629 · total_tok=10022 · $0.0287 · 10.12s
fetched line ranges: `605`, `636`

**Answer:**

When a company collects personal data, its obligations depend on whether the data was collected directly from the individual or obtained from another source.

### 1. **If the Data is Collected Directly (Article 13)**:
The company (data controller) must inform the individual **at the time of collection** about:
- **Identity and contact details** of the controller (and representative, if any).
- Contact details of the data protection officer (if applicable).
- Purposes and legal basis for processing.
- Recipients (or categories of recipients) of the data.
- If data will be transferred to a third country, information on safeguards or adequacy decisions.
- Storage period (or criteria to define it).
- Rights of the individual (e.g., access, rectification, erasure, data portability, objection to processing, withdrawing consent, filing complaints).
- Whether providing the data is mandatory, the consequences of refusal to provide data, and information about any automated decision-making (e.g., profiling).

### 2. **If the Data is Obtained from Other Sources (Article 14)**:
The company must provide similar information to that listed above, adding:
- The **categories of personal data** collected.
- The **source of the data**, including whether it originated from public sources.

The company must provide this information:
- **Within one month** after obtaining the data.
- At the time of first contact with the individual, or before disclosing the data to another party.

### Key Differences:
- **Timing**: Direct collection requires information at the time of data collection. For other sources, the controller has a one-month deadline (or sooner if first contact/disclosure occurs earlier).
- **Source Disclosure**: For data not collected directly, the source of the data must also be disclosed.
- **Category of Data**: If not collected directly, the type/categories of data being processed must be communicated.

These obligations aim to ensure transparency and fairness in personal data processing as stipulated under the GDPR. (Cited: Articles 13 and 14).

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GE1 — boundary-absence

**Q:** Does the GDPR apply to a private individual who keeps a personal address book or uses social media purely for personal reasons? Where does its scope stop?

metrics: tools=3 · struct_tok=2853 · content_tok=497 · total_tok=8498 · $0.0224 · 5.47s
fetched line ranges: `380-395`

**Answer:**

The GDPR explicitly does not apply to a natural person who processes personal data "in the course of a purely personal or household activity," as stated in **Article 2(2)(c)—Material Scope**. This means that activities such as maintaining a personal address book or using social media purely for personal reasons typically fall outside the GDPR’s scope. 

However, the regulation applies broadly to processing personal data through automated means or forming part of a filing system unless specifically exempted.

Cited: **Article 2—Material Scope**.

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GE2 — boundary-absence

**Q:** Does the GDPR protect the personal data of people who have died, and can individual countries set their own rules on this?

metrics: tools=5 · struct_tok=2853 · content_tok=2021 · total_tok=13861 · $0.0361 · 6.58s
fetched line ranges: `1884`, `380`, `405`

**Answer:**

The GDPR defines "personal data" as data relating to an "identified or identifiable natural person" (Article 4). It does not specifically extend protection to the personal data of deceased individuals, as such people no longer meet the definition of "natural person."

However, under Article 2, GDPR provisions do not impose restrictions on Member States concerning the deceased, meaning individual countries can establish their own legal rules to address this matter. 

This interpretation is grounded in Articles 2 (Material Scope) and 4 (Definitions).

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GE3 — boundary-absence

**Q:** Does the GDPR set a fixed maximum length of time — a specific number of days or years — that personal data may be kept? If not, what does it require instead?

metrics: tools=4 · struct_tok=2853 · content_tok=961 · total_tok=9146 · $0.0251 · 5.62s
fetched line ranges: `478`, `714`

**Answer:**

The GDPR does not set a fixed maximum length of time (e.g., a specific number of days or years) for which personal data may be kept. Instead, it requires that personal data be kept "no longer than is necessary for the purposes for which the personal data are processed." This principle is known as "storage limitation" (Article 5(1)(e)). 

However, data can be stored for longer periods if it is processed exclusively for purposes such as archiving in the public interest, scientific or historical research, or statistical purposes, provided appropriate safeguards are implemented to protect individuals' rights and freedoms [Article 5 — Principles relating to processing of personal data]. 

In addition, personal data must be erased without delay if it is no longer necessary for the purposes it was collected, as specified in the "right to erasure" (Article 17). This requires controllers to evaluate the necessity of data retention periodically. 

Cited Articles:
- [Article 5 — Principles relating to processing of personal data]
- [Article 17 — Right to erasure ('right to be forgotten')]

---

### [IDX-D-gdpr | gpt-4o-2024-11-20] GE4 — boundary-absence

**Q:** Does the GDPR apply to anonymous information that cannot be traced to a specific person, including when it is used for statistics or research?

metrics: tools=5 · struct_tok=2853 · content_tok=2801 · total_tok=10948 · $0.0293 · 5.55s
fetched line ranges: `380-395`, `1850-1857`, `405-475`

**Answer:**

The GDPR does not apply to anonymous information that cannot be traced to an identifiable individual. Article 4 defines "personal data" as information related to an identified or identifiable person. Fully anonymized data that cannot be linked back to an individual falls outside GDPR's scope. 

Moreover, Article 89 emphasizes safeguards for processing data for archiving, statistical, or research purposes. It explicitly states that when these purposes can be fulfilled without permitting the identification of data subjects (such as through anonymization), this approach should be adopted. 

Thus, statistical or research use of genuinely anonymous information is not regulated by the GDPR. 

(Cited sections: "Article 4 — Definitions," "Article 89 — Safeguards and derogations relating to processing for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes.")

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GA1 — single-hop-lookup

**Q:** If a company breaks the data protection rules, how large a fine can it face at most, and what sorts of violations carry the steepest penalties?

metrics: tools=3 · struct_tok=2891 · content_tok=1467 · total_tok=9717 · $0.0264 · 7.54s
fetched line ranges: `0106,0107`

**Answer:**

Under the GDPR:

1. The maximum fine a company can face is **€20 million** or **4% of the total worldwide annual turnover** of the preceding financial year, whichever is higher ([Article 83](#)).

2. **Steepest penalties** apply to violations such as:
   - Breach of **basic principles for processing data** (e.g., lawful processing, consent conditions) under Articles 5, 6, 7, and 9.
   - Failing to respect data subject rights (e.g., access, deletion) under Articles 12–22.
   - Unlawful **transfers of personal data** to third countries or international organizations under Articles 44–49.
   - Ignoring supervisory authority orders to limit or suspend activities ([Article 83(5)](#)).

Violations of other obligations, such as failing to maintain adequate records or implement required safeguards, may incur fines of up to **€10 million** or **2% of the total worldwide turnover** of the previous year ([Article 83(4)](#)).

These penalties are meant to be effective, proportionate, and dissuasive.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GA2 — single-hop-lookup

**Q:** If a company suffers a personal data breach, how quickly must it tell the regulator, and what does it have to include if it reports later than that?

metrics: tools=3 · struct_tok=2891 · content_tok=422 · total_tok=8588 · $0.023 · 7.17s
fetched line ranges: `0044`

**Answer:**

If a company suffers a personal data breach:

1. **Notification Timing:** The controller must notify the supervisory authority **without undue delay** and, where feasible, **within 72 hours** of becoming aware of the breach. If they notify later than 72 hours, they must provide reasons for the delay.

2. **Required Information in a Notification:**
   - A description of the breach, including the categories and approximate number of data subjects and records affected.
   - The name and contact details of the data protection officer or another contact point for further information.
   - The likely consequences of the breach.
   - Measures taken or proposed to address the breach and mitigate its effects.

(Referenced from **Article 33 — Notification of a personal data breach to the supervisory authority**.)

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GA3 — single-hop-lookup

**Q:** What counts as 'personal data' under the GDPR, and what makes a person 'identifiable'?

metrics: tools=3 · struct_tok=2891 · content_tok=1941 · total_tok=10048 · $0.0265 · 8.84s
fetched line ranges: `0005`

**Answer:**

Under the GDPR, **'personal data'** is defined as "any information relating to an identified or identifiable natural person ('data subject')." An identifiable person is someone who can be identified, directly or indirectly, through various means, such as:

1. Identifiers like:
   - Name,
   - Identification number,
   - Location data,
   - Online identifiers.
2. Factors specific to their physical, physiological, genetic, mental, economic, cultural, or social identity.

Thus, a person is considered 'identifiable' when they can be distinguished either by unique personal attributes or through the use of relevant data (e.g., online or technical identifiers). [Referenced: Article 4 — Definitions]

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GA4 — single-hop-lookup

**Q:** How old does a child have to be to agree on their own to an online service, and how much are individual countries allowed to lower that age?

metrics: tools=3 · struct_tok=2891 · content_tok=295 · total_tok=8399 · $0.0221 · 4.28s
fetched line ranges: `0010`

**Answer:**

According to **Article 8** of the GDPR, a child must be at least **16 years old** to independently consent to the use of information society services. If a child is below 16, consent must be provided or authorized by the holder of parental responsibility. However, **Member States** are allowed to lower this age, but it cannot go below **13 years**.

This information comes from **Article 8 — Conditions applicable to child's consent in relation to information society services**.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GB1 — multi-hop-synthesis

**Q:** When is a company required to carry out a data protection impact assessment, and what must it do if that assessment shows a high risk it cannot reduce?

metrics: tools=4 · struct_tok=2891 · content_tok=1560 · total_tok=9795 · $0.0264 · 7.25s
fetched line ranges: `0048`, `0047`

**Answer:**

A company must carry out a Data Protection Impact Assessment (DPIA) when a type of data processing is "likely to result in a high risk to the rights and freedoms of natural persons," particularly when using new technologies. Examples include systematic automated evaluation affecting individuals significantly, large-scale processing of sensitive data, or systematic monitoring of public areas (refer to **Article 35**).

The DPIA must describe the processing, its purposes, assess risks, and outline measures to address them. If the DPIA reveals risks that cannot be mitigated, the controller is required to consult the supervisory authority before proceeding. The supervisory authority may advise on mitigating the risk or, if it deems the processing to violate regulations, suggest changes or prohibit the activity (**Article 36**).

Cited sections: **Article 35 — Data Protection Impact Assessment** and **Article 36 — Prior Consultation**.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GB2 — multi-hop-synthesis

**Q:** Health data and similar sensitive information get special treatment. How does the GDPR's default stance on processing sensitive data differ from its default stance on ordinary personal data, and give two grounds that allow sensitive data to be processed anyway.

metrics: tools=3 · struct_tok=2891 · content_tok=960 · total_tok=9209 · $0.0247 · 5.9s
fetched line ranges: `0011`

**Answer:**

The GDPR's default stance is to prohibit the processing of sensitive personal data (e.g., racial or ethnic origin, political opinions, health data, etc.), as stated in Article 9(1). This stands in contrast to its default approach to ordinary personal data, which can be processed as long as it meets at least one lawful ground under Article 6.

Processing sensitive data is only allowed if specific conditions are met. Two such grounds include:

1. **Explicit Consent**: The data subject must give explicit consent for one or more specified purposes unless restricted by Union or Member State law. [Article 9(2)(a)].
2. **Vital Interests**: Processing is necessary to protect the vital interests of the data subject or another natural person when the subject is incapable of giving consent [Article 9(2)(c)].

For further conditions, see **Article 9: Processing of special categories of personal data**.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GB3 — multi-hop-synthesis

**Q:** After a data breach, how do the rules for notifying the regulator differ from the rules for notifying the affected individuals — in when each is required, how fast, and when you don't have to tell the individuals at all?

metrics: tools=4 · struct_tok=2891 · content_tok=860 · total_tok=9251 · $0.0258 · 6.02s
fetched line ranges: `0044`, `0045`

**Answer:**

The rules for notifying the regulator (supervisory authority) and affected individuals following a data breach differ based on urgency, circumstances, and exceptions, described in **Articles 33 and 34 of the GDPR**.

### Notification to the Supervisory Authority (Regulator)
- **Timing**: Notification must occur without undue delay and **no later than 72 hours** after becoming aware of the breach, unless it is unlikely to result in a risk to the rights and freedoms of data subjects.
- **Exceptions**: No notification is required if no risk is posed to the rights and freedoms of individuals.

### Notification to Affected Individuals (Data Subjects)
- **Timing**: Notification must occur **without undue delay** if the breach is likely to result in a **high risk** to the rights and freedoms of individuals.
- **Exceptions**: Notification is not required if:
  1. **Measures such as encryption** make the data unintelligible to unauthorized persons.
  2. **Mitigation measures** have been taken to prevent the high risk from materializing.
  3. Notification would involve a **disproportionate effort**, in which case a public communication serving the same purpose may suffice.
- The supervisory authority may compel or waive the need for communication to individuals depending on the risk assessment.

**Sources Consulted**: Articles 33 and 34.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GB4 — multi-hop-synthesis

**Q:** When is a company required to appoint a Data Protection Officer, and what job protections and reporting line does that officer have?

metrics: tools=4 · struct_tok=2891 · content_tok=820 · total_tok=9179 · $0.0259 · 6.3s
fetched line ranges: `0050`, `0051`

**Answer:**

A company is required to appoint a Data Protection Officer (DPO) in the following situations (Article 37):

1. **Public Authorities**: If the processing is carried out by a public authority or body, except for courts acting in their judicial capacity.
2. **Systematic Monitoring**: If the core activities involve processing that requires regular and systematic monitoring of data subjects on a large scale.
3. **Sensitive Data**: If the core activities involve large-scale processing of special categories of data (Article 9) or personal data relating to criminal convictions and offenses (Article 10).

### Job Protections and Reporting Line (Article 38):
1. **Involvement in Data Protection Issues**: The DPO must be involved properly and in a timely manner in all issues relating to personal data protection.
2. **Resources and Support**: The DPO must have the necessary resources to perform their tasks, access to processing operations, and opportunities to maintain their expert knowledge.
3. **Independence**: The DPO must not receive instructions regarding their tasks, and they cannot be dismissed or penalized for fulfilling their duties.
4. **Reporting Line**: The DPO must directly report to the highest management level of the controller or processor.
5. **Confidentiality**: They are bound by secrecy or confidentiality as per Union or Member State law.
6. **Other Duties**: The DPO may perform other tasks, provided these do not lead to a conflict of interest. 

These provisions ensure the role of the DPO is safeguarded and effective in maintaining compliance with data protection laws.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GB5 — multi-hop-synthesis

**Q:** If a country has not been officially recognised as offering adequate data protection, how can a company still lawfully send personal data there, and what last-resort option remains if none of those tools are available?

metrics: tools=5 · struct_tok=2891 · content_tok=2612 · total_tok=11082 · $0.0309 · 6.14s
fetched line ranges: `0061`, `0064`, `0060`

**Answer:**

If a country is not officially recognized as offering adequate data protection, a company can still lawfully transfer personal data to that country using the following mechanisms:

1. **Appropriate Safeguards**: As per Article 46, these include:
   - Legally binding agreements between public authorities.
   - Binding corporate rules (Article 47).
   - Standard data protection clauses adopted by the EU Commission or supervisory authorities.
   - Approved codes of conduct or certification mechanisms, accompanied by binding commitments to protect data.

2. **Derogations for Specific Situations**: As outlined in Article 49, transfers are permitted without adequacy or safeguards in situations like:
   - Explicit consent from the data subject after explaining associated risks.
   - Transfers necessary for contract performance or pre-contractual measures.
   - Public interest, legal claims, or vital interests.
   - Data sourced from public registers, if allowed under certain conditions.

### Last-Resort Option
The final option, if no adequacy decision, safeguards, or standard derogations apply, is transferring data for a controller's **compelling legitimate interests.** This requires:
   - Non-repetitive transfers concerning limited data subjects.
   - Circumstantial assessments ensuring suitable safeguards.
   - Notifying supervisory authorities and informing the data subjects about the transfer and legitimate interests pursued (Article 49, paragraph 1, second subparagraph).

Sections referenced:
- [Article 45: Transfers on the basis of an adequacy decision](#)
- [Article 46: Transfers subject to appropriate safeguards](#)
- [Article 49: Derogations for specific situations](#).

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GB6 — multi-hop-synthesis

**Q:** Someone who previously agreed to let a company use their data changes their mind and withdraws that agreement. What does the GDPR require about how withdrawal works, and can the person then demand their data be deleted — on what basis?

metrics: tools=4 · struct_tok=2891 · content_tok=960 · total_tok=9306 · $0.0255 · 7.35s
fetched line ranges: `0009`, `0023`

**Answer:**

Under the GDPR:

1. **Withdrawing Consent**: 
   - Article 7(3) states that a person has the right to withdraw their consent at any time. The withdrawal must not affect the lawfulness of data processing that occurred before the withdrawal.
   - It must be **as easy to withdraw consent as it is to give it**, and individuals must be informed of this right before granting consent.

2. **Demanding Data Erasure** ("Right to Be Forgotten"):
   - According to Article 17(1), a person can demand data erasure without undue delay when:
     - Their consent (the basis for processing) has been withdrawn (Article 17(1)(b)).
     - Other conditions such as unlawful processing or data no longer being necessary also apply.
   - However, exceptions exist where erasure is not possible, as outlined in Article 17(3), such as compliance with legal obligations, public interest purposes, or the exercise/defense of legal claims.

**Cited Articles**: 
- Article 7 (Conditions for consent) 
- Article 17 (Right to erasure).

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GC1 — cross-reference-resolution

**Q:** If a person objects to a company continuing to use their personal data, on what basis can they object, and when can the company refuse to stop despite the objection?

metrics: tools=4 · struct_tok=2891 · content_tok=1050 · total_tok=9446 · $0.0266 · 8.78s
fetched line ranges: `0028`, `0031`

**Answer:**

A person can object to a company processing their personal data based on the following grounds under the General Data Protection Regulation (GDPR):

1. **Grounds for Objection**:
   - **Personal Situation**: They can object, at any time, to data processing based on the company’s legitimate interests (Article 6(1)(f)) or a task carried out in public interest (Article 6(1)(e)) if it relates to their specific situation (Article 21(1)).
   - **Direct Marketing**: They can object at any time if the personal data is processed for direct marketing purposes, including profiling related to such marketing. In these cases, the company must stop processing the data (Article 21(2)–(3)).
   - **Research or Statistics**: They can also object to data processing for scientific, historical, or statistical purposes unless the processing is necessary for a task in the public interest (Article 21(6)).

2. **When the Company Can Refuse**:
   The company may continue processing despite the objection if:
   - It can demonstrate **compelling legitimate grounds** that override the interests, rights, and freedoms of the individual.
   - The processing is required for the **establishment, exercise, or defense of legal claims** (Article 21(1)).
   - The restriction is legally justified under Union or Member State law for reasons such as national security, public security, prevention of crime, or other significant public interest objectives (Article 23).

Cited sections: Articles 21 ("Right to object") and Article 23 ("Restrictions").

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GC2 — cross-reference-resolution

**Q:** Can a company make fully automated decisions about a person using sensitive data such as health information? If it is ever allowed, under what two conditions, and what safeguard must be in place?

metrics: tools=4 · struct_tok=2891 · content_tok=1309 · total_tok=13402 · $0.0353 · 5.76s
fetched line ranges: `0029`, `0011`

**Answer:**

A company may make fully automated decisions about a person using sensitive data, such as health information, only under strict conditions:

1. **Conditions:**
   - The decision must be based on **explicit consent** from the data subject, or
   - The decision must be **necessary for reasons of substantial public interest** and permitted by Union or Member State law, which includes safeguards for the data subject.

2. **Safeguard:**
   - Suitable measures must be implemented to protect the rights, freedoms, and legitimate interests of the data subject. This includes ensuring the right to obtain human intervention, to express their viewpoint, and to contest the decision (per **Article 22** of the GDPR).

Additional limitations apply when using sensitive data; such processing is generally prohibited unless explicitly exempted, as outlined in **Article 9** (Processing of special categories of personal data).

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GC3 — cross-reference-resolution

**Q:** A multinational wants to move personal data between its own entities in different countries using 'binding corporate rules.' What conditions must those binding corporate rules satisfy to be valid?

metrics: tools=3 · struct_tok=2891 · content_tok=1104 · total_tok=9459 · $0.0265 · 13.16s
fetched line ranges: `0062`

**Answer:**

Under Article 47 of the GDPR, binding corporate rules (BCRs) must meet the following conditions to be valid:

1. **Legally Binding Nature**: BCRs must be legally binding, enforceable by all entities in the group, including their employees, and must confer enforceable rights to data subjects.
   
2. **Approval Process**: The BCRs need to be approved by a competent supervisory authority through the consistency mechanism in Article 63.

3. **Detailed Specifications**: They must include:
   - The group's structure and contact information.
   - Details of the transfers, such as categories of personal data, types of processing, purposes, affected data subjects, and the involved third countries.
   - Application of general data protection principles, including purpose limitation, data minimization, and security measures.
   - Rights of data subjects, including complaints, lodging claims, and obtaining compensation.
   - The controller's or processor's acceptance of liability for breaches of the BCRs performed outside the EU.

4. **Operational Mechanisms**:
   - Information on BCRs to be communicated to data subjects.
   - Appointment of a data protection officer or an equivalent entity to monitor compliance.
   - Internal compliance mechanisms like audits and corrective actions.
   - Procedures for complaints and their resolution.
   - Reporting and updating mechanisms for supervisory authorities.
   - Mechanisms for handling external legal impacts on the rules, and training programs for their personnel handling personal data.

5. **Additional Provisions**: The European Commission may establish formats and procedures for the exchange of information related to BCRs among controllers, processors, and supervisory authorities.

(Source: Article 47 — Binding corporate rules)

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GC4 — cross-reference-resolution

**Q:** The right to have your data erased does not apply when the data is needed for certain public-health purposes. What kinds of health-related processing fall under that exception?

metrics: tools=4 · struct_tok=2891 · content_tok=1174 · total_tok=9503 · $0.0263 · 10.12s
fetched line ranges: `0113`, `0023`

**Answer:**

The exception to the right to have data erased for public health-related purposes is outlined in Article 17(3) of the GDPR. It specifies that the right of erasure does not apply when the processing is necessary for reasons of public interest in the field of public health, as permitted under:

- **Article 9(2)(h)**: For purposes such as preventive or occupational medicine, assessing workers' capability to work, medical diagnoses, or management of health or social care systems.
- **Article 9(2)(i)**: For protecting against serious cross-border health threats or ensuring high standards of quality and safety in healthcare (e.g., medicines or devices).
- **Article 9(3)**: Provided that the processing is conducted by a professional obligated to maintain secrecy under Union or Member State laws.

These activities are further safeguarded by technical and organizational measures, as mentioned in **Article 89**, such as pseudonymization to respect the principle of data minimization. The safeguards aim to balance public health goals while protecting individual rights. 

Referenced texts: "Article 17 — Right to erasure (‘right to be forgotten’)" and "Article 89 — Safeguards and derogations relating to processing for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes."

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GC5 — cross-reference-resolution

**Q:** If a company ignores a formal order from the data protection regulator, which level of fine does it face, and name three of the corrective powers the regulator can use.

metrics: tools=4 · struct_tok=2891 · content_tok=2399 · total_tok=10608 · $0.0281 · 6.54s
fetched line ranges: `0076`, `0106`

**Answer:**

If a company ignores a formal order from the data protection regulator (supervisory authority), it could face an administrative fine of up to €20,000,000 or, in the case of an undertaking, up to 4% of its total worldwide annual turnover for the preceding financial year, whichever is higher ("Article 83 — General conditions for imposing administrative fines").

Three corrective powers that the regulator can use include:
1. Imposing a temporary or definitive limitation, including a complete ban on processing.
2. Ordering the rectification or erasure of personal data or restriction of processing.
3. Imposing an administrative fine, depending on the circumstances of the case ("Article 58 — Powers").

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GD1 — scattered-enumeration

**Q:** What rights does the GDPR give individuals over their own personal data? List them.

metrics: tools=6 · struct_tok=2891 · content_tok=3613 · total_tok=12044 · $0.0335 · 6.95s
fetched line ranges: `0016`, `0020`, `0028,0029`, `0022,0023,0024,0026`

**Answer:**

The GDPR grants individuals the following rights over their personal data:

1. **Right to Access**: Individuals can request confirmation about whether their data is being processed and access such data, including information about processing purposes, categories of data, recipients, and more (Article 15).

2. **Right to Rectification**: Individuals can request inaccuracies in their personal data to be corrected and incomplete data to be completed (Article 16).

3. **Right to Erasure (‘Right to be Forgotten’)**: Individuals can request deletion of their personal data under certain conditions, such as when data is no longer needed or unlawfully processed (Article 17).

4. **Right to Restriction of Processing**: Individuals can request a restriction of data processing under specific circumstances, such as disputing the accuracy of the data (Article 18).

5. **Right to Data Portability**: Individuals can receive their data in a structured, commonly used, machine-readable format and transfer it to another controller (Article 20).

6. **Right to Object**:
   - Objection to processing based on public interest or legitimate interests.
   - Specifically, objection to processing for direct marketing purposes (Article 21).

7. **Right to Avoid Automated Decision-Making**: Individuals have the right not to be subjected to decisions based solely on automated processing, including profiling, unless certain safeguards are in place (Article 22).

These rights are supported by transparency and accessibility requirements laid out in Article 12.

Cited sections: Articles 12, 15, 16, 17, 18, 20, 21, 22.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GD2 — scattered-enumeration

**Q:** What documentation and record-keeping must a company maintain to show it complies with the GDPR — from the overarching duty to demonstrate compliance down to specific records of processing activities and of breaches?

metrics: tools=5 · struct_tok=2891 · content_tok=1365 · total_tok=9958 · $0.0291 · 9.02s
fetched line ranges: `0004`, `0040`, `0044`

**Answer:**

To comply with the GDPR, companies must maintain documentation and records to demonstrate compliance. The GDPR outlines specific documentation requirements, spanning from an overarching obligation to demonstrate compliance to maintaining detailed records of processing activities and breach logs. These include:

1. **General Obligation to Document Compliance Activities**:
   - Controllers must demonstrate compliance with GDPR requirements (Article 24).

2. **Records of Processing Activities**:
   Under Article 30, both controllers and processors are required to maintain detailed records of their processing activities. Key contents include:
   - For controllers:
     - Names and contact details of key parties (controller, joint controllers, representative, data protection officer).
     - Purposes of processing.
     - Categories of data subjects and personal data.
     - Categories of data recipients, including any third-country recipients.
     - Where applicable, records of data transfers, safeguards implemented, time limits for data erasure, and descriptions of security measures (e.g., encryption).
   - For processors:
     - Names and contact details of processors, their controllers, and (where applicable) their representatives and data protection officers.
     - Categories of processing conducted.
     - Records of cross-border transfers and documentation of safeguards.
     - General descriptions of applicable security measures.
   - These records must be available in writing (electronic form is acceptable) and made available to supervisory authorities upon request.
   - Exceptions exist for smaller organizations (<250 employees) unless processing poses risks, involves special categories of data (e.g., sensitive data), or is not occasional.

3. **Breach Notification and Documentation**:
   - Article 33 mandates that in the event of a data breach, controllers must notify the supervisory authority without undue delay, within 72 hours if feasible. This includes:
     - Describing the breach’s nature, affected data records, and categories of individuals affected.
     - Details of mitigation measures and possible consequences.
     - Contact details of a data protection officer or equivalent authority.
   - Importantly, companies must **document all breaches** (even those not reported to a supervisory authority), including facts, effects, and remedial actions taken, to allow supervisory authorities to verify compliance.

These requirements cover overarching duties to demonstrate compliance and specific obligations to document and retain detailed records of processing activities and breaches. Cited sections: *Articles 24, 30, 33*.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GD3 — scattered-enumeration

**Q:** If someone believes their data protection rights have been violated, what avenues of complaint and legal action can they pursue, and can they obtain compensation?

metrics: tools=6 · struct_tok=2891 · content_tok=1203 · total_tok=9737 · $0.0282 · 6.63s
fetched line ranges: `0101`, `0102`, `0100`, `0105`

**Answer:**

If someone believes their data protection rights under the GDPR have been violated, several avenues of complaint and legal action are available. Additionally, they may obtain compensation. Here are the details:

1. **Lodge a Complaint with a Supervisory Authority**:
   - Every data subject has the right to file a complaint with a supervisory authority, particularly in the Member State of their habitual residence, workplace, or where the alleged infringement occurred ([Article 77](#), *Right to lodge a complaint with a supervisory authority*).
   - The supervisory authority is obligated to inform the complainant about the progress and outcome of their complaint and the possibility of a judicial remedy.

2. **Judicial Remedy against a Supervisory Authority**:
   - If a supervisory authority fails to handle a complaint or does not inform the data subject of its progress or outcome within three months, the data subject has a right to seek an effective judicial remedy against the supervisory authority ([Article 78](#), *Right to an effective judicial remedy against a supervisory authority*).

3. **Judicial Remedy against a Controller or Processor**:
   - If the data subject believes their rights have been infringed as a result of non-compliant data processing, they can bring proceedings against the controller or processor. Such proceedings can be initiated in the courts of the Member State where the controller/processor is established or where the data subject resides ([Article 79](#), *Right to an effective judicial remedy against a controller or processor*).

4. **Compensation for Damages**: 
   - Any person who suffers material or non-material damage due to a violation of the GDPR has the right to claim compensation from the responsible controller or processor ([Article 82](#), *Right to compensation and liability*).
   - Controllers or processors may be held liable for the entire damage to ensure effective compensation. However, they can seek recovery from other involved parties proportionate to their responsibility.

These articles outline clear mechanisms for resolving grievances and obtaining redress under the GDPR framework.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GD4 — scattered-enumeration

**Q:** The GDPR encourages voluntary codes of conduct and certification schemes. What are these mechanisms, and who checks that organisations actually comply with each of them?

metrics: tools=4 · struct_tok=2891 · content_tok=3431 · total_tok=11786 · $0.0323 · 5.84s
fetched line ranges: `0054,0055`, `0056,0057`

**Answer:**

The GDPR encourages voluntary mechanisms like **codes of conduct** and **certification schemes** to support compliance with data protection principles.

### **Codes of Conduct**
- **Mechanism**: Associations of controllers or processors can create or amend codes of conduct specifying the application of GDPR provisions in areas such as fair processing, pseudonymization, data breach management, and cross-border data transfer (Article 40(2)). 
- **Monitoring**: Compliance is monitored by independent bodies accredited by competent supervisory authorities. These bodies must:
  1. Demonstrate expertise and independence.
  2. Establish procedures to assess eligibility and monitor compliance.
  3. Transparently handle complaints about code violations.
  (Article 41)

### **Certification**
- **Mechanism**: Voluntary **data protection certification mechanisms** serve to demonstrate compliance with GDPR. They may issue data protection seals or marks and are valid for a maximum of three years (Article 42(1), 42(7)).
- **Monitoring**: Certifications are issued, renewed, and withdrawn by either:
  1. Competent supervisory authorities, or
  2. Accredited certification bodies demonstrating independence, expertise, and compliance with legal requirements. 
  National accreditation bodies or supervisory authorities provide the accreditation (Article 43).

Both mechanisms emphasize transparency, and supervisory authorities retain oversight to enforce GDPR obligations. 

(Cited: Articles 40-43, "Codes of Conduct" and "Certification.")

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GD5 — scattered-enumeration

**Q:** When a company collects someone's personal data, what must it tell that person, and how do those obligations differ depending on whether the data was collected directly from the person or obtained from somewhere else?

metrics: tools=4 · struct_tok=2891 · content_tok=1918 · total_tok=10532 · $0.0308 · 10.38s
fetched line ranges: `0018`, `0019`

**Answer:**

When a company collects personal data, the obligations to inform the individual differ depending on whether the data was collected directly from the individual or obtained from another source. The relevant rules are specified in Articles 13 and 14 of the GDPR.

### 1. **When Data Are Collected Directly (Article 13)**:
At the time of collection, the controller must provide the individual with the following:
- **Identity and contact details** of the controller and, if applicable, their representative.
- Contact details of the **data protection officer**, if applicable.
- **Purpose and legal basis** for processing.
- If processing is based on "legitimate interests," these interests must be stated.
- **Recipients or categories of recipients**, if any.
- If applicable, information regarding data transfers to third countries or international organizations, along with any adequacy decisions or safeguards.

Additionally, the data subject must be informed about:
- The period for storing the data or the criteria used to determine it.
- Their rights (e.g., access, rectification, erasure, restriction of processing, objection, and data portability).
- The right to withdraw consent at any time.
- The **right to lodge a complaint** with a supervisory authority.
- Whether providing the data is mandatory or voluntary and the consequences of refusing.
- The use of automated decision-making, including profiling, and its significance for them.

### 2. **When Data Are Obtained From Another Source (Article 14)**:
In addition to most of the above requirements (identity, contact details, purpose, legal basis, recipients, transfer information, and rights), the company must also specify:
- The **categories** of the personal data processed.
- The **source** of the data, and whether it originates from publicly accessible sources.

The information must be provided:
- Within **one month** of obtaining the data.
- At the latest, with first communication to the individual if the data are used to communicate with them.
- Before any disclosure to another recipient.

### Key Differences:
- **Direct Source (Article 13):** Information must be provided "at the time" the data are obtained.
- **From Another Source (Article 14):** Extra details (like data source) must be disclosed, and timing varies (up to one month or first communication).

### Exceptions:
For both cases, the requirements may not apply if:
1. The individual already has the information.
2. Providing the information is impossible, requires disproportionate effort, or conflicts with legal confidentiality obligations. 

_Cited Articles: Article 13 and Article 14._

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GE1 — boundary-absence

**Q:** Does the GDPR apply to a private individual who keeps a personal address book or uses social media purely for personal reasons? Where does its scope stop?

metrics: tools=3 · struct_tok=2891 · content_tok=354 · total_tok=8474 · $0.0224 · 6.03s
fetched line ranges: `0003`

**Answer:**

Under **Article 2 — Material scope** of the GDPR:

- The GDPR **does not apply** when personal data is processed:
  - **By a natural person in the course of a purely personal or household activity**.
  - Examples might include a private individual keeping a personal address book or using social media for personal purposes.

The GDPR applies to personal data processed wholly or partly by automated means or which form part of a filing system unless it falls into the exceptions listed, where purely personal or household activities are explicitly excluded.

Refer to **Article 2 — Material scope** for details.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GE2 — boundary-absence

**Q:** Does the GDPR protect the personal data of people who have died, and can individual countries set their own rules on this?

metrics: tools=4 · struct_tok=2891 · content_tok=395 · total_tok=8535 · $0.0227 · 8.77s
fetched line ranges: `0119`, `0003`

**Answer:**

The General Data Protection Regulation (GDPR) does not protect the personal data of deceased individuals. The GDPR concerns the processing of personal data of living individuals only.

Additionally, Article 2 of the GDPR does not specifically regulate the data of deceased individuals, which means that EU Member States are allowed to establish their own rules regarding the protection of such data. Hence, the regulation leaves it to national laws to determine whether and how the personal data of deceased persons is safeguarded. For context, see **Article 2 — Material Scope**.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GE3 — boundary-absence

**Q:** Does the GDPR set a fixed maximum length of time — a specific number of days or years — that personal data may be kept? If not, what does it require instead?

metrics: tools=3 · struct_tok=2891 · content_tok=568 · total_tok=8722 · $0.0231 · 6.2s
fetched line ranges: `0007`

**Answer:**

The GDPR does not establish a fixed maximum length of time for retaining personal data (e.g., a specific number of days or years). Instead, Article 5(1)(e) requires that personal data be kept "no longer than is necessary for the purposes" for which the data is processed. Data may, however, be stored for longer periods if it is processed solely for archiving in the public interest, scientific or historical research, or statistical purposes, provided appropriate safeguards are in place to protect the rights and freedoms of individuals.

This principle is known as “storage limitation.” [Article 5 — Principles relating to processing of personal data].

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GE4 — boundary-absence

**Q:** Does the GDPR apply to anonymous information that cannot be traced to a specific person, including when it is used for statistics or research?

metrics: tools=4 · struct_tok=2891 · content_tok=566 · total_tok=12580 · $0.033 · 5.84s
fetched line ranges: `0003`, `0013`

**Answer:**

The GDPR does not apply to anonymous information that cannot be traced to a specific individual. According to **Article 2 (Material Scope)**, the regulation applies to the processing of "personal data"—information relating to identified or identifiable natural persons. Additionally, **Article 11 (Processing which does not require identification)** clarifies that data controllers are not obligated to maintain, acquire, or process additional information to identify individuals if the purposes of processing do not require identification. 

Thus, fully anonymous data, such as data used for statistics or research where individuals are not identifiable, falls outside the scope of the GDPR. 

Referenced sections:
- “Article 2 — Material scope”
- “Article 11 — Processing which does not require identification”

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GA1 — single-hop-lookup

**Q:** If a company breaks the data protection rules, how large a fine can it face at most, and what sorts of violations carry the steepest penalties?

metrics: tools=3 · struct_tok=15272 · content_tok=1275 · total_tok=34303 · $0.0874 · 5.74s
fetched line ranges: `1772,1822`

**Answer:**

A company that violates data protection rules under the GDPR can face fines of up to:

- **€20,000,000**, or
- **4% of its total worldwide annual turnover** (whichever is higher),

for serious breaches, such as:
  - Violating basic principles for data processing (Articles 5–9).
  - Breaching data subject rights (Articles 12–22).
  - Failing to meet requirements for cross-border data transfers (Articles 44–49).
  - Non-compliance with supervisory authority orders (Article 58).

Less severe violations, such as failure to implement appropriate technical and organizational measures (Articles 25–39), may incur fines of up to **€10,000,000** or **2% of global annual turnover**.

(Source: [Article 83 — General conditions for imposing administrative fines](1772))

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GA2 — single-hop-lookup

**Q:** If a company suffers a personal data breach, how quickly must it tell the regulator, and what does it have to include if it reports later than that?

metrics: tools=3 · struct_tok=15272 · content_tok=711 · total_tok=33754 · $0.0861 · 6.4s
fetched line ranges: `962,978`

**Answer:**

If a company suffers a personal data breach, it must notify the supervisory authority without undue delay and, where feasible, within 72 hours after becoming aware of it. If this deadline is missed, the notification must include reasons for the delay (Article 33). 

The notification must provide the following:
1. A description of the nature of the breach, including the categories and approximate number of affected data subjects and records.
2. Contact information for the data protection officer or another inquiry point.
3. Possible consequences of the breach.
4. Measures taken or planned to mitigate adverse effects (Article 33(3)).

If all the required information cannot be included initially, it may be submitted in phases, provided there is no undue further delay. The company also has to document the breach, including details about its effects and the actions taken, to demonstrate compliance (Article 33(4)-(5)). 

These provisions ensure transparency and accountability in handling data breaches.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GA3 — single-hop-lookup

**Q:** What counts as 'personal data' under the GDPR, and what makes a person 'identifiable'?

metrics: tools=3 · struct_tok=15272 · content_tok=1696 · total_tok=34648 · $0.088 · 5.9s
fetched line ranges: `405`

**Answer:**

Under the General Data Protection Regulation (GDPR), **personal data** is defined as "any information relating to an identified or identifiable natural person (‘data subject’)." A person is considered "identifiable" if they can be identified, either directly or indirectly, "in particular by reference to an identifier such as a name, an identification number, location data, an online identifier, or one or more factors specific to their physical, physiological, genetic, mental, economic, cultural, or social identity" (*Article 4 — Definitions*).

This broad definition includes not only traditional identifiers like names and ID numbers but also factors such as IP addresses, location data, or biometric and genetic information, as well as information revealing a person’s social identity.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GA4 — single-hop-lookup

**Q:** How old does a child have to be to agree on their own to an online service, and how much are individual countries allowed to lower that age?

metrics: tools=3 · struct_tok=15272 · content_tok=220 · total_tok=33221 · $0.0845 · 14.97s
fetched line ranges: `537`

**Answer:**

Under **Article 8** of the GDPR, a child must be at least **16 years old** to lawfully consent to the processing of personal data for online services (referred to as "information society services"). If the child is below 16, consent must be provided or authorized by a **parent or guardian**. 

However, Member States are allowed to lower the minimum age for this purpose, but it cannot be set below **13 years old**. Controllers are also required to make reasonable efforts to verify that parental consent is valid using available technology. 

This provision does not override general contract law in Member States (e.g., rules about the validity of contracts involving children). 

(Source: **Article 8 — Conditions applicable to child's consent in relation to information society services**)

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GB1 — multi-hop-synthesis

**Q:** When is a company required to carry out a data protection impact assessment, and what must it do if that assessment shows a high risk it cannot reduce?

metrics: tools=4 · struct_tok=15272 · content_tok=1316 · total_tok=34401 · $0.088 · 5.96s
fetched line ranges: `1022`, `994`

**Answer:**

A company is required to carry out a Data Protection Impact Assessment (DPIA) when a type of processing, particularly involving new technologies, is likely to result in a high risk to individuals' rights and freedoms. This includes scenarios such as automated decision-making, large-scale processing of sensitive data, or systematic large-scale monitoring of publicly accessible areas (as per **Article 35**).

If the DPIA indicates high risks that cannot be mitigated, the company must consult the supervisory authority before commencing processing. The supervisory authority evaluates the risks and may provide guidance, advice, or directives. If the processing is deemed to infringe the regulation or inadequately addresses risks, the supervisory authority may disallow it, extend the review period for further assessment, or apply corrective measures under its powers (as per **Article 36**). 

Cited Articles:
- **Article 35 — Data Protection Impact Assessment**
- **Article 36 — Prior Consultation**

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GB2 — multi-hop-synthesis

**Q:** Health data and similar sensitive information get special treatment. How does the GDPR's default stance on processing sensitive data differ from its default stance on ordinary personal data, and give two grounds that allow sensitive data to be processed anyway.

metrics: tools=3 · struct_tok=15272 · content_tok=824 · total_tok=33956 · $0.0869 · 8.11s
fetched line ranges: `544`

**Answer:**

The General Data Protection Regulation (GDPR) distinguishes between the processing of ordinary personal data and sensitive personal data (special categories). By default:

- **Ordinary personal data:** The GDPR permits the processing of personal data if it meets one of the lawful bases outlined in Article 6, such as consent, performance of a contract, compliance with legal obligations, or legitimate interests.

- **Sensitive personal data:** The processing of sensitive data (e.g., health, biometric, racial, or religious information) is **prohibited by default**, as stated in Article 9(1), unless specific exceptions apply.

### Grounds allowing processing of sensitive data:
1. **Explicit Consent:** The data subject has given explicit consent for specified purposes, except where the law prevents this exception (Article 9(2)(a)).
   
2. **Legal or Public Interest Necessity:** Processing is necessary for the establishment, exercise, or defense of legal claims, or for reasons of substantial public interest based on Union or Member State law (Article 9(2)(f), (g)).

Refer to **Article 9 — Processing of special categories of personal data** for details.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GB3 — multi-hop-synthesis

**Q:** After a data breach, how do the rules for notifying the regulator differ from the rules for notifying the affected individuals — in when each is required, how fast, and when you don't have to tell the individuals at all?

metrics: tools=4 · struct_tok=15272 · content_tok=712 · total_tok=34087 · $0.089 · 7.61s
fetched line ranges: `962`, `978`

**Answer:**

The rules for notifying the regulator (supervisory authority) differ from those for notifying affected individuals in cases of a personal data breach in the following ways:

### **1. When notification is required:**
   - **Regulator Notification:** The controller must notify the supervisory authority if the breach affects natural persons' rights and freedoms, unless the breach is unlikely to pose such a risk (Article 33.1).
   - **Individual Notification:** Individuals must be informed only when the breach is likely to result in a high risk to their rights and freedoms (Article 34.1). 

### **2. Timing of notification:**
   - **Regulator Notification:** Notification must occur without undue delay, and where feasible, within 72 hours of awareness of the breach. If delayed, reasons must be provided (Article 33.1).
   - **Individual Notification:** Notification to affected individuals must also be without undue delay but does not have a specific timeframe like the 72-hour rule for regulators (Article 34.1).

### **3. Conditions under which individual notification is unnecessary:**
Notification to individuals is not required if:
   - **Protective measures** (e.g., encryption) render the data unintelligible to unauthorized persons, mitigating the risk (Article 34.3(a)).
   - **Mitigatory actions** ensure the high risk is no longer likely to materialize (Article 34.3(b)).
   - Communication would involve **disproportionate effort**, in which case public communication or a similar equally effective measure can be used (Article 34.3(c)).

### Supervisory Role:
Even if the organization does not notify individuals, the supervisory authority may require such a notification if it determines a high risk exists or concludes that none of the exceptions in Article 34.3 apply (Article 34.4).

### Conclusion:
While both notifications aim to ensure transparency and safety, the regulator is notified in a broader range of scenarios, with stricter timing requirements. Conversely, notifying individuals is necessary only when the breach poses a high risk, with specific mitigating conditions allowing exceptions.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GB4 — multi-hop-synthesis

**Q:** When is a company required to appoint a Data Protection Officer, and what job protections and reporting line does that officer have?

metrics: tools=4 · struct_tok=15272 · content_tok=674 · total_tok=33762 · $0.0866 · 6.57s
fetched line ranges: `1061`, `1045`

**Answer:**

A company is required to appoint a Data Protection Officer (DPO) under the following circumstances (Article 37):  
1. When the processing is conducted by a public authority or body (except courts in a judicial capacity).  
2. When the organization's core activities involve regular and systematic large-scale monitoring of data subjects.  
3. When the organization's core activities include processing large-scale special categories of data (e.g., health, biometric data) or personal data related to criminal convictions and offenses.

Regarding job protections and the reporting line of the DPO (Article 38):  
- **Protections:** The DPO must not receive instructions on their tasks and cannot be dismissed or penalized for performing their duties. They are also bound by confidentiality in performing their duties.  
- **Reporting Line:** The DPO must directly report to the highest management level of the organization.  
- **Additional Tasks:** The DPO can perform other roles provided those do not create a conflict of interest.  

These provisions ensure the DPO operates independently and effectively in overseeing data protection compliance.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GB5 — multi-hop-synthesis

**Q:** If a country has not been officially recognised as offering adequate data protection, how can a company still lawfully send personal data there, and what last-resort option remains if none of those tools are available?

metrics: tools=5 · struct_tok=15272 · content_tok=2564 · total_tok=35779 · $0.0918 · 9.48s
fetched line ranges: `1204-1208`, `1272-1296`, `1181-1185`

**Answer:**

When a country is not recognized as ensuring adequate data protection, personal data can still be transferred there if appropriate safeguards are provided. These include:

1. **Legally Binding Agreements**: Between public authorities (Article 46).
2. **Binding Corporate Rules (BCRs)**: For intra-group data transfers (Article 47).
3. **Standard Data Protection Clauses**: Adopted by the EU Commission or supervisory authorities (Article 46).
4. **Approved Codes of Conduct or Certifications**: Binding the third-country recipient to specific safeguards for data protection (Article 46).

As a last resort, if none of these tools are applicable, data transfers may occur under specific derogations outlined in **Article 49**. These include cases where:
- The data subject has explicitly consented after being informed of risks.
- The transfer is necessary for contract performance, legal claims, or vital interests.
- It involves compelling legitimate interests, provided appropriate safeguards and notifications to supervisory authorities are in place.

These provisions are grounded in **Articles 44–50** of the GDPR.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GB6 — multi-hop-synthesis

**Q:** Someone who previously agreed to let a company use their data changes their mind and withdraws that agreement. What does the GDPR require about how withdrawal works, and can the person then demand their data be deleted — on what basis?

metrics: tools=4 · struct_tok=15272 · content_tok=813 · total_tok=34055 · $0.0878 · 6.91s
fetched line ranges: `530`, `714`

**Answer:**

Under the GDPR:

1. **Right to Withdraw Consent**: As per **Article 7(3)**, an individual has the right to withdraw previously given consent to data processing at any time. This withdrawal must be as easy as giving consent, and the withdrawal does not affect the legality of any processing that took place before the consent was withdrawn. Controllers must inform individuals of their right to withdraw consent before they give it.

2. **Right to Erasure ("Right to be Forgotten")**: Under **Article 17(1)**, a data subject can request the deletion of their personal data from the data controller without undue delay if:
   - They withdraw their consent, and there are no other legal grounds for processing the data (**Article 17(1)(b)**).
   - The personal data are no longer necessary for the purposes for which they were collected.
   - The data has been unlawfully processed, or other specified grounds for erasure apply.

    However, exceptions to this right exist under **Article 17(3)**, such as where processing is necessary for:
   - Exercising the right of freedom of expression and information.
   - Compliance with legal obligations.
   - Public interest in health, historical, scientific, or statistical purposes.
   - Legal claims.

Thus, an individual can withdraw their consent and demand the deletion of their data under specific conditions. The controller must comply unless one of the exceptions applies.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GC1 — cross-reference-resolution

**Q:** If a person objects to a company continuing to use their personal data, on what basis can they object, and when can the company refuse to stop despite the objection?

metrics: tools=4 · struct_tok=15272 · content_tok=869 · total_tok=34144 · $0.0887 · 7.14s
fetched line ranges: `774`, `799`

**Answer:**

A person can object to the processing of their personal data under the following grounds:

1. **Personal Situation Related to Legal Grounds (Article 6(1)(e) or (f))**: Individuals may object to processing that is based on public interest tasks, the exercise of official authority (Article 6(1)(e)), or the controller's legitimate interests (Article 6(1)(f)), including profiling. The controller must cease processing unless they demonstrate compelling legitimate grounds that override the individual's interests or if processing is necessary to establish, exercise, or defend legal claims (Article 21(1)).

2. **Direct Marketing**: Individuals can object to processing for direct marketing purposes, including related profiling. If raised, the controller must stop processing for these purposes immediately (Article 21(2)–(3)).

3. **Research and Statistics**: Processing for scientific, historical research, or statistical purposes can be objected to if it relates to the individual’s particular situation, unless it is necessary to perform a public interest task (Article 21(6)).

### Company Reasons to Refuse an Objection:
A company (data controller) can refuse to halt processing in two circumstances:
- If there are **compelling legitimate grounds** that override the individual's rights, freedoms, or interests (e.g., critical organizational needs).
- If the processing is required for the **establishment, exercise, or defense of legal claims** (Article 21(1)).

Additionally, restrictions imposed by Union or Member State law may limit data subjects' rights, including objections, for reasons such as national security, public security, or other significant public interest objectives like public health or defense (Article 23). 

Thus, objections and refusals hinge on the balance between the individual's rights and overriding legal or public interest justifications.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GC2 — cross-reference-resolution

**Q:** Can a company make fully automated decisions about a person using sensitive data such as health information? If it is ever allowed, under what two conditions, and what safeguard must be in place?

metrics: tools=3 · struct_tok=15272 · content_tok=291 · total_tok=33351 · $0.0851 · 9.1s
fetched line ranges: `783`

**Answer:**

Under Article 22 of the GDPR, a company can make fully automated decisions about a person using sensitive data like health information only under specific conditions:

1. **Conditions:**  
   - The decision is either necessary for entering into or performing a contract between the data subject and the data controller.  
   - It is based on the data subject's **explicit consent**.

2. **Safeguard:**  
   - The data controller must ensure appropriate protections for the person's rights and freedoms, such as allowing for **human intervention**, enabling the data subject to express their point of view, and providing the ability to contest the decision.

Additionally, decisions involving sensitive data categories (e.g., health) must have further specific legal justifications under Article 9(2). This ensures robust safeguards are consistently applied to protect the data subject's rights and legitimate interests. 

**Source:** Article 22 — *Automated individual decision-making, including profiling*.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GC3 — cross-reference-resolution

**Q:** A multinational wants to move personal data between its own entities in different countries using 'binding corporate rules.' What conditions must those binding corporate rules satisfy to be valid?

metrics: tools=3 · struct_tok=15272 · content_tok=941 · total_tok=34220 · $0.0891 · 7.31s
fetched line ranges: `1228`

**Answer:**

For binding corporate rules (BCRs) to be valid under GDPR, they must satisfy the following conditions, as specified in **Article 47**:

1. **Approval by a Supervisory Authority**:
   - The competent supervisory authority must approve the BCRs through the consistency mechanism under **Article 63**.

2. **Legal Bindingness**:
   - The BCRs must be legally binding and enforceable across all members of the corporate group, including employees.

3. **Enforceable Data Subject Rights**:
   - They must confer enforceable rights to data subjects concerning the processing of their personal data.

4. **Specified Details**:
   BCRs must include:
   - Structure and contact details of the group and its members.
   - Scope of data transfers, including types of personal data, processing purposes, affected data subjects, and destination countries.
   - Their internal and external legally binding nature.
   - Adherence to data protection principles like purpose limitation, data minimization, data security, and legal bases for processing.
   - Data subjects’ rights, including the right to lodge complaints with supervisory authorities and courts, obtain redress, and receive compensation for breaches.
   - Mechanisms for compliance verification, audits, complaint handling, and reporting mechanisms.

5. **Liability**:
   - A controller or processor within the EU must accept liability for breaches by non-EU members of the group, unless it proves those members are not responsible for the damage.

6. **Supervisory Authority Cooperation**:
   - Mechanisms for cooperation with supervisory authorities must be established, including reporting results of compliance audits.

7. **Training and Compliance Monitoring**:
   - Appropriate training on data protection and mechanisms for monitoring compliance must be in place.

8. **Reporting Obligations**:
   - Provisions for reporting and recording changes to the BCRs and any requirements in third countries that may adversely affect data protection guarantees.

These provisions ensure that BCRs provide adequate safeguards for data protection during international data transfers within corporate groups ([Chapter V — Article 47, "Binding Corporate Rules"]).

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GC4 — cross-reference-resolution

**Q:** The right to have your data erased does not apply when the data is needed for certain public-health purposes. What kinds of health-related processing fall under that exception?

metrics: tools=3 · struct_tok=15272 · content_tok=562 · total_tok=33575 · $0.0855 · 5.79s
fetched line ranges: `714`

**Answer:**

The right to have personal data erased does not apply when the processing of the data is necessary for public interest in the area of public health. Specifically, this includes processing related to:

1. **Preventive or occupational medicine**, such as health assessments.
2. **Healthcare services**, including diagnosis, treatment, or management of healthcare systems.
3. **Public health measures**, aimed at ensuring high standards of health protection (e.g., combating epidemics).
4. Adherence to **professional secrecy** or confidentiality rules, as stipulated in Article 9(2)(h) and (i) and Article 9(3) of GDPR.

These exceptions ensure that necessary health-related processing continues to serve public welfare. (Referenced from *Article 17 — Right to erasure (‘right to be forgotten’)*).

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GC5 — cross-reference-resolution

**Q:** If a company ignores a formal order from the data protection regulator, which level of fine does it face, and name three of the corrective powers the regulator can use.

metrics: tools=3 · struct_tok=15272 · content_tok=9956 · total_tok=42993 · $0.1091 · 7.37s
fetched line ranges: `1431,1772`

**Answer:**

If a company ignores a formal order from the data protection regulator, it can face administrative fines of up to **20 million EUR** or **4% of the total worldwide annual turnover** of the preceding financial year, whichever is higher (Article 83). This penalty level can apply under **non-compliance with an order by the supervisory authority**, as outlined in Article 58(2).

Three corrective powers that the supervisory authority can use include:
1. Imposing a temporary or definitive limitation, including a ban on data processing.
2. Ordering the rectification, erasure, or restriction of processing of personal data.
3. Imposing administrative fines as outlined under Article 83 (Article 58 — Powers). 

Citations:
- **Article 58 — Powers** (Corrective Actions)
- **Article 83 — General conditions for imposing administrative fines**.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GD1 — scattered-enumeration

**Q:** What rights does the GDPR give individuals over their own personal data? List them.

metrics: tools=6 · struct_tok=15272 · content_tok=2419 · total_tok=35636 · $0.0921 · 7.48s
fetched line ranges: `710,714`, `742,760`, `684`, `774,783`

**Answer:**

The GDPR provides the following rights to individuals over their personal data:

1. **Right of Access** (Article 15): Individuals can access their personal data and learn details regarding its processing, including purposes, recipients, and storage duration.

2. **Right to Rectification** (Article 16): Individuals can request correction of inaccurate data or completion of incomplete data.

3. **Right to Erasure (‘Right to be Forgotten’)** (Article 17): Individuals can request deletion of their data under certain conditions, e.g., if it is no longer necessary or was unlawfully processed.

4. **Right to Restriction of Processing** (Article 18): Individuals can request restricted processing under specific circumstances, such as contesting the accuracy of the data.

5. **Right to Data Portability** (Article 20): Individuals can receive their data in a structured, machine-readable format and transfer it to another controller.

6. **Right to Object** (Article 21): Individuals can object to data processing for certain purposes, like direct marketing or processing based on certain legal grounds.

7. **Rights Related to Automated Decision-Making and Profiling** (Article 22): Individuals can demand not to be subjected to decisions based solely on automated processing if they significantly affect them, except under specific circumstances.

These rights underline transparency, user control, and accountability in data processing within the GDPR framework. [Sources: Articles 15-22, Chapter III, GDPR]

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GD2 — scattered-enumeration

**Q:** What documentation and record-keeping must a company maintain to show it complies with the GDPR — from the overarching duty to demonstrate compliance down to specific records of processing activities and of breaches?

metrics: tools=4 · struct_tok=15272 · content_tok=942 · total_tok=34194 · $0.0885 · 6.64s
fetched line ranges: `962`, `910`

**Answer:**

To comply with the GDPR, companies must maintain the following documentation and records:

### General Duty to Demonstrate Compliance
- Controllers must ensure compliance with all applicable GDPR principles, implementing appropriate technical and organizational measures (e.g., data protection policies, privacy impact assessments) and adhering to certification mechanisms to demonstrate compliance (Article 30).

### Specific Records of Processing Activities
- **Controllers' Records:** These should include details such as the name and contact information of the controller, purposes of processing, descriptions of data categories and recipients, transfers to third countries (if applicable), deletion timelines, and security measures in place (Article 30(1)).
- **Processors' Records:** These must include the name/contact details of processors and controllers, descriptions of processing activities, international transfers of data, and general descriptions of security measures (Article 30(2)).

### Accessibility and Reporting of Records
- All records must be in writing (including electronic format) and made available to the supervisory authority upon request (Article 30(4)).

### Documentation of Personal Data Breaches
- **Notification Obligations:** Controllers must report personal data breaches to the supervisory authority within 72 hours if it poses a risk to individuals' rights and freedoms. They must also provide details such as the breach nature, affected data subjects and records, consequences, and measures taken to mitigate harm (Article 33(1)-(4)).
- **Breach Records:** Controllers must document every breach, including the facts, effects, and remedial actions, so that regulatory compliance can be assessed by supervisory authorities (Article 33(5)).

These measures ensure transparency, accountability, and prompt responses to ensure GDPR compliance.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GD3 — scattered-enumeration

**Q:** If someone believes their data protection rights have been violated, what avenues of complaint and legal action can they pursue, and can they obtain compensation?

metrics: tools=6 · struct_tok=15272 · content_tok=883 · total_tok=34230 · $0.0892 · 8.41s
fetched line ranges: `1740`, `1735`, `1747`, `1763`

**Answer:**

Under the General Data Protection Regulation (GDPR), individuals who believe their data protection rights have been violated have the following avenues for complaint, legal action, and compensation:

1. **Right to Lodge a Complaint** *(Article 77)*:
   - Individuals can file a complaint with a supervisory authority in the Member State of their habitual residence, workplace, or where the alleged infringement occurred. The authority must inform the complainant of the progress and outcome, including any judicial remedy. 

2. **Judicial Remedy Against Supervisory Authorities** *(Article 78)*:
   - If a supervisory authority fails to act on a complaint or does not address it within three months, the individual has the right to seek judicial remedies in the courts of the Member State where the supervisory authority is established.

3. **Judicial Remedy Against Controllers or Processors** *(Article 79)*:
   - Individuals may take legal action against data controllers or processors who have infringed their rights under the regulation. These proceedings can be initiated in the Member State where the controller/processor operates or where the individual resides.

4. **Right to Compensation** *(Article 82)*:
   - Data subjects are entitled to compensation for material or non-material damages resulting from a GDPR infringement. Controllers are liable for damages caused by non-compliance, and processors are liable if they fail to fulfill obligations or act contrary to lawful instructions. Controllers/processors who pay full compensation can reclaim a proportionate amount from other responsible parties, if applicable.

These provisions ensure individuals have access to administrative, judicial, and compensatory mechanisms for resolving data protection violations. 

Sections referenced:
- *Article 77 (Complaint with Supervisory Authority)*, 
- *Article 78 (Judicial Remedy against Authority)*, 
- *Article 79 (Judicial Remedy against Controller/Processor)*,
- *Article 82 (Compensation and Liability)*.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GD4 — scattered-enumeration

**Q:** The GDPR encourages voluntary codes of conduct and certification schemes. What are these mechanisms, and who checks that organisations actually comply with each of them?

metrics: tools=4 · struct_tok=15272 · content_tok=2839 · total_tok=36094 · $0.0935 · 7.8s
fetched line ranges: `1088-1124`, `1141-1159`

**Answer:**

The GDPR establishes mechanisms such as codes of conduct and certification schemes to encourage voluntary compliance with data protection standards. Here's an explanation of these mechanisms and how compliance with each is monitored:

### **1. Codes of conduct**
- **Purpose**: These aim to guide specific sectors (e.g., industries or enterprises) on applying the GDPR, considering their unique processing needs (e.g., ensuring fair processing, pseudonymization, and protecting children).
- **Development & Approval**: Codes of conduct are drafted by sectoral associations or bodies and submitted to supervisory authorities for approval. They should include mandatory monitoring mechanisms.
- **Monitoring Compliance**: Independent accredited bodies with expertise monitor adherence to the codes. Supervisory authorities also retain oversight, especially for serious violations, and can revoke accreditations of monitoring bodies if required.

### **2. Certification mechanisms**
- **Purpose**: Certification seals and marks signify that controllers or processors comply with the GDPR. They may also facilitate data transfers to non-EU countries if appropriate safeguards are implemented.
- **Approval**: Certifications are issued by accredited certification bodies or supervisory authorities. Certification criteria must align with GDPR standards, and such certifications are valid for three years (renewable).
- **Monitoring Compliance**: Certification bodies are tasked with conducting assessments, handling complaints, and ensuring certifications adhere to GDPR standards, with supervisory authorities overseeing these bodies.

**Relevant Supervisory Authorities**: In both cases, supervisory authorities are responsible for ensuring adherence to codes and certifications, handling complaints, and withdrawing approvals or certifications if standards are violated.

Cited sections: [Article 40](#article-40), [Article 41](#article-41), [Article 42](#article-42), and [Article 43](#article-43).

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GD5 — scattered-enumeration

**Q:** When a company collects someone's personal data, what must it tell that person, and how do those obligations differ depending on whether the data was collected directly from the person or obtained from somewhere else?

metrics: tools=4 · struct_tok=15272 · content_tok=1629 · total_tok=35172 · $0.0931 · 12.46s
fetched line ranges: `605`, `636`

**Answer:**

When a company collects someone's personal data, its obligations to inform the person depend on whether the data is collected directly from the individual or obtained from another source:

### When Data Is Collected Directly from the Individual (Article 13):
1. **Requirements at the Time of Collection**:
   - The controller must provide clear and comprehensive information, including:
     - Identity and contact details of the controller and, if applicable, its representative and Data Protection Officer (DPO).
     - The purpose and legal basis of data processing, and any applicable legitimate interests (§1(a)-(d)).
     - Recipients of the data and whether the data will be transferred to a third country or international organization (§1(e)-(f)).
   - Additional details, such as:
     - How long the data will be stored or the criteria to determine storage period.
     - Data subjects’ rights including access, rectification, erasure, restriction of processing, and withdrawal of consent (§2(a)-(c)).
     - Rights to lodge complaints with supervisory authorities (§2(d)).
     - Whether providing the data is mandatory and the consequences of failure to provide it (§2(e)).
     - Details of automated decision-making or profiling, if involved (§2(f)).

2. **Future Use of Data**:
   - If the controller processes data for purposes different from the original intent, the individual must be informed before this additional processing (§3).

### When Data Is Obtained from Another Source (Article 14):
1. **Requirements Upon Obtaining Data**:
   - The controller must inform the data subject of the information required under Article 13, along with:
     - Categories of personal data collected.
     - The source of the data, and whether it came from publicly accessible sources (§1(d), §2(f)).
     
2. **Timing and Mode of Information**:
   - Information must be provided:
     - Within one month of obtaining the data.
     - At the time of first communication, if contacting the individual.
     - At the first disclosure to another recipient (§3).

3. **Exemptions**:
   - These obligations do not apply if:
     - The individual already has the information.
     - Providing the information is impossible or requires disproportionate effort (e.g., public interest, research, or statistical use).
     - A specific legal obligation exists that ensures equivalent protections for data.
     - Secrecy obligations, such as professional secrecy, apply (§5(a)-(d)).

### Key Differences:
- **Timing**: Direct collection requires companies to provide information upfront, while indirect collection allows up to one month.
- **Content**: Indirect collection necessitates details about the data source and category.
- **Exemptions**: Indirect collection has broader exemptions, such as infeasibility due to effort or legal constraints.

*[Cited from "Article 13 — Information to be provided where personal data are collected from the data subject" and "Article 14 — Information to be provided where personal data have not been obtained from the data subject."]*

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GE1 — boundary-absence

**Q:** Does the GDPR apply to a private individual who keeps a personal address book or uses social media purely for personal reasons? Where does its scope stop?

metrics: tools=3 · struct_tok=15272 · content_tok=306 · total_tok=33222 · $0.0839 · 5.11s
fetched line ranges: `380`

**Answer:**

The GDPR does not apply to the processing of personal data by a natural person in the course of a purely personal or household activity. This includes activities like keeping a personal address book or using social media strictly for personal reasons. However, the regulation applies when personal data processing is done for professional or commercial purposes.

For more on this topic, see **Article 2 — Material scope**.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GE2 — boundary-absence

**Q:** Does the GDPR protect the personal data of people who have died, and can individual countries set their own rules on this?

metrics: tools=5 · struct_tok=15272 · content_tok=683 · total_tok=49964 · $0.1266 · 6.14s
fetched line ranges: `1827`, `380`, `1827-1836`

**Answer:**

The GDPR does not explicitly protect the personal data of deceased individuals, as Article 2 (Material Scope) does not cover such data. However, under **Article 85** (Processing and freedom of expression and information), Member States are permitted to draft specific laws regarding data processing situations, which could include rules about the data of deceased individuals. The regulation allows Member States flexibility in addressing these specific situations by setting local rules per their requirements.

This means the protection of personal data for deceased persons, if any, would depend on the national laws of individual EU Member States. The document does not impose a uniform EU-wide protection for such cases.

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GE3 — boundary-absence

**Q:** Does the GDPR set a fixed maximum length of time — a specific number of days or years — that personal data may be kept? If not, what does it require instead?

metrics: tools=3 · struct_tok=15272 · content_tok=399 · total_tok=33436 · $0.0852 · 5.57s
fetched line ranges: `478`

**Answer:**

The GDPR does not set a fixed maximum length of time (e.g., a specific number of days or years) for which personal data may be retained. Instead, it establishes the principle of **"storage limitation"** under Article 5. Personal data must be kept in a form that allows identification of data subjects **"for no longer than is necessary"** for the purposes for which the data was processed. Exceptions to this include scenarios where data is processed solely for archiving in the public interest, scientific or historical research, or statistical purposes, provided appropriate safeguards are implemented.

The regulation emphasizes that the data controller is responsible for ensuring compliance with these principles and must be able to demonstrate such compliance. This ensures flexibility to determine retention periods based on the specific context while safeguarding data subjects' rights. 

(Source: Article 5 — Principles relating to processing of personal data)

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GE4 — boundary-absence

**Q:** Does the GDPR apply to anonymous information that cannot be traced to a specific person, including when it is used for statistics or research?

metrics: tools=3 · struct_tok=15272 · content_tok=403 · total_tok=33388 · $0.085 · 5.45s
fetched line ranges: `1850`

**Answer:**

Under the GDPR, the regulation explicitly applies to personal data rather than anonymous data. Article 89 specifies that when personal data is processed for archiving, scientific or historical research, or statistical purposes, it must include safeguards like pseudonymization and data minimization to protect the rights of data subjects. However, if the purposes can be fulfilled in a manner that no longer permits the identification of individuals, then the processing should be done in that way.

Anonymous data that cannot be used to identify a person—even when combined with other data—is not subject to the GDPR. Thus, such completely anonymous information used for statistics or research would not fall within its scope. 

This is consistent with GDPR's approach to restricting its application to identifiable personal data and excluding fully anonymized data from regulatory ambit.

---
