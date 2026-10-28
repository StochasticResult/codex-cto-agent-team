# ASD-STE100 for handoffs

Apply this guidance to English PM task instructions, engineer handoffs, and questions for other people. Use the official [ASD-STE100 standard, Issue 9, 2025-01-15](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf): Part 1 for writing rules and Part 2 for the dictionary. The [official FAQ](https://www.asd-ste100.org/STE_faq.html) gives supporting information. Get a reference through the [official download page](https://www.asd-ste100.org/STE_downloads.html) if necessary. Keep a local reference outside the public repository. Do not publish the standard, an extracted dictionary, or a substitute word list.

This file gives application guidance. It does not replace the standard. Short sentences alone do not establish compliance. Keep Chinese user summaries clear. Do not identify Chinese text as formally compliant with this English standard.

## Draft

Keep task identity, authorization, target, input files, write resources, acceptance criteria, evidence, and delivery ownership in labeled fields. Keep exact values as data. Put actions in numbered work steps. Use a separate item for each question. This team's one-question-per-item convention is not a quoted STE rule.

Use the applicable rules in the source, including vocabulary, grammar, sentence construction, and consistency. For procedures, apply section 5's 20-word sentence limit, command form, and separation of instructions. Rule 5.2 permits simultaneous actions in one sentence. Separate other instructions into sentences. Page 1-5-3 also permits multiple sentences in a work step for simultaneous actions or an immediate result after an action. Preserve these relationships when you divide work steps. Put a necessary condition before its action. For descriptions, apply section 6. Apply section 8's counting method, rather than a whitespace counter. Preserve necessary context when you divide a sentence.

## Check words and terms

For each general word, inspect its Part 2 entry: approval, part of speech, intended meaning, and permitted form. Apply rules 1.1-1.4. A familiar word is not automatically approved in every use. For example, the dictionary approves `check` and `test` as nouns, not as general verbs. Use an approved construction for the intended action.

For a technical noun or verb, apply rules 1.5-1.13 and the applicable multi-word-noun rules in section 2. Keep a task glossary with the exact term, meaning, part of speech, source, category, and approval basis. Use the project's authorized terminology. Do not classify ordinary unapproved wording as technical language to bypass the dictionary. A technical noun does not automatically become a permitted verb. Prefer a dictionary-approved construction when it expresses the same action.

Treat software concepts as subject-field terms only where the category fits. For example, `file` is a computer-science technical noun under rule 1.5, category 19. A role abbreviation such as PM means product manager in this team. Define an unfamiliar abbreviation for its reader. STE does not prescribe the project's abbreviation system or unit format. Use the applicable project requirements for units, symbols, precision, and conversions. Verify the value as well as the text.

Preserve exact filenames, paths, commands, parameters, API names, and code identifiers. Show literals distinctly, for example, `team_state.py`, `--require-ready`, or `threadId`. Explain their purpose with checked English. Do not rename an identifier to satisfy a dictionary check. Apply section 8 to quoted text, identifiers, numbers with units, and abbreviations. A counting exception does not make arbitrary prose compliant. Do not hide an instruction inside quoted data.

## Review status

Keep three states separate in the private task record:

| State | Evidence |
| --- | --- |
| Draft | Text prepared with STE as the target. Source or language checks can remain open. |
| Checked | Named rules, dictionary entries, and technical terms examined against an identified issue. Record the text revision, reviewer, findings, and gaps. |
| Verified compliance | A competent reviewer completed the applicable rule, vocabulary, and terminology checks for that exact text revision. Retain the evidence and scope. |

Do not infer verified compliance from an AI draft, a word counter, or a software checker. A partial review remains partial. If a source or required expertise is unavailable, state the gap. Do not invent a rule number or silently certify the text. Language checks do not replace technical acceptance or action authorization.

## Short human examples

These are example work steps, not complete task records. Add the required task data separately.

PM task instructions:

1. Read the file "task.json".
2. Do the test.
3. Write the result in "result.json".

Engineer handoff:

1. Read the file "test_plan.md".
2. Do the test.
3. Write the result in "result.json".
4. Do not change "roster.json".

Question for a person:

- Is the test result correct?

The example check used Issue 9, Part 1 sections 1, 3-5, and 8, and Part 2 entries for the general words. `read`, `do`, `write`, `change`, and `be` have the applicable verb uses. `test` and `result` have noun uses. `correct` has an adjective use. The filenames are literal data. The five distinct sentence forms have 4, 3, 5, 4, and 5 words respectively under the applicable counting rules. This is a source-based check of these examples, not formal certification of this guide or future handoffs.
