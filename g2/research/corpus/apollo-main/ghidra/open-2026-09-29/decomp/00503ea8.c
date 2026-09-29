
undefined8 FUN_00503ea8(byte param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_005040d4,&DAT_005040c0,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_005040d4,DAT_005040d4,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_005040d4,DAT_005040c4,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00503ff0,&DAT_00503ff8,3), iVar1 != 0)) {
              WsfTrace(DAT_005040d4,DAT_00504120,0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              param_2 = 0x3a5;
              param_3 = DAT_00504120;
              FUN_0043d574(4,&DAT_00503ff0,DAT_005040d0,DAT_00504128,0x3a5,DAT_00504120,0);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            param_2 = 0x3a5;
            param_3 = DAT_00504120;
            FUN_0043d574(3,&DAT_00503ff0,DAT_005040d0,DAT_00504128,0x3a5,DAT_00504120,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x3a5;
          param_3 = DAT_00504120;
          FUN_0043d574(2,&DAT_00503ff0,DAT_005040d0,DAT_00504128,0x3a5,DAT_00504120,0);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x3a5;
        param_3 = DAT_00504120;
        FUN_0043d574(1,&DAT_00503ff0,DAT_005040d0,DAT_00504128,0x3a5,DAT_00504120,0);
      }
    }
  }
  else {
    iVar1 = DAT_0050411c + (uint)param_1 * 0x30;
    if (((*(char *)(*DAT_00503ff4 + 4) == '\0') && (*(char *)(iVar1 + -0x28) == '\0')) &&
       (iVar2 = DmConnSecLevel(param_1), iVar2 == 0)) {
      FUN_00503498(param_1,1,iVar1 + -0x30);
    }
  }
  return CONCAT44(param_3,param_2);
}

