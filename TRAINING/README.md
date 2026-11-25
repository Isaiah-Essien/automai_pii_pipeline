# Contextual PHI training (placeholder)

Fine-tuning stack for **Stage 1 NER** and **Stage 2 REDACT vs PRESERVE** on African clinical span JSONL. This folder is a **placeholder**: paths and CLIs are wired so we can drop in shards once `DATA_GENERATION` (or merged `part-*.jsonl`) is ready. We **fine-tune** `xlm-roberta-base`; we do **not** pretrain a language model from scratch on the full corpus (see [Fine-tuning vs pretraining](#fine-tuning-vs-pretraining)).

Generation lives in [`DATA_GENERATION/`](../DATA_GENERATION/README.md). Training consumes seven-field JSONL lines (`sentence_id`, `sentence`, `span_start`, `span_end`, `span`, `phi_type`, `decision`).

## Layout

```
TRAINING/
  README.md                 # this file
  requirements.txt          # torch, transformers, eda extras
  contextual_phi/           # importable package (trainers, loaders, EDA)
  scripts/                  # CLIs (sample shards, run NER, EDA, adjudication)
```

| Module | Role |
| --- | --- |
| `project_settings.py` | `DeidProjectSettings`, paths, 3M/5M profile |
| `span_io.py` | `SpanJsonlReader`, `SentenceSpanGrouper` |
| `bio_tagging.py` | BIO alignment for Hugging Face token classification |
| `ner_finetune.py` | `NerFineTuningJob` (Stage 1) |
| `adjudication_finetune.py` | `AdjudicationFineTuningJob` (Stage 2) |
| `shard_eda.py` | Word cloud, bar charts, bigrams |
| `shard_sampler.py` | Reservoir sampling from `part-*.jsonl` |
| `deid_inference.py` | `ClinicalTextDeidentifier` (inference stub) |

## Fine-tuning vs pretraining

| | Pretraining | Fine-tuning (what we ship) |
| --- | --- | --- |
| Goal | Learn language from huge unlabeled text | Teach BIO NER + REDACT/PRESERVE on labeled shards |
| Data | Billions of tokens, raw text | `eval_100k`, `ner_3M` / `ner_5M`, `adj_400k` |
| Compute | Cluster, weeks | Colab Pro + Drive checkpoints |
| Default encoder | Random init | `xlm-roberta-base` (multilingual, Colab-sized) |

**Why xlm-roberta-base:** clinical notes mix English, French, Swahili, and local names; one multilingual encoder beats English-only BERT for v1. Same tokenizer for NER and adjudication. Override with `FineTuningHyperparameters.encoder_name` when ablations say so.

## Local setup (before data lands)

```bash
cd automai_pii_pipeline
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r TRAINING/requirements.txt
```

Optional env var for any machine:

```bash
set PHI_DEID_PROJECT_ROOT=D:\phi_project
```

That root should contain:

```
phi_project/
  shards/       eval_100k.jsonl, ner_3M.jsonl, adj_400k.jsonl, manifest.json
  checkpoints/  ner_3M/, adj_supervised/, ...
  logs/eda/     plots and stats JSON
```

## Step 0 — Sample shards (local CPU, external HDD)

When `part-*.jsonl` exists (from phigen or merged corpus):

```bash
python TRAINING/scripts/sample_training_shards.py ^
  --source L:\AUTOMAI\parts ^
  --output L:\AUTOMAI\shards ^
  --ner-size 3000000
```

Use `--ner-size 5000000` for the 5M profile; upload only `shards/` to Drive for Colab.

## Step 1 — EDA

```bash
python TRAINING/scripts/run_shard_eda.py --shard eval --profile 3M ^
  --project-root D:\phi_project
```

On Colab, omit `--project-root` (defaults to `/content/drive/MyDrive/phi_project`).

## Step 2 — Stage 1 NER (pilot then full)

```bash
python TRAINING/scripts/run_ner_finetune.py --profile 3M --pilot --project-root D:\phi_project
python TRAINING/scripts/run_ner_finetune.py --profile 3M --project-root D:\phi_project
```

Interruptions: re-run the same command; `NerFineTuningJob` resumes the latest `checkpoint-*`.

## Step 3 — Stage 2 adjudication

```bash
python TRAINING/scripts/run_adjudication_finetune.py --profile 3M --project-root D:\phi_project
python TRAINING/scripts/run_adjudication_finetune.py --profile 3M --full --project-root D:\phi_project
```

Weights: `checkpoints/adj_supervised/adj_model.pt`.

## Move this repo to Google Colab

Colab does not need the whole monorepo on GPU unless you want it. Minimum flow:

1. **Mount Drive**

   ```python
   from google.colab import drive
   drive.mount("/content/drive")
   ```

2. **Clone or copy this repo** (or only `TRAINING/`):

   ```python
   !git clone https://github.com/Isaiah-Essien/automai_pii_pipeline.git
   %cd automai_pii_pipeline
   ```

3. **Install deps**

   ```python
   !pip install -q -r TRAINING/requirements.txt
   ```

4. **Upload shards** to  
   `/content/drive/MyDrive/phi_project/shards/`  
   (not the full 130GB `part-*.jsonl` tree).

5. **Run from repo root** (scripts add `TRAINING/` to `sys.path` automatically):

   ```python
   !python TRAINING/scripts/run_shard_eda.py --shard eval --profile 3M
   !python TRAINING/scripts/run_ner_finetune.py --profile 3M --pilot
   !python TRAINING/scripts/run_ner_finetune.py --profile 3M
   !python TRAINING/scripts/run_adjudication_finetune.py --profile 3M --full
   ```

6. **Optional:** set project root explicitly:

   ```python
   import os
   os.environ["PHI_DEID_PROJECT_ROOT"] = "/content/drive/MyDrive/phi_project"
   ```

7. **Zip `TRAINING/` for offline copy** (no git on a machine):

   ```bash
   zip -r contextual_phi_training.zip TRAINING/
   ```

   In Colab: upload zip, `!unzip contextual_phi_training.zip`, then run scripts as above with `%cd` pointing at the folder that contains `TRAINING/`.

## Switch 3M ↔ 5M

Only `--profile 3M` or `5M` changes the NER filename and epoch count (`ner_3M.jsonl` / 4 epochs vs `ner_5M.jsonl` / 2 epochs). Same scripts.

## What is still stubbed

- `ClinicalTextDeidentifier._collect_span_candidates` — proper BIO span decoding before production demos.
- RL phase — optional after supervised adjudication clears eval thresholds.
- Unit tests — add once we freeze a small public eval slice in the repo.

## Relationship to data generation

```text
DATA_GENERATION (phigen)  -->  part-*.jsonl on HDD
        |
        v
sample_training_shards.py -->  shards/ on Drive
        |
        v
run_shard_eda / run_ner_finetune / run_adjudication_finetune
```

When the corpus is ready, we adapt hyperparameters and manifests only; folder layout and class names stay stable.