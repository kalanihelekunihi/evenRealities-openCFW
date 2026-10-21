# Offline application LP phase

application.c reconstructs all-LP wrapper7050 and the state3 application slice3e28 up to state/budget assignment, before logs/configuration/common-loop work. It composes independent LP launch, explicitly ignores launch/sleep returns as stock does, polls busy under saved critical state and selects state1/budget640 or state2/budget160. PM providers are explicit dependencies; no production retry/watchdog/patch is implemented.

Evidence: ../../../analysis/touch-lp-application-closure-2026-10-08/REPORT.md.120 comparisons separate full wrapper/launch, bounded app composition and pre-WFI preparation. IRQ scheduling is synthetic and PRIMASK-aware; real callbacks, physical sleep/wake/analog timing, exact history allocation and whole-image source remain unproven.
