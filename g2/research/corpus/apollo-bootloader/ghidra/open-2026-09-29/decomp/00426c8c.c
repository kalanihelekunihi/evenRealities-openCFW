
undefined8 dual_switch_426c8c(char param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_1 == '\0') {
    *DAT_00426d30 = *DAT_00426d30 & 0xffffffdf;
  }
  else if (-1 < (int)(*DAT_00426d30 << 0x1a)) {
    *DAT_00426d30 = *DAT_00426d30 | 0x20;
    unaff_r7 = 1;
    uVar1 = delay_us_status_check(100,DAT_00426d38,0x1000000,0x1000000);
    goto LAB_00426cca;
  }
  uVar1 = 0;
LAB_00426cca:
  return CONCAT44(unaff_r7,uVar1);
}

