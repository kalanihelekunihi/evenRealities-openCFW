
undefined8 FUN_0050afa4(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar1 = FUN_0043d0ce();
    iVar4 = param_2;
    if (iVar1 << 0x1e < 0) {
      iVar4 = 0x3bc;
      FUN_0043d574(2,DAT_0050b5dc,DAT_0050b5d8,DAT_0050b730,0x3bc,DAT_0050b72c,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050b734);
    }
    uVar2 = 0;
  }
  else {
    iVar4 = param_2;
    iVar1 = FUN_0050b168(param_1);
    if (iVar1 == 0) {
      FUN_00439be4(param_2,(uint)*(ushort *)(param_1 + 2) * 0xc88 + param_1 + 0x10,0xc88);
      uVar3 = *(ushort *)(param_1 + 2) + 1;
      *(ushort *)(param_1 + 2) =
           (short)uVar3 - *(ushort *)(param_1 + 8) * (short)(uVar3 / *(ushort *)(param_1 + 8));
      *(short *)(param_1 + 4) = *(short *)(param_1 + 4) + -1;
      uVar2 = 1;
    }
    else {
      uVar2 = 0;
    }
  }
  return CONCAT44(iVar4,uVar2);
}

