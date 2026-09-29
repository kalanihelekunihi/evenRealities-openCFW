
undefined4 register_power_toggle_42f1c8(char param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == '\0') {
    FUN_0041c838(0);
    delay_us(5);
    *DAT_0042f5f0 = *DAT_0042f5f0 & 0xfffffffe;
  }
  else {
    *DAT_0042f5f0 = *DAT_0042f5f0 | 1;
    delay_us(5);
    FUN_0041c838(1);
  }
  return unaff_r7;
}

