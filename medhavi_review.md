# CRITIQ — Peer Review

**Manuscript:** *Causal Inference and Adaptive Measurement in an LLM-Based Tutoring Platform: A Framework for the Medhavi Project*

**Type:** Methodological / architectural framework paper (no empirical data)

**Reviewer frame:** The standard for a framework paper is internal consistency, novelty, feasibility, and honest accounting of open problems. I'm not grading it on replicability of results, because it reports no results. I am grading it on whether the architecture it proposes could actually support the claims it wants to make — and on whether the paper admits where it can't.

---

## VERDICT

This paper's core conceptual move — the intervention / diagnostic / context split applied to Hattie's inventory, and the three-mode operational architecture that follows from it — is genuinely useful and well-motivated. The DAG formalism is deployed correctly, the critique of flat effect-size rankings is sound, and the integration with the EU AI Act is unusually serious for a methods paper. This is the strong spine of a good paper.

But the manuscript as submitted has three structural problems that will sink it with most reviewers. First, an entire load-bearing section (§5, the outcome-measurement layer) rests on a single citation (Brown 2026) that appears to be an unpublished preprint in a non-standard venue, with no visible validation and, unusually, no author byline on the manuscript itself — so it is not possible to assess whether this is self-citation. Second, the paper tries to do seven things in one submission (Hattie critique, DAG methodology, mode architecture, GLP integration, SWIG longitudinal analysis, LLM execution discipline, EU AI Act compliance, empirical Bayesian baselines, and a proposed evaluation standard), and no single venue will be the right home for all of them. Third, several sections (§6 on SWIGs, §3.3 on measurement bias, §5.5 on gaming defense) assert that hard problems are handled and then punt on them.

**Recommendation: Major Revision.** The bones are good. The scope and the sourcing need surgery.

---

## STRUCTURAL DIAGNOSIS

### Title and abstract

The title accurately reflects the framework. It does not, however, signal the two things the paper spends the most space on — the critique of Hattie and the EU AI Act compliance argument. If those are core contributions, the title should say so. If they are supporting material, the paper should not spend one and a half sections on Hattie and a full section on the AI Act.

The abstract announces four contributions but describes them in inert language — "reframes," "formalizes," "integrates," "specifies." A reader cannot tell from the abstract what is demonstrated versus what is proposed, or what would make the framework fail. The abstract never states a falsifiable claim about the framework itself.

### Introduction

§1.1 and §1.2 are the strongest pages in the manuscript. The clarity/grade-retention mediation example (§2.2) is well-chosen — it uses Hattie's own variables to expose the limitation of Hattie's own method, which is the right rhetorical move. The intervention/diagnostic/context distinction is operationalized cleanly and the paper is careful to say a variable's category depends on the research question, not on the variable itself.

§1.3 introduces the three-mode architecture plus a "fourth pattern" (diagnostic-triggered revision via interrupted time series). The fourth pattern is introduced in the introduction and then almost never mentioned again. It is not developed in §3, §4, or §5. If it is a real part of the framework, it needs its own treatment. If it is an aside, remove it from §1.3 — right now it introduces an unresolved thread on the first page of structural content.

The "soft hierarchy" framing of mode escalation (fixed → adaptive → RCT) is useful but conflates two things. The transition fixed → adaptive is a response to a detected problem (diagnostic signals failing). The transition adaptive → RCT is a researcher choice about what kind of claim to produce (unbiased effect estimate vs. practical improvement). These are not the same kind of decision and the paper treats them as stations on the same track.

### Reverse outline test

I ran the reverse outline test — summarizing each section in five words. The sequence reads:

1. Hattie is wrong in a specific way.
2. DAGs fix that specific wrongness.
3. Medhavi architecture neutralizes causal bias.
4. Here is what the platform does.
5. GLP measures the outcomes.
6. Longitudinal analysis is hard; we'll try.
7. The LLM must behave.
8. The AI Act requirements emerge naturally.
9. Conclusion.

The arc from §1 through §5 is coherent. §6 is an acknowledged weak point (the paper admits the hard problems in time-varying causal inference remain hard). §7 is operational discipline, not a conceptual contribution. §8 covers regulatory compliance, empirical Bayesian baselines, transparency principles, *and* a proposed evaluation standard — four things fused into one section because they all happen to involve things outside the core framework.

The structural fix is surgical: **§8.1 (EU AI Act) and §8.4 (proposed evaluation standard) should probably be separated out of the current submission entirely.** They are each strong enough to be their own paper in the right venue (AI policy, learning analytics standards). Keeping them in the same manuscript as the causal-inference framework splits the audience: a learning scientist who doesn't care about Annex III will skim past §8, and a policy reader won't fight through §2–§6 to reach it.

