
undefined8 attcSendMtuReq(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  if ((int)((uint)*(byte *)(*param_1 + (uint)*(byte *)((int)param_1 + 0xe) * 4 + 2) << 0x1f) < 0) {
    attcFreePkt(param_1 + 1);
    *(undefined1 *)((int)param_1 + 6) = 0;
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b90,&DAT_00531154,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b90,DAT_00531b90,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b90,DAT_00531b18,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00531158,&LAB_0053115c,3), iVar1 != 0)) {
              WsfTrace(DAT_00531b90,DAT_00531ab4);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              uStack_c = DAT_00531ab4;
              uStack_10 = 0x13c;
              FUN_0043d574(4,&DAT_00531158,DAT_00531abc,DAT_00531ab8);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uStack_c = DAT_00531ab4;
            uStack_10 = 0x13c;
            FUN_0043d574(3,&DAT_00531158,DAT_00531abc,DAT_00531ab8);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uStack_c = DAT_00531ab4;
          uStack_10 = 0x13c;
          FUN_0043d574(2,&DAT_00531158,DAT_00531abc,DAT_00531ab8);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uStack_c = DAT_00531ab4;
        uStack_10 = 0x13c;
        FUN_0043d574(1,&DAT_00531158,DAT_00531abc,DAT_00531ab8);
      }
    }
  }
  else {
    *(byte *)(*param_1 + (uint)*(byte *)((int)param_1 + 0xe) * 4 + 2) =
         *(byte *)(*param_1 + (uint)*(byte *)((int)param_1 + 0xe) * 4 + 2) | 1;
    attcSendSimpleReq(param_1);
  }
  return CONCAT44(uStack_c,uStack_10);
}

