
undefined8 FUN_004f7f18(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = param_1;
  if ((param_1 != 0) && (*DAT_004f8090 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar4 = 0xb03;
      param_2 = DAT_004f88c8;
      param_3 = param_1;
      FUN_0043d574(4,DAT_004f81e0,DAT_004f81dc,DAT_004f88cc,0xb03,DAT_004f88c8,param_1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004f88d0,DAT_004f88d0,param_1,iVar4,param_2,param_3);
    }
    for (iVar2 = 0; (iVar1 = DAT_004f8638, iVar2 < (int)(uint)*DAT_004f8628 && (iVar2 < 0x28));
        iVar2 = iVar2 + 1) {
      if (*(int *)(DAT_004f8638 + iVar2 * 0x10) != 0) {
        iVar3 = FUN_0043fce0(*(undefined4 *)(DAT_004f8638 + iVar2 * 0x10));
        FUN_0043f142(*(undefined4 *)(iVar1 + iVar2 * 0x10),param_1 + iVar3);
      }
    }
  }
  return CONCAT44(param_2,iVar4);
}

