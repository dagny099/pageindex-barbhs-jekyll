# Retrieval run 20260715T002754Z

- Indexes: `IDX-PDF-vanilla-paper`, `IDX-D-paper-book-v1`, `IDX-D-paper-book-v1-clean`
- Retrievers: `gpt-4o-2024-11-20`
- Corpus: `paper-book-v1` (`5d712efb8471…`)
- Repo commit: `1cffdcafd2`  ·  questions: 8

## Comparison — means across questions

| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|---|
| `IDX-PDF-vanilla-paper` | `gpt-4o-2024-11-20` | 8 | 3.4 | 4515.0 | 3203.0 | 14892 | 0.3124 | 6.1 |
| `IDX-D-paper-book-v1` | `gpt-4o-2024-11-20` | 8 | 4.5 | 698.0 | 2709.9 | 13475 | 0.2796 | 5.4 |
| `IDX-D-paper-book-v1-clean` | `gpt-4o-2024-11-20` | 8 | 4.6 | 686.0 | 1127.9 | 5525 | 0.1202 | 5.3 |

## Per-question detail (question, expected evidence, ground truth, answer)
*Everything needed to score each answer is inline below — no cross-referencing.*

### [IDX-PDF-vanilla-paper | gpt-4o-2024-11-20] PDL1 — direct-location

**Q:** How many observers and how many scenes were used in the main eye-tracking search experiment, and what was the search target?

**Expected evidence:** Abstract L46; Introduction L77; Participants L83 ('Fourteen observers'); Stimuli L93 ('912 colour pictures').

**Ground truth:** 14 observers searched 912 outdoor urban scenes (half target-present, half target-absent) for a person/pedestrian.

metrics: tools=3 · struct_tok=4515 · content_tok=1680 · total_tok=13249 · $0.0341 · 6.11s
fetched line ranges: `0004,0005,0007`

**Answer:**

The main eye-tracking search experiment involved 14 observers and utilized 912 scenes of urban environments, with half of the images containing a pedestrian. The search target for the experiment was a person (pedestrian), typically located in the periphery of the images. Each participant completed all 912 trials. 

This information is based on details from the following sections:
- **Experimental Method**
- **Participants**
- **Stimuli**.

---

### [IDX-PDF-vanilla-paper | gpt-4o-2024-11-20] PMP1 — methods-procedural

**Q:** In the Dalal-Triggs target-features detector, what scanning-window size was used and how many pedestrians was the reported implementation trained on?

**Expected evidence:** Guidance by target features, L159 ('scanning window of 32×64 pixels and was trained on 2000 upright, unoccluded pedestrians').

**Ground truth:** A 32x64-pixel scanning window; trained on 2000 upright, unoccluded pedestrians (plus their left-right reflections).

metrics: tools=3 · struct_tok=4515 · content_tok=3164 · total_tok=14738 · $0.0378 · 7.75s
fetched line ranges: `0014,0015`

**Answer:**

In the Dalal-Triggs target-features detector, the scanning window size was set to **32 × 64 pixels**, and it was trained on **2000 upright, unoccluded pedestrians**, along with their left-right reflections. Pedestrians were cropped from images in the LabelMe database and adjusted to fit specific criteria for training. 

Cited section: "Guidance by target features" under "MODELLING METHODS".

---

### [IDX-PDF-vanilla-paper | gpt-4o-2024-11-20] PFT1 — figure-or-table-evidence

**Q:** According to Table 1, what is the scene-context model's Area-Under-Curve (AUC) in target-absent scenes, and how does it compare with the saliency model in the same condition?

**Expected evidence:** Table 1, target-absent block, L217 (Scene context .845) and L215 (Saliency .773).

**Ground truth:** Scene context AUC = .845 vs saliency AUC = .773 in target-absent scenes; scene context is higher by .072.

metrics: tools=3 · struct_tok=4515 · content_tok=1042 · total_tok=12699 · $0.0329 · 4.56s
fetched line ranges: `0018`

