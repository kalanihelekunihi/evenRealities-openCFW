
undefined8 FUN_004d3952(char param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_1 == '\0') {
    *DAT_004d3a08 = *DAT_004d3a08 & 0xffffffdf;
  }
  else if (-1 < (int)(*DAT_004d3a08 << 0x1a)) {
    *DAT_004d3a08 = *DAT_004d3a08 | 0x20;
    unaff_r7 = 1;
    uVar1 = FUN_00480826(100,DAT_004d3a10,0x1000000,0x1000000);
    goto LAB_004d3990;
  }
  uVar1 = 0;
LAB_004d3990:
  return CONCAT44(unaff_r7,uVar1);
}

