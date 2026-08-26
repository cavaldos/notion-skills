---
name: french-structure-highlight
description: Apply consistent color-coded highlighting to French sentence structure - sujet, verbe, COD/COI/attribut, proposition relative, comparatif/superlatif, attribut de l'objet, plus collocation overlay - via rich-text annotations in Notion pages/tables or plain markdown. Use when asked to highlight, color-code, or format French sentences by grammar role, e.g. "highlight câu tiếng Pháp", "tô màu cấu trúc tiếng Pháp", "format lại đoạn văn français", "tô màu chủ ngữ động từ tiếng Pháp", "mệnh đề quan hệ màu xám". Touches French text only; never edits wording.
---

# Highlight French Sentence Structure

Color-code the grammatical skeleton of French sentences so anyone can read the S-V-O structure at a glance. Sister skill to `english-structure-highlight` (same 7-layer legend) adapted to French grammar. Built for study pages in Notion but works on any French prose.

## Core Rule

- **Preserve text verbatim.** This skill changes *annotations only* (color, bold, italic, underline). Never add, remove, reword, or "fix" accents/agreements in the target text unless explicitly asked.
- **One legend for all sentences.** Every sentence in the document must follow the exact same mapping from grammar role to style. Consistency beats completeness.
- **French only by default.** Do not annotate Vietnamese translations or plans in the same table.
- **Default means untouched.** Text outside the seven legend layers keeps Notion's pure default state — every annotation flag `false`, `color: "default"`. Never restyle default territory: transitions (`pourtant`, `en effet`, `donc`), adverbial clauses (`quand`, `parce que`, `si`, `bien que`), prepositional phrases, purpose infinitives (`pour + inf`, `afin de + inf`) receive zero formatting, including overlays.
- **Main clause only.** Like its English sister skill, only the main clause gets S-V-O annotation. Adverbial subordinate clauses stay fully default *including* their internal subject and verb. Exception: relative clauses are always gray wherever they nest.

## Default Legend

Use this when the user does not specify colors. Apply it **immediately without waiting for confirmation**; include the legend table in your final summary and note that any entry can be overridden.

| Grammar role | Annotation (`annotations` values) |
| --- | --- |
| Sujet (chủ ngữ) | `color: "yellow"` |
| Verbe principal (động từ chính) | `color: "red"`, `bold: true` |
| COD / COI / attribut du sujet (tân ngữ / bổ ngữ chủ) | `color: "blue"`, `italic: true` |
| Proposition relative (mệnh đề quan hệ) | `color: "gray"` |
| Comparatif / superlatif (so sánh) | `color: "pink"` |
| Attribut de l'objet (bổ ngữ cho tân ngữ) | `color: "blue"`, `underline: true` |
| Collocation (overlay) | merge `italic: true` into the segment's existing annotations — keep the role's color |
| Everything else (transitions, adverbiales, compléments circonstanciels…) | all defaults |

Notes:

- Red + bold carries the strongest visual weight, which is why the verb uses it by default.
- The legend is capped at **7 layers**, identical to the English version. Do not add more colors without an explicit user request.

## Grammar Classification Rules

### Sujet → yellow

- The full noun phrase of a finite clause, including determiners (`le`, `une`, `des`, `ces`, `mon`) and adjectives on either side of the noun — `une grande entreprise`, `les employés fidèles`, `le salaire seul`. Compound subjects are marked whole (`la rémunération et la reconnaissance`).
- Subject pronouns: `je, tu, il, elle, nous, vous, ils, elles`; stressed pronouns used as subject (`moi`, `eux`) too.
- Impersonal `il` is still the grammatical subject → yellow (`Il faut`, `Il arrive que`). In `C'est` / `Ce sont`, mark `C'` / `Ce` yellow and the verb red; in `il y a`, mark `Il` yellow and `y a` as one red segment.
- Disjunctive emphatic subjects (`Les employés, eux, ...`) → both segments yellow.

### Verbe principal → red + bold

- The conjugated verb **plus everything of its verbal cluster**:
  - Auxiliaries and past participles in compound tenses are one segment: `a été augmenté`, `ont travaillé`, `est parti`.
  - Semi-auxiliary constructions are one segment: `peut offrir`, `doit garantir`, `va partir` (futur proche), `vient de partir` (passé récent).
  - Reflexive pronouns belong to the verb segment: `se développe`, `s'améliore`.
  - Negation wraps into the red segment when it surrounds that same verb cluster: `ne suffit plus`, `n'a pas travaillé`.