**Answer:**

According to Table 1:

- The **scene-context model** achieves an **Area-Under-Curve (AUC)** of **0.845** in **target-absent scenes**.
- In the same condition, the **saliency model** has an AUC of **0.773**.

Thus, the scene-context model outperforms the saliency model by **0.072 points** in AUC, demonstrating better accuracy in predicting fixation regions for target-absent scenes.

(Referenced Section: "MODELLING RESULTS")

---

### [IDX-PDF-vanilla-paper | gpt-4o-2024-11-20] PFT3 — figure-or-table-evidence

**Q:** What does Figure 8 compare, and how are the two panels defined?

**Expected evidence:** Figure 8 caption, L205 ('Comparison between (a) the computationally defined scene context map and (b) the empirically defined context oracle map for a single image').

**Ground truth:** Figure 8 compares, for a single image, (a) the computationally-defined scene-context map vs (b) the empirically-defined context-oracle map (both thresholded at 20% of image area, with human-fixation dots).

metrics: tools=3 · struct_tok=4515 · content_tok=2363 · total_tok=13949 · $0.0363 · 4.87s
fetched line ranges: `0018,0020`

**Answer:**

Figure 8 compares two maps that predict human fixation locations during visual search:

1. **Panel (a): Computationally Defined Scene Context Map** - A computational model predicting the locations where observers are likely to fixate, based on scene context.
   
2. **Panel (b): Empirically Defined Context Oracle Map** - A data-driven "oracle" map developed using human-labeled plausible pedestrian locations, designed to capture empirically-based predictions.

Both maps are shown thresholded at 20% of the image area, with dots representing human fixations. The comparison demonstrates differences between computational predictions and empirically guided context understanding regarding their ability to predict human behavior. 

Cited Sections:
- "MODELLING RESULTS"
- "Context models"

---

### [IDX-PDF-vanilla-paper | gpt-4o-2024-11-20] PEG2 — evidence-gap

**Q:** Does the paper report human behavioural performance (accuracy, reaction time) for the search task, or only computational model AUCs?

**Expected evidence:** Accuracy and eye movement statistics, L109 ('hits was 87%. The false alarm rate (fa)... was 3%... mean reaction time was 1050 ms... 1517 ms').

**Ground truth:** It reports both: human behavioural stats appear in 'Accuracy and eye movement statistics' - hits 87%, false-alarm rate 3%, mean RT 1050 ms (target-present) / 1517 ms (target-absent), ~3.5 vs 5.1 fixations. So the answer is 'yes, behavioural measures are reported', not only AUCs.

metrics: tools=3 · struct_tok=4515 · content_tok=1751 · total_tok=13420 · $0.0353 · 5.69s
fetched line ranges: `0008,0009`

**Answer:**

Yes, the paper reports human behavioral performance metrics for the search task. Specifically, it provides:

1. **Accuracy**: Participants achieved an 87% correct response rate (hits) in target-present scenes, with a 3% false alarm rate in target-absent scenes.
2. **Reaction Time**: The mean reaction time was 1050 ms for target-present scenes and 1517 ms for target-absent scenes.
3. **Fixation Analysis**:
   - Average fixations: 3.5 in target-present scenes and 5.1 in target-absent scenes.
   - Fixation durations: 147 ms on target-present trials and 225 ms on target-absent trials.
   - Observers spent 428 ms on average fixating the target-person before responding.

These metrics complement the computational model evaluations. (Cited sections: "Procedure" and "Accuracy and eye movement statistics").

---

### [IDX-PDF-vanilla-paper | gpt-4o-2024-11-20] PCS1 — cross-section-synthesis

**Q:** The model combines three sources of guidance. Where is each source defined, and which section reports their combined performance?

**Expected evidence:** Guidance by saliency L141; Guidance by target features L153; Guidance by scene context features L177; combined L195; Modelling Results / Table 1 L207+.