### Narrative break

The hardest narrative break is between §5 and §6. §5 ends with a strong synthesis ("In-flow causal experiments"). §6 opens with "Learning is not a static event" and dives into SWIGs. The bridge is missing. Why does the reader now need counterfactual analysis across thirty days of instruction when §5 just finished telling them the in-flow measures solve the outcome problem? The paper doesn't answer this. My guess is that §5 handles the cross-sectional causal question (does Policy X outperform Policy Y in this moment?) and §6 handles the longitudinal counterfactual question (what would this student's trajectory have been under a different policy?), but the paper doesn't say this explicitly.

---

## METHODOLOGICAL REALITY (ARCHITECTURAL FEASIBILITY)

This is where the paper earns most of its keep, and also where it overpromises most.

### What the architecture can actually deliver

The paper's core operational claim is that an LLM-based tutoring platform can function as a "clinical protocol execution engine" supporting randomized causal inference. This is defensible. The three required capabilities — pre-call policy assignment, policy-constraint prompts, and post-generation adherence verification — are all implementable with current tooling. The semantic logging claim (§3.3) is correct in principle.

### Where the architecture is underspecified

**The adherence classifier (§7) is load-bearing and its validation is not discussed.** The paper states that "a post-generation classifier scores every output for policy adherence" and treats this as the operational mechanism that makes the claim "the LLM executed this policy" true rather than aspirational. But validating the classifier is its own problem. Ground truth for "did this output adhere to the assigned policy?" requires human rating. Establishing interrater reliability on pedagogical policy adherence is nontrivial — pedagogy researchers routinely fail to agree on what counts as "specific corrective feedback" versus "generic corrective feedback." The paper does not acknowledge that the validator needs validating. This is a significant oversight in a framework that rests on it.

**Context variables are enumerated but not operationalized.** §1.2 lists "prior achievement, device and network conditions, session timing, baseline engagement history, language background" as context covariates. §3.1 says these must be "logged as context covariates and included in the analysis via stratification or regression adjustment." But the paper never specifies how much context data the system actually has, whether student-side context (prior achievement) is captured at enrollment or inferred from platform behavior, or what happens when context is missing. For a framework that claims to satisfy Article 10 (data governance), this is light.

**Mode 2's "composite reward signal" is a hand-wave.** §1.3 says the bandit reward is "a composite of diagnostic measures drawn from the GLP framework." How are the seven GLP components combined into a scalar reward? Is it a weighted sum? A latent variable model? Does the weighting depend on content type? The paper leaves this unspecified and then in §5.2 notes that a composite GLP score is produced by "an ensemble model combining the seven components, weighted according to the cognitive tier of the learning activity" — which pushes the problem into Brown 2026, a source the reader cannot access.

### The always-on variable problem is real but the solution is thin

§1.3's "fourth pattern" — interrupted time series for variables like teacher clarity that cannot be randomized — is the correct general strategy, but interrupted time series has strong internal validity threats (history, maturation, selection, regression to the mean) that the paper does not address. For a platform that will have rolling content updates anyway, distinguishing a clarity-revision effect from a content-update effect will be hard. This deserves a paragraph, not a sentence.

### Red flags

- **"Standard protocols" verbatim.** §2.1 refers to DAGs as supporting "formal derivation of which statistical adjustments are needed to identify a causal effect" — correct, but the derivation methods (backdoor criterion, d-separation) are named in §3.2 without citation to the operational algorithms (ID algorithm, Tian-Pearl) that would be needed for a real implementation.
- **Underpowered-by-design worry in Mode 2.** Contextual bandits in educational settings typically run with small per-arm samples before the allocator concentrates. The paper does not discuss early-stopping safeguards against premature convergence on a false best arm.
- **Missing regulatory compliance detail.** IRB approval is never mentioned in the manuscript, even though Modes 2 and 3 involve randomized assignment of students to pedagogical variants. Adaptive clinical trials have a developed IRB framework; adaptive educational trials do not, but a framework paper that proposes randomized educational intervention should at least gesture at what human-subjects approval looks like here.

---

## STATISTICAL INTEGRITY (LOGICAL VALIDITY OF CAUSAL CLAIMS)

### What is correct

The paper is honest about the central statistical tradeoff: **bandit-based adaptive allocation produces biased effect-size estimates.** §1.3 explicitly states this as the reason Mode 3 exists. This is correct and matters — a lot of adaptive-learning systems paper over this. Naming it is a real virtue.

