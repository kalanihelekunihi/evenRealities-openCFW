
int gx8002_send_message(undefined2 param_1,undefined2 param_2,undefined4 param_3,uint param_4,
                       undefined1 param_5)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined2 local_14 [2];
  uint uStack_10;
  
  uVar1 = DAT_0057cb30;
  local_14[0] = 0;
  uStack_10 = param_4;
  iVar2 = gx8002_pack_message(param_1,param_2,param_3,param_4 & 0xffff,param_5,DAT_0057cb30,local_14
                             );
  if (iVar2 == 0) {
    FUN_0043dacc(DAT_0057cb40,0x10,uVar1,local_14[0]);
    iVar2 = FUN_0058fb38(uVar1,local_14[0]);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0057c61c,DAT_0057c618,DAT_0057cb38,0xe5,DAT_0057cb50);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0057ccd4,DAT_0057ccd4);
      }
      iVar2 = 0;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057cb38,0xe2,DAT_0057cb48,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0057cb4c,DAT_0057cb4c,iVar2);
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057cb38,0xda,DAT_0057cb34,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0057cb3c,DAT_0057cb3c,iVar2);
    }
  }
  return iVar2;
}

