
undefined8 FUN_005346e4(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  undefined4 local_18;
  undefined4 local_14;
  
  iVar1 = FUN_0047b45a();
  if ((iVar1 != 0) && (iVar2 = FUN_004751c8(*(undefined4 *)(param_1 + 4),iVar1,0x10), iVar2 != 0)) {
    iVar1 = 0;
  }
  local_18 = param_2;
  local_14 = param_3;
  if (iVar1 == 0) {
    FUN_0047b468(*(undefined4 *)(param_1 + 4));
    FUN_0047b438(0,3);
    AttsCsfSetClientsChangeAwarenessState(0,3);
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0053487c,&DAT_00534870,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0053487c,DAT_0053488c,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0053487c,DAT_0053487c,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00534874,&DAT_00534878,3), iVar1 != 0)) {
              WsfTrace(DAT_0053487c,DAT_00534880);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              local_14 = DAT_00534880;
              local_18 = 0xbd;
              FUN_0043d574(4,&DAT_00534874,DAT_00534888,DAT_00534884);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            local_14 = DAT_00534880;
            local_18 = 0xbd;
            FUN_0043d574(3,&DAT_00534874,DAT_00534888,DAT_00534884);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          local_14 = DAT_00534880;
          local_18 = 0xbd;
          FUN_0043d574(2,&DAT_00534874,DAT_00534888,DAT_00534884);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_14 = DAT_00534880;
        local_18 = 0xbd;
        FUN_0043d574(1,&DAT_00534874,DAT_00534888,DAT_00534884);
      }
    }
    GattSendServiceChangedInd(0,1,0xffff);
  }
  return CONCAT44(local_14,local_18);
}

