
undefined * FUN_005540d6(byte param_1)

{
  undefined *puVar1;
  
  puVar1 = PTR_s_UNKNOWN_EVENT_00554b1c;
  if (param_1 < 0x13) {
    puVar1 = *(undefined **)(DAT_00554d30 + (uint)param_1 * 4);
  }
  return puVar1;
}

