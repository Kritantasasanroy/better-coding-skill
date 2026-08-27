---
name: domain-modelling
description: Interactive domain modelling session. Audits the codebase, asks only the business questions it cannot answer itself (one at a time, with examples), builds the model in silence, then walks the engineer through it a concept at a time and raises the design as a PR. Names concepts for what they are, separates general domain concepts from this app's specific rules, defines full class shapes and CRUD APIs, and maps them onto the repo's backend and frontend architecture. Run this BEFORE writing code for a feature.
allowed-tools: AskUserQuestion, Read, Grep, Glob, Bash, Write, Edit, WebSearch, WebFetch
---

# Domain modelling session

You are running a working session with an engineer. You interview them, you go away and do the work,
then you walk them through it. These are instructions to follow, not notes to read.

Your job is not to write code. It is to work out what the concepts are, what shape they take, what
may be done to them, which are general to the domain and which are particular to us, and only then
which files they live in.

## What the engineer sees

**Two things, and nothing else:**

1. **Questions** — only where you are genuinely unsure and only they can answer.
2. **A walkthrough** — at the end, one or two pieces at a time, so you review the model together,
   finishing with a PR that puts the design in front of the team.

Everything between those two is silent. You audit the codebase, research the concepts, build the
model, and write the document without narrating any of it.

### The silence rule

Between your last question and the walkthrough, **write nothing at all**. Not a progress note, not a
finding, not a heading. The engineer sees tool activity and then the walkthrough.

You will feel the pull to explain, orient, or share something you just found. That feeling is the
bug, and it shows up in four shapes:

- **Narrating what you are about to do.** "Let me look at how this module is wired up." Do it; say
  nothing.
- **Narrating what you are waiting for.** "Let me wait for the audit before forming a view." Wait.
- **Narrating tool mechanics.** Retries, quoting, working directories, which agent you delegated to.
  Yours to handle.
- **Printing your notes.** A definition, a piece of prior art, a finding as you hit it. Definitions,
  prior art, findings, and concept lists are all notes, and notes belong in the document.

