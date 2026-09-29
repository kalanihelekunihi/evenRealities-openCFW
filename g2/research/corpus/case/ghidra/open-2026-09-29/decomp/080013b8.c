
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void idle_mode_exit(void)

{
  int iVar1;
  
  iVar1 = _DAT_080013f0;
  *(undefined1 *)(DAT_080013ec + 0x17) = 0;
  case_start_scheduler(*(undefined4 *)(iVar1 + 0x2c));
  case_start_scheduler(*(undefined4 *)(iVar1 + 0x30));
  case_start_scheduler(*(undefined4 *)(iVar1 + 0x28));
  *(undefined1 *)(iVar1 + 3) = 0;
  if (*(char *)(iVar1 + 7) == '\0') {
    g2_log_printf(s_Exit_idle_mode_080013f3 + 1);
    g2_log_printf(&DAT_08001404);
  }
  return;
}

