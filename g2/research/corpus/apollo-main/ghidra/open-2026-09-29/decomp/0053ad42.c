
undefined4 DRV_Bq25180SetInputCurrentLimit(ushort param_1)

{
  undefined1 uVar1;
  undefined4 unaff_r7;
  
  uVar1 = 0;
  if (param_1 < 0x44c) {
    if (param_1 < 700) {
      if (param_1 < 500) {
        if (param_1 < 400) {
          if (param_1 < 300) {
            if (param_1 < 200) {
              if (99 < param_1) {
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
        }
        else {
          uVar1 = 4;
        }
      }
      else {
        uVar1 = 5;
      }
    }
    else {
      uVar1 = 6;
    }
  }
  else {
    uVar1 = 7;
  }
  bq25180_update_field(8,0,7,uVar1);
  return unaff_r7;
}

