# UI skill selection

Consider Anthropic Frontend Design for applicable frontend work. Select Frontend Design, `emil-design-eng`, or both according to the task and actual skill content. There is no fixed Emil priority. Honor user overrides and preserve product requirements, the existing design system, accessibility, and task speed. Pure backend, invisible build configuration, or unrelated research work does not require loading complete UI design skills.

| Task | Useful selection |
| --- | --- |
| New page or changed information structure | Often both. Frontend Design for visual direction and hierarchy, Emil for components and interaction feedback. |
| Local form, interaction, or motion repair | Consider Frontend Design and emphasize Emil. Keep the existing components and style. |
| Visual direction or brand presentation | Emphasize Frontend Design. Add Emil when interaction needs it. |
| Copy, spacing, or static hierarchy | Frontend Design can suffice. Validate only the affected behavior and viewports. |

These are content and task-fit choices, not measured performance rankings. Both skills cover usability. Read the selected content instead of treating this table as an exclusive capability boundary. For new visual work, use real content and a brief plan that fits the user's requirements. Aesthetic examples are not universal bans on cards, labels, numbers, or arrows. Missing information that changes the result can require clarification. Existing clear requirements and authorization do not need a new approval gate.

Sources: [Anthropic Frontend Design](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design) (Apache-2.0) and [Emil](https://github.com/emilkowalski/skills). Keep installed source versions and any local differences in private evidence. This repository does not bundle either skill or establish its installation in another environment.

Find each selected skill in the current environment's skill catalog. Read its actual `SKILL.md` and only the references relevant to the task. Resolve references through that skill's own provider or directory. Do not assume a machine-specific path or embed third-party skill text here. If a dependency is absent, reuse its installation owner or the available authorized skill-installer workflow. State an access or installation failure and its effect accurately. Do not claim a skill was read when it was unavailable.

Give the assigned engineer the UI goal, target component or view, product constraints, existing design system, expected interaction, and acceptance criteria. Require actual application of the skill, rather than a name in the handoff. Keep evidence in private task records: the source/version read where available, applicable sections, concrete choices, reasons, and validation limits.

Useful decisions include whether motion serves a real interaction, how feedback preserves task speed, and how keyboard, focus, reduced-motion, touch, and narrow-screen behavior remain usable. Preserve the current design system and user requirements. Add motion only for a useful purpose. Do not automatically apply every animation technique or load every skill from the upstream collection. Other skills retain their own applicability and explicit-invocation rules.

For a UI code review, follow the selected skill's applicable review format. When using Emil, use its required Before/After/Why table. Tie findings to observed interface behavior and scoped source. Do not invent issues to fill the table. A real accessibility or behavior failure justifies a targeted correction and affected checks. A preference alone does not justify repeating completed work, unchanged tests, or release review.

Apply this selection rule to unfinished UI work. Keep accepted candidates moving through the existing release path. Record any concrete design issue that changes readiness, rather than adding a general design approval gate. Model settings, resource ownership, action permissions, ASD-STE100 handoffs, and completion-notification rules remain unchanged.

For UI implementation and code review, also use [the core Ponytail coding guidance](coding.md). It governs unnecessary code complexity alongside the selected design guidance. Preserve both the requested interface behavior and the required quality checks.