**Ground truth:** Saliency (§Guidance by saliency, L141), target features (§Guidance by target features, L153), scene context (§Guidance by scene context features, L177); combined in §Guidance by a combined model of attention (L195), with combined performance in §Modelling Results / Table 1 (L207+).

metrics: tools=4 · struct_tok=4515 · content_tok=6733 · total_tok=18609 · $0.0498 · 6.26s
fetched line ranges: `0021`, `0013,0014,0015,0016`

**Answer:**

### Sources of Guidance and Their Definition
The document defines three sources of visual guidance used to construct the combined attentional map:

1. **Image Saliency** (M_S): Derived from the statistical saliency model, it predicts regions with rare or locally distinct features such as color and orientation that stand out (Section: *Guidance by saliency*).

2. **Target Features** (M_T): Based on a sliding-window detector trained to identify specific target attributes (e.g., pedestrians), using Histograms of Oriented Gradients (HOG) (Section: *Guidance by target features*).

3. **Scene Context** (M_C): Uses global image features to infer the likely locations of targets based on scene layout (e.g., sidewalks for pedestrians) (Section: *Guidance by scene context features*).

These contributions are mathematically integrated using Equation 1, where weights balance their relative importance (Section: *MODELLING METHODS*).

---

### Performance of Combined Models
Performance of the combined attentional map integrating saliency, target features, and scene context is detailed in the section:

- **Combined Source Models**: Reports that the combined model achieved **94% agreement with human fixation patterns**, outperforming individual sources. Most explanatory power came from the **scene context component**, with predictive accuracies in both target-present and target-absent scenarios (Section: *Combined source models*).

The combined model's performance is enhanced but exhibits room for improvement when integrating oracle-like context guidance.

### Relevant Sections
Cited sections include:
- *MODELLING METHODS* (Defining saliency, target features, and scene context)
- *Combined source models* (Performance details of the combined model).

---

### [IDX-PDF-vanilla-paper | gpt-4o-2024-11-20] PCS2 — cross-section-synthesis

**Q:** What role does the 'context oracle' play across the paper, and does the purely computational combined model ever match it?

**Expected evidence:** Upper-bound rationale L189; construction L193; comparison L286 ('not significant in target-absent, t(405)=−1.233, p=.218'); oracle-substituted 96% L209.

**Ground truth:** DRAFT: The context oracle is an empirical UPPER BOUND on context-only guidance (L189), built from 7 participants' markings (L193). The computational combined model matches it in target-absent scenes - the difference is not significant (t(405)=−1.233, p=.218, L286) - though substituting the oracle for the computational context model still lifts performance to ~96% of human agreement (L209).

metrics: tools=5 · struct_tok=4515 · content_tok=3621 · total_tok=15554 · $0.0424 · 8.79s
fetched line ranges: `0017`, `0016`, `0021`

**Answer:**

### Role of the Context Oracle
The "context oracle" plays a key role as an upper-bound benchmark for evaluating the scene context model. It provides a theoretical approximation of "ground truth" scene context by asking human participants to identify plausible locations for a pedestrian in each scene. The participants' collective responses are aggregated into the "context oracle," achieving near-perfect performance, as it distills human judgment into an idealized predictor. Its purpose is to highlight where computational scene-context models fail due to incorrect regional identification or lack of correspondence with human fixations. Notably, the oracle significantly outperforms the computational scene context model, with AUC scores of 0.88 and 0.89 for target-absent and target-present scenes, respectively (from *Guidance by scene context features* and *Combined source models*).

### Purely Computational Combined Model Performance
The purely computational combined model integrates saliency, target features, and scene context as weighted components. It demonstrates remarkable predictive power with AUC scores of 0.88 for target-absent scenes and 0.90 for target-present scenes. Notably, this model closely approximates the performance of the context oracle, with no significant difference in target-absent scenes and only a minor difference in target-present scenes. However, the combined model's success correlates strongly with the contributions of the scene context component, as the largest performance drop occurs when this component is removed. Substituting the context oracle for the scene context component further boosts the model's performance, demonstrating how the oracle sets an aspirational benchmark (*Combined source models*).

