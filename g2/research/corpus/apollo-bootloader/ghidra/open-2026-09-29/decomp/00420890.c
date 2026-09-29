
undefined8 FUN_00420890(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (*DAT_00421010 == 0) {
    iVar1 = 2;
  }
  else {
    iVar1 = FUN_004207f4();
    if (iVar1 == 0) {
      iVar1 = FUN_00420984();
      if (iVar1 == 0) {
        param_3 = 0;
        iVar1 = FUN_0042069e(0xb7,0,0,0,0,param_4);
        if (iVar1 == 0) {
          FUN_004207f4();
          iVar1 = FUN_00420800();
          if (iVar1 == 0) {
            param_3 = 0x3de;
            elog_output(2,DAT_00420adc,DAT_00420978,DAT_00421018,0x3de,DAT_00421024);
            iVar1 = 1;
          }
          else {
            iVar1 = FUN_004209c4();
            if (iVar1 == 0) {
              iVar1 = 0;
            }
            else {
              param_3 = 0x3e4;
              elog_output(2,DAT_00420adc,DAT_00420978,DAT_00421018,0x3e4,DAT_00421028);
            }
          }
        }
        else {
          param_3 = 0x3d6;
          elog_output(2,DAT_00420adc,DAT_00420978,DAT_00421018,0x3d6,DAT_00421020);
        }
      }
      else {
        param_3 = 0x3cf;
        elog_output(2,DAT_00420adc,DAT_00420978,DAT_00421018,0x3cf,DAT_0042101c);
      }
    }
    else {
      param_3 = 0x3c8;
      elog_output(2,DAT_00420adc,DAT_00420978,DAT_00421018,0x3c8,DAT_00421014);
      iVar1 = 3;
    }
  }
  return CONCAT44(param_3,iVar1);
}

