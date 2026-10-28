# Recovery from temporary model-capacity failure

The CTO owns recovery for PM chats and may designate one authorized supervisor as the sole PM retry executor. Each PM owns recovery for its own engineers. Record one recovery owner and one retry executor per chat. An observer must not send a competing retry. The executor's own model does not change the failed worker's configuration. Reuse the user's authorization for internal task messages within its scope.

Keep the failed turn's verified model, complete native settings, and quality history. Read its dispatch record and tool evidence. Do not infer that configuration from a role default or the latest [task routing policy](model-routing.md). A policy update does not alter an earlier turn's request. If the request is unknown, reconcile the evidence before retrying. Do not change the model or effort to get capacity. A change outside the user's approved scope requires explicit approval. Do not reset an existing override to a default.

## Identify the failure

Read the latest task record, actual chat state, latest turn, and available error details. Retry only when evidence identifies a failed or stopped turn caused by temporary model capacity, and unfinished authorized work remains. A tool-command failure, a slow response, or an idle chat is not sufficient evidence.

Do not send a retry while a turn is active. Do not retry completed or cancelled work. Distinguish temporary capacity from invalid credentials, account or quota exhaustion, approval requests, permanent errors, and an intentional stop. Resolve those conditions through the applicable task workflow. Ask the user only when a specific decision or action is necessary. Do not ask the user to click retry for an ordinary temporary capacity error.

## Resume with evidence

Before each send, inspect current task and turn state again. Read saved outputs, accepted work, running processes, release ownership, and any external-operation evidence relevant to the unfinished step. Continue in the same chat with the failed turn's recorded configuration. Pass its exact native request through the verified host mapping. Do not discard a speed, effort, or other supported parameter. Use the current supported message tool and its schema. Do not create replacement engineers or duplicate chats to get around capacity.

Record a pending attempt before sending. Identify the failed-turn record with the chat ID and failed turn ID. Keep a chain attempt count across related capacity failures so a new failed turn does not reset the delay. The same observed failure must not generate multiple pending attempts.

Resume only unfinished work. In the message, retain the task ID, exact scope, current authorization, saved evidence, remaining acceptance, resource ownership, and recovery limits. Apply [handoffs.md](handoffs.md) to English recovery instructions. Do not repeat completed publication, builds, releases, data writes, or external messages. If an earlier external action has an unknown result, inspect that external state before another action.

After the send, save its returned outcome and the observed new turn ID when available. If the result is uncertain, inspect the chat before another send. An active turn, a completed result, or an accepted continuation must not receive a duplicate retry. Do not infer failure from a missing immediate reply.

## Delay and follow-up

Use the recorded task policy for delays. This team's default intervals, measured after each failure, are 0, 2, 5, 10, and 15 minutes. Later ordinary capacity retries use a 15-minute interval. A provider retry-after value is a minimum: use the later of that time and the team's next eligible time, even if the provider requires more than 15 minutes. Record the attempt, failure time, and next eligible time privately.

Do not hold a tool call open for a long backoff or repeatedly poll unchanged state. When a later turn is necessary, use an available, authorized heartbeat or automation and reuse existing supervision. Persist its ID and cursors. Keep unchanged checks and ordinary retries quiet. This skill describes a recovery procedure, not a built-in recovery daemon. If no supported follow-up capability can perform a delayed retry, record that limit and provide a concrete continuation path. Do not claim a scheduled retry exists when none was created.

Stop retrying when work completes, is cancelled, is already active, or the observed cause is no longer temporary capacity. After successful recovery or terminal resolution, stop a separate one-time recovery monitor only if it has no remaining duty. If supervision is shared with task progress or completion notification, remove only the completed recovery duty and preserve the other follow-up. Do not disable a task's completion monitor merely because a retry succeeded. Preserve unrelated monitor settings when updating it. Report a distinct persistent blocker only when it needs user action. Completion notifications retain the existing result-evidence and deduplication rules.

## Review limits

Keep actual chat IDs, failed turns, paths, errors, attempts, and notification state in the private state directory. Public guidance uses role names and generic task references only. A recorded attempt does not prove success. Inspect the resumed turn and its work. Tests or walkthroughs of this procedure do not establish provider availability or guarantee recovery within a fixed time.

## Exact request selection

Use the routing helper's `--retry-from` mode with the verified retry envelope described in [model-routing.md](model-routing.md#capacity-retry).
It bypasses normal candidate freshness and cost ranking. An expired or absent ordinary catalog is not evidence of revocation.
A source-backed revocation or new user hard stop blocks recovery. It does not authorize a substitute model.
If quality history is missing, the original request can still be recovered. Later automatic quality escalation requires reconciled history.
The helper returns parameters only. The recovery owner still checks actual turn state, unfinished work, authorization, and duplicate effects before sending.
