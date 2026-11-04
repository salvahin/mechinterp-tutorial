#!/usr/bin/env python3
"""Word-for-word speaker script for Block 5 (Víctor Terrón-Macías), 2:10 - 3:00.

parts/part3_victor.html keeps the terse director's notes ("do this, then say
that"); this file holds the other thing a presenter wants: the sentences
themselves, written to be read out loud. build.py injects each entry as a second
<aside class="speech"> on the slide, and deck.js shows it when the presenter or
notes window is switched to SPEECH (the button, or the S key). A slide with no
entry here falls back to its notes, so Parts 1 and 2 are unaffected.

Conventions, the same ones notes_es.py and script_1h.py use
-----------------------------------------------------------
  <b>2:10:15 -> 2:11:15.</b>    running time inside the four-hour tutorial
  <p class="cue" data-cue="n">  the paragraph you say at build step n; deck.js
                                labels it and tells you when to press ->
  <i>[ ... ]</i>                stage direction, not read aloud

Written for roughly 130 words a minute. The hands-on slides (p3-predict, p3-nb5)
are a short script plus floor instructions rather than prose: during those 22
minutes the room is typing, not listening.

Every figure quoted here is on the slide or in the slide's own notes. The NB5
numbers come from the test run with the Qwen2.5-0.5B fallback judge and are
always introduced as "in our test run" / "en nuestra prueba".
"""

# ================================================================== English

