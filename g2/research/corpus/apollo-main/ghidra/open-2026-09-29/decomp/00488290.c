
undefined8 FUN_00488290(byte param_1)

{
  undefined4 unaff_r5;
  
  if (param_1 < 0x13) {
    FUN_00439be4(&stack0xfffffff0,DAT_004883d4 + (uint)param_1 * 3,3);
  }
  else {
    FUN_0044d25c(2,DAT_004883d0,0x2e,DAT_004883cc);
    unaff_r5 = FUN_004410a6();
  }
  return CONCAT44(unaff_r5,unaff_r5);
}