### Summary
- The context oracle acts as a performance ceiling for computational models grounded solely in scene context.
- The combined model incorporating computational scene context approximates the oracle's performance but is not entirely equivalent. Integrating oracle-level scene context would further refine its accuracy.

---

### [IDX-PDF-vanilla-paper | gpt-4o-2024-11-20] PRD1 — reflective-discovery

**Q:** What does the paper identify as the core limitation preventing any model from reaching human-level fixation prediction, and what future direction does it propose?

**Expected evidence:** Abstract L46; Discussion L294 ('map selectivity... region size of roughly 40%... tightly clustered'); Concluding Remarks L320.

**Ground truth:** The core limitation is selectivity/precision: human fixations cluster tightly in small regions while models select much broader regions - all models' accuracy falls off sharply as the selected region shrinks (a ~40% region is needed for the combined model to match human detection rate; L294). Proposed direction: future models that capture the mechanisms underlying the tight clustering of human search fixations (L320).

metrics: tools=3 · struct_tok=4515 · content_tok=5270 · total_tok=16916 · $0.0438 · 5.1s
fetched line ranges: `0022,0023`

**Answer:**

The paper identifies the core limitation preventing models from achieving human-level fixation prediction as their inability to fully capture the selectivity of human attentional maps. Specifically, computer models fail to replicate the tight clustering of human fixations and struggle with complex scenes involving multiple surfaces or semantic variations.

For future directions, it proposes:
1. Developing flexible weighting mechanisms in combined models to account for varying guidance factors (scene context, saliency, target features) depending on task constraints.
2. Improving representations of target features, saliency, and scene context to better approximate human search behavior.
3. Exploring semantic influences and contextual associations (e.g., the presence of a person being more linked to doorways than other objects) to refine models further.

These insights are drawn from the "Discussion" and "Concluding Remarks" sections.

---

### [IDX-D-paper-book-v1 | gpt-4o-2024-11-20] PDL1 — direct-location

**Q:** How many observers and how many scenes were used in the main eye-tracking search experiment, and what was the search target?

**Expected evidence:** Abstract L46; Introduction L77; Participants L83 ('Fourteen observers'); Stimuli L93 ('912 colour pictures').

**Ground truth:** 14 observers searched 912 outdoor urban scenes (half target-present, half target-absent) for a person/pedestrian.

metrics: tools=8 · struct_tok=698 · content_tok=6 · total_tok=6689 · $0.0189 · 7.19s
fetched line ranges: `0009`, `0011`, `0008`, `0012`, `0013`, `0015`

**Answer:**

The sections reviewed so far do not provide information about the number of observers, scenes used, or the search target in the eye-tracking experiment. Either this data is absent in the document, or I need clarification on where to investigate further. Would you like me to pursue other sections or refine the inquiry?

---

### [IDX-D-paper-book-v1 | gpt-4o-2024-11-20] PMP1 — methods-procedural

**Q:** In the Dalal-Triggs target-features detector, what scanning-window size was used and how many pedestrians was the reported implementation trained on?

**Expected evidence:** Guidance by target features, L159 ('scanning window of 32×64 pixels and was trained on 2000 upright, unoccluded pedestrians').

**Ground truth:** A 32x64-pixel scanning window; trained on 2000 upright, unoccluded pedestrians (plus their left-right reflections).

metrics: tools=3 · struct_tok=698 · content_tok=1 · total_tok=3639 · $0.0098 · 3.75s
fetched line ranges: `0019`

**Answer:**

The relevant section, "Guidance by target features," appears to be inaccessible in the document. Consequently, I cannot provide the specific scanning-window size used in the Dalal-Triggs target-features detector or the number of pedestrians the implementation was trained on.

---

### [IDX-D-paper-book-v1 | gpt-4o-2024-11-20] PFT1 — figure-or-table-evidence

