
undefined4 FUN_0050b054(int param_1,int param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0050b5dc,DAT_0050b5d8,DAT_0050b738,0x3e5,DAT_0050b72c,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050b734,DAT_0050b734);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0050b168(param_1);
    if (iVar1 == 0) {
      if ((param_3 & 0xffff) < (uint)*(ushort *)(param_1 + 4)) {
        uVar3 = (param_3 & 0xffff) + (uint)*(ushort *)(param_1 + 2);
        FUN_00439be4(param_2,(uVar3 - (uint)*(ushort *)(param_1 + 8) *
                                      (uVar3 / *(ushort *)(param_1 + 8)) & 0xffff) * 0xc88 + param_1
                             + 0x10,0xc88);
        uVar2 = 1;
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,DAT_0050b5dc,DAT_0050b5d8,DAT_0050b738,0x3ef,DAT_0050ba5c,param_3 & 0xffff,
                       *(undefined2 *)(param_1 + 4));
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8800000,DAT_0050ba60,DAT_0050ba60,param_3 & 0xffff,
                              *(undefined2 *)(param_1 + 4));
        }
        uVar2 = 0;
      }
    }
    else {
      uVar2 = 0;
    }
  }
  return uVar2;
}

