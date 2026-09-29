
undefined4 DRV_Bq25180SetTerminationPercent(byte param_1)

{
  undefined1 uVar1;
  undefined4 unaff_r7;
  
  uVar1 = 0;
  if (param_1 < 0x14) {
    if (param_1 < 10) {
      if (4 < param_1) {
        uVar1 = 1;
      }
    }
    else {
      uVar1 = 2;
    }
  }
  else {
    uVar1 = 3;
  }
  bq25180_update_field(5,4,3,uVar1);
  return unaff_r7;
}