**Q:** According to Table 1, what is the scene-context model's Area-Under-Curve (AUC) in target-absent scenes, and how does it compare with the saliency model in the same condition?

**Expected evidence:** Table 1, target-absent block, L217 (Scene context .845) and L215 (Saliency .773).

**Ground truth:** Scene context AUC = .845 vs saliency AUC = .773 in target-absent scenes; scene context is higher by .072.

metrics: tools=3 · struct_tok=698 · content_tok=4552 · total_tok=8341 · $0.0222 · 5.14s
fetched line ranges: `207-318`

**Answer:**

According to Table 1, in **target-absent scenes**, the **scene-context model** achieves an **Area-Under-Curve (AUC)** of **0.845**, while the **saliency model** has an AUC of **0.773**. This shows that the scene-context model outperforms the saliency model by a margin of **0.072** in this condition.

This result highlights the superior ability of the scene-context model to predict fixation locations in target-absent scenes compared to the saliency model, which relies solely on visual salience.

**Cited Section: Modelling Results > Saliency and Target Features Models**.

---

### [IDX-D-paper-book-v1 | gpt-4o-2024-11-20] PFT3 — figure-or-table-evidence

**Q:** What does Figure 8 compare, and how are the two panels defined?

**Expected evidence:** Figure 8 caption, L205 ('Comparison between (a) the computationally defined scene context map and (b) the empirically defined context oracle map for a single image').

**Ground truth:** Figure 8 compares, for a single image, (a) the computationally-defined scene-context map vs (b) the empirically-defined context-oracle map (both thresholded at 20% of image area, with human-fixation dots).

metrics: tools=6 · struct_tok=698 · content_tok=16993 · total_tok=74204 · $0.1871 · 9.74s
fetched line ranges: `1-479`, `18-26`, `11`, `195-207`

**Answer:**

Figure 8 compares two scene context maps for a single image: 
1. **(a)** The *computationally defined scene context map*, which is generated by a model predicting locations based on scene features.
2. **(b)** The *empirically defined context oracle map*, generated by human observers who marked regions they believed most likely to contain the target. 

