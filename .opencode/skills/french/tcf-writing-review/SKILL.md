---
name: tcf-writing-review
description: Review and grade a user's TCF Expression Écrite production (Tâche 1, 2 or 3) against the official FEI criteria - respect de la consigne, développement des faits, compétence linguistique, cohérence et cohésion - with anchored comments, italic corrections, a score /20 mapped to CEFR and NCLC levels, and a model rewrite. Use when the user asks to correct or grade a TCF essay, "chấm bài TCF", "sửa bài expression écrite", "review Tâche 1/2/3", "điểm TCF bao nhiêu", or pastes a French exam production for feedback.
---

# TCF Écrit — Chấm bài theo tiêu chí giám khảo

Grade the user's TCF writing like a trained FEI corrector would: criteria-based scoring first, language polish second. Works for any tâche; detect which one from length/format before grading.

## Core Rule

Score what is on the page against **official criteria**, not against your taste:

1. **Respect de la consigne** — all required points treated? correct text type & register? length inside min/max?
2. **Capacité à présenter les faits / développer** — information clear and relevant? examples appropriate? content developed (not listed)?
3. **Compétence linguistique** — étendue du lexique, correction grammaticale, orthographe, élaboration des phrases.
4. **Cohérence et cohésion** — logical organization, paragraphing, connecteurs, readability.

Official anchors per criterion and conversions: read `references/scoring-grid.md` before scoring.

## Hard Gates (check BEFORE anything else)

These can sink the copy to « A1 non atteint » regardless of quality — verify each explicitly:

- [ ] Word count inside the tâche's limits (FEI rule: *1 mot = ensemble entre deux espaces*; `l'école` = 1 word). Limits: T1 60–120 · T2 120–150 · T3 120–180 (P1 40–60, P2 80–120).
- [ ] On topic; no sentences copied from consigne/documents.
- [ ] Task actually done in full (T3 = both parts, both documents).
- [ ] All consigne points covered.

If a gate fails: say so first, grade anyway for learning value, and show how far off the limit it was.

## Workflow

1. **Identify the tâche** from format and length; restate its requirements as a checklist.
2. **Run hard gates**, report results.
3. **Unit-by-unit review**: split into sentences (local problems) or paragraphs (logic/coherence problems). For each unit:
   - Short anchored comments quoting exact words — explanation in Vietnamese, quote in French (`"je suis aller" → "je suis allé(e)" — sai quá khứ hợp ngữ` / `hors sujet` / `répétition` / `registre trop familier`).
   - Italic corrected rewrite right after the unit, close to the student's meaning — stable B2 standard, not over-polished C2.
4. **Score**: rate each of the 4 criteria on the /5 anchor scale from `references/scoring-grid.md`, sum to a note **/20**, convert to CEFR level; if the user mentions TCF Canada, also give the estimated NCLC band. Score the ORIGINAL text, never the rewrite.
5. **Feedback block**: separate (a) issues blocking the target level from (b) upgrades toward the next one. Max 5 bullets total, concrete.
6. **Model rewrite**: full model at stable B2+ respecting the SAME consigne and word limits; report its word count too.
7. **Priority list**: top-3 fixes for their next attempt (e.g., `1. Học thuộc 5 connecteurs tier-1`, `2. Ôn imparfait vs PC`, `3. Đếm từ trước khi nộp`).

## Output Format

```
## Kết quả
Tâche: N — ~X mots (giới hạn A–B ✅/❌)
| Tiêu chí | Điểm /5 |
... 4 rows ...
Note: X/20 → CECRL B2 (+ NCLC 7 nếu TCF Canada)

## Nhận xét từng câu
[unit] comment + *rewrite*
...

## Để đạt mục tiêu
(a) blockers ... (b) upgrades ...

## Bài mẫu tham khảo (~Y mots)
[full model]

## Ưu tiên lần sau
1..2..3..
```

Default output in chat. If the user asks to save, write `tcf-tache<N>-<slug>.md` in the workspace root.

## Notion Question Banks

The user's Notion hub "Tổng hợp đề thi Viết (Expression écrite) — TCF" (page id `3c0f312e-ab25-80ab-a46d-d96586d799e4`) has child databases per tâche: T1 `dee4fb0f-db50-46f5-bf3c-ddcbe2a2a640`, T2 `8c30d919-5171-4a7b-91c6-d89fa0da95ad`, T3 `1d14187d-3558-43e1-a15e-2b99208ecb73`. They are currently NOT shared with the integration (404). If the user asks to pull a random đề: ask them to share those databases with the integration "CodeAgent" first, then query by `notion_find`/data-source tools. Fallback: generate a fresh realistic consigne using the recurring themes in the tcf-tacheN skills.

## Quality Bar

- Comments are short, anchored to real strings in the student's text, never generic praise.
- Corrections preserve the student's intended meaning.
- The score reflects the original draft; every point deduction is backed by an evidence quote.
- Model rewrite obeys the same word limits and reports its count honestly.
