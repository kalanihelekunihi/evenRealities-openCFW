
undefined4 clkgen_hfadj_enable_426c58(char param_1)

{
  *DAT_00426d30 = *DAT_00426d30 & 0xfffffffe | (uint)(param_1 != '\0');
  return 0;
}

