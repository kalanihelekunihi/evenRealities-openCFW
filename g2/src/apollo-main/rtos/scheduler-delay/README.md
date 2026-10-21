# Experimental Apollo scheduler delay source

`delay.c` composes retained CMSIS-RTOS2 FreeRTOS adapter `osDelay` and
FreeRTOS `vTaskDelay` bodies. Source copies are under
`pre-consolidation:g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/runtime-action-416200/upstream/`;
the Apollo original entries are `0x449376` and `0x454b4c`. The selected
Apollo lower providers supply IRQ context, scheduler suspend/resume, delayed
list insertion, and yield. The source follows the actual nonzero caller
values, including 33 and `UINT32_MAX` ticks.

The suspended-scheduler assertion path is an explicit `noreturn` import,
`audio_delay_scheduler_assert`. Its product diagnostic implementation is not
owned here. The selected Audio builder excludes this experimental directory;
this file has not passed a joint original/source scheduler fixture covering
ready/delayed lists, pending ticks, BASEPRI and PendSV. It is not an admitted
provider or an elapsed-time/hardware result.
