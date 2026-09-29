
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void aging_sequence_start(void)

{
  int iVar1;
  
  iVar1 = _DAT_08001378;
  *(undefined1 *)(_DAT_08001378 + 1) = 1;
  *(undefined1 *)(iVar1 + 6) = 1;
  *(undefined1 *)(iVar1 + 2) = 0;
  *(undefined1 *)(iVar1 + 3) = 0;
  *(undefined1 *)(iVar1 + 4) = 0;
  *(undefined4 *)(iVar1 + 0xc) = 0;
  *(undefined1 *)(iVar1 + 5) = 0;
  *(undefined1 *)(iVar1 + 7) = 4;
  if (*(char *)(iVar1 + -0x35) == '\0') {
    g2_log_printf(s__AGING_RUNNING___Start_aging__go_0800137b + 1);
    g2_log_printf(&DAT_080013b0);
  }
  osTimerStart(*(undefined4 *)(iVar1 + -0x20),DAT_080013b4);
  osTimerStart(*(undefined4 *)(iVar1 + -0x1c),2000);
  return;
}

