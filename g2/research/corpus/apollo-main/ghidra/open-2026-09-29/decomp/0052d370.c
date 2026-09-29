
undefined8 AttsCsfConnOpen(uint param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = DAT_0052da1c;
  if ((param_1 & 0xff) == 0) {
    uVar2 = param_1;
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052da20,&DAT_0052d4f0,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052da20,DAT_0052da20,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052da20,DAT_0052d4fc,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0052d4f4,&DAT_0052d4f8,3), iVar1 != 0)) {
              WsfTrace(DAT_0052da20,DAT_0052da34,param_1 & 0xff);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              uVar2 = 0x137;
              param_2 = DAT_0052da34;
              FUN_0043d574(4,&DAT_0052d4f4,DAT_0052da2c,DAT_0052da38,0x137,DAT_0052da34,
                           param_1 & 0xff);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar2 = 0x137;
            param_2 = DAT_0052da34;
            FUN_0043d574(3,&DAT_0052d4f4,DAT_0052da2c,DAT_0052da38,0x137,DAT_0052da34,param_1 & 0xff
                        );
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = 0x137;
          param_2 = DAT_0052da34;
          FUN_0043d574(2,&DAT_0052d4f4,DAT_0052da2c,DAT_0052da38,0x137,DAT_0052da34,param_1 & 0xff);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = 0x137;
        param_2 = DAT_0052da34;
        FUN_0043d574(1,&DAT_0052d4f4,DAT_0052da2c,DAT_0052da38,0x137,DAT_0052da34,param_1 & 0xff,
                     param_4);
      }
    }
  }
  else if (param_3 == 0) {
    FUN_0043c0e4(DAT_0052da1c + (param_1 & 0xff) * 2 + -2,2,0);
    uVar2 = param_1;
  }
  else {
    *(char *)(DAT_0052da1c + (param_1 & 0xff) * 2 + -1) = (char)param_2;
    FUN_00439be4(iVar1 + (param_1 & 0xff) * 2 + -2,param_3,1);
    uVar2 = param_1;
  }
  return CONCAT44(param_2,uVar2);
}