The intent-to-treat / per-protocol distinction in §3.2 is deployed correctly. The note that ITT analysis includes protocol-violating outputs ("because ITT is the point of ITT") is the right instinct.

The recognition that time-varying confounding cannot be handled by standard regression (§6) and requires g-methods is correct.

### What is underdeveloped

**The bandit inference literature is missing.** The paper mentions Thompson sampling and upper-confidence-bound but cites neither. The inference problem for bandit-collected data is active ongoing research — Dimakopoulou et al. on doubly robust estimators for contextual bandits, Nie et al. on adaptive inference, Zhang et al. on post-bandit estimation. A framework paper that proposes bandit-based allocation and then retrospective causal analysis on the same event log needs to address how the two are reconciled. The paper acknowledges the tension (§6's last paragraph: "The adaptive mode makes real-time decisions; the causal-inference layer makes retrospective claims. Both draw on the same event log.") but does not describe the methodology that would allow this.

**Multiple comparisons are not addressed.** With seven GLP components, per-content Bayesian posteriors, and per-arm outcomes in bandits, the platform is producing many statistical comparisons. Nothing in the paper indicates how the multiple-testing problem is handled. This matters because diagnostic-triggered escalation (§1.3) is a decision rule fired on a statistical signal, and if that signal is tested against many thresholds without correction, false positive escalations are likely.

**The Bayesian baselines in §8.2 have a prior-shopping problem.** The paper says priors are "constructed from three sources: historical learning-science literature where it exists, pilot deployment data with instructor-verified engagement, and content-author judgments about conceptual difficulty." Mixing evidence-based priors with instructor-verified engagement data introduces selection: which pilot sessions get instructor-verified? The paper acknowledges that priors are "known to be weak" at launch, which is honest, but does not acknowledge that the prior construction process itself is a researcher degree of freedom.

**"Genuine Learning Probability" is not a probability.** This is a terminological issue but it matters. A composite score produced by an ensemble model, even one with a credible interval, is not generally a probability. If it is P(genuine learning | observations), then the generative model and the calibration procedure need to be specified. If it is a score, it should not be called a probability. The paper treats the name as a given because it comes from Brown 2026, but the name is doing work throughout §5 that a score name could not do.

### Detection patterns

- **HARKing risk in adaptive mode.** Mode 2's escalation trigger is defined post hoc, and the bandit reward can be respecified as the framework evolves. The paper should commit to a pre-registration discipline for which diagnostic thresholds are locked before deployment.
- **Graphic standards.** The one DAG in the manuscript (§2.2) is presented as ASCII art in the text rather than as a figure. For a framework built on DAGs, this is odd and will look unprofessional to reviewers. Every DAG should be a proper figure.

---

## ARGUMENT COHERENCE AND OVERREACH

### The gaming defense (§5.5) is weak

The claim that "simultaneously gaming all seven components without performing the underlying cognitive work approaches the cost of performing that work" and therefore "the gaming has become indistinguishable from learning in the only sense that matters" is clever but does not survive scrutiny.

First, the seven components are not clearly independent. Gaming Y₁ (time distribution) can also affect Y₇ (scaffolding response) because a student who waits before accepting hints is producing a different pattern on both measures. The defense-in-depth argument requires independent layers; the paper does not establish independence.

Second, "indistinguishable from learning in the only sense that matters" smuggles in a definition. The only sense that matters *to the platform's measurement system*. From a learning-science perspective, there is a real difference between a student who has stored and can retrieve a schema versus a student who has successfully simulated all seven behavioral signatures without storage. The second student will fail on genuinely novel transfer. The paper collapses this distinction in a way Brown 2026 may not intend.

### "Does not replace Hattie" — stated three times

This phrase appears in the abstract (implicitly), §1.1, §1.4, and §9. Three statements of "we're not replacing Hattie" in a paper whose first major section is called "The problem with effect-size rankings" reads as defensive. Say it once, clearly, and move on. The overuse signals anxiety about the critique rather than confidence in it.

### Overreach language

The claim that Medhavi "systematically neutralizes the confounding, selection, and measurement biases that have historically plagued educational research" (§9) is too strong. The framework provides infrastructure that, if used correctly, mitigates these biases under specific conditions (Modes 2 and 3, adherence-verified LLM output, complete semantic logging). "Systematically neutralizes" is marketing language. A framework paper can afford to be more modest than a product paper.

Similarly, the claim in §5.4 that Medhavi provides "the 'cause' end of the causal chain" and GLP provides "the 'effect' end" is cute but reifies a proposal as an operating system. The framework proposes an architecture. Whether the architecture delivers causes and effects is an empirical question that the paper does not yet test.

### Underreach in places

The ethics of adaptive allocation get one paragraph in §3.2 (differential attrition as a safety signal). Adaptive educational interventions raise real ethical questions that adaptive clinical trials have spent decades working through. The fact that Mode 2 systematically exposes some students to worse-performing pedagogical variants during the exploration phase deserves engagement, not deflection. The paper does not cite any adaptive-trial ethics literature.

---

## WRITING AS DESIGN

### Clarity

The writing is generally clean. Technical terms are defined at first use. The vocabulary discipline about avoiding "retention" as a learning outcome (noted in the change log) is exactly the right kind of craft decision. Sentences are long but not unreadably so.

### Claim calibration

Calibration is uneven. In §1 and §2, the paper is careful — "a plausible DAG is therefore," "almost certainly wrong as a causal model." In §3 and §4, the architecture is described in declarative language as if it existed: "The platform logs every interaction," "The platform assigns pedagogical policies." This is a framework paper; the architecture is proposed, not operational. The declarative mood implies otherwise.

The fix is not to weasel-word everything. The fix is to be explicit up front that §3 and §4 describe the architecture as proposed, and then the declarative voice is fine within that frame.

### Jargon audit

The paper uses "DAG," "SWIG," "g-methods," "ITT," "IPW," "CE marking," "CARS framework," "d-separation," "backdoor path," "Thompson sampling," "marginal structural models," "interrupted time series," and more. Every term is legitimate, but the cumulative load is high. Any individual reader — causal inference researcher, learning scientist, AI policy person — will be fluent in some of these and lost in others. If the paper goes to an interdisciplinary venue, a glossary or a more aggressive just-in-time definition strategy would help. If it splits into two or three papers (as I recommend below), each can target its native vocabulary.

### Signposting

Section transitions are functional but mostly read "Section N addresses X" rather than building narrative. The paper knows what it's doing internally but does not hold the reader's hand through the arc. This is a solvable problem with better transition sentences between sections.

### Specific language issues

- "Genuine learning" vs "borrowed certainty" is a vivid distinction that does real work in §5, but it also imports a strong prior about what AI-assisted learning is *actually doing* to students. This framing is Brown's, not the paper's, but the paper adopts it uncritically. A reviewer sympathetic to LLM-augmented learning will read "borrowed certainty" as a thumb on the scale.
- "Irreducibly Human Research Series" as the venue for Brown 2026 is worth examining. It sounds like a mission-statement publication rather than a peer-reviewed venue.

---

## ETHICAL SCREENING

### Conflict of interest and author identity

**The manuscript has no author byline visible to me.** This is the single most concerning thing in the submission. I cannot tell whether Brown 2026 — the source that carries §5 — is self-citation, a collaborator, or an independent source. I cannot tell whether the authors have a commercial interest in the Medhavi platform whose architecture is being proposed as a framework. I cannot tell whether the paper is preprint, submission, or internal document. All of these are fixable; none should be absent from a submission.

### Citation practices

The reference list is short (approximately ten sources) for a paper of this scope. Several specific gaps:

- **No citations for the Hattie critique.** The paper's critique of Hattie rests on independent reasoning, which is fine, but there is a real literature on the methodological problems with Hattie's syntheses (Bergeron & Rivard; Simpson; Wiliam; Shanahan). Not citing this literature is either an oversight or suggests the authors are not aware of it — either is a problem.
- **No adaptive trial ethics citations.** The paper proposes randomized educational intervention and adaptive allocation of students to pedagogical variants, with essentially no citation of the adaptive clinical trial ethics literature (Lipkus, Berry, etc.).
- **No bandit-in-education citations.** Villar, Bowden & Wason; Rafferty et al.; Williams et al. have published specifically on multi-armed bandits in educational settings. Zero of this work is cited.
- **No LLM-in-education citations.** The paper proposes an LLM-based tutoring platform and cites zero LLM papers. The architecture choices (policy-as-system-prompt, post-generation classification, system-prompt-as-constraint) have a growing literature that the paper ignores.
- **Heavy reliance on Hernán and Robins.** These are the right citations for the causal inference material, but the paper leans on them exclusively.

### Representation and scope

The diagnostic layer (GLP) is built on a model of learning that is mostly individualistic and cognitive. The paper does not engage with sociocultural learning theory, situated cognition, or the social dimensions of tutoring that chatbot platforms may structurally eliminate. This is a scope choice, not an error — but it should be named as a scope choice.

### Language and bias

No obvious bias issues in the writing itself. The "genuine learning vs borrowed certainty" framing does carry a normative load, as noted above.

### Human subjects

IRB / human-subjects research approval is never mentioned. For a framework that proposes randomized assignment of students to pedagogical variants, this is a gap.

---

## RANKED IMPROVEMENTS

1. **[CRITICAL]** — The paper rests a full section on Brown 2026, a source that appears to be an unpublished preprint in a non-standard venue, while the manuscript itself has no visible authorship. → Either establish Brown 2026's credibility (peer review, validation, access), make the dependency on GLP conditional ("if an outcome-measurement layer with these properties exists"), or remove §5 and propose the outcome-measurement layer as an open problem. Add author byline and affiliations. Declare any commercial interest in the Medhavi platform. → Without this, the whole framework is resting on a citation the reader cannot evaluate and the review process cannot audit.

2. **[CRITICAL]** — The paper tries to do seven things. → Split. The causal-inference-plus-mode-architecture framework is one paper (§1–§5, §6, §7). The EU AI Act compliance mapping is a second paper for a policy/compliance venue. The empirical Bayesian baseline proposal and the four-element evaluation standard are a third paper for a learning analytics or standards venue. The single-submission version is too scope-spread to land well anywhere. → Without this, the paper will get rejected at specialist venues for being off-topic and at general venues for being too technical.

3. **[MAJOR]** — The adherence classifier (§7) is load-bearing and its validation is undiscussed. → Add a subsection on classifier validation: how ground truth is established, what interrater reliability is achieved, what the classifier's error rate is, and how classifier error propagates into the causal estimates it gates. → Without this, the operational mechanism for "the LLM executed this policy" is not actually established.

4. **[MAJOR]** — The ethics of Mode 2 (bandit-based adaptive allocation) get one paragraph. → Expand §3.2 or add a subsection. Engage adaptive trial ethics literature. Address what the framework does when the best-performing arm identified by the bandit is substantially better than the exploration arms — which is the case that matters ethically. IRB framing should appear somewhere in the paper. → Without this, reviewers with a human-subjects frame will treat the framework as ethically incomplete.

5. **[MAJOR]** — §6 punts on time-varying causal inference while claiming the framework handles it. → Either develop the g-methods implementation for the Medhavi logs in enough detail that a reader can evaluate feasibility, or explicitly scope §6 as an open problem the framework can eventually accommodate. The current treatment is the worst of both: implies the problem is solved, admits it isn't. → Without this, the longitudinal claims in the abstract and §9 are not supported.

6. **[MAJOR]** — Citation coverage is insufficient for the paper's scope. → Add at minimum: (a) methodological critique-of-Hattie literature; (b) multi-armed bandits in educational settings; (c) adaptive trial ethics; (d) bandit-collected data inference methods; (e) LLM-in-education architectural work. → Without this, reviewers in any of the paper's component fields will read it as under-scholarly.

7. **[MINOR]** — The DAG in §2.2 is ASCII art in running text rather than a figure. Every DAG in a DAG-based paper should be a proper figure with consistent styling, node labels, and edge annotations.

8. **[MINOR]** — "Does not replace Hattie" appears three times. Once is sufficient. The repetition reads defensive.

9. **[MINOR]** — Declarative mood in §3–§4 implies the architecture exists. Add one sentence at the start of §3 scoping the section as describing a proposed architecture, so the declarative voice within the section is honest.

10. **[MINOR]** — "Genuine Learning Probability" is not, as described, a probability. Either define the generative model that makes it a probability or push back on the name when you cite Brown.

---

## WHAT WORKS

The three-category variable decomposition (intervention / diagnostic / context) is the paper's best idea and deserves to be the centerpiece. The three-mode operational architecture (fixed / adaptive / RCT) is a real design contribution — it respects the reality that most instructors are not researchers while preserving the option for researcher-grade rigor. The clarity-retention DAG example (§2.2) is a well-chosen motivating case. The honest acknowledgment that Mode 2 produces biased estimates (§1.3) is the kind of methodological integrity that elevates a framework paper.

The EU AI Act section, if split out, is a genuinely useful standalone contribution. Almost no published work maps causal-inference architectural commitments onto Annex III Category 3 requirements, and this paper does it concretely.

**The strongest path forward: treat the intervention/diagnostic/context decomposition and the three-mode architecture as the core contribution, build §1–§4 out around them with proper citations and a sharper scope, demote GLP integration to "one possible outcome-measurement layer," and move the regulatory material to a companion paper. The bones are good. Rebuild on them.**
