# Host capabilities and installation

Keep organization, task acceptance, and resource ownership in the [workflow](workflow.md).
Use a host adapter for installation, execution, model parameters, result collection, and follow-up.
The adapter must use the current tool schema and the user's authorization.

## Support boundary

The following documentation was reviewed on 2026-10-28. Documentation is not an account inventory or a client execution test.

| Host | Documented entry and execution | Boundary of this package |
| --- | --- | --- |
| Codex | Local skills and custom subagents. Role configuration can affect model-setting precedence. | Existing local state helper and a configurable payload selector. Desktop thread tools depend on the environment. |
| Claude Code | Local `.claude/skills`, subagent model selection, foreground/background execution, and resume. Effort overrides depend on client version and configuration. | Documented integration guidance and offline native-key fixtures. No live Claude Code validation or installed native adapter. |
| Cursor | `.cursor/skills` or `.agents/skills`, subagents, and model-dependent settings, including bracket syntax in some model IDs. | Documented integration guidance. No live Cursor validation or bracket-syntax generator. |
| Generic or cloud | The caller must establish skill loading, tools, identity, model controls, persistence, and follow-up. | Manual context loading, serial work, or planning when required capabilities are absent. No native plugin claim. |

Official sources: [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[Claude Code skills](https://code.claude.com/docs/en/skills),
[Claude Code subagents](https://code.claude.com/docs/en/sub-agents),
[Claude Code model configuration](https://code.claude.com/docs/en/model-config),
[Cursor skills](https://cursor.com/docs/skills), and [Cursor subagents](https://cursor.com/docs/subagents).
Refresh the relevant source and local capability evidence when the host or client changes.

Copy the complete skill folder to a supported skill location. Confirm that the host discovers `SKILL.md` and its references.
Local installation does not establish cloud loading, account access, or tool permission.
For manual integration, provide the skill text and required references through an authorized channel.
Keep private configuration and evidence outside the installed skill. Follow [portable setup](state.md#portable-setup-and-resume).

## Execution operations

Map these operations to actual host tools: discover projects, find existing workers, create authorized workers, send work, collect results, and stop work.
Keep real worker identities and result cursors in private state. Record actual tool outcomes.
If creation is unavailable, give the work to a suitable existing role or proceed serially within authorization.
A task that requires parallel execution remains blocked when only serial execution is possible.

In a reviewed Codex desktop consumer, `list_projects` establishes the project before authorized `create_thread` calls.
`send_message_to_thread` forwards authorized work. `wait_threads` collects results with saved cursors.
Discover their current schemas. A namespace, field name, or target limit can differ between environments.
Keep waits bounded to 60 seconds under this team's convention.
Do not use private shell APIs to replace missing thread tools.

For supported collaboration tools, creation can use `model`, `reasoning_effort`, and `fork_turns="none"` with complete task context.
Fixed role settings can override a request. Inspect the applicable precedence before claiming a setting changed.
Independent chats and subagents are different capabilities. A subagent-tree limit does not establish a global chat limit.

For completion follow-up, discover the supported scheduler or notification tool.
In Codex desktop, prefer an authorized thread heartbeat unless the user requests a standalone job.
Read back supported model settings or documented inheritance before claiming the supervisor route is configured.
If follow-up is unavailable, save a continuation checkpoint and state the limit. Do not promise automatic wakeup.
Check browser, device, file, and shell capabilities separately from model selection.

## Native parameter boundary

The selector emits a flat settings payload for one identified consumer. It does not invoke that consumer.
`mapping.model_key` supplies the model field. `mapping.settings_keys` lists the exact permitted native setting names.
The selected values must occur in that model's verified `native_settings` and route support.
An unknown key blocks the request. The helper does not discard it or translate its meaning.

For example, a desktop consumer can use `model` and `thinking`.
A separate consumer can use `model` and `reasoning_effort`, or another verified native setting.
Configure each consumer separately from its actual schema. An `effort` fixture does not establish Claude API or CLI support.
The words `high` and `xhigh` have no cross-vendor equivalence in this package.
Embedded model-ID syntax, nested API objects, and command-line adapters need separate verified integration. The flat mapper does not generate them.

## Evidence levels

Keep these claims separate:

1. Documentation lists a capability or model.
2. Current account evidence establishes availability for the identified host.
3. User policy permits the task, model, native settings, and resource use.
4. A configuration or fixture produces the expected request.
5. The tool accepts that request.
6. An actual turn or independent backend observation establishes the execution facts it can support.

The local helper checks supplied references and constraints. It cannot authenticate those references or discover account entitlements.
Refresh stale evidence with a supported read-only interface or relevant actual-work records. Do not start a paid probe for this package.
If a host silently falls back, record the mismatch and reconcile it. Tool acceptance does not establish the actual backend model.
