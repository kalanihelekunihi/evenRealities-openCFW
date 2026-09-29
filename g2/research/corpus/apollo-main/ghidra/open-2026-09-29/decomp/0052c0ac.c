
void attsCccMainCback(undefined1 param_1,char param_2,undefined2 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_4;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c688,&DAT_0052c23c,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c688,DAT_0052c678,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c688,DAT_0052c688,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0052c240,&DAT_0052c3c4,3), iVar1 != 0)) {
            WsfTrace(DAT_0052c688,DAT_0052c69c,param_1,param_3);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(4,&DAT_0052c240,DAT_0052c684,DAT_0052c6a0,300,DAT_0052c69c,param_1,param_3)
            ;
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_0052c240,DAT_0052c684,DAT_0052c6a0,300,DAT_0052c69c,param_1,param_3);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_0052c240,DAT_0052c684,DAT_0052c6a0,300,DAT_0052c69c,param_1,param_3);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_0052c240,DAT_0052c684,DAT_0052c6a0,300,DAT_0052c69c,param_1,param_3,uVar2)
      ;
    }
  }
  if (param_2 == '\x05') {
    attsCccReadValue(param_1,param_3,param_4);
  }
  else {
    attsCccWriteValue(param_1,param_3,param_4);
  }
  return;
}

