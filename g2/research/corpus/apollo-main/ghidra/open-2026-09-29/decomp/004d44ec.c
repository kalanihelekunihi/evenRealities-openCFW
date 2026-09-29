
undefined8 FUN_004d44ec(byte param_1,byte param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (*DAT_004d4604 << 0x1f < 0) {
    uVar1 = 3;
  }
  else {
    FUN_004d43b4((uint)param_1 << 2 | (uint)param_2 << 1);
    uVar1 = 0;
  }
  return CONCAT44(unaff_r7,uVar1);
}

