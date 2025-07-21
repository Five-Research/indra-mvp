**Indra MVP – Product Requirements Document (PRD)**
*Scope: “Stupid‑Simple” Python framework that mimics full‑scale Indra flow using file‑based JSON hand‑offs. Inspired by OpenAI’s swarm repo.* ([GitHub][1])

---

## 0. Overview:

| Aspect             | TL;DR                                                                                                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Problem**        | Knowledge work is bottlenecked by manual orchestration (copy‑pasting across tools, status checks, etc.).                                                                       |
| **Vision**         | Indra is a *hive* of AI agents—**Queen → Scribe → Workers → Compiler**—that turns a single human prompt into a multi‑step, multi‑tool workflow without human micro‑management. |
| **Why an MVP?**    | We need a bare‑bones demo that proves the agent flow *works*—no cloud infra, no marketplace—just show that a prompt becomes tasks, tasks run, results merge.                   |
| **Philosophy**     | **K.E.S.S. – Keep Everything Stupid Simple** in v0 → polish speed later.                                                                                                       |
| **Demo Narrative** | Run `indra run "Plan a 3‑city trip"` → CLI prints steps → JSON files pop into `results/` → final JSON (or simple PDF) prints itinerary + cost.                                 |
| **Success Signal** | A teammate who has **never** heard of Indra can clone the repo, follow README, and in < 5 min produce the demo output.                                                         |



## 1  Objective

Deliver a demo‑able backend that shows:

1. A **Queen** prompt breaks a user request into sub‑tasks.
2. A **Router/Scribe** assigns those tasks to **Worker** scripts.
3. Workers write results to JSON; **Compiler** stitches them.
4. End‑to‑end run is launchable via one CLI command and passes unit tests.

No networking, DB, or async infra—pure Python + local files.

---

## 2  Success Criteria

| Metric                      | Target                                          |
| --------------------------- | ----------------------------------------------- |
| Setup time on clean machine | ≤ 5 min (`pip install -e .`)                    |
| Demo command completes      | ≤ 30 s, zero errors                             |
| Unit‑test coverage          | ≥ 80 % of core package                          |
| Code footprint              | ≤ 800 LOC (excluding tests)                     |
| External deps               | `openai`, `pydantic`, `python‑json‑logger` only |

---

## 3  User Stories (Happy‑Path)

1. **Demo Runner**
   *As a* demo host *I want* to run `python examples/trip_demo.py "Plan a 3‑city trip"` *so that* I see step‑by‑step JSON logs and a final `result.pdf`.

2. **Developer**
   *As a* dev *I want* to drop a new Worker (`/indra/workers/summariser.py`) *so that* Queen can auto‑discover it via a one‑line registration.

3. **QA**
   *As a* tester *I want* to run `pytest` and get green ticks *so that* I know refactors didn’t break routing.

---

## 4  System Slice

```
CLI → Queen(prompt) → tasks.json → Router
      Router → /queue/task_<uuid>.json
      Worker_X watches /queue, processes, outputs /results/<uuid>.json
      Compiler waits until all expected results exist → merges → final.json / PDF
```

*All communication is file‑based.* One task = one JSON blob:

```json
{
  "id": "1234-uuid",
  "task": "find_flights",
  "inputs": {"from": "BOM", "to": "DEL"},
  "status": "PENDING",
  "result_path": null
}
```

                      +-------------+
User prompt  ───────▶ │   Queen     │  prompt template → list of tasks
                      +-------------+
                             │
                             ▼
                      +-------------+
                      │   Router    │  creates /queue/task_*.json
                      +-------------+
          ┌───────────────┴───────────────┐
┌─────────▼────────┐            ┌─────────▼────────┐
│  Worker: travel  │            │ Worker: finance  │  poll /queue
│  (travel.py)     │            │ (finance.py)     │
└─────────┬────────┘            └─────────┬────────┘
          │ results/*.json                │
          └───────────────┬───────────────┘
                          ▼
                      +-------------+
                      │  Compiler   │  waits → merge → final.json
                      +-------------+


---

## 5  Tech Stack & Folder Layout

```
indra-mvp/
├─ indra/
│  ├─ __init__.py
│  ├─ router.py          # dispatch + polling
│  ├─ compiler.py        # merges results
│  ├─ prompts/
│  │   ├─ queen.txt
│  │   └─ worker_system.txt
│  ├─ workers/
│  │   ├─ __init__.py
│  │   ├─ travel.py
│  │   └─ finance.py
│  └─ utils.py
├─ examples/
│  ├─ trip_demo.py
│  └─ launch_demo.py
├─ tests/
│  ├─ test_router.py
│  └─ test_worker_travel.py
├─ requirements.txt
└─ README.md
```

*Design mirrors the `swarm` repo hierarchy (package + examples + tests).* ([GitHub][1])

---

## 6  Component Requirements

| Component       | Extra Guidance for New Devs                                                                                                                   |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Queen**       | Prompt lives in `prompts/queen.txt`. Use OpenAI o3. Output **must** be a valid JSON list—validate with `json.loads`.                          |
| **Router**      | No concurrency; simple `while True: scan folder, sleep(1)`. Keep a per‑task `status` field so Compiler knows when to stop waiting.            |
| **Worker Base** | Sub‑class must implement `execute(**inputs)` and write result JSON `{task_id, outputs}`. Import side‑effect adds worker to `WORKER_REGISTRY`. |
| **Compiler**    | Block until every `task.status == "DONE"` **or** 30 s timeout. For MVP, just concatenate outputs into one JSON.                               |
| **CLI**         | `indra run "<prompt>" --out results/`                                                        | Orchestrates flow. Uses blocking loop; no concurrency needed. |

Logging: simple `[timestamp][component] msg` to `logs/indra.log`.

---


## 9  FAQs

“Do we use real APIs?”
No. Workers return stubbed data so demo always works offline.

“Where do I add a new worker?”
Create a file in indra/workers/, inherit BaseWorker, add @register_worker("worker_name").

“How are tasks matched to workers?”
The Queen’s JSON includes "worker": "travel". Router imports workers and looks up the registry.

“What if the Queen output is malformed?”
Router raises InvalidTaskFormat; CLI prints error; we fail fast—don’t silence bugs.

“Can I use async or threads to speed up?”
Not in MVP. Keep single‑thread for determinism; optimise later.





[1]: https://github.com/openai/swarm/tree/main "GitHub - openai/swarm: Educational framework exploring ergonomic, lightweight multi-agent orchestration. Managed by OpenAI Solution team."