- **Precedence rule:** object pronouns (`me, te, le, la, les, lui, leur, y, en`) sitting inside the verbal cluster win over red — they become their own blue segments, splitting the red one: `je ne le vois pas` → `ne`(red) + `le`(blue) + `vois pas`(red).
- Imperatives count (`Écoutez`, `Soyez`). `Voici` / `Voilà` count as verbs.

### Objet slot → blue + italic

- Direct objects: noun phrases with determiners — `aucune raison financière`, `leurs employés`.
- Indirect objects governed by the verb: `parle à ses collègues` → `à ses collègues` blue. Free circumstantial complements stay default (`dans le bureau`, `depuis lundi`).
- Attribut du sujet after linking verbs (`être`, `devenir`, `sembler`, `paraître`, `rester`, `demeurer`, `avoir l'air`, `passer pour`): `est l'actif le plus précieux` → whole slot blue.
- Complétives (`que`-clauses) filling the object slot: `voient que leur effort est récompensé` → the `que`-clause is one blue segment.
- Object pronouns anywhere before the verb → blue (`Ces avantages les encouragent` → `les` blue).
- **NOT blue:** catenative/purpose infinitive phrases (`pour garder les talents`, `de chercher ailleurs`, `à rester`) — default territory, mirroring the English skill's treatment of infinitives.

### Proposition relative → gray

- Clauses introduced by `qui, que, quoi, dont, où, lequel/laquelle/lequel...` and reduced relatives → gray, including the relative's own verb and object, wherever it nests.
- Complétives (`savoir que...`) are **not** relatives: if they fill an object slot they are blue per the objet rule; otherwise default.

### Comparatif / superlatif → pink

- Comparative/superlative forms and connectors: `plus/moins/aussi ... que`, `meilleur`, `pire`, `mieux`, `le plus`, `tel que`, `comparé à`, `par rapport à`. Mark the comparative phrase plus its connector when adjacent.
- Precedence: when the comparative form fills the objet/attribut slot (`est la meilleure solution`), blue wins — pink is reserved for comparatives in unmarked territory (`plus longtemps`, `plutôt que d'attendre`).

### Attribut de l'objet → blue + underline

- The element completing the object after `rendre`, `croire`, `considérer ... comme`, `trouver`, `laisser`, `faire`: `ils rendent les employés productifs` → `productifs` blue+underline; the COD `les employés` stays plain blue italic.

### Collocation overlay → italic

- Natural multi-word chunks (`prendre des vacances`, `réduire le stress`, `équilibre vie-travail`, `faire attention`). Overlay layer applied last:
  1. Take each chunk's existing segment annotations and set `italic: true`; keep the role's color.
  2. Lands **only on already-colored objet/attribut segments** (blue family). Chunks in default territory are left completely untouched.
  3. Never italicize subjects, verbs, or relatives *solely* because they belong to a chunk — grammar roles always win.

### NOT annotated (leave default)

- Adverbial clauses introduced by `quand, lorsque, parce que, puisque, si, bien que, afin que, après que, alors que` — fully default including internal S-V-O.
- Transitions: `cependant, pourtant, en effet, par conséquent, ainsi, d'une part ... d'autre part`.
- Prepositional phrases and purpose/catenative infinitives (`pour réduire`, `afin de garantir`, `à rester`).

### Compound sentences

Annotate each finite clause independently, splitting at `mais`, `donc`, `or`, `ni`, `car`, `;`, `, et`.

## French Typography Pitfalls

- Preserve typographic apostrophes (`’` vs `'`) exactly as written; concatenation check must reproduce them byte-for-byte.
- Elisions split words: `l'actif`, `n'a`, `qu'il`. Keep elision characters attached to whichever segment owns the word; never drop the space after an elided article when it separates two colored segments.
- Preserve espaces insécables before `: ; ! ?` and guillemets `« »` if present in the source cell.
- Ligature `œ` must survive untouched.

## Notion Implementation

### Reading

1. `notion_read_page` with `content_format: "markdown"` → locate the target table block ID and row block IDs.
2. `notion_retrieve_block` (`format: "json"`) on **each row** you will modify → capture exact current cells. Identify which column holds the French text before touching anything.

