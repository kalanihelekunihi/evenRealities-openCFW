
undefined8 FUN_004e772c(uint param_1,undefined4 param_2)

{
  byte bVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar4 = 0;
  uVar5 = param_1;
  while( true ) {
    iVar3 = DAT_004e7ffc;
    if (*DAT_004e80dc <= (int)uVar4) break;
    if (*(int *)(DAT_004e7ffc + uVar4 * 4) != 0) {
      if (uVar4 == param_1) {
        uVar2 = FUN_0044104c(0xffffff);
        FUN_0044127e(*(undefined4 *)(iVar3 + uVar4 * 4),uVar2,0);
        FUN_0044129e(*(undefined4 *)(iVar3 + uVar4 * 4),0xff,0);
      }
      else {
        uVar2 = FUN_0044104c(DAT_004e7ff8);
        FUN_0044127e(*(undefined4 *)(iVar3 + uVar4 * 4),uVar2,0);
        FUN_0044129e(*(undefined4 *)(iVar3 + uVar4 * 4),0x96,0);
      }
    }
    uVar4 = uVar4 + 1;
  }
  if (0 < *DAT_004e80dc) {
    bVar1 = FUN_004ffeb4(param_1);
    iVar3 = FUN_005000cc(param_1,bVar1);
    if (iVar3 != 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        uVar5 = 0x153;
        param_2 = DAT_004e80e0;
        FUN_0043d574(2,DAT_004e7fe8,DAT_004e7fe4,DAT_004e80e4,0x153,DAT_004e80e0,param_1,bVar1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        uVar5 = (uint)bVar1;
        compress_log_output(0x8800000,DAT_004e83b4,DAT_004e83b4,param_1);
      }
    }
  }
  return CONCAT44(param_2,uVar5);
}

