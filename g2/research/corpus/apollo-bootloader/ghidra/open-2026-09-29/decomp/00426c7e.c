
undefined4 clkgen_hfadj_disable_426c7e(void)

{
  *DAT_00426d34 = *DAT_00426d34 & 0xfffffffe;
  return 0;
}

