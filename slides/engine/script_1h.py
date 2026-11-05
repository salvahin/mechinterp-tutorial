#!/usr/bin/env python3
"""Speaker script for the one-hour solo run, injected by build_1h.py.

SCRIPT maps slide id -> the HTML that becomes that slide's <aside class="notes">.
Press N during the deck to open the panel; T starts the clock.

Conventions
-----------
  <b>0:00 -> 0:45</b>   running time from the start of the hour, not the tutorial
  -> Step n               advance the slide here (matches the slide's data-steps)
  <i>[ ... ]</i>          stage direction, not meant to be read aloud

The text is written to be read out loud at roughly 130 words a minute. Every
figure quoted is either on the slide or recorded in the four-hour deck's own
notes; the Block 5 numbers come from the test run in p3-debrief, which is the
Qwen2.5-0.5B fallback judge and is always introduced as "in our test run".

PATCHES are the few literal edits the four-hour slides need to make sense in a
solo hour: the block's own clock, and the two places that promise hands-on work.
"""

PATCHES = {
    # The other four primer slides are not in this run, so "2 / 5" counts a
    # sequence the audience never sees.
    "p1-pr-direction": [
        ('<p class="kicker">Primer · 2 / 5 · directions and dot products</p>',
         '<p class="kicker">Primer · directions and dot products</p>'),
    ],
    "p3-section": [
        ('<p class="kicker">2:10 – 2:50 · Víctor Terrón-Macías</p>',
         '<p class="kicker">0:09 – 0:50 · Víctor Terrón-Macías</p>'),
    ],
    # p3-nb5 is left exactly as it is: it describes the tutorial's hands-on block
    # truthfully, and the script says in its first line that today it is a walkthrough.
    # (Lengthening the "22 minutes, in pairs" card pushed the glossary off the stage.)
    "p3-transfer": [
        ('<p class="small">2 minutes in pairs · printed transfer canvas on your table</p>',
         '<p class="small">Two minutes in pairs in the tutorial · the transfer canvas is a '
         'printable in the repository</p>'),
    ],
}


