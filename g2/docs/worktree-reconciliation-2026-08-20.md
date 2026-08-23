# Worktree reconciliation — 2026-08-20

This review note reconciles every local branch and registered auxiliary
worktree with `main` at `1ce485be`. No commit or push was performed while
preparing this review copy.

## Local branches

All local branch tips are ancestors of `main`, so their committed work is
already present:

- `g2-leaf-impl` at `45cec988`
- `worktree-wf_d411e20e-bce-{1,2,3,5,6}` at `3290aace`

Fast-forward-only merge checks for every branch returned `Already up to date`.
An exhaustive `rev-list --left-right --count <branch>...main` check reports
zero branch-only commits for every local branch. `g2-leaf-impl` is three
commits behind `main`; each `worktree-*` branch is eight commits behind.

The directory named `wf_d411e20e-bce-6` is currently attached to branch
`worktree-wf_d411e20e-bce-1`; the branch named
`worktree-wf_d411e20e-bce-6` is unattached. Both branch tips are the same
`3290aace` commit. Reconciliation below follows the actual worktree directory,
index, and file content rather than inferring state from the branch suffix.

## Auxiliary working-copy deltas

### `wf_d411e20e-bce-2`

- `runtime_freertos_task_priority_disinherit_after_timeout.c` is byte-identical
  to the tracked production file on `main` (SHA-256
  `921a706041143aae3473d5026b0f79e6efd2c1965db3335caf97573350897a83`).
- Its overlay function, allowlist entry, redirect, relocation contract, and
  artifact pins are already integrated and superseded by the current aggregate
  overlay.
- The worktree's `AUTO_MERGE` tree contains exactly the same overlay blob as
  its unstaged working copy, so it contributes no additional hidden variant.

### `wf_d411e20e-bce-3`

- `iar_dlib_scanset_matcher.S` is byte-identical to the tracked production
  candidate on `main` (SHA-256
  `2645fa16052452768fd90da9357d6073f45443ce1768a84f16fa8c0f7c8a92f7`).
- Its Apple-clang overlay function and stock-entry replacement are already
  integrated and superseded by the finalized `g2-leaf-impl` aggregate overlay.
  The raw worktree's Apple-only `profiles` restriction was intentionally absent
  from that finalized integration; source identity, compiled-byte identity,
  stock-entry identity, and the empty relocation contract were retained.

### `wf_d411e20e-bce-5`

- The worktree contains an earlier, diagnostic-rich ALS-scale reconstruction
  named `service_kvdb_als_scale.c`. The production tree now contains the newer,
  host-testable `kvdb_als_scale.c` implementation and its complete overlay,
  tests, evidence, and manifest accounting.
- The exact earlier source was retained for review as
  `candidates/worktree_service_kvdb_als_scale.c` (original SHA-256
  `890b85dd9607238ce42d8d75cbf8f08ad0d9dd07dd36f206a740f2f7d3645971`).
  It is not included in the production build.

### `wf_d411e20e-bce-6`

- `runtime_littlefs_file_size_public.c` is byte-identical to the tracked
  production file on `main` (SHA-256
  `de6c56d8abd1d85af1e33e82f45f6a8ac951d30f2610408cf26e17fd05273c25`).
- The worktree header is an earlier, more explicit ABI-layout variant. Its exact
  content was retained for review as
  `candidates/worktree_runtime_littlefs_file_size_public.h` (original SHA-256
  `b70d1cf3a28e9d135cb155ff8b7c9e88278759879957f991cb262e0118a9cb94`).
  It is not included in the production build.
- The worktree index has a real staged overlay delta: the public file-size
  source leaf, function allowlist entry, relocation contract, stock-entry
  redirect, and then-current aggregate artifact pins. The current `main`
  overlay contains the same source identity, toolchain contract, two
  relocations, and byte-identical stock-entry replacement. Only aggregate
  placement and relocated hashes changed as later leaves were appended.
- The worktree's `AUTO_MERGE` tree is byte-identical to its index tree, so it
  contributes no additional hidden variant.

## Ignored and internal state audit

Every ignored file in the four auxiliary worktrees is either one of the six
documented proprietary firmware inputs or a generated component-build binary
or report. No ignored C, assembly, header, linker, script, documentation, or
manifest input exists in those worktrees.

The `refs/codex/turn-diffs/*` objects are internal tree snapshots rather than
local branches. They were audited separately because they can retain transient
working state. None contains a G2 path absent from `main`; the snapshot nearest
these worktrees contains the same finalized four-leaf source set that was
subsequently committed through `g2-leaf-impl`.

## Review disposition

The two `worktree_*` candidate files are the only non-identical source content
that was not already represented on `main`. They are deliberately isolated
from the build so they can be compared with the production implementations
without regressing the validated firmware image.
