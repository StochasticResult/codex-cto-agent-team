# UI skill selection

Start with explicit user or project design direction and find matching skills in the available catalog. Consider Anthropic Frontend Design for applicable frontend work. Select Frontend Design, `emil-design-eng`, or both as useful alongside that specific guidance. There is no fixed Emil priority. Preserve product requirements, the existing design system, accessibility, and task speed. Pure backend, invisible build configuration, or unrelated research work does not require loading complete UI design skills.

| Task | Useful selection |
| --- | --- |
| New page or changed information structure | Often both. Frontend Design for visual direction and hierarchy, Emil for components and interaction feedback. |
| Local form, interaction, or motion repair | Consider Frontend Design and emphasize Emil. Keep the existing components and style. |
| Visual direction or brand presentation | Emphasize Frontend Design. Add Emil when interaction needs it. |
| Copy, spacing, or static hierarchy | Frontend Design can suffice. Validate only the affected behavior and viewports. |

These are content and task-fit choices, not measured performance rankings. Both skills cover usability. Read the selected content instead of treating this table as an exclusive capability boundary. For new visual work, use real content and a brief plan that fits the user's requirements. Aesthetic examples are not universal bans on cards, labels, numbers, or arrows. Missing information that changes the result can require clarification. Existing clear requirements and authorization do not need a new approval gate.

Sources: [Anthropic Frontend Design](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design) (Apache-2.0) and [Emil](https://github.com/emilkowalski/skills). Keep installed source versions and any local differences in private evidence. This repository does not bundle either skill or establish its installation in another environment.

Find each selected skill in the current environment's skill catalog. Read its actual `SKILL.md` and only the references relevant to the task. Resolve references through that skill's own provider or directory. Do not assume a machine-specific path or embed third-party skill text here. If a dependency is absent, reuse its installation owner or the available authorized skill-installer workflow. State an access or installation failure and its effect accurately. Do not claim a skill was read when it was unavailable.

Give the assigned engineer the UI goal, explicit product style, and target component or view. Include constraints, the existing design system, expected interaction, and observable acceptance. Keep this direction in the handoff. Record the few skill-informed decisions that changed the output, their reasons, the artifact pointer, and validation limits privately. Installation, catalog presence, a skill label, and reading evidence do not establish application or acceptance.

Useful decisions include whether motion serves a real interaction, how feedback preserves task speed, and how keyboard, focus, reduced-motion, touch, and narrow-screen behavior remain usable. Preserve the current design system and user requirements. Add motion only for a useful purpose. Do not automatically apply every animation technique or load every skill from the upstream collection. Other skills retain their own applicability and explicit-invocation rules.

For a UI code review, follow the selected skill's applicable review format. When using Emil, use its required Before/After/Why table. Tie findings to observed interface behavior and scoped source. Do not invent issues to fill the table. A real accessibility or behavior failure justifies a targeted correction and affected checks. A preference alone does not justify repeating completed work, unchanged tests, or release review.

The responsible PM compares the actual artifact with the explicit style, constraints, and acceptance. Visual claims need relevant observed views tied to the artifact revision, such as screenshots or inspected rendered states. Passing code tests alone does not establish appearance or business acceptance. A claim about published appearance needs evidence from the served version. Record unavailable observations and remaining limits. Keep checks proportional to changed views and unresolved concerns, without a blanket browser gate or full-site review. Owners address observed failures within scope instead of leaving obvious checks to the user.

Apply this selection rule to unfinished UI work. Keep accepted candidates moving through the existing release path. Record any concrete design issue that changes readiness, rather than adding a general design approval gate. Model settings, resource ownership, action permissions, ASD-STE100 handoffs, and completion-notification rules remain unchanged.

For UI implementation and code review, also use [the core Ponytail coding guidance](coding.md). It governs unnecessary code complexity alongside the selected design guidance. Preserve both the requested interface behavior and the required quality checks.

## Usability baseline

Use first-time scenarios for people with no product background and limited attention or patience. Give useful defaults. The primary task should not depend on reading long instructions or organizing the product first. When essential setup is required, make the next action clear. Use relevant parts for operator-facing tools and outputs as well as visual interfaces.

Make primary tasks, important objects, and results easy to find from normal entry points. Use clear names and consistent controls. Keep text short and the visual hierarchy clear. Show secondary details when needed. Neither a flat layout nor hiding everything is a universal solution. Do a check of affected narrow-screen and keyboard flows, visible focus, contrast, and appropriate accessibility needs.

Keep these outcomes distinct:

| State | What the user needs to understand |
| --- | --- |
| Loading | The system is getting or preparing information. |
| Empty | No relevant items exist, or the current filter has no matches. Show the reason. |
| Denied | The operation needs permission the user does not have. |
| Failed | The attempted operation did not complete. |
| Pending | Work is queued or still awaits a result or decision. |
| Unsaved | Changes have not been saved. |
| Successful | Evidence shows the intended effect occurred. |

Give a short actionable recovery path and appropriate undo or restoration. Preserve useful input where possible. Repeated confirmations do not repair unclear design. Keep approved automation and its permission boundaries. For AI results, make the basis, relevant sources, and uncertainty understandable. While an AI action is unfinished, keep its pending state accurate. Missing information must not appear as a certain answer or a completed action.

Include a representative primary-task scenario in the handoff and acceptance. It should work without navigation hints from its author. Examine the actual path from entry to understood result. Record the artifact revision, starting conditions, actions, observed result, and limits. Label the method as a design assumption, an agent or fixture walkthrough, or research with real first-time users. Do not claim universal usability or measured efficiency from these assumptions. Keep validation proportional to the changed task and states.