### Updating

3. Use `notion_update_block` with payload shape:

```json
{
  "type": "table_row",
  "table_row": { "cells": [ [/*cell0*/], [/*cell1*/], /*...one flat array per cell*/ ] }
}
```

Hard-won pitfalls — do not skip:

- Each cell must be a **flat** array of rich_text segments. Double-nesting a cell as `[[{...}]]` fails with `400 validation_error: body.table_row.cells[0][0] should be an object`.
- Segment shape: `{"type":"text","text":{"content":"..."},"annotations":{"bold":false,"italic":false,"strikethrough":false,"underline":false,"code":false,"color":"..."}}`. Specify every flag explicitly — omitted flags may reset to defaults.
- Valid `color` values: `default, gray, brown, orange, yellow, green, blue, purple, pink, red` plus `<name>_background` variants.
- The API **replaces the whole row**. Re-send ALL cells; copy untouched cells byte-for-byte from the retrieved JSON.
- Batch at most 2–3 row updates per message. Larger parallel payloads risk truncation → `JSON Parse error: Unterminated string`. Retry truncated rows individually.
- Verification: re-read the page afterwards and spot-check one row.

### Segment-building checklist

Before sending an update, verify:

1. Concatenating every segment's `text.content` reproduces the original cell string exactly — same spaces, apostrophes (`’`), punctuation, trailing spaces, intentional typos.
2. Leading/trailing spaces live inside adjacent segments; a dropped space between two colored segments merges words visually.
3. No segment has empty content except deliberate single-space spacers.

## Workflow

1. **Apply legend immediately** — use the default legend (or user's custom colors) right away. Do NOT ask for confirmation. State the legend used in the final summary.
2. **Locate targets** — read the page; identify rows/blocks holding French text.
3. **Retrieve exact JSON** for every row to modify.
4. **Analyze** each sentence into roles per the rules above; produce a segmentation plan (identify main clause first, then nest gray relatives, then fill slots).
5. **Build segment arrays**, run the checklist.
6. **Update rows** in small batches; verify by reading back; summarize what was applied.

## Worked Examples

Example A — attribut with superlative precedence + negation in verb segment:

Text: `Les employés fidèles sont l’actif le plus précieux d’une entreprise. Cependant, dans un marché concurrentiel, le salaire seul ne suffit plus pour garder les talents.`

```
[default   ] ""
[yellow    ] "Les employés fidèles"
[red+bold  ] " sont"
[blue+it   ] " l’actif le plus précieux d’une entreprise"
[default   ] ". Cependant, dans un marché concurrentiel, "
[yellow    ] "le salaire seul"
[red+bold  ] " ne suffit plus"
[default   ] " pour garder les talents."
```

(`le plus précieux` stays blue: the superlative fills the attribut slot — blue wins.)

Example B — adverbial clause fully default, negation + object slot in main clause:

Text: `Quand les salariés voient que leur effort est récompensé, ils n’ont aucune raison financière de chercher ailleurs.`

```
[default   ] "Quand les salariés voient que leur effort est récompensé,"
[yellow    ] " ils"
[red+bold  ] " n’ont"
[blue+it   ] " aucune raison financière"
[default   ] " de chercher ailleurs."
```

Example C — relative clause + comparative in unmarked territory:

Text: `Les entreprises qui écoutent leurs équipes retiennent leurs employés plus longtemps.`

```
[default   ] ""
[yellow    ] "Les entreprises"
[gray      ] " qui écoutent leurs équipes"
[default   ] " "
[red+bold  ] " retiennent"
[blue+it   ] " leurs employés"
[pink      ] " plus longtemps"
[default   ] "."
```

Example D — object pronoun precedence inside the verbal cluster:

Text: `Ces avantages les encouragent à rester.`

```
[default   ] ""
[yellow    ] "Ces avantages"
[default   ] " "
[blue+it   ] "les"
[red+bold  ] " encouragent"
[default   ] " à rester."
```

Full annotation presets and a ready-to-paste segment array: see `references/annotation-presets.json`.

## Constraints

- Formatting skill, not editing skill — zero wording changes; list spotted errors (accents, agreements, conjugations) at the end of your reply instead of fixing silently.
- Never touch columns/languages outside the requested target.
- If the user asks for different colors mid-task, rebuild affected rows with the new legend uniformly — never mix legends within one document.
