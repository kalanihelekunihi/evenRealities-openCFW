
undefined4 clkgen_disable_426d1e(void)

{
  *DAT_00426d40 = *DAT_00426d40 & 0xfffffffe;
  return 0;
}