EN = {

"p3-section": """
    <b>2:10:00 &rarr; 2:10:15.</b> <i>[Nothing to add to the title. Say it and move.]</i>
    <p>Block five. One question: when an LLM judges, which of its verdicts do we trust?</p>
""",

"p3-open": """
    <b>2:10:15 &rarr; 2:11:15.</b>
    <p>Two tools from this afternoon, pointed at a new subject. On screen is Salvador's last
    line: a plain probe can match a sparse-autoencoder feature, and patching tests what the
    model actually relies on.</p>
    <p>Those two sentences are the whole toolkit for the next forty minutes. What changes is
    what we point them at &mdash; not a factual completion like &ldquo;Paris&rdquo;, but a
    <i>verdict</i> from a model acting as a judge.</p>
    <p class="cue" data-cue="1">The probe becomes a confidence signal. Not the confidence the
    judge states, but the confidence its hidden state carries. And I want to be careful about
    what that is: it is a learned correlate, not a lie detector. It can be wrong, and before
    the end of the block you will watch it fail.</p>
    <p class="cue" data-cue="2">And Block 2's idea &mdash; intervene, then watch the output
    &mdash; becomes a grounding check: did this verdict rest on the evidence that actually
    matters? Today we intervene on the input text, removing or replacing the evidence, which
    is the simplest form of it. Patching the hidden states of those tokens is the natural next
    step, and we are not doing it today.</p>
""",

"p3-grid": """
    <b>2:11:15 &rarr; 2:12:15.</b> <i>[2 steps.]</i>
    <p>An LLM-assisted audit has two bodies of text. Rules on one axis &mdash; what a standard
    requires. Evidence on the other &mdash; plans, minutes, change logs, commits. The judge
    answers one cell at a time: this rule, against this document, compliant or not.</p>
    <p class="cue" data-cue="1">And it fills every cell. Fast, cheap and tireless. The sizes
    here are illustrative; a real audit is tens of rules against hundreds of documents, so
    thousands of verdicts.</p>
    <p class="cue" data-cue="2">Nobody reviews all of those. Which means the question is not
    &ldquo;is the judge accurate on average&rdquo;. The question is: <i>which verdicts need a
    human?</i></p>
    <p>That reframing is the whole block. Average accuracy is a number you report. A routing
    decision is a number you have to defend.</p>
    <i>[Ask: "how would you decide which cells to check?" Take one or two answers &mdash;
    random sample, the low-confidence ones &mdash; then move.]</i>
""",

"p3-iso": """
    <b>2:12:15 &rarr; 2:13:00.</b>
    <p>A word on where this comes from, because it is context, not content.</p>
    <p>My work is on process audits of very small software teams. ISO/IEC 29110 is the
    lifecycle standard written for exactly those organisations &mdash; up to twenty-five
    people &mdash; covering project management and software implementation. The technical
    report, 29110-3-1, gives the assessment guidelines: you check each expected practice
    against the project's own records. An assessor sits down and reads plans, minutes and
    change logs, rule by rule.</p>
    <p>That is the grid from the previous slide. And a team of eight cannot afford a full-time
    assessor, which is precisely why LLM assistance is attractive here &mdash; and precisely
    why trust is the binding problem.</p>
    <p>I will not quote the standard: its text is licensed. The rule you are about to see is
    invented, written in its style.</p>
""",

"p3-rule": """
    <b>2:13:00 &rarr; 2:13:45.</b> <i>[1 step. Read both boxes aloud, slowly &mdash; the next
    slide depends on the room having actually heard them.]</i>
    <p>One rule, one piece of evidence. Rule R-PM-07, invented, in the style of the standard.
    Every change request is recorded; its impact on schedule and cost is assessed; and the
    customer approves it before work on it starts.</p>
    <p>And the evidence, from the meeting minutes: &ldquo;Twelfth of March status meeting.
    Client asked to add CSV export to the reports module. Dev lead estimates three extra days;
    added to Sprint 4. Action: update the project plan.&rdquo;</p>
    <p class="cue" data-cue="1">Three clauses. Recorded. Schedule <i>and cost</i> assessed.
    Customer approval <i>before</i> work starts. Hold those three in your head.</p>
    <i>[Hands up: compliant, or non-compliant? Let them commit before the reveal.]</i>
""",

"p3-verdict": """
    <b>2:13:45 &rarr; 2:14:45.</b> <i>[2 steps.]</i>
    <p>The judge says compliant. And its reasoning sounds right: the request was recorded, and
    its schedule impact was assessed. It is fluent, it is specific, it cites the evidence. It
    also tells us it is ninety per cent confident.</p>
    <p class="cue" data-cue="1">Here is the human auditor's label. Non-compliant. Clause one
    is met. Clause two is half met &mdash; schedule was assessed, cost was never mentioned.
    And clause three is simply absent: the work went into Sprint 4 with no customer approval
    at all.</p>
    <p class="cue" data-cue="2">So this is the dangerous case. Not a confused verdict, not a
    hedge &mdash; a confident, fluent, wrong verdict. And if our routing policy is &ldquo;send
    the low-confidence ones to a human&rdquo;, using the judge's own ninety per cent, this
    verdict is never reviewed by anybody.</p>
    <p>That is the failure we are going to try to catch.</p>
""",

"p3-probe": """
    <b>2:14:45 &rarr; 2:15:30.</b> <i>[2 steps.]</i>
    <p>So let us ask the judge's hidden state instead of its words.</p>
    <p>The probe is a linear read-out on the judge's residual stream, taken at the answer
    position &mdash; the last prompt token, where the next token is about to be Yes or No.
    That is exactly what notebook five caches. Block 3's tool; what changes is the target. It
    is trained to predict &ldquo;is this verdict correct?&rdquo;</p>
    <p class="cue" data-cue="1">The needle settles at a probability of correctness of about
    0.4. The judge told us 0.9. Our threshold for automatic acceptance here is 0.7, and that
    number is illustrative.</p>
    <p class="cue" data-cue="2">Below threshold, so the case is routed to a human auditor.</p>
    <p>The model's words said ninety per cent. Its hidden state did not. And notice what this
    costs: one forward pass we were already doing, plus a dot product.</p>
""",

"p3-ground": """
    <b>2:15:30 &rarr; 2:16:45.</b> <i>[3 steps.]</i>
    <p>A score tells us to look at this verdict. It does not tell us what is wrong with it.
    For that, intervene &mdash; Block 2's idea, applied to the input text. Change one piece of
    evidence, hold everything else fixed, and watch the verdict.</p>
    <p class="cue" data-cue="1">Remove the sentence with the three-day estimate. The verdict
    flips to non-compliant. So that one sentence was carrying the decision.</p>
    <p class="cue" data-cue="2">Now put it back, and add a new sentence: &ldquo;The customer
    rejected the change.&rdquo; The verdict does not move. Still compliant. A customer
    rejection should make this non-compliant immediately, and the judge does not notice.</p>
    <p class="cue" data-cue="3">Put those together. The schedule estimate <i>is</i> relevant
    evidence &mdash; for clause two. The problem is that the verdict depends on it alone, and
    is completely insensitive to clause three, the approval. An auditor would never accept a
    verdict grounded like that, even if it happened to be right.</p>
    <p>This is a text-level intervention, and it is exactly what step six of the notebook
    does: the excerpt is replaced by irrelevant boilerplate, or one segment is dropped, all
    precomputed so it runs without a GPU. Patching the hidden states of those tokens would
    tell us <i>where</i> the clue is read. That is the next step, and it is not in today's
    notebook.</p>
""",

"p3-why": """
    <b>2:16:45 &rarr; 2:17:30.</b>
    <p>The R-PM-07 story I just told you is invented. This result is not.</p>
    <p>Radharapu and colleagues train linear probes on the hidden states of reasoning judges,
    with a Brier-score loss. Compared against verbalized confidence and against multi-sample
    methods, the probes were better calibrated, at roughly ten times less compute. And in
    their experiments the probes generalised to evaluation domains they had not seen.</p>
    <p>I want to be careful with that last claim, because you may well contradict it in the
    next half hour. In our own test run, on our data, the probe did <i>not</i> transfer to
    rules it had never seen. So take transfer as something you test, not something you
    inherit.</p>
    <p>Their own honest caveat is interesting for us: the probes are conservative, and
    under-confident on easy data. That is a bad property for a leaderboard and a good one for
    an audit, where a missed error costs far more than an unnecessary review.</p>
    <p>And the baseline to keep in view: for a Yes/No judge, the probability it assigns to its
    own answer token is free. Any probe has to beat that, or it is not worth the trouble. The
    line at the bottom, semantic entropy probes, does the same trick for hallucination:
    predict uncertainty from one forward pass instead of many samples.</p>
""",

"p3-a10": """
    <b>2:17:30 &rarr; 2:19:30.</b> <i>[4 steps. Centrepiece. Say "synthetic" in the first
    sentence.]</i>
    <p>This slide is synthetic: three thousand simulated verdicts, with a judge about
    seventy-four per cent accurate. I use it because it shows the shape of the problem
    cleanly, and I want to be explicit that no number on it was measured.</p>
    <p>On the left is a reliability diagram. Stated confidence on the x-axis, how often the
    verdict is actually correct on the y-axis. The diagonal is perfect calibration.</p>
    <p class="cue" data-cue="0">Verbalized confidence piles up between 0.8 and 1.0, while
    accuracy stays near 0.75. Every bar sits well below the diagonal: overconfident,
    systematically.</p>
    <p class="cue" data-cue="1">The probe's bars hug the diagonal. When it says 0.6, it is
    right about sixty per cent of the time.</p>
    <p class="cue" data-cue="2">Now the right-hand chart, which is the one an auditor cares
    about. Auto-accept every verdict whose score is at or above a threshold. Coverage is the
    share you accept automatically; the vertical axis is the error rate among the ones you
    accepted. Set the threshold low and you accept nearly everything &mdash; and every error
    escapes with it.</p>
    <p class="cue" data-cue="3" data-range="3-4">Raise the threshold. Fewer automatic
    acceptances, and far fewer escaped errors. Read the line under the chart: escaped errors
    are verdicts that are wrong <i>and</i> auto-accepted, as a share of all verdicts &mdash;
    the same definition the notebook uses. The dashed line is our routing target: at most ten
    per cent error among auto-accepted verdicts. The probe curve meets it at about
    thirty-eight per cent coverage. Routing by the judge's own words only gets under ten per
    cent at about eight per cent coverage &mdash; which is to say, it barely separates right
    from wrong at all.</p>
    <p>So a calibrated score turns review into a dial. You choose coverage, and you are told
    what it costs you. That dial is what you are about to build in the notebook.</p>
    <i>[The slider is draggable if someone asks "what about 90% coverage?" &mdash; clicks on
    the chart do not advance the slide.]</i>
""",

"p3-conformal": """
    <b>2:19:30 &rarr; 2:20:15.</b> <i>[3 steps.]</i>
    <p>Which raises the obvious question: can we turn that dial into a guarantee? Before I
    start &mdash; this slide is a research direction, my thesis line, LLM-assisted quality and
    security audits of software projects. It is not a published result.</p>
    <p class="cue" data-cue="1">Start with a calibration set that has gold labels. Sixty
    synthetic verdicts, placed along the axis by probe score. Grey means the judge was right,
    red means it was wrong. Most of the red sits at low scores. Not all of it.</p>
    <p class="cue" data-cue="2">Define an escape: a verdict that is wrong <i>and</i>
    auto-accepted. The rule is the one in the notebook's <code>crc_threshold</code>: scan
    thresholds from low to high and take the first one where the empirical escape rate, plus a
    finite-sample correction of one over n plus one, stays under your budget alpha. With sixty
    calibration points that correction already eats 1.6 of a 10-point budget, which is the
    honest price of a small calibration set.</p>
    <p>If new verdicts are exchangeable with the calibration verdicts, the <i>expected</i>
    escape rate on new verdicts is at most alpha &mdash; in expectation over calibration sets,
    not a promise about any single audit. A note for the experts: this bounds escapes over all
    verdicts, not the share of errors that escape. With a seventy-four per cent accurate
    judge, ten per cent of all verdicts can still be a large share of the errors. Choose alpha
    with the auditor, not alone.</p>
    <p class="cue" data-cue="3">And there is the hinge. The guarantee needs exchangeability. A
    new 29110 process area &mdash; or a held-out assertion in the notebook &mdash; is exactly
    where that assumption dies. Which is why what you are about to run is the test, not the
    theorem.</p>
""",

"p3-legal": """
    <b>2:20:15 &rarr; 2:21:00.</b>
    <p>We cannot share real audit records, so the notebook uses a public analogue with the
    same shape.</p>
    <p>LegalBench has fourteen contract-NLI tasks, derived from ContractNLI. Each task is one
    assertion applied to clauses from non-disclosure agreements &mdash; for example, whether a
    clause states that the receiving party may share confidential information with third
    parties. So the mapping is exact: the assertion is my rule, the contract excerpt is my
    evidence, and the verdict is Yes or No.</p>
    <p>And the shift test is built into the data. Eleven assertions are split by document into
    train, calibration and test, so no test contract was seen in training. Then three
    assertions are held out <i>entirely</i> &mdash; notice on compelled disclosure, return of
    confidential information, survival of obligations. No example of those rules anywhere in
    training. They stand in for a new process area appearing in next year's audit.</p>
    <p>The verdict is read straight from the Yes/No logits, which is also where the
    token-probability baseline comes from, and the hidden states at the last prompt token are
    cached &mdash; which is why the notebook runs on a free CPU runtime and nobody needs a
    GPU.</p>
    <p>Which is the notebook Salvador asked you to open when he handed over. Let me check that
    here: everyone with NB5 on screen? Run the first cell while I finish this slide &mdash; a CPU
    runtime is fine, you do not need a GPU and there is nothing to install. If you do not have it,
    it is <b>bit.ly/micai-mi-nb5</b>, and the link is on the hands-on slide in a moment too. If your
    neighbour is not open either, share a laptop; one per pair is plenty.</p>
    <i>[Say the link slowly, twice, and do not leave this slide until most screens show Colab. The
    assistant goes to whoever is stuck. Check before the session which judge the published cache
    actually uses: this row says Gemma 3 4B IT, and the debrief numbers are the Qwen2.5-0.5B
    fallback. Say which one the room is running.]</i>
""",

"p3-predict": """
    <b>2:21:00 &rarr; 2:21:30.</b> <i>[Commitment device. Do not reveal the answer.]</i>
    <p>Before anyone runs anything: commit. Hands up for A, B, C, D &mdash; which signal will
    rank wrong verdicts best?</p>
    <i>[Count each option out loud and write the four numbers on the whiteboard. We come back
    to them in the debrief.]</i>
    <p>Options C and D are the interesting ones: token probability is free, it is already in
    the logits, and a probe that merely ties it has added cost and no information. Now write
    your own prediction in the Predict cell of the notebook, before the first result appears.
    Being wrong here is the point of the exercise.</p>
    <p>If NB5 is not open on your screen yet, open it now &mdash; <b>bit.ly/micai-mi-nb5</b>
    &mdash; or look over at your neighbour's.</p>
""",

"p3-nb5": """
    <b>2:21:30 &rarr; 2:43:30 (22 minutes).</b> <i>[Hands-on. Say the frame, then stop talking
    and circulate.]</i>
    <p>Notebook five, the link on the slide: <b>bit.ly/micai-mi-nb5</b>. Twenty-two minutes, in
    pairs: one person drives, the other reads the cells out loud and predicts before each run.
    One laptop per pair is all you need, a CPU runtime is enough, and it does not matter whether
    you got NB0 working this morning &mdash; this notebook runs on cached activations.</p>
    <p>Six steps. Run the judge on a few pairs, so you have seen it work. Train a probe to
    predict which of its verdicts are wrong. Compare that probe against the two cheap
    baselines &mdash; the verbalized number and the token probability &mdash; on AUROC and on
    calibration error. Pick a routing threshold that holds error among accepted verdicts under
    ten per cent. Then test on the three held-out assertions. And finally, remove the evidence
    behind the most confident verdicts and see whether they move. Steps one to four are core,
    five is the key result, six is the grounding check, and the conformal threshold at the end
    is an optional stretch.</p>
    <p>Three terms, because the results depend on them. AUROC is ranking: the chance that a
    wrong verdict scores lower than a right one, so 0.5 is useless. ECE is the average gap
    between stated confidence and actual accuracy. Brier is the mean squared gap to the actual
    zero-one outcome. And the reason AUROC comes first: recalibration can fix ECE, but it can
    never change ranking.</p>
    <p>One subtlety that catches everybody: the target is &ldquo;is this verdict wrong&rdquo;,
    not &ldquo;is the answer Yes&rdquo;. So the confidence has to be the probability of
    whichever answer the judge actually gave &mdash; the larger of P(Yes) and P(No). Start
    now; we are both here, and ask early rather than late.</p>
    <i>[Circulate with the assistant. Time checks out loud at 2:30 (should be at step 3) and
    2:37 (step 5). If the room is mid-flow, take 2-3 minutes from the debrief, never from the
    wrap-up.]</i>
""",

"p3-debrief": """
    <b>2:43:30 &rarr; 2:48:00.</b> <i>[Five minutes. Their numbers first, mine second.]</i>
    <p>Laptops half-closed. Back to the whiteboard: here is what this room predicted twenty
    minutes ago.</p>
    <i>[Ask two pairs to read out their AUROC and ECE for the three signals. Those are the
    session's real numbers &mdash; use them, not mine.]</i>
    <p>In our own test run, with the small fallback judge, this is what came out. The judge is
    right about seventy-five per cent of the time on test, and sixty-four per cent on the
    held-out assertions. For ranking wrong verdicts: asking the judge how confident it is
    scores 0.43 &mdash; worse than chance, and the reason is almost funny, across the whole
    test split it only ever answered 75, 80, 85 or 95. It has four moods; there is nothing in
    there to rank with. The token probability scores 0.63, and it is free. The probe scores
    0.71.</p>
    <p>So: where did the probe win? Against the judge's words, decisively &mdash; and that is
    a low bar. Against token probability, yes, but only on rules it had been calibrated on,
    and by 0.71 to 0.63. A real margin, and a modest one.</p>
    <p>Where did it fail? On a rule it had never seen. With its calibrated threshold, seventeen
    and a half per cent of verdicts escaped review &mdash; wrong and auto-accepted &mdash;
    against eight per cent for the free baseline. It did not merely degrade; it ended up worse
    than the thing it beat. My reading, and it is a hypothesis, not a measurement: the probe
    may have learned which <i>rules</i> are hard rather than when the judge is uncertain.</p>
    <p>And it failed a second, independent way. Of the forty most confident Yes verdicts,
    seventy per cent stayed Yes when the evidence was replaced by irrelevant boilerplate
    &mdash; and those verdicts were <i>correct</i>. The judge got the right answer without
    reading the evidence. Accuracy cannot see that. A confidence score cannot see that. Only
    the intervention can.</p>
    <p>So what counts as evidence that a verdict is safe to skip? My answer: a calibrated
    score alone is not evidence. A score, plus a stated escape bound, plus a grounding check
    on a sample of accepted verdicts &mdash; that combination starts to look like something an
    assessor could sign, because each one covers a failure the other two cannot see.</p>
""",

"p3-map": """
    <b>2:48:00 &rarr; 2:49:30.</b> <i>[6 steps, one row per advance.]</i>
    <p>Stepping back: the whole afternoon in one table. Pick the method from your question,
    and then pick the validation from the method &mdash; that second half is the part people
    skip.</p>
    <p class="cue" data-cue="1">Is concept X represented? A linear probe. Validate on held-out
    <i>and</i> out-of-distribution splits &mdash; which is exactly the failure you just
    ran.</p>
    <p class="cue" data-cue="2">Which component causes Y? Activation patching. Check the
    effect survives other corruptions, and use path patching to separate direct from indirect
    routes.</p>
    <p class="cue" data-cue="3">Which features does it use? Sparse autoencoders. And the
    validation is blunt: if a plain probe matches it, the SAE added nothing.</p>
    <p class="cue" data-cue="4">How is one prompt computed? An attribution graph &mdash; which
    is a hypothesis until you intervene on the features in it.</p>
    <p class="cue" data-cue="5">Can I control behaviour Z? A steering vector. And test it
    against orthogonal directions, because steering directions turn out not to be
    identifiable: perturbations orthogonal to yours can reach much of the same effect.</p>
    <p class="cue" data-cue="6">Note what is highlighted. Block five used only the first two
    rows &mdash; and the second only in its simplest form, intervening on input text rather
    than on hidden states. The simplest tools did the auditing work. Hidden-state patching is
    the obvious next step, and that is where I am going.</p>
""",

"p3-transfer": """
    <b>2:49:30 &rarr; 2:51:30.</b> <i>[Printed canvas on the tables:
    printables/transfer_canvas.pdf.]</i>
    <p>Two minutes in pairs, and this is the part that transfers out of this room.</p>
    <p>Six boxes. What does the model decide? Who or what gives you the gold label? Where
    would the confidence signal be read from &mdash; which layer, which token? What escape
    rate can you actually tolerate? Which piece of evidence <i>should</i> flip the verdict, so
    you can test grounding? And what is your unseen assertion &mdash; what plays the role of a
    rule the probe has never been calibrated on?</p>
    <p>If you judge anything with a model &mdash; grading, labelling data, reviewing code,
    screening papers, checking claims against sources &mdash; boxes one to three take about
    five minutes. Boxes four to six are where the interesting problems are. Fill one to three
    now, and four to six if you have time.</p>
    <i>[Take one example from the room out loud before moving on.]</i>
""",

"p3-field": """
    <b>2:51:30 &rarr; 2:55:00.</b> <i>[7 steps.]</i>
    <p>Where the field is, in one arc.</p>
    <p class="cue" data-cue="1" data-range="1-5">We observed, with the logit lens. We
    intervened, with patching. We decomposed, with sparse autoencoders. We traced, with
    attribution graphs. And then we audited &mdash; a probe on a judge. Every one of those is
    a tool for turning an internal state into a claim you can test.</p>
    <p class="cue" data-cue="6">The open problems, and these are not mine &mdash; they are the
    field's, from the Open Problems review. Most circuit results explain one prompt, not a
    general mechanism. Attribution graphs explain a replacement model, and how faithful that
    is to the real one is genuinely open. Automating interpretability with agents is just
    starting. And there are no agreed evaluation standards, which is why so many results are
    hard to compare.</p>
    <p class="cue" data-cue="7">And the implications, which is why I work on this. Assurance
    and audits of AI systems &mdash; today's block. Evidence that a regulator could actually
    ask for. And using models as objects of scientific study.</p>
    <p>Let me end the technical part honestly. These tools are young. Most published results
    are on small models or single prompts. The headline result of the block you just ran was
    that my method lost to a free baseline the moment the rule changed. Treat every
    interpretation as a hypothesis with a test attached &mdash; that is the discipline the
    field needs, and it is the one thing from this afternoon I would most like you to keep.</p>
""",

"p3-res": """
    <b>2:55:00 &rarr; 2:56:00.</b> <i>[Do not read the list.]</i>
    <p>Everything we used is open, and this slide is a reference rather than something to read
    out.</p>
    <p>Left column: the tools from the notebooks, and where to learn more. If you want a
    proper course rather than a tutorial, ARENA chapter one is the best free follow-up I
    know.</p>
    <p>Right column: the papers the blocks were built on. The Open Problems review at the
    bottom is the map of what nobody knows yet, and it is the most useful thing on this slide
    if you are looking for a research question. All of these links are in the materials folder
    as well.</p>
""",

"p3-exit": """
    <b>2:56:00 &rarr; 2:58:00.</b>
    <p>Before you close the laptop: an exit ticket. Two questions, two minutes, anonymous. One
    thing you will try in your own research, and one thing that confused you.</p>
    <p>The second question is the one we learn the most from, and it is the reason these
    materials have been rewritten twice already. So if something this afternoon did not land,
    that is the box I want it in.</p>
    <i>[Insert the form link and QR code in the dashed box before the session. Then give them
    the full two minutes in silence.]</i>
""",

"p3-thanks": """
    <b>2:58:00 &rarr; 3:00:00.</b>
    <p>Thank you &mdash; for four hours, and for the predictions you got wrong on purpose.</p>
    <p>This is joint work with Miguel Gonz&aacute;lez and Salvador Hinojosa at Tec de
    Monterrey, and thanks to our student assistant, who kept Colab alive all afternoon.</p>
    <i>[Thank the assistant by name.]</i>
    <p>Slides, all six notebooks and the printables are at the link on screen. The notebooks
    keep working after today, and the fifth one is the one I would start with if you judge
    anything with a model. We will stay for questions &mdash; and the one I am most interested
    in is the shift result: if you think the probe is learning rule difficulty rather than
    uncertainty, I would like to hear how you would separate the two.</p>
    <i>[If someone asks "which tool for my problem", jump back to the method map, p3-map.]</i>
""",

}


