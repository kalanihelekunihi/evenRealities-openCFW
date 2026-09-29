
void dmDevPassEvtToDevPriv(undefined1 param_1,byte param_2,undefined1 param_3,undefined1 param_4)

{
  int iVar1;
  ushort local_1c;
  undefined1 local_1a;
  undefined1 local_18;
  undefined1 local_17;
  
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b3078,&DAT_004b3060,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b3078,DAT_004b3088,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b3078,DAT_004b3078,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004b3064,&DAT_004b3068,3), iVar1 != 0)) {
            WsfTrace(DAT_004b3078,DAT_004b307c,param_1,param_2,param_3);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(4,&DAT_004b3064,DAT_004b3084,DAT_004b3080,0xd6,DAT_004b307c,param_1,param_2
                         ,param_3);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_004b3064,DAT_004b3084,DAT_004b3080,0xd6,DAT_004b307c,param_1,param_2,
                       param_3);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_004b3064,DAT_004b3084,DAT_004b3080,0xd6,DAT_004b307c,param_1,param_2,
                     param_3);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_004b3064,DAT_004b3084,DAT_004b3080,0xd6,DAT_004b307c,param_1,param_2,
                   param_3);
    }
  }
  local_1c = (ushort)param_2;
  local_1a = param_1;
  local_18 = param_3;
  local_17 = param_4;
  (**(code **)(*(int *)(DAT_004b3070 + 4) + 8))(&local_1c);
  return;
}