In both cases, the maps are thresholded to 20% of the image area and overlaid with dots representing human fixations ([“Guidance by a combined model of attention”](#195)).

---

### [IDX-D-paper-book-v1 | gpt-4o-2024-11-20] PEG2 — evidence-gap

**Q:** Does the paper report human behavioural performance (accuracy, reaction time) for the search task, or only computational model AUCs?

**Expected evidence:** Accuracy and eye movement statistics, L109 ('hits was 87%. The false alarm rate (fa)... was 3%... mean reaction time was 1050 ms... 1517 ms').

**Ground truth:** It reports both: human behavioural stats appear in 'Accuracy and eye movement statistics' - hits 87%, false-alarm rate 3%, mean RT 1050 ms (target-present) / 1517 ms (target-absent), ~3.5 vs 5.1 fixations. So the answer is 'yes, behavioural measures are reported', not only AUCs.

metrics: tools=4 · struct_tok=698 · content_tok=2 · total_tok=3682 · $0.0101 · 4.39s
fetched line ranges: `0015`, `0022`

**Answer:**

The sections I consulted do not provide text, so I'm unable to verify whether the paper reports human behavioral performance (such as accuracy or reaction time) alongside computational model AUCs. Let me know if I should examine additional sections for this information.

---

### [IDX-D-paper-book-v1 | gpt-4o-2024-11-20] PCS1 — cross-section-synthesis

**Q:** The model combines three sources of guidance. Where is each source defined, and which section reports their combined performance?

**Expected evidence:** Guidance by saliency L141; Guidance by target features L153; Guidance by scene context features L177; combined L195; Modelling Results / Table 1 L207+.

**Ground truth:** Saliency (§Guidance by saliency, L141), target features (§Guidance by target features, L153), scene context (§Guidance by scene context features, L177); combined in §Guidance by a combined model of attention (L195), with combined performance in §Modelling Results / Table 1 (L207+).

metrics: tools=4 · struct_tok=698 · content_tok=121 · total_tok=3876 · $0.0112 · 4.3s
fetched line ranges: `0025`, `0018,0019,0020`

**Answer:**

The document defines the three sources of guidance and reports the combined performance as follows:

1. **Sources of Guidance**:
   - **Guidance by Saliency**: Found in the section "Guidance by saliency."
   - **Guidance by Target Features**: Found in the section "Guidance by target features."
   - **Guidance by Scene Context Features**: Found in the section "Guidance by scene context features."

2. **Combined Performance**:
   - The section "Combined source models" reports the combined performance of these sources.

Let me know if you'd like specific details extracted for any of these sections!

---

### [IDX-D-paper-book-v1 | gpt-4o-2024-11-20] PCS2 — cross-section-synthesis

**Q:** What role does the 'context oracle' play across the paper, and does the purely computational combined model ever match it?

**Expected evidence:** Upper-bound rationale L189; construction L193; comparison L286 ('not significant in target-absent, t(405)=−1.233, p=.218'); oracle-substituted 96% L209.

**Ground truth:** DRAFT: The context oracle is an empirical UPPER BOUND on context-only guidance (L189), built from 7 participants' markings (L193). The computational combined model matches it in target-absent scenes - the difference is not significant (t(405)=−1.233, p=.218, L286) - though substituting the oracle for the computational context model still lifts performance to ~96% of human agreement (L209).

metrics: tools=4 · struct_tok=698 · content_tok=2 · total_tok=3677 · $0.0101 · 5.04s
fetched line ranges: `0020`, `0025`

**Answer:**

The content related to the roles of the "context oracle" and how the combined computational model compares to it appears to be missing or unavailable in the document. If you have access to another source or specific details to guide a more focused search, let me know!

---

### [IDX-D-paper-book-v1 | gpt-4o-2024-11-20] PRD1 — reflective-discovery

**Q:** What does the paper identify as the core limitation preventing any model from reaching human-level fixation prediction, and what future direction does it propose?

**Expected evidence:** Abstract L46; Discussion L294 ('map selectivity... region size of roughly 40%... tightly clustered'); Concluding Remarks L320.

**Ground truth:** The core limitation is selectivity/precision: human fixations cluster tightly in small regions while models select much broader regions - all models' accuracy falls off sharply as the selected region shrinks (a ~40% region is needed for the combined model to match human detection rate; L294). Proposed direction: future models that capture the mechanisms underlying the tight clustering of human search fixations (L320).

metrics: tools=4 · struct_tok=698 · content_tok=2 · total_tok=3695 · $0.0102 · 3.85s
fetched line ranges: `0026`, `0027`

**Answer:**

The sections "DISCUSSION" and "CONCLUDING REMARKS" in the document did not contain any text. I could not locate the core limitation or the proposed future direction regarding models achieving human-level fixation prediction. Would you like me to explore another specific aspect or section of the document?

---

### [IDX-D-paper-book-v1-clean | gpt-4o-2024-11-20] PDL1 — direct-location

**Q:** How many observers and how many scenes were used in the main eye-tracking search experiment, and what was the search target?

**Expected evidence:** Abstract L46; Introduction L77; Participants L83 ('Fourteen observers'); Stimuli L93 ('912 colour pictures').

**Ground truth:** 14 observers searched 912 outdoor urban scenes (half target-present, half target-absent) for a person/pedestrian.

metrics: tools=5 · struct_tok=686 · content_tok=3 · total_tok=3699 · $0.0103 · 4.59s
fetched line ranges: `0008`, `0010`, `0011`

**Answer:**

The document contains sections on "Participants," "Stimuli," and "Procedure," but relevant details about the number of observers, scenes, or the search target were not extracted from those sections. Could you clarify your query or allow further exploration?

---

### [IDX-D-paper-book-v1-clean | gpt-4o-2024-11-20] PMP1 — methods-procedural

**Q:** In the Dalal-Triggs target-features detector, what scanning-window size was used and how many pedestrians was the reported implementation trained on?

**Expected evidence:** Guidance by target features, L159 ('scanning window of 32×64 pixels and was trained on 2000 upright, unoccluded pedestrians').

**Ground truth:** A 32x64-pixel scanning window; trained on 2000 upright, unoccluded pedestrians (plus their left-right reflections).

metrics: tools=3 · struct_tok=686 · content_tok=1 · total_tok=3617 · $0.0097 · 3.79s
fetched line ranges: `0018`

**Answer:**

The document does not contain details about the Dalal-Triggs detector, its scanning-window size, or the number of pedestrians the implementation was trained on. If you have another question or need clarification on a different topic, let me know!

---

### [IDX-D-paper-book-v1-clean | gpt-4o-2024-11-20] PFT1 — figure-or-table-evidence

**Q:** According to Table 1, what is the scene-context model's Area-Under-Curve (AUC) in target-absent scenes, and how does it compare with the saliency model in the same condition?

**Expected evidence:** Table 1, target-absent block, L217 (Scene context .845) and L215 (Saliency .773).

**Ground truth:** Scene context AUC = .845 vs saliency AUC = .773 in target-absent scenes; scene context is higher by .072.

metrics: tools=4 · struct_tok=686 · content_tok=2 · total_tok=5033 · $0.0135 · 4.91s
fetched line ranges: `0021`, `0023,0024`

**Answer:**

The document does not contain the necessary information in the accessed sections, and I couldn't find the values from Table 1 for the AUC comparison between the scene-context model and the saliency model in target-absent scenes. Let me know if you want me to search further or assist with another question.

---

### [IDX-D-paper-book-v1-clean | gpt-4o-2024-11-20] PFT3 — figure-or-table-evidence

**Q:** What does Figure 8 compare, and how are the two panels defined?

**Expected evidence:** Figure 8 caption, L205 ('Comparison between (a) the computationally defined scene context map and (b) the empirically defined context oracle map for a single image').

**Ground truth:** Figure 8 compares, for a single image, (a) the computationally-defined scene-context map vs (b) the empirically-defined context-oracle map (both thresholded at 20% of image area, with human-fixation dots).

metrics: tools=4 · struct_tok=686 · content_tok=8462 · total_tok=12197 · $0.0323 · 7.02s
fetched line ranges: `157-226`, `79-157`

**Answer:**

Figure 8 compares two types of scene context maps for the task of predicting human fixations during a visual search: 

1. **The computationally defined scene context map**: This is based on the computational model of scene guidance, which selects "relevant" image regions based on global scene features and associations with probable pedestrian locations.

2. **The empirically defined context oracle map**: This is based on observer-marked regions indicating the most plausible places for pedestrians, using cues like horizon lines, heights of doorways, cars, and signs.

The comparison highlights differences in predictive accuracy and alignment with human search patterns. Both maps are thresholded at 20% of the image area, with human fixations depicted as dots. 

Cited from: "Guidance by a combined model of attention".

---

### [IDX-D-paper-book-v1-clean | gpt-4o-2024-11-20] PEG2 — evidence-gap

**Q:** Does the paper report human behavioural performance (accuracy, reaction time) for the search task, or only computational model AUCs?

**Expected evidence:** Accuracy and eye movement statistics, L109 ('hits was 87%. The false alarm rate (fa)... was 3%... mean reaction time was 1050 ms... 1517 ms').

**Ground truth:** It reports both: human behavioural stats appear in 'Accuracy and eye movement statistics' - hits 87%, false-alarm rate 3%, mean RT 1050 ms (target-present) / 1517 ms (target-absent), ~3.5 vs 5.1 fixations. So the answer is 'yes, behavioural measures are reported', not only AUCs.

metrics: tools=5 · struct_tok=686 · content_tok=3 · total_tok=6289 · $0.0168 · 6.19s
fetched line ranges: `0013,0014`, `0014`, `0013`

**Answer:**

The sections potentially discussing human behavioral performance, such as "Human Eye Movements Result" and "Accuracy and eye movement statistics," returned no content. Thus, I cannot determine from the document whether it reports human behavioral performance metrics (like accuracy or reaction time) or only the computational model AUCs.

---

### [IDX-D-paper-book-v1-clean | gpt-4o-2024-11-20] PCS1 — cross-section-synthesis

**Q:** The model combines three sources of guidance. Where is each source defined, and which section reports their combined performance?

**Expected evidence:** Guidance by saliency L141; Guidance by target features L153; Guidance by scene context features L177; combined L195; Modelling Results / Table 1 L207+.

**Ground truth:** Saliency (§Guidance by saliency, L141), target features (§Guidance by target features, L153), scene context (§Guidance by scene context features, L177); combined in §Guidance by a combined model of attention (L195), with combined performance in §Modelling Results / Table 1 (L207+).

metrics: tools=6 · struct_tok=686 · content_tok=275 · total_tok=5687 · $0.0163 · 6.69s
fetched line ranges: `0024`, `0017,0018,0019`, `0020`, `0016`

**Answer:**

The sources of guidance (saliency, target features, and scene context features) and their definitions are discussed under the following subsections within "Modelling Methods":

1. **Guidance by saliency** - defines how saliency drives attention.
2. **Guidance by target features** - describes the role of target-specific attributes.
3. **Guidance by scene context features** - explains features derived from the scene's semantics.

The combined performance of these models is reported in the subsection **"Combined source models"** within the "Modelling Results" section. However, attempts to fetch their descriptions and the combined performance specifics were unsuccessful. Let me know if you'd like a retry for content retrieval or tailored queries.

---

### [IDX-D-paper-book-v1-clean | gpt-4o-2024-11-20] PCS2 — cross-section-synthesis

**Q:** What role does the 'context oracle' play across the paper, and does the purely computational combined model ever match it?

**Expected evidence:** Upper-bound rationale L189; construction L193; comparison L286 ('not significant in target-absent, t(405)=−1.233, p=.218'); oracle-substituted 96% L209.

**Ground truth:** DRAFT: The context oracle is an empirical UPPER BOUND on context-only guidance (L189), built from 7 participants' markings (L193). The computational combined model matches it in target-absent scenes - the difference is not significant (t(405)=−1.233, p=.218, L286) - though substituting the oracle for the computational context model still lifts performance to ~96% of human agreement (L209).

metrics: tools=6 · struct_tok=686 · content_tok=275 · total_tok=4009 · $0.0112 · 4.17s
fetched line ranges: `0023`, `0024`, `0020`, `0019`

**Answer:**

The sections related to the role of the 'context oracle' and its comparison to any purely computational combined model lack content or are inaccessible from the document. I cannot provide the requested information. Let me know if you'd like to explore other sections or clarify further.

---

### [IDX-D-paper-book-v1-clean | gpt-4o-2024-11-20] PRD1 — reflective-discovery

**Q:** What does the paper identify as the core limitation preventing any model from reaching human-level fixation prediction, and what future direction does it propose?

**Expected evidence:** Abstract L46; Discussion L294 ('map selectivity... region size of roughly 40%... tightly clustered'); Concluding Remarks L320.

**Ground truth:** The core limitation is selectivity/precision: human fixations cluster tightly in small regions while models select much broader regions - all models' accuracy falls off sharply as the selected region shrinks (a ~40% region is needed for the combined model to match human detection rate; L294). Proposed direction: future models that capture the mechanisms underlying the tight clustering of human search fixations (L320).

metrics: tools=4 · struct_tok=686 · content_tok=2 · total_tok=3672 · $0.0101 · 5.14s
fetched line ranges: `0025`, `0026`

**Answer:**

The document does not provide detailed information in the "Discussion" or "Concluding Remarks" sections regarding the core limitation preventing a model from achieving human-level fixation prediction or the proposed future direction. Let me know if you'd like me to investigate other sections of the document.

---
