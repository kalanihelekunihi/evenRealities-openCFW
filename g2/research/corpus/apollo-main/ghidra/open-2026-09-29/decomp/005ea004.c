
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined * semantic_terminal_event_name(byte param_1)

{
  undefined *puVar1;
  
  puVar1 = PTR_s_TERMINAL_EVENT_INVALID_005ea1fc;
  if (param_1 < 0xd) {
    puVar1 = *(undefined **)(_DAT_005ea200 + (uint)param_1 * 4);
  }
  return puVar1;
}

