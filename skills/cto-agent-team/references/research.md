# Optional research

Keep the core organization at five PMs with ten engineer roles each.
A shared researcher is an optional extension. It is not a required extra worker or a permanently active service.
The CTO can request bounded research when a material uncertainty affects an authorized decision.
Use a suitable existing role when worker creation is unavailable or unnecessary. Engineers do not create subordinates.
Use the selected host capabilities and [task routing policy](model-routing.md).

Start with the current project, existing tools, and relevant prior results.
Then examine first-party documentation and actual open-source implementations where they answer the question.
Keep implementation preparation moving when it has no dependency on the research.
Urgent recovery, small changes, and ready releases have no mandatory research gate.

Optional private task data can describe the extension:

```json
{
  "research": {
    "enabled": false,
    "owner": "CTO",
    "assignee": null,
    "max_candidates": 3,
    "max_recommendations": 1,
    "stop_condition": "Evidence answers the scoped question, or the agreed boundary is reached"
  }
}
```

The owner maintains this task data. Neither local helper reads this block or creates a researcher.
An assignee can be an existing suitable role. A real extension worker requires the applicable creation authorization and host capability.

## Bounded report

Record the following in existing private task evidence:

| Field | Required content |
| --- | --- |
| Question and limit | The decision, scope, owner, evidence needed, and agreed time or search boundary. |
| Existing capability | Relevant project code, tools, prior results, and gaps. |
| Candidates | At most three useful alternatives, with source, version or commit, license, and relevant behavior. |
| Evidence and uncertainty | Separate observed facts, inference, author claims, and untested benefits. Mark missing evidence as unknown. |
| Recommendation | At most one recommended option, its tradeoffs, the smallest reuse path, and a concrete validation step. |
| Adoption | The owning PM's decision, implementation owner, required acceptance, and rollback or rejection reason. |
| Resume pointer | Input versions, report location, remaining question, and next unfinished action. |

Do not replace the report with a link list. Popularity, stars, and pull-request counts do not establish suitability or quality.
Preserve license and attribution requirements before reuse. Do not copy a whole project when a smaller authorized reuse solves the task.
Do not add paid comparisons or repeated user approvals to ordinary authorized work.

Stop when the evidence answers the decision, the agreed boundary is reached, or further search yields no useful evidence.
Urgent work can preempt research. Save the useful evidence and remaining uncertainty at that point.
The PM decides adoption. Research acceptance does not replace engineering or product acceptance.
Use actual artifacts and proportional checks for implementation. End the researcher's turn when there is no assigned work.