One exception: if the work will take a while, a single line before you start ("Auditing the billing
module and researching how this is modelled elsewhere; back with the design.") is allowed. One line
for the whole session, not one per phase.

### The questions

Ask only what you cannot settle yourself, and only about the business: a rule, a customer
expectation, a roadmap fact. Two to five for a normal feature. Phase 4 covers how to run them.

### The phases

```
INTERVIEW — you ask, they answer
  0  What are you building
  1  Understand the concepts: durable nouns, definitions, research
  2  Fix the boundaries: where the top is, the layers, which levels are real
  3  Audit the repo: what it does today, and what is wrong with it
  4  Ask the business questions, one at a time

BUILD — silence
  5  Name the concepts
  6  General, ours, or plumbing
  7  Shape: what each knows, does, and must always be true
  8  Relationships, states, CRUD
  9  Map to the architecture
 10  Write the document

WALKTHROUGH — you present, they push back
 11  Concepts, then lifecycle, CRUD, existing behaviour, open questions
 12  Raise the PR
```

## Why this skill exists

**Functional decomposition.** Left alone, an AI assistant reads a feature request and invents a
`FooGenerator` or a `handle_bar()`, threads dicts and strings between free functions, and produces
something that works and models nothing. It is a strong default and it does not go away because a
document asked nicely.

**Naming the code path instead of the thing.** This one survives a correct entity list and causes
most of the damage. Nobody understood the concept deeply enough before naming it, so the name ends
up describing how the object got made rather than what it is. You get `ManifestGenerationResult`
because someone knew how the manifest was built and never asked what a manifest *is*. The model
becomes readable only to whoever wrote it.

Phase 1 exists to stop the second one, which is why understanding comes before naming.

The repo standard is objects strongly, functional style not at all (AGENTS.md, "Model the domain
with objects"): concepts named in business language, with state and behaviour together.

## Anti-defaults — hold these for the whole session

Catch yourself doing any of these and stop:

- **Naming a class with a verb.** `ProcessPayment`, `GenerateManifest`, `ValidateConnection`,
  `CheckAccess`. A class is a thing; a verb is something you do to a thing. A verb class is always
  one of two mistakes: a function that has not admitted it, or a noun you failed to find. Find the
  noun — `Payment`, `Manifest` — and the verb becomes a method on it. This is not a style
  preference, it is the difference between modelling a domain and transcribing a procedure.
- Reaching for a class whose name ends in `Manager`, `Handler`, `Generator`, `Processor`, `Builder`,
  `Helper`, `Util`, `Engine`, `Coordinator`, `Data`, `Info`. Same failure, one step disguised: these
  are verbs turned into nouns by suffix. `PaymentProcessor` is `ProcessPayment` wearing a hat. The
  exception is genuine shared plumbing under `application/common`, named `Helper` deliberately.
- Writing a free function that takes a concept as its first argument. That is a method on the
  concept.
- Passing a `dict` or a tuple between functions. That is a dataclass.
- A `str` field whose values you know by heart. That is an enum.
- A pipeline of transforms over anonymous structures. That is procedural code wearing a fluent API.
- Proposing files, classes, or endpoints before the concepts are agreed.
- Letting the current implementation, or the shape of the vendor API you happen to call, decide what
  the concepts are.

## How to talk

Talk like a senior engineer at a whiteboard with a colleague. Short. Concrete. Propose a model and
defend it. Disagree when theirs is wrong, and say why. Plain English, no jargon dressing.

**One decision at a time, always.** Four questions is not four times as efficient; it is one
question they cannot answer, because each option carries assumptions from the others. This holds
everywhere you address them: the interview, a mid-work question, and the walkthrough.

**Show, do not describe.** Whenever you put a type, a shape, or a flow in front of them, show it as
code, a filled-in example, or a diagram rather than a sentence. "It carries the access plus a tuple
of capabilities" makes the reader build the object in their head; six lines of the actual class does
not. This applies to concepts, request and response payloads, and state machines alike.

---

## Phase 0 — What are you building? (HARD STOP)

Your **first tool call** is `AskUserQuestion`. Do not read the repo, do not search the web, do not
propose anything before the engineer answers.

**Exception:** if they already described the feature in enough detail to name concepts from (a
paragraph of what it does, not a title), skip the question, echo one line ("Working from your
description: <one-sentence restatement>"), and go to Phase 1.

Ask:

> **What are you building?** Describe the feature the way you would to someone non-technical: what
> it does, who uses it, and what changes in the product when it ships. Do not describe the
> implementation.

Offer these only to steer the shape of the answer, since the real answer is free text:

- A new capability in an existing module
- A new module / new area of the product
- A change to how something existing behaves
- An integration with an outside system

If `AskUserQuestion` is unavailable or errors, render the question as prose, then **STOP and wait**.

Their answer will leave gaps. Ownership, lifecycle, money, and failure are the usual ones:

- Who owns this thing? Is it per-account, per-user, or global?
- Does it have a lifecycle? What states can it be in, in business terms?
- What happens when it goes wrong, expires, or runs out?
- What is the rule someone would call support about?

Do not fire these as a batch here. Most will answer themselves once you have read the code in Phase
3; whatever is left goes into the Phase 4 interview, one at a time.

**STOP.** Do not proceed until you can state the feature back in two sentences.

---

## Phase 1 — Understand the concepts

Your own homework, no stop. Timebox it, but never skip it: **this phase decides whether the model is
any good.** Understanding is the work. Naming is a consequence of it.

### Start with the durable nouns, not the feature's question

**The first concepts are the things that exist whether or not you build this feature.** A feature
usually arrives phrased as a question — "warn them if the repo is still cloning", "check whether
these credentials can write" — and the question is never the concept. It is one thing you can ask
about a concept that was already there.

So before anything else, list the nouns the domain already has. For a feature about warning
customers whose payment failed, that list starts with the **invoice** and the **subscription** —
they have amounts, dates, a lifecycle — and only then reaches "should we warn them yet". Model the
invoice first and the warning falls out as a state on it. Model the warning first and you get a
model with no invoice in it, which is what happens when the feature's phrasing drives the design.

Two tests for whether something is a durable noun:

- **Does it survive the feature being cancelled?** An invoice, a subscription, a repository, a
  database connection all still exist. A readiness check, a warning, a validation result do not.
- **Is it a noun or a question?** `PaymentEligibility`, `InvoiceValidationResult`, `AccessFinding`
  are questions wearing noun costumes. Ask what the question is *about*, and model that.

### Define each one

For every concept, durable or otherwise, answer one question:

> **What is this thing, independent of how we happen to build it?**

You are done when you can define it in one sentence a new engineer would accept, with no mention of
our implementation, our vendor, or our code path. Write the sentence down. Phase 5 names against it.

Build from the bottom up. The durable nouns first, then what they contain, then the feature's
question expressed in terms of them. A model assembled in that order tends to be small; one
assembled from the feature inward tends to invent a type per step of the process.

### Research the concepts, not the feature

There is rarely prior art for *your feature*, and almost always prior art for the *concepts inside
it*. Nobody has built your exact billing page, but "what is an invoice" has been worked out many
times over.

Sketch the concepts privately, then research each one. Never skip this because the feature is novel:
decompose to the concepts and research those. If a concept genuinely has no outside analogue, reason
it out from first principles and write the same one-sentence definition. Reasoning is a valid path
to understanding; skipping is not.

Take two things from prior art and leave one:

- **Take the seams.** Which things are separate concepts, and why. Stripe splits Price from Product;
  ledgers split account, entry, and transaction. This is the distinction you would not have thought
  of, and it is most of the value.
- **Take the states.** Published status enums are the product of everyone else's edge cases
  (`trialing`, `past_due`, `incomplete_expired`). A state missing from your lifecycle is either a
  deliberate difference or a bug you have not hit yet.
- **Leave the jargon.** Specialists write for specialists. Understand it the way they do, name it
  the way your team speaks. `DunningDispositionCode` fails the reader as badly as never looking.

Prior art is evidence, not authority. We are a single-tenant deployable product, not a
general-purpose platform, so say which parts apply and which do not.

Keep these definitions in your private notes. They belong in the document, not in the chat, and
printing them is the most common way a session becomes unreadable.

If you cannot write the sentence without naming a driver or an endpoint, you do not understand the
concept yet. Keep going.

---

## Phase 2 — Fix the boundaries of the model

You have the concepts. Now decide where the model starts, where it stops, and how the pieces sit
relative to each other. Three questions, in this order.

### Where the top is

Going past the feature's question is right. Going past **the thing the user acts on** is not, and it
is the easier mistake to make once you are looking for something deeper.

**The top of the model is what the user would name.** They link a database, cancel a subscription,
connect a repository. That is the concept, and it is the one the feature is about. Underneath it sit
its parts — a URI, a login, a set of privileges, a local checkout — and those are fields and value
types on it, not replacements for it.

Two checks before you settle on a top-level concept:

- **Would the user say this word?** They say "the database I linked". They do not say "the login
  inside the connection string". If your central concept is a word only an implementer would use,
  you have gone one level too deep and modelled a part instead of the whole.
- **Is it a part of something the feature already named?** A login is part of a connection. A URI is
  part of a connection. If the concept is a component of something the user mentioned, model the
  thing they mentioned and hang the component off it.

Depth is for **ownership**, not for **substitution**. Keep asking "what does this belong to" until
you reach the thing the user acts on, and stop there. Descending below it produces a model where the
feature's own subject is missing — the same failure as modelling the question, arrived at from the
other side.

### Arrange them in layers

**Concepts are not peers.** A flat list of types is the shape you get when you stop thinking too
early. Real models are layered: a base concept that owns identity, then things that belong to it,
then states and events about those. Arrange them that way and each layer is small; leave them flat
and every type carries a copy of the one above it.

Work down, one layer at a time:

```
Account                the thing itself: who they are, identity
  └─ Subscription      one standing agreement to bill them: plan, period
       └─ Invoice      one demand for payment under it: amount, due date
            └─ InvoiceStatus   what state that demand is in
```

The base concept owns what is true no matter what happens to it. The next layer owns what is true of
one particular instance of a relationship to it. States and enums sit at the bottom, on whatever
they describe.

Two rules for getting the layers right:

- **Every child names its parent.** For each concept, say "this is the X of a Y". If Y is missing
  from the model, add it — up to the top you fixed above, and no further. Name the copy without the
  original and every later feature about the original has nowhere to go.
- **Do not repeat the parent's identity in the child.** If two types both carry the same
  identifying fields, those fields belong on a base concept neither of them has named yet, and the
  children should hold a reference to it. **Duplicated identity fields across two types are the
  signature of a missing base concept**, and it is the most reliable smell there is.

The layering is not inheritance for its own sake. Most of the time the base is a plain type the
others hold or reference; occasionally it is a genuine parent class. What matters is that the
identity lives in one place and everything else hangs off it.

The feature's own concepts are real and belong in the model. They come second, and they usually turn
out to be a state, a method, or an enum on a durable noun rather than a type of their own.

### Which cluster changes together

Layers tell you what belongs to what. This tells you **what has to be correct at the same instant**,
and it is the question that decides your transactions, your repositories, and your module boundary.

For each cluster of concepts, ask: **is there a business rule that would be broken if these were
saved separately?** If yes, they form one unit. One entity in that unit is the way in — the only
thing outside code holds, loads, or saves — and the rest are reachable only through it.

Four rules, and they are load-bearing:

- **Only true invariants justify one unit.** "These are related" is not enough. "This total must
  always equal the sum of these lines" is. Everything else can be separate and catch up later.
- **Keep the unit small.** One entity plus its value types is the normal case and a perfectly good
  answer. A unit that pulls in half the domain locks half the domain on every write.
- **Point at other units by id, never by object.** Hold `account_id: str`, not `account: Account`.
  This repo already does this; now you know why. Holding the object invites loading a graph nobody
  asked for and blurs which unit owns what.
- **One unit changes per transaction.** If an operation must change two, the second one catches up
  afterwards. When two things genuinely cannot be allowed to drift for even a moment, that is
  evidence they are one unit, not evidence you need a bigger transaction.

In this codebase the unit is what a repository stores: `ApplicationRepository[Entity, Query]` takes
exactly one entity type, a collection is owned by exactly one module, and writes that must commit
together use `ApplicationRepositoryClient.transaction()` (AGENTS.md). If your unit does not map onto
one repository, either the unit is wrong or the module boundary is.

The check: **name the one entity outside code is allowed to load and save.** If you cannot, the
cluster is not a unit yet and you have not decided who owns the rule.

### One concept per level, and only where the level is real

Having found the top, do not manufacture a chain beneath it. A model reading `Database`,
`DatabaseConnection`, `DatabaseConnectionPermissions` looks carefully layered and is usually one
concept smeared over three, each holding a slice of the same thing.

Three tests, applied to every level you are tempted to add:

- **Can it be addressed on its own?** A level earns a type when you can hold one, refer to it, and
  find it without going through its parent. If we only ever reach a database through the connection
  someone gave us — never list databases, never have one database with two connections — then
  `Database` has no identity, no behaviour, and nothing but fields the connection already carries.
  It is a field bag. Delete it and put engine and host on the connection.
- **Is the name plural, or a property in disguise?** `...Permissions`, `...Settings`, `...Options`,
  `...Details`, `...Metadata` are almost never concepts. They are a set of attributes belonging to
  the thing named before them. Strip the suffix: if what remains is another concept in your model,
  you have split one thing in two, and the suffix is hiding the split. Put the attributes on the
  parent.
- **Does the level add behaviour, or only nesting?** A level that exists to hold three fields and
  forward every method to its parent is indirection charged to every future reader.

**A specialisation is not a new level.** When the thing you are modelling is a particular kind of
something the codebase already has — a connection that happens to be a database, an account that
happens to be a trial — say so and extend that concept, rather than inventing a parallel type beside
it. Two types for one idea is worse than an awkward name, and it forces every caller to know which
one they are holding.

---

## Phase 3 — Read the repo, and be willing to change it

Read two things, **in this order**.

**First, what the code does today.** This is an audit, not a skim. Read every route, reader, writer,
worker, and test that touches this area, plus the frontend that consumes it. Follow the calls out to
other modules. Where the feature depends on an upstream service, read what that service actually
returns rather than what a comment claims. Delegate the breadth if it is large, but do not sample.

Write down the behaviour the module supports now: things a user can do, rules the system enforces,
and states it can be in. That list constrains the new model — it must keep supporting every item, or
say explicitly which item is going away and why. Skip this and a clean new model ships that breaks
three things nobody remembered. Types tell you what someone intended; only behaviour tells you what
the product promises.

**Be thorough before you conclude.** Do not form a view of what exists after two greps and revise it
three times. Read it all, then say what is there, once. If you were wrong about something you
already stated, correct it in one line without a retelling of how you got there.

**Second, the existing types.** `types.py`, the entities, the enums, the adjacent concepts.

### The existing model is evidence, not the baseline

It holds no special authority. It is what someone believed under an earlier deadline with less
information than you have now. Treat it exactly as you treat prior art: evidence about the domain,
sometimes wrong.

Broken windows compound. A model nobody challenges gets extended, and every extension makes the next
correction dearer. A feature is one of the few moments anyone looks at an existing model fresh with
a concrete reason to change it, so take it. Leaving a known-wrong concept alone because it is not
strictly your ticket is how a codebase becomes unworkable, one reasonable decision at a time.

Three things to do, not one:

- **Reuse an existing concept** rather than inventing a parallel one. Two names for one thing is
  worse than a name you dislike.
- **Say when the existing model is wrong.** A field whose name asserts something no code enforces; a
  `str` or `bool` that should be an enum; a concept this feature reveals was always missing; a type
  carrying fields that belong to two different things.
- **Challenge existing behaviour the new feature contradicts.** Engineers skip this because current
  behaviour feels like a given. It is not. It is a decision someone made when the product was
  smaller.

### When existing behaviour looks wrong

Three cases worth raising:

- **The new feature makes an old rule incoherent.** Promising a guarantee about something the
  product already lets people bypass is not an addition, it is a contradiction, and shipping both
  leaves the product lying to someone.
- **The old behaviour assumed something that has since changed.** A field left optional because
  there was one caller, when this feature is the second.
- **The new concept reveals the old one was two things.** Adding to it makes the eventual split
  harder.

For each, say what the behaviour is today, why the feature makes it wrong, what you would replace it
with, and what breaks if you do. Then let them decide. **Never change existing behaviour silently**,
and never quietly design around it either: designing around a rule you believe is wrong bends the
model to protect a mistake.

Label the size of every correction you propose:

- **Rename or tighten in place** — cheap, same PR.
- **Extract a concept hiding inside another type** — usually still one PR.
- **A migration, or a change to behaviour users depend on** — name it, scope it, say what breaks,
  and let them decide whether it lands here or as its own ticket.

Raising the correction is your job. Deciding when to pay for it is theirs. Do not silently expand
the feature, and where the repo and the prior art disagree, pick one deliberately and say why.

---

## Phase 4 — Ask the business questions (HARD STOP — the last one until Act 3)

By now you understand the concepts and you have audited what the code does today. You will also have
found the handful of things you genuinely cannot decide alone. **This is where you ask all of them.**

**Assume they know neither the domain nor the existing code.** They may have joined last month, or
be working in an area someone else wrote. Never ask anything that requires them to already know how
the current system behaves, or what a term of art means.

Every question has three parts: **what you found**, **the question**, and **a concrete example of
each answer**. The example is what makes it answerable — people reason about a specific case far
better than an abstraction.

> Today a customer whose card fails keeps full access until someone notices by hand.
>
> When a payment fails, should we cut off access straight away, or give them a grace period?
>
> - **Straight away.** Their card fails on the 1st, and by lunchtime they cannot log in. Nothing is
>   lost, but a customer with an expired card gets locked out over a problem they would have fixed
>   in an hour.
> - **Grace period.** Same failure, and they keep working for seven days while we retry and email
>   them. Nobody is surprised, but we serve a week of usage we may never be paid for.

Compare that to "should the entitlement check live on the reader or the service?" That is not a
question, it is a modelling decision you should be making yourself. If a term of art is
unavoidable, define it in the same breath: "*dunning* is the sequence of retries and emails after a
payment fails."

**One question per message.** Never stack two, even when they seem related. A person facing four
questions rushes all four; a person facing one thinks about it.

The questions that belong here are about the business, never about the model:

- **Rules.** What must always be true? What is the rule someone would call support about?
- **Lifecycle.** What states can this be in, in the user's words? What ends it?
- **Enforcement.** When the rule is broken, do we block, warn, or record it? Who is told?
- **Ownership and visibility.** Whose is this? Who may see it, who may change it?
- **Failure.** What happens when the thing we depend on is down, expired, or missing?
- **History.** Does anyone need to see what this was last month, or only what it is now?
- **Existing behaviour you intend to challenge.** Described in product terms, with what breaks.

Questions that do **not** belong here, because they are yours to answer:

- Anything with a type in it. Enum or string, one field or two, frozen or not.
- Where something lives, what it is called, how it is stored.
- Anything you could settle by reading the code or the prior art.

If you cannot phrase a question without naming a type, it is a modelling decision wearing a
question mark. Decide it, note the assumption, and move on.

### How to run it

Sort everything you are unsure about into three piles:

- **Decide it yourself.** Anything a competent engineer would settle the same way. Most things land
  here. Decide, and move on without mentioning it.
- **Assume it.** You need an answer but the default is obvious. Note the assumption for the list
  below; do not spend a question on it.
- **Ask.** Only when the answers lead to genuinely different models and the answer lives in their
  head, not in the code.

Ask the third pile **one question at a time**, most consequential first, because an answer usually
collapses the questions behind it. Two to five for a normal feature; ten means you are asking things
you should be deciding.

Each question gets a headline sentence saying what turns on the answer, then two or three options,
never four. Lead with the one you would pick and mark it recommended, and say what each option gives
up rather than only what it does. A menu of equal options is you refusing to have a view.

If an answer surprises you or contradicts something said earlier, resolve it now rather than
carrying it forward.

Before you finish, say what you are assuming, in a short list, in plain product language. That is
their last chance to correct a premise cheaply, and it is far easier to read than a model.

**STOP.** When the questions are answered, tell them you are going away to work it through and will
come back with the document and walk them through it. Then go quiet: no phase headings, no running
commentary, no partial models. The next thing they should see is the finished document (Phase 10) and
the walkthrough that follows it.

---

## Phase 5 — Name the concepts

Working notes, not chat output. Build the list for yourself; it reaches the engineer in the
document.

One line each, carrying the Phase 1 definition rather than a fresh gloss:

```
<Name> — <the one-sentence definition from Phase 1> — <entity | value | enum> — <general | ours | plumbing>
```

If the definition drifted to fit a name you liked, you have it backwards. The definition was settled
first; the name serves it.

Classify each one:

- **Entity** — identity that persists. You would say "*that* one" and mean a specific instance
  across time. Gets an id.
- **Value** — no identity, compared by contents, immutable. Money, a date range, an email, a count.
  `@dataclass(frozen=True)`.
- **Enum** — a fixed set of possibilities. Every one of these, without exception (AGENTS.md, "Enums
  over strings").

### How to find them

- Take the nouns from the engineer's own description. "The customer pays ninety-nine a month and
  then burns tokens on top" names Subscription, Plan, TokenUsage, TokenCreditBalance, and Invoice.
  They said them; they just have not written them down.
- Take the seams from Phase 1. If prior art consistently separates two things you were treating as
  one, that is a missing concept until you can say why you are different.
- Anything with a lifecycle contributes a status enum.
- Anything the business has a rule about is a concept, even when it feels too small for a class.

### Name it so a new engineer can follow

Assume the reader has no domain background and is opening `types.py` for the first time. They should
guess what a concept is from its name alone, with no glossary and without having read what you read
in Phase 1.

**Name against the definition, not the code.** Put the Phase 1 sentence beside the candidate name
and check they point at the same thing. The tell for a bad name is that defending it means
describing how the system works: if your justification starts "well, we connect and then read the
grant tables, so...", you have named a code path.

Tests a name has to pass:

- **Would someone say this out loud?** "Check the database permission" is a thing people say. "Run
  the privilege audit and read the verdict" is not.
- **Does it need domain background to decode?** `EntitlementGrant`, `DispositionCode`,
  `RemittanceAdvice` all describe the right thing in a vocabulary the reader must acquire first.
  Prefer the plain word.
- **Is there an adjective on the front?** `ConnectedRepository`, `ActiveSubscription`,
  `VerifiedAccount`, `PaidInvoice`. An adjective is a state, not a kind. A repository does not become
  a different sort of thing once it is connected; it is the same thing with a fact attached. Drop the
  adjective and put the fact on the noun as a field, a status enum, or a method. The tell: if the
  adjective can be false and the thing survives, it is a state. The rare exception is a genuine
  subtype with its own behaviour, and it almost never is.
- **Is a word doing no work?** `Audit`, `Verdict`, `Record`, `Entry`, `Detail`, `Item`, `Result`,
  `Finding`, `Info`, `State` are usually padding on a name that was already complete. **Strip the
  padding word and see what is left.** If the remainder is a name you already used for something
  else, you have not found a second concept — you have split one concept in two, and the padding
  word is hiding the collision. Merge them.

**Apply these before you settle the name, not after.** A test you run on a name you have already
chosen becomes a search for reasons to keep it. Write the candidate, strip its padding, check the
collision, and only then commit.
- **Read a field access back as a sentence.** `check.permission == DatabasePermission.CAN_WRITE`
  reads. `record.disposition == DispositionCode.TERMINAL` needs a second pass.
- **Short and specific beats long and precise.** Two or three plain words. A name needing four is
  usually two concepts.
- **Is the plain noun ambiguous in this codebase?** Brevity loses to precision. `Repository` means a
  git repo to one reader and the storage class in every module to another; `Connection` could be a
  database, a vendor, or a socket. When the bare noun collides with another meaning the team uses
  daily, qualify it with the thing that disambiguates: `GitRepository`, not `Repository`.

  This is a **qualifier**, not an adjective describing a state. `GitRepository` says which kind of
  repository; `ConnectedRepository` says what happened to one. The first is part of the name, the
  second is a field. Test it: can the qualifier ever become false for that object? "Git" cannot;
  "connected" can.

Not a licence to be vague. `Thing`, `Data`, `Info` and the `Manager`/`Handler` family stay banned.
The target is simple *and* unambiguous: the shortest name a newcomer reads once and gets right, in
a codebase where other people are using the same words for other things.

### Smells to call out explicitly

These are the ones engineers miss, so name them in your proposal when you see them:

- **Two booleans that cannot both be true** are one enum with an illegal-state problem.
  `is_active` + `is_trialing` + `is_cancelled` is `SubscriptionStatus`.
- **A string you know the values of** is an enum.
- **An int whose unit you have to remember** is a value type. `TokenCount`, not `count: int`.
- **Fields that always travel together** are a concept. `period_start` + `period_end` is a
  `BillingPeriod`; `amount` + `currency` is `Money`.
- **A running total that is written to** usually wants to be an append-only record with the total
  derived. Mutated balances lose the audit trail and race under concurrency.
- **A concept the feature needs but nobody mentioned.** Raise it as a question: "there is no concept
  here for what happens when they stop paying — is that a state on Subscription or its own thing?"

If a concept is genuinely contested — two defensible models, and the choice changes everything
downstream — do not stop the session for it. Pick the one you would defend, and record the other in
the document's decisions section as the alternative you rejected and why. The engineer can overturn
it on review, with the whole model in front of them rather than one fragment.

---

## Phase 6 — Separate the general concepts from our specific rules

Nearly every feature is two things stuck together: **the concepts the domain has always had**, and
**the rules particular to how we do it**. The general layer is stable; the specific layer moves with
the business. Mixed together, every pricing tweak edits the definition of an invoice.

Mark each concept from Phase 5 one of three ways:

- **General** — exists in any product doing this kind of work, and means the same thing everywhere.
  Invoice, Money, BillingPeriod, Subscription.
- **Ours** — how *this* business does it. Our plan tiers, our dunning sequence, the rule that a case
  reopens within seven days. Meaningless to another company.
- **Plumbing** — no business meaning at all. Encryption, JWTs, config, logging, retries.

Two tests, in order. **Would another company in this line of business recognise it?** If yes it is
general; if it only makes sense with our pricing page open it is ours. Then: **does it mean anything
to the business at all?** If a support engineer would not recognise the word, it is plumbing.

### Where each one lives

**General does not mean shared infrastructure.** This is the mistake to avoid: a generic `Invoice`
is still billing, so it belongs in `modules/billing/types.py` underneath our specific rules, not in
`application/common`. Depth inside the module, not a move out of it. Only plumbing leaves.

| Mark | Where | Exposed as |
| --- | --- | --- |
| General | `modules/<module>/types.py`, the base layer | part of the module's domain |
| Ours | the same module, built on the general concepts | a **service** |
| Plumbing | `application/common` | a **helper** |

A service exposes business functionality; a helper provides plumbing (AGENTS.md, "What makes a
module"). `EncryptionHelper` and `JwtHelper`, never `CryptoService` for what is really "encrypt this
string".

### Three failures this catches

- **A general concept wearing our vocabulary.** `OperateBillingPeriod` for what is a date range with
  a start and an end. The name blocks reuse and implies specificity that is not there.
- **Our rules baked into a general concept.** An `Invoice` hardcoding our net-30 terms is not an
  invoice, it is our invoice, and the next payment model will fight it.
- **A business concept exiled to plumbing.** A `DateRange` in `application/common` that quietly
  rejects ranges longer than a billing period is a `BillingPeriod` in the wrong place, with a
  business rule now invisible to everyone reading the module.

Two cautions. Do not split on the strength of one caller: with one way of doing something you cannot
see the seam yet, and a premature abstraction costs more than a duplicate. And do not use the
general layer to dodge a hard question — a concept carrying a business rule stays in the specific
layer, however tempting it is to bury it lower.

Note which general concepts already exist in the repo, so nobody builds a second. The split goes in
the document, one line per concept.

---

## Phase 7 — Get the shape right

This is where models fail even when the nouns are correct, so spend the most time here.

Work one concept at a time, starting with the one the others hang off, so a wrong field on the
central concept does not silently propagate. Keep it all in your notes; the shapes reach the
engineer in the document, not in the chat.

If shaping a concept turns up a genuine business question you did not think to ask in Phase 4 — not
a modelling choice, an actual rule only they know — ask it. One question, plainly, then carry on. A
missing rule is worth the interruption; a field-level preference is not.

Take each concept in turn (the important ones; do not grind through trivial enums) and settle three
things. **Write them out fully, with real types on every field and every method.** A method named
without its signature is a wish, not a design: the argument and return types are where the modelling
mistakes hide.

**What it knows.** Every field, with its type. Each one is a value type, an enum, another concept,
or a primitive with an obvious unit. If a field needs a comment to explain it, it wants to be its
own type.

**What it does.** The behaviour that belongs on it, in domain language, with full signatures:

```python
@dataclass(frozen=True)
class TokenCreditBalance:
    remaining: TokenCount
    granted_at: datetime

    def debit(self, amount: TokenCount) -> "TokenCreditBalance": ...
    def can_cover(self, amount: TokenCount) -> bool: ...
    def is_exhausted(self) -> bool: ...

    @classmethod
    def granted(cls, amount: TokenCount, at: datetime) -> "TokenCreditBalance": ...
```

`Subscription.renew()`, not `update_subscription_status(sub, "active")`. Reading the signature
should tell you what the domain does: `debit` returning a new balance rather than `None` says the
type is immutable, and `can_cover` returning `bool` says the caller decides what to do about it.

**What must always be true.** The invariants, and where each is enforced: `__post_init__`, the
constructor, or the method that would otherwise break it. An invariant defended only by a comment is
a bug waiting to happen.

### When behaviour belongs to no object

Not every piece of behaviour has a home on a concept, and forcing it onto the nearest one is a
common way a good model goes wrong. Producing a user-facing warning about a credential is not
something a credential does. Deciding whether an account may run an agent is not something an
account does alone.

Three homes, and picking the right one matters:

- **On the concept**, when the behaviour needs only that concept's own state. `Invoice.is_overdue(now)`
  reads its own fields. This is the default and most behaviour lands here.
- **On a reader or writer**, when the decision spans concepts or needs something fetched. It is
  still a business decision, so it stays in the module and speaks the domain:
  `SubscriptionWriter.cancel(...)`. This is what `internals/<module>_reader.py` and
  `_writer.py` are for.
- **Nowhere in the domain**, when it is orchestration rather than a decision: fetching, retrying,
  logging, transactions, calling a vendor. That belongs to the caller.

The test that separates the second from the third: **does it make a business decision, or does it
move things around?** Branching is not the test — a method with five `if`s that only routes data is
orchestration, and a one-line method that decides whether a customer keeps access is domain logic.

Two failures to watch, pulling opposite ways:

- **Homeless behaviour bolted onto the nearest noun.** If a method needs a second concept's fields,
  or a lookup, to do its job, it does not belong on the first concept.
- **Entities emptied into readers and writers.** If every concept is fields with no methods and all
  the logic sits one layer out, you have a procedure with dataclasses. Behaviour that needs only one
  concept's own state belongs on that concept.

### Shape checks — apply to every concept

- **Behaviour lives with the data it touches.** If a method reads three fields off another object to
  decide something, it belongs on that other object.
- **A method is one thing the domain does, not one step of a procedure.** `renew()` is domain
  language; `set_status_and_bump_period_and_write()` is a transcript of the implementation.
- **No setter that lets a caller break an invariant.** If a balance may only move via `debit()` and
  `credit()`, there is no public setter.
- **Would a second, unrelated caller use this method as written?** If the signature only makes sense
  to one screen or one workflow, that shaping belongs on the caller's side (AGENTS.md, "Service /
  Reader / Writer pattern").
- **Nouns for classes, verbs for methods.** Re-check the anti-default here: every class in the model
  is a thing, every method is something done to it or by it.
- **Can this be constructed in an invalid state?** If yes, fix it now.
- **Is any field here only meaningful to one caller?** Presentation and workflow state belong to the
  caller, not on the domain object.

### Separate the shapes of an operation

Do the same for operations that cross a boundary. Their inputs and outputs are named types, not
loose arguments and tuples: `CreateApiKeyParams` and `CreateApiKeyResult` in
`modules/api_key/types.py` are the pattern to copy.

### Last, cut what does not earn its place

Everything up to here pushed you to add types: enums over strings, values over primitives, concepts
over fields. That pressure runs one way only, and left alone it gives you three types where one
would do. Now that the shapes are written, go back over them and delete what is not carrying weight.

**Delete each type in your head and ask what breaks.** If the answer is "nothing, the field would
just be a `str`", delete it for real.

Three patterns to cut:

- **A wrapper around one primitive, with no behaviour and no invariant.** A `ChargeDescription`
  holding a single string, no methods, refusing nothing, is a `str` in a costume. A value type earns its
  place by enforcing something (`TokenCount` refusing negatives), by carrying a unit that would
  otherwise be guessed, or by having behaviour. "It travels in a list and the list means something"
  is not enough — that meaning belongs to the field holding the list.
- **A type that is another type plus a couple of fields.** If `XFinding` is an `X` and two more
  values, that is one concept split in two, and every caller has to work out which half to hold. Put
  the fields beside each other on whatever owns them and delete the wrapper.
- **A type with one construction site and one read site.** A local variable that got promoted.

Keep the type when it enforces an invariant that would otherwise be a comment, when it is a fixed
set (always an enum), or when a bare primitive would let a caller pass the wrong thing with the
type checker staying silent.

The test, applied out loud: **what does a reader gain from this type that they lose without it?** If
you cannot answer in one clause, cut it.

**Now check the opposite failure.** Cutting is one direction. The other is a model of the right size
where nothing does anything: every concept is fields with getters, all the behaviour one layer out.
That pays the whole price of a domain model — types, mapping, layers — and buys none of the benefit,
because the rules are still scattered across procedures.

So go through the concepts once more and ask **what does this one do?**

- A concept whose rules live elsewhere should have them moved back, if they need only its own state.
- A concept that genuinely holds no rules is fine, as long as you can say why. Something that only
  carries data across a boundary is a data holder and always has been; that is not anemia.
- A concept with no rules *and* no reason to be a separate thing was already caught by the cut pass.

The line: **paying for a domain model you did not build is the waste.** Either the concept carries
its own rules, or it is honestly just data and named as such.

---

## Phase 8 — Cardinality, states, and CRUD

### Cardinality

Phase 2 settled which cluster changes together and who owns what. This is the smaller question left
over: for each pair, how many of one go with the other. An account has one subscription; a
subscription has many invoices. Write it down — it decides list endpoints, indexes, and whether a
field is a value or a collection.

### State machines

For every concept with a lifecycle, write the states and the legal transitions as an ASCII diagram
or a Mermaid `stateDiagram-v2`. Then check the hard question: is every illegal transition actually
prevented by a method, or merely undocumented? If a caller can assign `status = CANCELLED` on an
already-expired subscription, the state machine is decoration.

### CRUD, per concept

This is a modelling question, not an HTTP question. Do not write routes here. For each **entity**,
state what may be done to it, by whom, and what it means. Value types and enums do not get CRUD;
they are created and discarded with their owner.

Fill this in for every entity:

```
<Entity>
  Create  — who creates it, from what, and what must be true first
  Read    — who may read it, and the field combinations it is genuinely read by
  Update  — which fields are mutable, via which domain methods, and which are set-once
  Delete  — hard delete / soft delete (a status) / not deletable, and why
  Owner   — the module that owns the collection and is the only writer
```

The questions that make this phase worth doing:

- **What is a valid create?** If the entity cannot exist without three other things already existing,
  that precondition is a rule, and it belongs on a writer or a `@classmethod`, not spread over
  callers.
- **Which fields are immutable after creation?** Most engineers make everything mutable by default.
  An `account_id` on a subscription, the `amount` on an invoice, and the `created_at` on anything are
  set once. Say so now.
- **Is "update" actually a state transition?** If the only legal updates are status changes, there
  is no generic update; there are named domain methods (`cancel()`, `renew()`), and the writer
  exposes those, not `update(fields)`.
- **What does delete mean here?** Three honest answers: it is really gone; it is a terminal status
  and the row stays (anything financial, audited, or referenced by another entity); or it cannot be
  deleted at all. Choosing "hard delete" for something an invoice points at is a data-integrity bug
  you are agreeing to now.
- **Is anything append-only?** Usage records, ledger entries, and audit events are create-and-read.
  No update, no delete. Say it explicitly so nobody adds a setter later.
- **Who may read it?** Cross-account reads and admin-only reads are a modelling fact, not a
  controller detail. If only the owning account may read it, the query object carries the
  `account_id` and it is not optional.

Only after this is agreed does the HTTP shape follow, and it follows mechanically in Phase 9 (a
resource is a noun, the method carries the verb; AGENTS.md, "CRUD endpoints").

### Module boundary

Decide where this lives. A module owns a meaningful chunk of business capability, something you could
imagine running as its own service, with a real domain and a public API (AGENTS.md, "What makes a
module"). Answer honestly:

- Does this module own at least one concept, with its own `types.py` and its own collection?
- Or is it a thin pass-through to another module wearing full service/reader/writer ceremony?

If the second, say so and fold it into the module that owns the concept. Also check the cycle rule:
a lower-level module (`application`, `config`, `logger`) must not import a higher one.

Then place what you marked in Phase 6. The general domain concepts and our specific rules both
live in this module — the general ones underneath, our rules built on top. Only the plumbing goes to
`application/common`, as a helper, and prefer extending an existing helper to adding a second.

Check the direction of every dependency while you are here. Our rules may use the general concepts;
the general ones must not know about our rules. The module may use a helper; a helper that imports a
module is the cycle rule broken and a piece of plumbing that was never plumbing.

The CRUD table and the boundary decision go in the document; do not print them in the chat.

---

## Phase 9 — Map to the architecture

Only now do files appear. The mapping is mechanical. If it feels forced, the model is wrong: go back
to Phase 7 rather than bending the model to fit the layout.

### Backend

Detail in [backend-architecture.md](../../../docs/backend-architecture.md).

| From the model | Where it goes |
| --- | --- |
| Concepts, enums, value types, query objects, operation params/results | `modules/<module>/types.py` |
| Entity persisted to Mongo | a `BaseModel` dataclass in `types.py`, hydrated by the repository's `from_doc` |
| Invariants on construction | `__post_init__` on the dataclass |
| Behaviour on a concept | a method or `@classmethod` on that dataclass |
| Rules that span concepts, reading | `internals/<module>_reader.py` |
| Rules that span concepts, writing | `internals/<module>_writer.py` |
| Public API other modules call | `<module>_service.py` — thin delegation, no logic |
| Storage | `internals/store/<module>_repository.py`, extending `ApplicationRepository[Entity, Query]` |
| A read by a field combination | a typed query object passed to `query()`, never a raw Mongo filter |
| Failure modes | `errors.py`, an `AppError` subclass raised by reader/writer, rendered by the shared handler |

### CRUD table → HTTP and storage

Each row of the Phase 8 CRUD table lands in three places. Walk them in this order:

| CRUD decision | Repository | Reader / Writer | Route |
| --- | --- | --- | --- |
| Create with preconditions | inherited `create(entity)` | writer enforces the preconditions and raises from `errors.py` | `POST /resources` → **201** with the created resource |
| Read by id | inherited `find(id)` | reader returns the entity or raises not-found | `GET /resources/{id}` |
| Read by a field combination | inherited `query()` / `query_paginated()` with a typed query object | `reader.get_by_<thing>` calls the verb; **not** a `find_by_x` on the repository | `GET /resources` → `{"items": [...]}`, paginated adds `total_count`, `total_pages`, `page`, `size` |
| Update of mutable fields | inherited `update()` / `update_fields()` | writer patches; set-once fields are simply absent from its signature | `PATCH /resources/{id}` |
| Update that is a state transition | same verbs | writer exposes `cancel()` / `renew()`, and the entity method guards the transition | `PATCH /resources/{id}` with the new status, or `POST /resources/{id}/<noun>` for a sub-resource — never a verb route |
| Soft delete | `update_fields(id, {...})` | writer moves it to the terminal status | `DELETE /resources/{id}` → **204**, empty body |
| Hard delete | inherited `delete(id)` | writer checks nothing references it first | `DELETE /resources/{id}` → **204**, idempotent |
| Append-only | `create` only | writer has no update path; reader derives totals | create + read routes only |
| Owner-scoped read | the query object carries a non-optional `account_id` | reader takes the account as an argument, never defaults it | scoping comes from the authenticated principal, never from a client-supplied id |

Before writing anything, check:

- Every fixed set is an enum; every structured value is a dataclass; no bare dicts or tuples cross a
  boundary.
- The repository has only the generic CRUD verbs plus what genuinely cannot be expressed as one
  (upsert by natural key, get-or-create, atomic `$inc`, aggregation). `find_by_email` goes on the
  reader, not the repository.
- No `ObjectId`, `$set`, or `{"field": ...}` filter crosses the module's public surface.
- The service exposes only what another module would actually call.
- No module-level functions or constants that belong on a class.

### Frontend

Detail in [frontend-architecture.md](../../../docs/frontend-architecture.md) and
[frontend-design-system.md](../../../docs/frontend-design-system.md).

The same concepts appear on the frontend with the same names. A backend `SubscriptionStatus` enum
and a frontend union of raw strings are one modelling failure split across two languages.

| From the model | Where it goes |
| --- | --- |
| Concepts and DTOs | `types/<domain>.ts`, mirroring backend names exactly |
| Enums the backend owns | a matching TS enum or union, kept in step with the backend copy |
| API calls, one per CRUD row | a service in `services/`, returning typed responses |
| Shared state for a concept | a context in `contexts/` |
| Screens | pages in `pages/`, orchestrating context and services only |

Frontend rules that fall out of the model:

- **The enum is mirrored, not re-derived.** Adding a backend enum value the frontend mirrors means
  updating the frontend copy in the same PR and guarding any `Record<Enum, X>` lookup, or the page
  crashes on the new value.
- **Deletability is a model fact, not a button decision.** If the model says soft delete, the UI
  shows the terminal status somewhere; it does not make the row vanish and pretend.
- **Set-once fields are not editable inputs.** If the model says `account_id` is immutable after
  creation, it does not appear in the edit form.
- **Derived values are read, not recomputed.** If the backend derives a balance from usage records,
  the frontend renders that number. It does not sum the records itself and drift.

### The implementation order

Backend first, outside-in within it, frontend last:

1. `types.py` — concepts, enums, value types, query objects, params/results
2. The general domain concepts, then our specific rules on top of them
3. The repository, including `from_doc` and `_to_filter`
4. Reader and writer, and `errors.py` alongside them
5. The service
6. Routes, one per CRUD row
7. Frontend types mirroring the backend names
8. Frontend service, then context, then pages

Tests follow the convention in AGENTS.md ("Tests"), and mock only third-party APIs, never our own
internals. Say which steps are one PR and which are their own, so the work can be picked up in
pieces rather than landing as one large change.

---

## Phase 10 — Write the design document

The session's output is a document, not a chat log. A model nobody can review, disagree with, or
read in three months has not been delivered.

Write it to `docs/designs/<feature>.md` (unless the engineer names somewhere else — a GitHub issue
or an active plan file are both fine). Use `Write`, then tell them the path.

Structure it in this order, which is the order a reader needs it, not the order you produced it:

```markdown
# <Feature>

What this is
  Two sentences from Phase 0: what it does, who it is for, what changes when it ships.

The concepts
  The Phase 5 table with the Phase 6 marks — name, definition, entity/value/enum,
  general/ours/plumbing. Definitions in plain words, no implementation.

The model
  Per concept: what it knows, what it does, what must always be true.
  Relationships and cardinality. State machines as Mermaid stateDiagram-v2.

CRUD
  The Phase 8 table per entity: create preconditions, who may read it, what is
  mutable versus set-once, what delete means, which module owns it.

Where it lives
  The module decision. What sits in the general layer, what is ours on top of it,
  any plumbing that went to application/common. Say what is new, what is extended,
  and what already exists.

Existing behaviour
  What the module does today and how the new model carries each item forward.
  Anything changed or removed, with the reason and what breaks. A reviewer should
  be able to check this against the product and find nothing missing.

Implementation plan
  The Phase 9 mapping and the step order. Enough for someone else to start.

Decisions and open questions
  Every decision that could have gone the other way, with the reason in one line.
  Then the open questions, still written as questions.
```

Two rules for the writing. **The decisions section is the part that ages well**: in three months
nobody remembers why delete is soft, and the document is where that lives. And **open questions stay
open** — a guess dressed as a decision is worse than an admitted gap, because the next reader cannot
tell which is which.

Tell them the path, in one line. Do not summarise the document in the chat — you are about to walk
them through it properly.

---

## Phase 11 — Walk them through it, one piece at a time

**The session does not end when the file is written.** A document handed over in silence gets
skimmed and approved, and the modelling mistakes survive into the code. This phase is where the
engineer actually reviews it, and it is the second half of the interactive session.

Go through the model **one or two concepts at a time**, in dependency order: the concept the others
hang off first, then what builds on it. Never more than two in one message.

**Show the shape, then a real instance, then talk.** Prose describing a type makes the reader
assemble it in their head; six lines of code and one filled-in example land immediately. Never
describe a class in a sentence when you could show it.

Each concept gets four short parts, in this order:

**1. The shape.** The class, trimmed to what matters. Fields with types, the methods that carry
behaviour. Cut anything obvious.

```python
@dataclass(frozen=True)
class TokenCreditBalance:
    remaining: TokenCount
    granted_at: datetime

    def debit(self, amount: TokenCount) -> "TokenCreditBalance": ...
    def can_cover(self, amount: TokenCount) -> bool: ...
```

**2. A real instance**, with values a person recognises, and what happens to it:

```python
balance = TokenCreditBalance(remaining=TokenCount(500_000), granted_at=renewed_on)
balance.can_cover(TokenCount(120_000))   # True
balance.debit(TokenCount(120_000))       # a new balance of 380,000
```

Then the sentence that ties it to the product: *their plan renews on the 1st and they get a fresh
500,000; by mid-month they are down to 380,000, and the number only ever falls.*

**3. The decision that could have gone the other way**, in one or two lines, with why you chose as
you did.

**4. What you are least sure about**, if anything. One line.

Then ask: **does this match how you think about it?** Then wait.

Show a state machine as a diagram, never as prose. Three states and two transitions are instantly
readable drawn and hard work described:

```
TRIALING ──first payment clears──> LIVE ──payment fails──> PAST_DUE
                                    ^                         │
                                    └──── payment clears ─────┤
                                                              │
                                              7 days elapse ──> EXPIRED (terminal)
```

Take the answer and move on. If they change something, say in one line what it changes downstream
(a field that no longer belongs, a state that becomes unreachable) and carry the correction forward
rather than re-reading the whole model back at them.

Keep it tight. This is a review, not a re-run of Act 2:

- **Do not re-print the document.** They have it. You are walking them through the thinking, not the
  file. A few lines per concept, not the full field list.
- **Lead with the contested parts.** A concept with no real alternative gets one line and no
  question. Spend the conversation where a decision could genuinely have gone the other way.
- **Enums, values, and anything obvious go in a batch at the end.** "The rest are enums, nothing
  surprising in them" is a complete treatment.

After the concepts, four short rounds in this order, one question each.

**1. Lifecycle.** For anything with states, walk the transitions as a story rather than a diagram:
"a subscription starts in trial, goes live when the first payment clears, and can only reach expired
from past_due — never straight from live." Ask whether any transition is missing or should be
impossible.

**2. The CRUD API.** Per entity, in plain words, with the endpoint beside it:

```
Subscription
  Create   nobody. It appears when a payment clears upstream.       (no endpoint)
  Read     the account owner sees their own; admins see any.         GET /subscriptions/{id}
  Update   only the status, and only via cancel() or renew().        PATCH /subscriptions/{id}
  Delete   never. Cancelling sets a terminal status; the row stays.  (no endpoint)
```

For anything whose response shape is not obvious, show it once:

```
GET /subscriptions/sub_8f2a
{ "id": "sub_8f2a", "status": "past_due", "renews_on": "2026-09-01",
  "plan": { "name": "Pro", "amount": "99.00", "currency": "USD" } }
```

Ask the question that catches the real mistakes: **is there anything here you would expect to be
able to change that this model will not let you?** Set-once fields and the meaning of delete surface
here, or they surface in production.

**3. Existing behaviour.** Everything the module does today that the new model carries forward, and
anything you are proposing to change. Their call, and this is the moment for it.

**4. Open questions.** Read them out as questions. Some will be answerable now; the rest stay in the
document as questions.

Update the file as decisions land. When they have no more changes, go to Phase 12.

---

## Phase 12 — Raise the PR

The design gets reviewed by the team the same way code does, so the document goes up as a pull
request before anyone writes the implementation.

Ask first — one question, and take no for an answer:

> The design is settled. Shall I put it up as a PR so the team can review the model before we build?

If yes:

1. **Branch.** Never commit to main. `docs/<feature>-design`.
2. **Commit** just the design document. Nothing else: no types, no scaffolding, no unrelated
   formatting the tooling touched. Use the engineer's own configured git identity — do not set or
   override `user.email` — and add no Claude co-author trailer.
3. **Open the PR** following the repo's convention (`.claude/skills/pr-conventions`): a `docs:`
   title, and a description that gives the business context rather than a diff summary.
4. **Hand back the URL**, in one line.

Write the PR description for a reviewer who was not in the session:

- What the feature is, in two sentences.
- The concepts, named, with one line each.
- The two or three decisions that could have gone the other way, with the reasoning.
- Anything the model changes about existing behaviour, called out plainly so nobody misses it.
- The open questions, still as questions.

Do not implement anything. The document is the deliverable; the code is a separate ticket, informed
by the implementation plan already in it.

---

## Worked reference: one good, one bad

Point the engineer at both. They are in this repo.

**Good — `src/apps/backend/modules/api_key/types.py`.** `ApiKeyStatus` and `ApiKeyKind` as enums
rather than strings. A frozen `ApiKeyQuery` that enforces a real invariant in `__post_init__`
(`expires_before` and `expired_before` are mutually exclusive because their null semantics differ).
The `ApiKey` entity. Separate `CreateApiKeyParams` and `CreateApiKeyResult`, so the input and output
shapes of an operation are each named types. Read this before writing a new `types.py`.

**Bad — `src/apps/backend/modules/billing`.** It has `billing_service.py`, `internals/billing_reader.py`,
and `errors.py`, and owns nothing: no `types.py`, no entity, no repository, no collection.
`BillingService.get_balance()` delegates to `BillingReader.get_balance()`, which reads an `app_id`
off settings and calls `OperatexService.get_account_balance()`. The one type it returns,
`AccountBalance`, is borrowed from `operatex`.

Two failures in one small module. It is ceremony around a single call to somewhere else, which is
what "not a module" looks like in practice. And for a product that charges a monthly fee plus token
usage, the billing domain (Subscription, Plan, TokenUsage, TokenCreditBalance, entitlement, the
states an account moves through when it stops paying) does not exist anywhere in the codebase. A
module named `billing` promises a domain and delivers a getter. When the real concepts arrive they
will have nowhere to live and will end up spread across settings, operatex, and the UI as strings
and integers.

Note the shortcut: nobody asked what a subscription or a balance *is*. The model was taken from the
shape of the vendor call we happened to make, so the only concept in the module is the one that
vendor returns. That is the failure Phase 1 exists to catch.

---

## Session self-check

**Did you interview properly?**

- You asked what they were building before proposing anything.
- Every question was about the business, with no type in it, asked one at a time with a
  recommendation rather than a menu, and carried a concrete example of each answer.
- Every question was answerable by someone who knows neither the domain nor the existing code: you
  said what you found, then asked the business question on top of it.
- You audited what the module does today rather than sampling it, and formed a view once instead of
  revising it in public three times.
- You said plainly where the existing model or its behaviour is wrong, sized the correction, and
  left the decision to them.

**Are the concepts right?**

- You wrote a one-sentence definition of every concept, in plain words, with no mention of our
  implementation, before choosing any name.
- The model has the durable nouns of the domain, not just the feature's own question. If the feature
  were cancelled tomorrow, everything that would still exist is in there and named.
- The top-level concept is the thing the user acts on and would name themselves. You did not descend
  past it into one of its parts and model that instead.
- No level exists only to hold fields. Every concept can be addressed on its own, and no name ends
  in `...Permissions`, `...Settings`, `...Options`, or `...Details` where those attributes belong on
  the thing named before them.
- Where the concept is a kind of something the codebase already has, you extended that concept
  rather than adding a parallel type beside it.
- The concepts are layered, not a flat list of peers: a base concept owning identity, things that
  belong to it, then states on those. Every "the X of a Y" has its Y, and no child repeats the
  parent's identity fields.
- You named which cluster must stay consistent together and the one entity that is the way into it.
  Other clusters are referenced by id, not by object, and no operation changes two of them at once.
- Every concept is marked general, ours, or plumbing. The general ones carry none of our rules, and
  the business concepts stayed in their module rather than being exiled to `application/common`.

**Are the names right?**

- Every class is a noun. None is a verb (`ProcessPayment`) or a verb in disguise
  (`PaymentProcessor`, `AccessChecker`).
- No name has an adjective bolted on (`ConnectedRepository`). Each such state is a field, a status
  enum, or a method on the plain noun.
- No two concepts differ only by a padding word (`Finding`, `Result`, `State`).
- No name is ambiguous with another meaning the team uses daily. Where the bare noun collides, it
  carries a qualifier that can never be false, not a state.
- A newcomer reads each name once and gets it right. None can only be justified by describing how
  the system works, and none imported jargon from what you read.

**Are the shapes right?**

- Every fixed set is an enum, and no `dict` or bare `str` survived into the model.
- Every class is written out with types on every field and method.
- Every concept with a lifecycle has a state machine, and illegal transitions are prevented by
  methods rather than by documentation.
- Every entity has a CRUD row, with an explicit answer on immutability and on what delete means.
- You ran the cut pass: nothing left is a wrapper around one primitive with no behaviour, another
  type plus two fields, or a promoted local variable.
- No free function takes a concept as its first argument.
- Behaviour sits where it belongs: on the concept when it needs only that concept's state, on a
  reader or writer when the decision spans concepts, and outside the domain when it is only
  orchestration. Nothing homeless was bolted onto the nearest noun.
- No concept is fields with no rules unless you can say why it is honestly just data.
- Files were chosen only after the model was settled.

**Did you stay quiet, then actually deliver?**

- You wrote nothing between the last question and the walkthrough, beyond at most one line saying
  you were going away to work. No progress notes, findings, definitions, prior art, or tables. You
  never narrated intent ("let me..."), waiting, or tool mechanics.
- You walked them through it one or two concepts at a time and waited after each, rather than
  handing over a file and a summary.
- You showed shapes rather than describing them: the class, a filled-in instance, a payload, a state
  diagram. No concept was explained in prose alone.
- Existing behaviour was walked item by item, and anything dropped was called out as a deliberate
  removal rather than left as a silence.
- The document is at `docs/designs/<feature>.md` with the concepts, model, CRUD, implementation
  plan, and why each decision went the way it did. Open questions are still questions.
- You updated the document with whatever they changed, and offered to raise the PR rather than
  assuming it.