SCRIPT = {

# ============================================================ PART A: 0:00-13:00

"p1-title": """
    <b>0:00 &rarr; 0:45.</b>
    <p>Good morning, and thank you for the hour.</p>
    <p>What you have on screen is the title slide of a four-hour hands-on tutorial that
    Miguel, Salvador and I are running at MICAI in November. Today I am presenting it
    alone, in sixty minutes. So I am going to do something slightly unusual with the
    beginning: I will run the first four blocks at speed, in about nine minutes, and then
    give the rest of the hour to the fifth block, which is the one I work on.</p>
    <p>That fifth block asks a single question. When a language model acts as a judge,
    which of its verdicts can you trust?</p>
""",

"h-roadmap": """
    <b>0:45 &rarr; 1:50.</b>
    <p>Here is the shape of the hour.</p>
    <p>The first nine minutes are a speed-run of blocks one to four. In the full tutorial
    each of those blocks comes with a Colab notebook and the room spends ten to fifteen
    minutes running it. Today nobody runs anything, and I am not going to pretend to
    cover four blocks properly in nine minutes either. I am going to give you three
    ideas, and only the three that block five actually stands on: a direction inside the
    model can carry a meaning; there is one stream where you can read it; and the way you
    test whether the model <i>uses</i> it is to intervene and watch what changes.</p>
    <p>Then at nine minutes we arrive at block five, audit, and it gets the remaining
    forty. That includes the results of the fifth notebook, which I will walk you through
    rather than ask you to run.</p>
    <p>Everything is open. The link is on the last slide, and the notebooks are the part
    you take home.</p>
""",

"p1-hook": """
    <b>1:50 &rarr; 3:00.</b> <i>[2 steps.]</i>
    <p>The reason any of this field exists is on this slide.</p>
    <p class="cue" data-cue="0">This is how we normally evaluate a model. A prompt goes in,
    an answer comes out, and we score the answer. Benchmarks, red-teaming, evaluations:
    all of it is behavioural. We see what the model did. We never see how.</p>
    <p class="cue" data-cue="1">But the box is not magic. It is a computation, and we can
    record every intermediate value it produces.</p>
    <p class="cue" data-cue="2">And when you look at those values, some internal directions
    behave like concepts &mdash; a direction that is active when the text is about Paris
    landmarks. The label in the figure is illustrative.</p>
    <p>One sentence for why that matters: in 2024 Anthropic turned a single internal
    feature up inside Claude, and it brought up the Golden Gate Bridge in every answer it
    gave. You can change behaviour by editing one internal variable &mdash; and that only
    works if the variable means something.</p>
    <i>[The four-hour version has a 90-second live Neuronpedia steering demo here.
    Skip it: no time, and no Wi-Fi risk.]</i>
""",

"p1-pr-direction": """
    <b>3:00 &rarr; 4:15.</b> <i>[3 steps. This is the slide block 5 depends on &mdash;
    do not rush it.]</i>
    <p>Everything drawn here is illustrative: two of seven hundred and sixty-eight
    dimensions, invented numbers, and &ldquo;French-ness&rdquo; is a teaching label, not a
    measured feature. The operation, though, is real, and it is the only piece of
    mathematics in my talk.</p>
    <p class="cue" data-cue="0">An activation is a list of numbers. Geometrically, it is an
    arrow.</p>
    <p class="cue" data-cue="1">Pick a direction &mdash; another arrow, of length one.</p>
    <p class="cue" data-cue="2">The dot product of the two is the length of the shadow the
    activation casts on that direction. How much of this direction is in this activation.
    That is the whole move.</p>
    <p>Now look at the panel on the right, because that is the entire tutorial in one
    list. The logit lens takes the dot product with a token's vector. A probe takes it
    with a learned weight vector. A sparse-autoencoder feature takes it with an encoder
    direction. And steering runs the operation backwards: it writes along a direction
    instead of reading one.</p>
    <p>Remember the second row. In block five my confidence signal is a probe &mdash;
    this operation, with the weights learned to answer one specific question.</p>
""",

"p1-residual-bus": """
    <b>4:15 &rarr; 5:40.</b> <i>[4 steps.]</i>
    <p>Now the same idea inside a real model. Each vertical line is one token position,
    and the line is the residual stream at that position &mdash; in GPT-2 small, a
    768-dimensional vector. Notice the tokenisation: &ldquo;Eiffel&rdquo; is three
    tokens, not one.</p>
    <p class="cue" data-cue="1">The embeddings are written onto the streams.</p>
    <p class="cue" data-cue="2">Attention is the only component that moves information
    between positions. Here the token &ldquo;of&rdquo; reads from &ldquo;Tower&rdquo;,
    &ldquo;French&rdquo; and &ldquo;city&rdquo;, and adds what it finds to its own
    stream.</p>
    <p class="cue" data-cue="3">The MLP works on one position at a time. It reads the stream
    and adds a vector back. A lot of the model's stored associations seem to live in
    these.</p>
    <p class="cue" data-cue="4">That repeats for twelve layers, and at the end the
    unembedding reads the final stream at the last position and gives you next-token
    probabilities.</p>
    <p>Here is the sentence to keep. The residual stream is a running sum. Nothing
    overwrites it; every component adds to it. That is the single architectural fact that
    makes the next slide possible.</p>
""",

"p1-logit-lens": """
    <b>5:40 &rarr; 6:50.</b> <i>[4 steps. Real numbers &mdash; GPT-2 small, computed with
    TransformerLens.]</i>
    <p>If the stream is a running sum written in roughly the basis the output is read in,
    then we can read it early. Take the residual stream at the last position after any
    block, apply the model's own final layer-norm and unembedding, and look at the result
    as if the model had stopped there. That is the logit lens, and the prompt here is
    &ldquo;The Eiffel Tower is in the French city of&rdquo;.</p>
    <p class="cue" data-cue="1">Early layers predict a generic &ldquo;the&rdquo;. The
    probability of &ldquo;Paris&rdquo; is essentially zero.</p>
    <p class="cue" data-cue="2">Blocks four to seven drift towards place-like tokens &mdash;
    &ldquo;La&rdquo;, &ldquo;Man&rdquo;, &ldquo;Rome&rdquo;.</p>
    <p class="cue" data-cue="3">Block eight jumps to &ldquo;Paris&rdquo; at 0.75. It peaks
    at block nine at 0.96. And then the last blocks actually bring it down to 0.21 at the
    output, while keeping it in first place &mdash; late layers spread probability mass to
    other cities, Nice, Lyon.</p>
    <p class="cue" data-cue="4">Look at the rank column: from about twenty-four thousandth
    to first.</p>
    <p>So you can watch an answer form, layer by layer.</p>
""",

"p1-limits": """
    <b>6:50 &rarr; 7:30.</b>
    <p>And now the sentence that generates the rest of the tutorial. Everything I just
    did was <i>reading</i>. A thermometer that shows the temperature rising does not show
    you what is heating the room.</p>
    <p>The lens tells us that by block eight the stream points at &ldquo;Paris&rdquo;. It
    does not tell us that block eight <i>causes</i> the answer, or which component
    computed it. Attention weights have the same problem: a head can look straight at a
    token and write nothing useful.</p>
    <p>To claim cause, you have to intervene.</p>
""",

"p2-transplant": """
    <b>7:30 &rarr; 8:45.</b> <i>[4 steps.]</i>
    <p>So here is intervention, and it is beautifully simple.</p>
    <p class="cue" data-cue="0">Two prompts. The clean one: &ldquo;When Mary and John went
    to the store, John gave a drink to&rdquo; &mdash; and the answer is Mary. The
    corrupted one changes the repeated name, so the answer flips to John. One token
    differs. Same length, same positions.</p>
    <p class="cue" data-cue="1">Run both forward and cache every activation: every layer, every
    position.</p>
    <p class="cue" data-cue="2">Now copy <i>one</i> activation &mdash; the residual stream
    entering layer nine at the last position &mdash; from the clean run into the corrupted
    run.</p>
    <p class="cue" data-cue="3">Let the corrupted run continue. Its answer moves back to
    Mary, ninety-nine per cent of the way there. One number, transplanted, and the answer
    changes.</p>
    <p class="cue" data-cue="4">Then do that for every layer and every position. Twelve
    layers by fifteen positions: a hundred and eighty runs, and one heatmap.</p>
""",

"p2-heatmap": """
    <b>9:20 &rarr; 10:05.</b>
    <p>And this is that heatmap, with real numbers.</p>
    <p>Every position before the repeated name is exactly zero, because those tokens are
    identical in both prompts. Up to layer seven the entire effect sits on the one token
    that differs. Then in layers seven and eight there is a handover: that token drops
    from 0.75 to 0.05, while the final token rises from 0.03 to 0.39 to 0.99.</p>
    <p>So attention heads in layers seven and eight move the information from the
    repeated name to the end of the sentence. That is a mechanism, localised in layers and
    positions, and we found it by intervening rather than by looking.</p>
""",

"p2-super": """
    <b>10:05 &rarr; 10:50.</b> <i>[4 steps. Toy model, Elhage et al. 2022.]</i>
    <p>Next question: if directions carry meaning, what are the units? Five features, a
    two-dimensional hidden space.</p>
    <p class="cue" data-cue="1">Pack five directions into two dimensions, turn one feature on,
    and read all of them: the others pick up part of it. That leak is interference.</p>
    <p class="cue" data-cue="2">If features are dense &mdash; often on together &mdash; the
    leaks pile up, so the model keeps two clean orthogonal features and throws three
    away.</p>
    <p class="cue" data-cue="3">But make the features sparse, rarely on at the same time, and
    the leak is mostly cut off by the non-linearity. Now the model packs all five, as a
    pentagon.</p>
    <p class="cue" data-cue="4">More features than dimensions, paid for with interference.
    That is superposition, and it is why single neurons fire for unrelated things.</p>
""",

"p2-sae": """
    <b>10:50 &rarr; 11:50.</b> <i>[3 steps.]</i>
    <p>Which gives us the tool. If features are directions packed into too few dimensions,
    try to learn the dictionary of directions.</p>
    <p class="cue" data-cue="1" data-label="STEPS 0-1">Take one dense residual vector. An encoder maps it into
    a much wider space where only a few entries are non-zero, because we trained it with a
    sparsity penalty. Gemma Scope uses a JumpReLU for that &mdash; a ReLU with a learned
    threshold per latent, so a latent is exactly zero until it clears its own bar. And each
    latent can be given a human label from the texts that switch it on.</p>
    <p class="cue" data-cue="2">The decoder adds those few directions back up, and that is a
    reconstruction of the original vector.</p>
    <p class="cue" data-cue="3">And the reconstruction is imperfect. What is left over is real
    computation that the dictionary does not explain. One concrete number from our notebook:
    splice the reconstruction back into Gemma 3 1B at layer seventeen and next-token loss
    goes up by 0.37 nats.</p>
    <p>Keep that error term in mind. It is honest, and it does not go away.</p>
""",

"p2-graph": """
    <b>11:50 &rarr; 12:35.</b> <i>[4 steps.]</i>
    <p>Put features and causality together and you can trace one answer end to end. The
    prompt: &ldquo;the capital of the state containing Dallas is&rdquo;.</p>
    <p class="cue" data-cue="1">&ldquo;Dallas&rdquo; activates a Texas feature.
    &ldquo;Capital&rdquo; and &ldquo;state&rdquo; activate a say-a-capital feature.</p>
    <p class="cue" data-cue="2">Those two combine into say-Austin. Thickness is the strength
    of the direct effect.</p>
    <p class="cue" data-cue="3">And that pushes the Austin logit.</p>
    <p class="cue" data-cue="4">The grey nodes are error nodes &mdash; the part of each layer
    the replacement model cannot explain. They are on the diagram because leaving them off
    would be dishonest.</p>
    <p>Two hops, with an inspectable intermediate. That is the most detailed thing this
    field can currently do, and it explains one prompt.</p>
""",

"p2-recap": """
    <b>8:45 &rarr; 9:15.</b>
    <p>This table is the four blocks I just compressed, and I want to be straight about
    which of them you actually saw. The first row, patching, is the one I showed you: it
    tells you where the model relies on information, and leaves open what that
    information is. The other two rows &mdash; decomposing the units, and tracing how they
    combine on one prompt &mdash; I skipped, and the notebooks are there if you want
    them.</p>
    <p>What I need from this slide is the line underneath all three. An explanation counts
    when an intervention can test it. That is the rule I am about to apply to a judge.</p>
""",

# ============================================================ PART B: 13:00-54:00

"p3-section": """
    <b>9:15 &rarr; 9:35.</b> <i>[Nothing to add to the title. Say it and move.]</i>
    <p>Block five. One question: when an LLM judges, which of its verdicts do we
    trust?</p>
""",

"p3-open": """
    <b>9:35 &rarr; 10:55.</b>
    <p>Two tools from the speed-run, pointed at a new subject.</p>
    <p>Read the sentence on screen: a plain probe can match a sparse-autoencoder feature,
    and patching tests what a model relies on. One gloss, since I skipped it: a sparse
    autoencoder is the heavier tool from block three that learns a whole dictionary of
    those directions. The claim here is that a plain linear probe often matches it &mdash;
    which is exactly why a probe is all I need today.</p>
    <p>Those two sentences are the whole toolkit for the next forty minutes. What changes
    is the thing we point them at &mdash; not a factual completion like
    &ldquo;Paris&rdquo;, but a <i>verdict</i> from a model acting as a judge.</p>
    <p>The probe becomes a confidence signal. Not the confidence the judge states, but the
    confidence its hidden state carries. And I want to be careful about what that is: it is
    a learned correlate, not a lie detector. It can be wrong, and later in this block you
    will watch it fail.</p>
    <p>And intervention becomes a grounding check: did this verdict rest on the evidence
    that actually matters? Today I intervene on the input text &mdash; I remove or replace
    the evidence &mdash; which is the simplest form of it. Patching the hidden states of
    those tokens is the natural next step, and I am not doing it yet.</p>
""",

"p3-grid": """
    <b>10:55 &rarr; 11:55.</b> <i>[2 steps.]</i>
    <p>An LLM-assisted audit has two bodies of text. Rules on one axis &mdash; what a
    standard requires. Evidence on the other &mdash; plans, minutes, change logs, commits.
    The judge answers one cell at a time: this rule, against this document, compliant or
    not.</p>
    <p class="cue" data-cue="1">And it fills every cell. Fast, cheap and tireless. The sizes
    here are illustrative; a real audit is tens of rules against hundreds of documents, so
    thousands of verdicts.</p>
    <p class="cue" data-cue="2">Nobody reviews all of those. Which means the question is not
    &ldquo;is the judge accurate on average&rdquo;. The question is: <i>which verdicts need
    a human?</i></p>
    <p>That reframing is the whole block. Average accuracy is a number you report. A
    routing decision is a number you have to defend.</p>
""",

"p3-iso": """
    <b>11:55 &rarr; 12:55.</b>
    <p>A word on where this comes from, because it is context, not content.</p>
    <p>My work is on process audits of very small software teams. ISO/IEC 29110 is the
    lifecycle standard written for exactly those organisations &mdash; teams of up to
    twenty-five people &mdash; covering project management and software implementation.
    And the technical report, 29110-3-1, gives the assessment guidelines: you check each
    expected practice against the project's own records. An assessor sits down and reads
    plans, minutes and change logs, rule by rule.</p>
    <p>That is the grid from the previous slide. And a team of eight cannot afford a
    full-time assessor, which is precisely why LLM assistance is attractive here &mdash;
    and precisely why trust is the binding problem.</p>
    <p>I will not quote the standard: its text is licensed. The rule you are about to see
    is invented, written in its style.</p>
""",

"p3-rule": """
    <b>12:55 &rarr; 14:05.</b> <i>[1 step. Read both boxes aloud, slowly &mdash; the whole
    next slide depends on the room having actually heard them.]</i>
    <p>So: one rule, one piece of evidence. Rule R-PM-07, invented, in the style of the
    standard. Every change request is recorded; its impact on schedule and cost is
    assessed; and the customer approves it before work on it starts.</p>
    <p>And the evidence, from the meeting minutes: &ldquo;Twelfth of March status meeting.
    Client asked to add CSV export to the reports module. Dev lead estimates three extra
    days; added to Sprint 4. Action: update the project plan.&rdquo;</p>
    <p class="cue" data-cue="1">Three clauses. Recorded. Schedule <i>and cost</i> assessed.
    Customer approval <i>before</i> work starts. Hold those three in your head.</p>
    <i>[Optional, 10 s: hands up &mdash; compliant, or non-compliant? Let them commit
    before the reveal.]</i>
""",

"p3-verdict": """
    <b>14:05 &rarr; 15:25.</b> <i>[2 steps.]</i>
    <p>The judge says compliant. And its reasoning sounds right: the request was recorded,
    and its schedule impact was assessed. It is fluent, it is specific, and it cites the
    evidence. It also tells us it is ninety per cent confident.</p>
    <p class="cue" data-cue="1">Here is the human auditor's label. Non-compliant. Clause one
    is met. Clause two is half met &mdash; schedule was assessed, cost was never mentioned.
    And clause three is simply absent: the work was scheduled into Sprint 4 with no customer
    approval at all.</p>
    <p class="cue" data-cue="2">So this is the dangerous case. Not a confused verdict, not a
    hedge &mdash; a confident, fluent, wrong verdict. And if our routing policy is
    &ldquo;send the low-confidence ones to a human&rdquo;, using the judge's own ninety per
    cent, this verdict is never reviewed by anybody.</p>
    <p>That is the failure I want to catch.</p>
""",

"p3-probe": """
    <b>15:25 &rarr; 16:35.</b> <i>[2 steps.]</i>
    <p>So let us ask the judge's hidden state instead of its words.</p>
    <p>The probe is a linear read-out on the judge's residual stream, taken at the answer
    position &mdash; the last prompt token, where the next token is about to be Yes or No.
    That is block three's tool exactly. What changes is the target: it is trained to predict
    &ldquo;is this verdict correct?&rdquo;</p>
    <p class="cue" data-cue="1">The needle settles at a probability of correctness of about
    0.4. The judge told us 0.9. Our threshold for automatic acceptance here is 0.7, and that
    number is illustrative.</p>
    <p class="cue" data-cue="2">Below threshold, so the case is routed to a human auditor.</p>
    <p>The model's words said ninety per cent. Its hidden state did not. And notice what
    this costs: one forward pass we were already doing, plus a dot product.</p>
""",

"p3-ground": """
    <b>16:35 &rarr; 18:15.</b> <i>[3 steps.]</i>
    <p>A score tells us to look at this verdict. It does not tell us what is wrong with it.
    For that, intervene &mdash; block two's idea, applied to the input text. Change one piece
    of evidence, hold everything else fixed, and watch the verdict.</p>
    <p class="cue" data-cue="1">Remove the sentence with the three-day estimate. The verdict
    flips to non-compliant. So that one sentence was carrying the decision.</p>
    <p class="cue" data-cue="2">Now put it back, and add a new sentence: &ldquo;The customer
    rejected the change.&rdquo; The verdict does not move. Still compliant. A customer
    rejection should make this non-compliant immediately, and the judge does not notice.</p>
    <p class="cue" data-cue="3">Put those together. The schedule estimate <i>is</i> relevant
    evidence &mdash; for clause two. The problem is that the verdict depends on it alone, and
    is completely insensitive to clause three, the approval. An auditor would never accept a
    verdict grounded like that, even if it happened to be right.</p>
    <p>And this is a text-level intervention, which is the cheap version. Patching the hidden
    states of those sentence tokens would tell us <i>where</i> the clue is read. That is the
    next step, and it is not in today's notebook.</p>
""",

"p3-why": """
    <b>18:15 &rarr; 19:55.</b>
    <p>The R-PM-07 story I just told you is invented. This result is not.</p>
    <p>Radharapu and colleagues train linear probes on the hidden states of reasoning judges,
    with a Brier-score loss. Compared against verbalized confidence and against
    multi-sample methods, the probes were better calibrated, at roughly ten times less
    compute. And in their experiments the probes generalised to evaluation domains they had
    not seen.</p>
    <p>I want to be careful with that last claim, because I am going to contradict it in ten
    minutes. In our own test run, on our data, the probe did <i>not</i> transfer to rules it
    had never seen. So take transfer as something you test, not something you inherit.</p>
    <p>Their own honest caveat is interesting for us: the probes are conservative. They are
    under-confident on easy data. That is a bad property for a leaderboard and a good one for
    an audit, where a missed error costs far more than an unnecessary review.</p>
    <p>And the baseline to keep in view: for a Yes/No judge, the probability it assigns to its
    own answer token is free. Any probe has to beat that, or it is not worth the trouble.</p>
""",

"p3-a10": """
    <b>19:55 &rarr; 22:35.</b> <i>[4 steps. Centrepiece. Say "synthetic" in the first
    sentence &mdash; three thousand simulated verdicts, nothing here is measured.]</i>
    <p>This slide is synthetic: three thousand simulated verdicts, with a judge about
    seventy-four per cent accurate. I use it because it shows the shape of the problem
    cleanly, and I want to be explicit that no number on it was measured.</p>
    <p>On the left is a reliability diagram. Stated confidence on the x-axis, how often the
    verdict is actually correct on the y-axis. The diagonal is perfect calibration.</p>
    <p class="cue" data-cue="0">Verbalized confidence piles up between 0.8 and 1.0, while
    accuracy stays near 0.75. Every bar sits well below the diagonal: overconfident,
    systematically.</p>
    <p class="cue" data-cue="1">The probe's bars hug the diagonal. When it says 0.6, it is right
    about sixty per cent of the time.</p>
    <p class="cue" data-cue="2">Now the right-hand chart, which is the one an auditor cares
    about. Auto-accept every verdict whose score is at or above a threshold. Coverage is the
    share you accept automatically; the vertical axis is the error rate among the ones you
    accepted. Set the threshold low and you accept nearly everything &mdash; and every error
    escapes with it.</p>
    <p class="cue" data-cue="3" data-label="STEPS 3-4">Raise the threshold. Fewer automatic acceptances, and far
    fewer escaped errors. The dashed line is our routing target: at most ten per cent error
    among auto-accepted verdicts. The probe curve meets it at about thirty-eight per cent
    coverage. Routing by the judge's own words only gets under ten per cent at about eight
    per cent coverage &mdash; which is to say, it barely separates right from wrong at all.</p>
    <p>So a calibrated score turns review into a dial. You choose coverage, and you are told
    what it costs you.</p>
""",

"p3-conformal": """
    <b>22:35 &rarr; 24:35.</b> <i>[3 steps.]</i>
    <p>Which raises the obvious question: can we turn that dial into a guarantee? This slide
    is a research direction &mdash; my thesis line, LLM-assisted quality and security audits
    of software projects &mdash; and not a published result.</p>
    <p class="cue" data-cue="1">Start with a calibration set that has gold labels. Sixty
    synthetic verdicts, placed along the axis by probe score. Grey means the judge was right,
    red means it was wrong. Most of the red sits at low scores. Not all of it.</p>
    <p class="cue" data-cue="2">Define an escape: a verdict that is wrong <i>and</i>
    auto-accepted. The rule is the one in our notebook: scan thresholds upward and take the
    first one where the empirical escape rate, plus a finite-sample correction of one over
    n plus one, stays under your budget alpha. With sixty calibration points that correction
    already eats 1.6 of a 10-point budget, which is the honest price of a small calibration
    set.</p>
    <p>If new verdicts are exchangeable with the calibration verdicts, the <i>expected</i>
    escape rate on new verdicts is at most alpha. In expectation over calibration sets
    &mdash; not a promise about any single audit.</p>
    <p class="cue" data-cue="3">And there is the hinge. The guarantee needs exchangeability. A
    new 29110 process area is exactly where that assumption dies. Which is why the next thing
    I show you is the test, not the theorem.</p>
""",

"p3-legal": """
    <b>24:35 &rarr; 25:55.</b>
    <p>I cannot share real audit records, so the notebook uses a public analogue with the same
    shape.</p>
    <p>LegalBench has fourteen contract-NLI tasks, derived from ContractNLI. Each task is one
    assertion applied to clauses from non-disclosure agreements &mdash; for example, whether a
    clause states that the receiving party may share confidential information with third
    parties. So the mapping is exact: the assertion is my rule, the contract excerpt is my
    evidence, and the verdict is Yes or No.</p>
    <p>And the shift test is built into the data. Eleven assertions are split by document into
    train, calibration and test, so no test contract was seen in training. Then three
    assertions are held out <i>entirely</i> &mdash; no example of those rules anywhere in
    training. Those three stand in for a new process area appearing in next year's audit.</p>
    <p>The verdict is read straight from the Yes/No logits, which is also where the
    token-probability baseline comes from, and the hidden states at the last prompt token are
    cached &mdash; so the notebook runs on a free CPU runtime.</p>
    <i>[Check before the session which judge the published cache actually uses: this row says
    Gemma 3 4B IT, and the numbers on the next three slides are the Qwen2.5-0.5B fallback.
    Say which one you are quoting.]</i>
""",

"p3-nb5": """
    <b>25:55 &rarr; 28:15.</b>
    <p>In the tutorial this is where the room works for twenty-two minutes, in pairs. Today I
    am going to walk you through what it asks and what we found, which takes about ten
    minutes.</p>
    <p>Six steps. Run the judge on a few pairs, so you have seen it work. Train a probe to
    predict which of its verdicts are wrong. Compare that probe against the two cheap
    baselines &mdash; the verbalized number and the token probability &mdash; on AUROC and on
    calibration error. Pick a routing threshold that holds error among accepted verdicts under
    ten per cent. Then test on the three held-out assertions. And finally, remove the evidence
    behind the most confident verdicts and see whether they move.</p>
    <p>Three terms, because the next slides use them. AUROC is ranking: the chance that a wrong
    verdict scores lower than a right one, so 0.5 is useless. ECE is the average gap between
    stated confidence and actual accuracy. Brier is the mean squared gap to the actual zero-one
    outcome.</p>
    <p>One subtlety that catches people every time: the target is &ldquo;is this verdict
    wrong&rdquo;, not &ldquo;is the answer Yes&rdquo;. So the confidence has to be the
    probability of whichever answer the judge actually gave &mdash; the larger of P(Yes) and
    P(No).</p>
""",

"h-nb5-result": """
    <b>28:15 &rarr; 32:15.</b>
    <p>Here is what came out. And the label matters: this is our test run, on the
    Qwen2.5-0.5B fallback judge, not the Gemma model in the paper-ready version, and it is
    not a published result. The judge is right about seventy-five per cent of the time on the
    test split.</p>
    <p>Three confidence signals, scored on how well they rank wrong verdicts below right
    ones.</p>
    <p>Asking the judge how confident it is scores 0.43. That is <i>worse than chance</i>. And
    the reason is almost funny: across the whole test split it only ever answered 75, 80, 85
    or 95. It has four moods. There is nothing in there to rank with.</p>
    <p>The probability it assigns to its own answer token scores 0.63. That number is free
    &mdash; it is already in the logits of the forward pass you just paid for. This is the
    baseline, and it is a real one.</p>
    <p>And the probe on the residual stream scores 0.71. One extra dot product, a few hundred
    labelled verdicts to fit it, and it beats both.</p>
    <p>Now the line at the bottom, because it is the methodological point of the whole
    notebook. Recalibration fixes calibration error. It cannot fix AUROC. If you have a score
    that systematically claims ninety when it should say seventy, a monotone transform repairs
    that. But if the score does not <i>rank</i> &mdash; if wrong verdicts do not sit below
    right ones &mdash; no transform will ever rescue it. So ranking is the thing to measure
    first, and it is where the words fail hardest.</p>
""",

"h-nb5-shift": """
    <b>32:15 &rarr; 35:55.</b>
    <p>And now the slide I would want someone to show me if I were sitting where you are.</p>
    <p>Same test run. Three assertions that appear in no training and no calibration example
    &mdash; notice on compelled disclosure, return of confidential information, survival of
    obligations. Rules the probe has never been calibrated on. The stand-in for a process area
    that turns up for the first time next year.</p>
    <p>Two numbers. First, the judge itself gets worse: accuracy falls from seventy-five per
    cent to sixty-four. Fine, expected, that is what shift means.</p>
    <p>The second number is the one that matters. Using the threshold it had calibrated,
    seventeen and a half per cent of verdicts escaped review &mdash; wrong and auto-accepted
    &mdash; against eight per cent for the free token-probability baseline. So the probe did not
    merely degrade. It ended up <i>worse than the thing it beat</i> on the test split.</p>
    <p>My reading is on the left, and it is a hypothesis, not a measurement: the probe may
    have learned which <i>rules</i> are hard, rather than when the judge is uncertain. That is
    a genuinely useful signal when tomorrow's documents arrive under rules you have already
    calibrated. It is worth nothing on a rule you have not.</p>
    <p>And then the grounding check, on the right, which fails in a different and more
    unsettling way. Take the forty most confident Yes verdicts and replace the evidence with
    irrelevant boilerplate. Seventy per cent of them stayed Yes. And here is the part that
    should bother you: those verdicts were <i>correct</i>. The judge got the right answer
    without reading the evidence, because it had a prior about the rule. Accuracy cannot see
    that. A confidence score cannot see that. Only the intervention can.</p>
""",

"h-nb5-routing": """
    <b>35:55 &rarr; 38:45.</b>
    <p>Which brings us to the number you would actually have to put your name on.</p>
    <p>The policy is simple: auto-accept a verdict when its score clears a threshold,
    otherwise it goes to a human. Two numbers describe it &mdash; coverage, the share you
    accept, and escape, the share that is wrong and accepted anyway. The notebook picks the
    threshold the obvious way: the lowest one whose accepted verdicts keep error under ten per
    cent, measured on the calibration split.</p>
    <p>On the calibration split, the target is met. Of course it is &mdash; that is where we
    fitted the threshold. It is met by construction, and a number that is true by construction
    is not evidence of anything.</p>
    <p>On test it can be exceeded, and that is not a bug. The threshold was tuned on roughly a
    hundred verdicts, so it inherits their sampling noise. Push it to a five per cent target
    with this judge and you are left with almost no coverage at all, which is why the
    notebook's target is ten.</p>
    <p>So here is the question I would put to an assessor, and the one I would like to be
    asked about. Suppose you have to certify that at most five per cent of verdicts are wrong
    and unreviewed. Is a threshold tuned on a hundred calibration verdicts evidence for that
    claim? I do not think it is, on its own. The conformal correction two slides back exists
    precisely to price that gap &mdash; and it still assumes the new cases look like the old
    ones, which the previous slide just showed you is the assumption that breaks.</p>
""",

"p3-debrief": """
    <b>38:45 &rarr; 42:15.</b>
    <p>So let me answer my own three questions, because in the tutorial this is where the room
    argues for five minutes and I would rather give you my position than a prompt.</p>
    <p>Where did the probe win? Against the judge's words, decisively &mdash; and the words were
    worse than chance, so that is a low bar. Against token probability, yes, but only on rules
    it had been calibrated on, and by 0.71 to 0.63. That is a real margin and a modest one.</p>
    <p>Where did it fail? On a rule it had never seen, where it fell below the free baseline. And
    it failed in a second, independent way: a verdict can be correct and still not rest on the
    evidence at all. Seventy per cent of our most confident verdicts survived having their
    evidence deleted.</p>
    <p>And so what counts as evidence that a verdict is safe to skip? My answer is that a
    calibrated score alone is not evidence. A score plus a stated escape bound plus a grounding
    check on a sample of accepted verdicts &mdash; that combination starts to look like something
    an assessor could sign, because each one covers a failure the other two cannot see.</p>
    <p>Three lessons I would take out of this block. Words are useless as a gate, and token
    probability is a real baseline that any new method has to beat. A probe can win
    in-distribution and fail on a new rule, which means it may be learning the difficulty of the
    task rather than the uncertainty of the model. And a correct verdict can still be ungrounded
    &mdash; neither accuracy nor any confidence score will reveal that, only an intervention.</p>
""",

"p3-map": """
    <b>42:15 &rarr; 44:15.</b> <i>[6 steps, one row per advance.]</i>
    <p>Stepping back: the whole hour in one table. Pick the method from your question, and then
    pick the validation from the method &mdash; that second half is the part people skip.</p>
    <p class="cue" data-cue="1">Is concept X represented? A linear probe. Validate on held-out <i>and</i>
    out-of-distribution splits, which is exactly the failure you just watched.</p>
    <p class="cue" data-cue="2">Which component causes Y? Activation patching. Check the effect survives other
    corruptions, and use path patching to separate direct from indirect routes.</p>
    <p class="cue" data-cue="3">Which features does it use? Sparse autoencoders. And the validation is blunt: if a
    plain probe matches it, the SAE added nothing.</p>
    <p class="cue" data-cue="4">How is one prompt computed? An attribution graph &mdash; which is a hypothesis
    until you intervene on the features in it.</p>
    <p class="cue" data-cue="5">Can I control behaviour Z? A steering vector. And test it against orthogonal
    directions, because steering directions turn out not to be identifiable: perturbations
    orthogonal to yours can reach much of the same effect.</p>
    <p class="cue" data-cue="6">Note what is highlighted. Block five used only the first two rows
    &mdash; and the second only in its simplest form, intervening on input text rather than on
    hidden states. The simplest tools did the auditing work. Hidden-state patching is the
    obvious next step, and that is where I am going.</p>
""",

"p3-transfer": """
    <b>44:15 &rarr; 45:15.</b>
    <p>In the tutorial this is a two-minute pair exercise with a printed canvas, and I will
    leave it on screen for a moment because it is the part that transfers out of this room.</p>
    <p>Six boxes. What does the model decide? Who or what gives you the gold label? Where would
    the confidence signal be read from &mdash; which layer, which token? What escape rate can you
    actually tolerate? Which piece of evidence <i>should</i> flip the verdict, so you can test
    grounding? And what is your unseen assertion &mdash; what plays the role of a rule the probe
    has never been calibrated on?</p>
    <p>If you judge anything with a model &mdash; grading, labelling data, reviewing code,
    screening papers, checking claims against sources &mdash; boxes one to three take about five
    minutes, and boxes four to six are where the interesting problems are.</p>
""",

"p3-field": """
    <b>45:15 &rarr; 48:15.</b> <i>[7 steps.]</i>
    <p>Where the field is, in one arc.</p>
    <p class="cue" data-cue="1" data-label="STEPS 1-5">We observed, with the logit lens. We intervened, with
    patching. We decomposed, with sparse autoencoders. We traced, with attribution graphs. And
    then we audited &mdash; a probe on a judge. Every one of those is a tool for turning an
    internal state into a claim you can test.</p>
    <p class="cue" data-cue="6">The open problems, and these are not mine &mdash; they are the
    field's, from the Open Problems review. Most circuit results explain one prompt, not a
    general mechanism. Attribution graphs explain a replacement model, and how faithful that is
    to the real one is genuinely open. Automating interpretability with agents is just starting.
    And there are no agreed evaluation standards, which is why so many results are hard to
    compare.</p>
    <p class="cue" data-cue="7">And the implications, which is why I work on this. Assurance and
    audits of AI systems &mdash; today's block. Evidence that a regulator could actually ask
    for. And using models as objects of scientific study.</p>
    <p>Let me end the technical part honestly. These tools are young. Most published results are
    on small models or single prompts. My own headline result today was that my method lost to a
    free baseline the moment the rule changed. Treat every interpretation as a hypothesis with a
    test attached &mdash; that is the discipline the field needs, and it is the one thing from
    this hour I would most like you to keep.</p>
""",

"p3-res": """
    <b>48:15 &rarr; 49:00.</b> <i>[Do not read the list.]</i>
    <p>Everything we used is open, and this slide is a reference rather than something to read
    out.</p>
    <p>Left column: the tools from the notebooks, and where to learn more. If you want a proper
    course rather than a tutorial, ARENA chapter one is the best free follow-up I know.</p>
    <p>Right column: the papers the blocks were built on. The Open Problems review at the bottom
    is the map of what nobody knows yet, and it is the most useful thing on the slide if you are
    looking for a research question.</p>
""",

"p3-thanks": """
    <b>49:00 &rarr; 49:40.</b>
    <p>Thank you. The tutorial is joint work with Miguel Gonz&aacute;lez and Salvador Hinojosa at
    Tec de Monterrey, and the full four-hour version runs at MICAI in November.</p>
    <p>Slides, all six notebooks and the printables are at the link on screen, or scan the code. The notebooks keep
    working after today, and the fifth one is the one I would start with if you judge anything
    with a model.</p>
    <p>I have about five minutes, and I am most interested in the shift result &mdash; if you
    think the probe is learning rule difficulty rather than uncertainty, I would like to hear how
    you would separate the two.</p>
    <i>[Invite questions. Keep the method map, p3-map, in mind: it is the best slide to jump
    back to if someone asks "which tool for my problem".]</i>
""",

}