# ================================================================== Español
#
# Mismo guion, escrito para decirlo, no traducido palabra por palabra. El
# vocabulario de campo que se dice en inglés se queda en inglés (residual
# stream, probe, patching, logits, token, feature, SAE, prompt, AUROC, ECE,
# Brier); las cifras, citas y rutas se conservan exactas.

ES = {

"p3-section": """
    <b>2:10:00 &rarr; 2:10:15.</b> <i>[El título se dice y se avanza.]</i>
    <p>Bloque cinco. Una sola pregunta: cuando un LLM juzga, ¿de cuáles de sus veredictos nos
    podemos fiar?</p>
""",

"p3-open": """
    <b>2:10:15 &rarr; 2:11:15.</b>
    <p>Dos herramientas de esta tarde, apuntadas a un objeto nuevo. En pantalla está la última
    frase de Salvador: un probe lineal sencillo puede igualar a una feature de sparse
    autoencoder, y el patching prueba de qué depende realmente el modelo.</p>
    <p>Esas dos frases son todo el instrumental de los próximos cuarenta minutos. Lo que cambia
    es a qué las apuntamos: ya no a un completado factual como &ldquo;Paris&rdquo;, sino a un
    <i>veredicto</i> de un modelo que actúa como juez.</p>
    <p class="cue" data-cue="1">El probe se convierte en una señal de confianza. No la
    confianza que el juez <i>dice</i>, sino la que lleva su estado interno. Y quiero ser
    cuidadoso con lo que eso es: es un correlato aprendido, no un detector de mentiras. Puede
    equivocarse, y antes de terminar el bloque lo van a ver fallar.</p>
    <p class="cue" data-cue="2">Y la idea del Bloque 2 &mdash; intervenir y mirar la salida
    &mdash; se convierte en una prueba de fundamento: ¿este veredicto se apoyó en la evidencia
    que de verdad importa? Hoy intervenimos sobre el texto de entrada, quitando o sustituyendo
    la evidencia, que es la forma más simple. Hacer patching de los estados internos de esos
    tokens es el paso natural siguiente, y hoy no lo hacemos.</p>
""",

"p3-grid": """
    <b>2:11:15 &rarr; 2:12:15.</b> <i>[2 pasos.]</i>
    <p>Una auditoría asistida por un LLM tiene dos cuerpos de texto. En un eje, las reglas: lo
    que exige un estándar. En el otro, la evidencia: planes, minutas, bitácoras de cambios,
    commits. El juez responde una celda a la vez: esta regla, contra este documento, ¿cumple o
    no cumple?</p>
    <p class="cue" data-cue="1">Y llena todas las celdas. Rápido, barato e incansable. Los
    tamaños de aquí son ilustrativos; una auditoría real son decenas de reglas contra cientos
    de documentos, o sea miles de veredictos.</p>
    <p class="cue" data-cue="2">Nadie revisa todos esos. Lo que significa que la pregunta no es
    &ldquo;¿el juez es exacto en promedio?&rdquo;. La pregunta es: <i>¿cuáles veredictos
    necesitan una persona?</i></p>
    <p>Ese cambio de pregunta es todo el bloque. La exactitud promedio es un número que
    reportas. Una decisión de ruteo es un número que tienes que defender.</p>
    <i>[Pregunta: "¿cómo decidirían ustedes qué celdas revisar?". Toma una o dos respuestas
    &mdash; muestra aleatoria, las de baja confianza &mdash; y avanza.]</i>
""",

"p3-iso": """
    <b>2:12:15 &rarr; 2:13:00.</b>
    <p>Dos palabras sobre de dónde sale esto, porque es contexto, no contenido.</p>
    <p>Mi trabajo es sobre auditorías de proceso en equipos de software muy pequeños. ISO/IEC
    29110 es el estándar de ciclo de vida escrito justamente para esas organizaciones &mdash;
    hasta veinticinco personas &mdash; y cubre gestión de proyecto e implementación de
    software. Y el reporte técnico, 29110-3-1, da las guías de evaluación: se revisa cada
    práctica esperada contra los registros del propio proyecto. Un evaluador se sienta y lee
    planes, minutas y bitácoras, regla por regla.</p>
    <p>Eso es la rejilla de la slide anterior. Y un equipo de ocho personas no puede pagar un
    evaluador de tiempo completo, que es exactamente por lo que la asistencia con LLMs es
    atractiva aquí &mdash; y exactamente por lo que la confianza es el problema que amarra
    todo.</p>
    <p>No voy a citar el estándar: su texto tiene licencia. La regla que van a ver es
    inventada, escrita en su estilo.</p>
""",

"p3-rule": """
    <b>2:13:00 &rarr; 2:13:45.</b> <i>[1 paso. Lee las dos cajas en voz alta, despacio: la
    siguiente slide depende de que la sala las haya oído de verdad.]</i>
    <p>Una regla y una pieza de evidencia. Regla R-PM-07, inventada, en el estilo del estándar.
    Toda solicitud de cambio se registra; se evalúa su impacto en calendario y en costo; y el
    cliente la aprueba antes de empezar el trabajo.</p>
    <p>Y la evidencia, de la minuta: &ldquo;Reunión de estatus del 12 de marzo. El cliente pidió
    agregar exportación a CSV en el módulo de reportes. El líder de desarrollo estima tres días
    extra; se agrega al Sprint 4. Acción: actualizar el plan de proyecto.&rdquo;</p>
    <p class="cue" data-cue="1">Tres cláusulas. Registrada. Calendario <i>y costo</i>
    evaluados. Aprobación del cliente <i>antes</i> de empezar. Quédense con esas tres.</p>
    <i>[Manos arriba: ¿cumple o no cumple? Que se comprometan antes de revelar.]</i>
""",

"p3-verdict": """
    <b>2:13:45 &rarr; 2:14:45.</b> <i>[2 pasos.]</i>
    <p>El juez dice que cumple. Y su razonamiento suena bien: la solicitud quedó registrada y
    se evaluó su impacto en el calendario. Es fluido, es específico y cita la evidencia.
    También nos dice que tiene noventa por ciento de confianza.</p>
    <p class="cue" data-cue="1">Aquí está la etiqueta del auditor humano. No cumple. La
    cláusula uno sí se cumple. La dos se cumple a medias: se evaluó el calendario, el costo
    nunca se mencionó. Y la tres simplemente no está: el trabajo se metió al Sprint 4 sin
    ninguna aprobación del cliente.</p>
    <p class="cue" data-cue="2">Este es el caso peligroso. No un veredicto confundido, ni uno
    que titubea: un veredicto confiado, fluido y equivocado. Y si nuestra política de ruteo es
    &ldquo;manda a revisión humana los de baja confianza&rdquo;, usando ese noventa por ciento
    que el juez se puso solo, este veredicto no lo revisa nadie, nunca.</p>
    <p>Ese es el fallo que vamos a intentar atrapar.</p>
""",

"p3-probe": """
    <b>2:14:45 &rarr; 2:15:30.</b> <i>[2 pasos.]</i>
    <p>Entonces preguntémosle al estado interno del juez en lugar de a sus palabras.</p>
    <p>El probe es una lectura lineal sobre el residual stream del juez, tomada en la posición
    de la respuesta: el último token del prompt, donde el siguiente token va a ser Yes o No. Eso
    es justo lo que cachea el notebook cinco. Es la herramienta del Bloque 3; lo que cambia es
    el objetivo: se entrena para predecir &ldquo;¿este veredicto es correcto?&rdquo;.</p>
    <p class="cue" data-cue="1">La aguja se queda en una probabilidad de ser correcto de
    alrededor de 0.4. El juez nos dijo 0.9. Nuestro umbral de aceptación automática aquí es
    0.7, y ese número es ilustrativo.</p>
    <p class="cue" data-cue="2">Está por debajo del umbral, así que el caso se rutea a un
    auditor humano.</p>
    <p>Las palabras del modelo decían noventa por ciento. Su estado interno, no. Y fíjense en
    lo que cuesta esto: un forward pass que ya estábamos haciendo, más un producto punto.</p>
""",

"p3-ground": """
    <b>2:15:30 &rarr; 2:16:45.</b> <i>[3 pasos.]</i>
    <p>Un score nos dice que miremos este veredicto. No nos dice qué tiene de malo. Para eso,
    intervenir &mdash; la idea del Bloque 2, aplicada al texto de entrada. Cambias una pieza de
    evidencia, dejas todo lo demás fijo, y miras el veredicto.</p>
    <p class="cue" data-cue="1">Quitamos la frase de los tres días de estimación. El veredicto
    se voltea a &ldquo;no cumple&rdquo;. Entonces esa sola frase cargaba con la decisión.</p>
    <p class="cue" data-cue="2">Ahora la regresamos y agregamos una frase nueva: &ldquo;El
    cliente rechazó el cambio.&rdquo; El veredicto no se mueve. Sigue diciendo que cumple. Un
    rechazo del cliente debería volverlo &ldquo;no cumple&rdquo; de inmediato, y el juez no se
    da cuenta.</p>
    <p class="cue" data-cue="3">Juntemos las dos cosas. La estimación de calendario <i>sí</i>
    es evidencia relevante, para la cláusula dos. El problema es que el veredicto depende solo
    de ella y es completamente insensible a la cláusula tres, la aprobación. Un auditor nunca
    aceptaría un veredicto fundamentado así, incluso si de casualidad fuera el correcto.</p>
    <p>Esta es una intervención a nivel de texto, y es exactamente lo que hace el paso seis del
    notebook: se sustituye el extracto por texto irrelevante, o se elimina un segmento, todo
    precalculado para que corra sin GPU. Hacer patching de los estados internos de esos tokens
    nos diría <i>dónde</i> se lee la pista. Ese es el paso siguiente, y no está en el notebook
    de hoy.</p>
""",

"p3-why": """
    <b>2:16:45 &rarr; 2:17:30.</b>
    <p>La historia de R-PM-07 que acabo de contarles es inventada. Este resultado no.</p>
    <p>Radharapu y colegas entrenan probes lineales sobre los estados internos de jueces de
    razonamiento, con una pérdida de Brier. Comparados contra la confianza verbalizada y contra
    métodos de muestreo múltiple, los probes quedaron mejor calibrados, con aproximadamente
    diez veces menos cómputo. Y en sus experimentos generalizaron a dominios de evaluación que
    no habían visto.</p>
    <p>Quiero tener cuidado con esa última afirmación, porque es muy posible que ustedes la
    contradigan en la siguiente media hora. En nuestra propia prueba, con nuestros datos, el
    probe <i>no</i> transfirió a reglas que nunca había visto. Así que traten la transferencia
    como algo que se prueba, no como algo que se hereda.</p>
    <p>Su propia advertencia honesta nos sirve: los probes son conservadores, y se quedan
    cortos de confianza en datos fáciles. Esa es una mala propiedad para un leaderboard y una
    buena para una auditoría, donde un error que se escapa cuesta mucho más que una revisión
    innecesaria.</p>
    <p>Y la línea base que hay que tener presente: para un juez de Yes/No, la probabilidad que
    le asigna a su propio token de respuesta es gratis. Cualquier probe tiene que ganarle, o no
    vale la molestia. La referencia de abajo, los semantic entropy probes, hace el mismo truco
    para alucinación: predecir incertidumbre con un solo forward pass en lugar de muchas
    muestras.</p>
""",

"p3-a10": """
    <b>2:17:30 &rarr; 2:19:30.</b> <i>[4 pasos. Pieza central. Di "sintético" en la primera
    frase.]</i>
    <p>Esta slide es sintética: tres mil veredictos simulados, con un juez de alrededor del
    setenta y cuatro por ciento de exactitud. La uso porque muestra la forma del problema con
    claridad, y quiero ser explícito en que ningún número de aquí fue medido.</p>
    <p>A la izquierda, un diagrama de confiabilidad. En el eje x, la confianza declarada; en el
    eje y, qué tan seguido el veredicto resulta correcto. La diagonal es calibración
    perfecta.</p>
    <p class="cue" data-cue="0">La confianza verbalizada se acumula entre 0.8 y 1.0, mientras
    la exactitud se queda cerca de 0.75. Todas las barras quedan muy por debajo de la diagonal:
    exceso de confianza, de forma sistemática.</p>
    <p class="cue" data-cue="1">Las barras del probe se pegan a la diagonal. Cuando dice 0.6,
    acierta alrededor del sesenta por ciento de las veces.</p>
    <p class="cue" data-cue="2">Ahora la gráfica de la derecha, que es la que le importa a un
    auditor. Aceptamos automáticamente todo veredicto cuyo score esté en el umbral o arriba. La
    cobertura es la fracción que aceptas automáticamente; el eje vertical es la tasa de error
    entre los que aceptaste. Pon el umbral bajo y aceptas casi todo &mdash; y con eso se escapa
    cada error.</p>
    <p class="cue" data-cue="3" data-range="3-4">Sube el umbral. Menos aceptaciones
    automáticas, y muchísimos menos errores escapados. Lean la línea debajo de la gráfica: los
    errores escapados son veredictos equivocados <i>y</i> aceptados automáticamente, como
    fracción de todos los veredictos &mdash; la misma definición que usa el notebook. La línea
    punteada es nuestro objetivo de ruteo: a lo más diez por ciento de error entre los
    veredictos aceptados automáticamente. La curva del probe lo alcanza alrededor del treinta y
    ocho por ciento de cobertura. Rutear con las palabras del propio juez baja del diez por
    ciento apenas con un ocho por ciento de cobertura, lo cual quiere decir que casi no separa
    lo correcto de lo incorrecto.</p>
    <p>Así que un score calibrado convierte la revisión en una perilla. Tú eliges la cobertura,
    y el método te dice lo que cuesta. Esa perilla es la que van a construir en el notebook.</p>
    <i>[El slider se arrastra con el mouse si alguien pregunta "¿y con 90% de cobertura?";
    hacer clic en la gráfica no avanza la slide.]</i>
""",

"p3-conformal": """
    <b>2:19:30 &rarr; 2:20:15.</b> <i>[3 pasos.]</i>
    <p>Lo que levanta la pregunta obvia: ¿podemos convertir esa perilla en una garantía? Antes
    de empezar: esta slide es una dirección de investigación, mi línea de tesis &mdash;
    auditorías de calidad y seguridad de proyectos de software asistidas por LLMs &mdash; y no
    un resultado publicado.</p>
    <p class="cue" data-cue="1">Empezamos con un conjunto de calibración con etiquetas de
    referencia. Sesenta veredictos sintéticos, colocados en el eje por score del probe. Gris
    significa que el juez tuvo razón; rojo, que se equivocó. Casi todo el rojo está en scores
    bajos. No todo.</p>
    <p class="cue" data-cue="2">Definimos un escape: un veredicto equivocado <i>y</i> aceptado
    automáticamente. La regla es la del <code>crc_threshold</code> del notebook: se barren los
    umbrales de abajo hacia arriba y se toma el primero donde la tasa empírica de escapes, más
    una corrección de muestra finita de uno sobre n más uno, se queda por debajo de tu
    presupuesto alpha. Con sesenta puntos de calibración esa corrección ya se come 1.6 de un
    presupuesto de 10 puntos, que es el precio honesto de un conjunto de calibración
    pequeño.</p>
    <p>Si los veredictos nuevos son intercambiables con los de calibración, la tasa
    <i>esperada</i> de escapes en los nuevos es a lo más alpha &mdash; en expectativa sobre
    conjuntos de calibración, no una promesa sobre ninguna auditoría en particular. Y una nota
    para quien conozca el tema: esto acota los escapes sobre todos los veredictos, no la
    fracción de errores que se escapan. Con un juez de setenta y cuatro por ciento de exactitud,
    diez por ciento de todos los veredictos puede seguir siendo una fracción grande de los
    errores. Alpha se elige con el auditor, no solo.</p>
    <p class="cue" data-cue="3">Y ahí está la bisagra. La garantía necesita intercambiabilidad.
    Un área de proceso nueva de 29110 &mdash; o una aserción held-out en el notebook &mdash; es
    exactamente donde ese supuesto se muere. Por eso lo que van a correr ahora es la prueba, no
    el teorema.</p>
""",

"p3-legal": """
    <b>2:20:15 &rarr; 2:21:00.</b>
    <p>No podemos compartir registros de auditoría reales, así que el notebook usa un análogo
    público con la misma forma.</p>
    <p>LegalBench tiene catorce tareas de contract-NLI, derivadas de ContractNLI. Cada tarea es
    una aserción aplicada a cláusulas de acuerdos de confidencialidad &mdash; por ejemplo, si
    una cláusula establece que la parte receptora puede compartir información confidencial con
    terceros. El mapeo es exacto: la aserción es mi regla, el extracto del contrato es mi
    evidencia, y el veredicto es Yes o No.</p>
    <p>Y la prueba de cambio de distribución viene incluida en los datos. Once aserciones se
    parten por documento en train, calibración y test, de modo que ningún contrato de test se
    vio en entrenamiento. Y luego tres aserciones se dejan fuera <i>por completo</i> &mdash;
    aviso sobre divulgación obligada, devolución de información confidencial y supervivencia de
    obligaciones. Ningún ejemplo de esas reglas en ninguna parte del entrenamiento. Esas tres
    hacen el papel de un área de proceso nueva que aparece en la auditoría del año que
    entra.</p>
    <p>El veredicto se lee directo de los logits de Yes/No, que es también de donde sale la
    línea base de probabilidad del token, y los estados internos en el último token del prompt
    están cacheados &mdash; por eso el notebook corre en un runtime de CPU gratuito y nadie
    necesita GPU.</p>
    <p>Que es el notebook que Salvador les pidió abrir cuando me pasó el micrófono. Déjenme
    confirmarlo aquí: ¿todos con NB5 en pantalla? Corran la primera celda mientras termino esta
    slide: con un runtime de CPU basta, no necesitan GPU y no hay nada que instalar. Si no lo
    tienen, es <b>bit.ly/micai-mi-nb5</b>, y el enlace también aparece en la slide del trabajo en
    un momento. Si quien está a su lado tampoco lo tiene, compartan laptop: con una por pareja
    sobra.</p>
    <i>[Di el enlace despacio, dos veces, y no dejes esta slide hasta que la mayoría de las
    pantallas muestren Colab. El asistente va con quien se atore. Verifica antes de la sesión qué
    juez usa de verdad la caché publicada: esta fila dice Gemma 3 4B IT, y los números del debrief
    son del fallback Qwen2.5-0.5B. Di cuál está corriendo la sala.]</i>
""",

"p3-predict": """
    <b>2:21:00 &rarr; 2:21:30.</b> <i>[Compromiso previo. No reveles la respuesta.]</i>
    <p>Antes de que nadie corra nada: comprométanse. Manos arriba por A, B, C y D: ¿qué señal
    va a ordenar mejor los veredictos equivocados?</p>
    <i>[Cuenta cada opción en voz alta y escribe los cuatro números en el pizarrón. Volvemos a
    ellos en el debrief.]</i>
    <p>Las opciones C y D son las interesantes: la probabilidad del token es gratis, ya está en
    los logits, y un probe que apenas la empata agregó costo y ninguna información. Ahora
    escriban su propia predicción en la celda Predict del notebook, antes de que aparezca el
    primer resultado. Equivocarse aquí es justamente el punto del ejercicio.</p>
    <p>Si todavía no tienen NB5 abierto en la pantalla, ábranlo ahora
    &mdash; <b>bit.ly/micai-mi-nb5</b> &mdash; o asómense a la laptop de al lado.</p>
""",

"p3-nb5": """
    <b>2:21:30 &rarr; 2:43:30 (22 minutos).</b> <i>[Manos a la obra. Di el encuadre, luego deja
    de hablar y circula.]</i>
    <p>Notebook cinco, el enlace está en la slide: <b>bit.ly/micai-mi-nb5</b>. Veintidós
    minutos, en parejas: uno maneja el teclado y el otro lee las celdas en voz alta y predice
    antes de cada corrida. Con una laptop por pareja basta, con runtime de CPU alcanza, y da
    igual si en la mañana NB0 no les funcionó: este notebook corre sobre activaciones
    cacheadas.</p>
    <p>Seis pasos. Correr el juez en unos cuantos pares, para haberlo visto funcionar. Entrenar
    un probe que prediga cuáles de sus veredictos están mal. Comparar ese probe contra las dos
    líneas base baratas &mdash; el número verbalizado y la probabilidad del token &mdash; en
    AUROC y en error de calibración. Elegir un umbral de ruteo que mantenga el error entre los
    aceptados por debajo del diez por ciento. Luego probar en las tres aserciones held-out. Y
    al final, quitar la evidencia detrás de los veredictos más confiados y ver si se mueven.
    Los pasos uno a cuatro son el núcleo, el cinco es el resultado clave, el seis es la prueba
    de fundamento, y el umbral conformal del final es opcional.</p>
    <p>Tres términos, porque los resultados dependen de ellos. AUROC es ordenamiento: la
    probabilidad de que un veredicto equivocado reciba un score más bajo que uno correcto, así
    que 0.5 no sirve de nada. ECE es la brecha promedio entre la confianza declarada y la
    exactitud real. Brier es la brecha cuadrática media contra el resultado real de cero o uno.
    Y la razón por la que AUROC va primero: recalibrar puede arreglar el ECE, pero nunca puede
    cambiar el ordenamiento.</p>
    <p>Un detalle que se le pasa a todo el mundo: el objetivo es &ldquo;¿este veredicto está
    mal?&rdquo;, no &ldquo;¿la respuesta es Yes?&rdquo;. Así que la confianza tiene que ser la
    probabilidad de la respuesta que el juez de hecho dio: el máximo entre P(Yes) y P(No).
    Arranquen; aquí andamos los dos, y mejor pregunten temprano que tarde.</p>
    <i>[Circula con el asistente. Avisos de tiempo en voz alta a las 2:30 (deberían ir en el
    paso 3) y a las 2:37 (paso 5). Si la sala va a medio flujo, toma 2-3 minutos del debrief,
    nunca del cierre.]</i>
""",

"p3-debrief": """
    <b>2:43:30 &rarr; 2:48:00.</b> <i>[Cinco minutos. Primero sus números, luego los míos.]</i>
    <p>Laptops a medio cerrar. De vuelta al pizarrón: esto es lo que predijo esta sala hace
    veinte minutos.</p>
    <i>[Pide a dos parejas que lean en voz alta su AUROC y su ECE para las tres señales. Esos
    son los números reales de la sesión: usa esos, no los míos.]</i>
    <p>En nuestra propia prueba, con el juez pequeño de respaldo, esto es lo que salió. El juez
    acierta alrededor del setenta y cinco por ciento en test, y sesenta y cuatro por ciento en
    las aserciones held-out. Para ordenar los veredictos equivocados: preguntarle al juez qué
    tan confiado está da 0.43 &mdash; peor que el azar, y la razón es casi chistosa: en todo el
    split de test solo contestó 75, 80, 85 o 95. Tiene cuatro estados de ánimo; ahí no hay nada
    con qué ordenar. La probabilidad del token da 0.63, y es gratis. El probe da 0.71.</p>
    <p>Entonces, ¿dónde ganó el probe? Contra las palabras del juez, de forma contundente
    &mdash; y es una vara baja. Contra la probabilidad del token, sí, pero solo en reglas en las
    que había sido calibrado, y por 0.71 contra 0.63. Un margen real, y modesto.</p>
    <p>¿Dónde falló? En una regla que nunca había visto. Con el umbral que había calibrado, se
    escapó de revisión el diecisiete y medio por ciento de los veredictos &mdash; equivocados y
    aceptados automáticamente &mdash; contra ocho por ciento de la línea base gratis. No es que
    solo se degradara: terminó <i>peor que aquello a lo que le había ganado</i>. Mi lectura, y
    es una hipótesis, no una medición: puede que el probe haya aprendido cuáles <i>reglas</i>
    son difíciles, en lugar de cuándo el juez está incierto.</p>
    <p>Y falló de una segunda forma, independiente. De los cuarenta veredictos Yes más
    confiados, el setenta por ciento siguió diciendo Yes cuando la evidencia se sustituyó por
    texto irrelevante &mdash; y esos veredictos eran <i>correctos</i>. El juez dio la respuesta
    correcta sin leer la evidencia. La exactitud no puede ver eso. Un score de confianza no
    puede ver eso. Solo la intervención.</p>
    <p>Entonces, ¿qué cuenta como evidencia de que un veredicto se puede saltar sin revisión?
    Mi respuesta: un score calibrado, solo, no es evidencia. Un score, más una cota declarada
    de escapes, más una prueba de fundamento sobre una muestra de los aceptados: esa
    combinación empieza a parecerse a algo que un evaluador podría firmar, porque cada una cubre
    un fallo que las otras dos no pueden ver.</p>
""",

"p3-map": """
    <b>2:48:00 &rarr; 2:49:30.</b> <i>[6 pasos, una fila por avance.]</i>
    <p>Un paso atrás: toda la tarde en una tabla. Elige el método desde tu pregunta, y luego
    elige la validación desde el método &mdash; esa segunda mitad es la parte que la gente se
    salta.</p>
    <p class="cue" data-cue="1">¿Está representado el concepto X? Un probe lineal. Valídalo en
    splits held-out <i>y</i> fuera de distribución, que es exactamente el fallo que acaban de
    correr.</p>
    <p class="cue" data-cue="2">¿Qué componente causa Y? Activation patching. Revisa que el
    efecto sobreviva a otras corrupciones, y usa path patching para separar rutas directas de
    indirectas.</p>
    <p class="cue" data-cue="3">¿Qué features usa? Sparse autoencoders. Y la validación es
    brutal: si un probe sencillo lo iguala, el SAE no agregó nada.</p>
    <p class="cue" data-cue="4">¿Cómo se computa un prompt concreto? Un attribution graph, que
    es una hipótesis hasta que intervienes sobre las features que tiene.</p>
    <p class="cue" data-cue="5">¿Puedo controlar el comportamiento Z? Un vector de steering. Y
    pruébalo contra direcciones ortogonales, porque resulta que las direcciones de steering no
    son identificables: perturbaciones ortogonales a la tuya pueden lograr buena parte del mismo
    efecto.</p>
    <p class="cue" data-cue="6">Fíjense en lo resaltado. El bloque cinco usó solo las dos
    primeras filas &mdash; y la segunda solo en su forma más simple, interviniendo sobre el
    texto de entrada y no sobre los estados internos. Las herramientas más simples hicieron el
    trabajo de auditoría. El patching de estados internos es el paso siguiente obvio, y es hacia
    allá donde voy.</p>
""",

"p3-transfer": """
    <b>2:49:30 &rarr; 2:51:30.</b> <i>[El canvas impreso está en las mesas:
    printables/transfer_canvas.pdf.]</i>
    <p>Dos minutos en parejas, y esta es la parte que se lleva fuera de este salón.</p>
    <p>Seis casillas. ¿Qué decide el modelo? ¿Quién o qué te da la etiqueta de referencia?
    ¿De dónde se leería la señal de confianza &mdash; qué capa, qué token? ¿Qué tasa de escapes
    pueden tolerar de verdad? ¿Qué pieza de evidencia <i>debería</i> voltear el veredicto, para
    poder probar el fundamento? Y ¿cuál es su aserción no vista &mdash; qué hace el papel de una
    regla en la que el probe nunca fue calibrado?</p>
    <p>Si ustedes juzgan cualquier cosa con un modelo &mdash; calificar, etiquetar datos,
    revisar código, filtrar artículos, verificar afirmaciones contra fuentes &mdash; las
    casillas uno a tres toman unos cinco minutos. Las casillas cuatro a seis son donde están los
    problemas interesantes. Llenen uno a tres ahora, y cuatro a seis si les da el tiempo.</p>
    <i>[Toma un ejemplo de la sala en voz alta antes de avanzar.]</i>
""",

"p3-field": """
    <b>2:51:30 &rarr; 2:55:00.</b> <i>[7 pasos.]</i>
    <p>Dónde está el campo, en un solo arco.</p>
    <p class="cue" data-cue="1" data-range="1-5">Observamos, con el logit lens.
    Intervenimos, con patching. Descompusimos, con sparse autoencoders. Trazamos, con
    attribution graphs. Y luego auditamos: un probe sobre un juez. Cada una de esas es una
    herramienta para convertir un estado interno en una afirmación que se puede poner a
    prueba.</p>
    <p class="cue" data-cue="6">Los problemas abiertos, y no son míos: son del campo, del
    review de Open Problems. La mayoría de los resultados de circuitos explican un prompt, no un
    mecanismo general. Los attribution graphs explican un modelo de reemplazo, y qué tan fiel es
    eso al modelo real está genuinamente abierto. Automatizar interpretabilidad con agentes
    apenas empieza. Y no hay estándares de evaluación acordados, que es la razón por la que
    tantos resultados son difíciles de comparar.</p>
    <p class="cue" data-cue="7">Y las implicaciones, que son la razón por la que trabajo en
    esto. Aseguramiento y auditoría de sistemas de IA &mdash; el bloque de hoy. Evidencia que un
    regulador pudiera de verdad pedir. Y usar los modelos como objetos de estudio
    científico.</p>
    <p>Déjenme cerrar la parte técnica con honestidad. Estas herramientas son jóvenes. La
    mayoría de los resultados publicados son sobre modelos pequeños o prompts individuales. El
    resultado principal del bloque que acaban de correr fue que mi método perdió contra una
    línea base gratis en el momento en que cambió la regla. Traten cada interpretación como una
    hipótesis con una prueba pegada: esa es la disciplina que el campo necesita, y es lo único
    de esta tarde que más me gustaría que se llevaran.</p>
""",

"p3-res": """
    <b>2:55:00 &rarr; 2:56:00.</b> <i>[No leas la lista.]</i>
    <p>Todo lo que usamos es abierto, y esta slide es una referencia, no algo para leer en voz
    alta.</p>
    <p>Columna izquierda: las herramientas de los notebooks y dónde aprender más. Si quieren un
    curso de verdad y no un tutorial, el capítulo uno de ARENA es el mejor seguimiento gratuito
    que conozco.</p>
    <p>Columna derecha: los artículos sobre los que se construyeron los bloques. El review de
    Open Problems, abajo, es el mapa de lo que todavía nadie sabe, y es lo más útil de esta
    slide si andan buscando una pregunta de investigación. Todos estos enlaces están también en
    la carpeta de materiales.</p>
""",

"p3-exit": """
    <b>2:56:00 &rarr; 2:58:00.</b>
    <p>Antes de cerrar la laptop: un boleto de salida. Dos preguntas, dos minutos, anónimo. Una
    cosa que vayan a intentar en su propia investigación, y una cosa que les haya confundido.</p>
    <p>La segunda pregunta es la que más nos enseña, y es la razón por la que estos materiales
    ya se reescribieron dos veces. Así que si algo de esta tarde no aterrizó, esa es la casilla
    donde lo quiero.</p>
    <i>[Inserta el enlace del formulario y el QR en la caja punteada antes de la sesión. Luego
    dales los dos minutos completos en silencio.]</i>
""",

"p3-thanks": """
    <b>2:58:00 &rarr; 3:00:00.</b>
    <p>Gracias &mdash; por cuatro horas, y por las predicciones que fallaron a propósito.</p>
    <p>Esto es trabajo conjunto con Miguel González y Salvador Hinojosa, del Tec de Monterrey,
    y gracias a nuestro asistente, que mantuvo Colab con vida toda la tarde.</p>
    <i>[Agradece al asistente por su nombre.]</i>
    <p>Las slides, los seis notebooks y los imprimibles están en el enlace de la pantalla. Los
    notebooks siguen funcionando después de hoy, y el quinto es por donde yo empezaría si
    ustedes juzgan cualquier cosa con un modelo. Nos quedamos para preguntas &mdash; y la que
    más me interesa es el resultado del cambio de distribución: si creen que el probe está
    aprendiendo la dificultad de la regla en lugar de la incertidumbre del modelo, me gustaría
    oír cómo separarían las dos cosas.</p>
    <i>[Si alguien pregunta "¿qué herramienta para mi problema?", regresa al mapa de métodos,
    p3-map.]</i>
""",

}
