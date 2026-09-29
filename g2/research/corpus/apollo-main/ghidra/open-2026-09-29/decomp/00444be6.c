
int _verifyFlashContent(int param_1,int param_2,uint param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  iVar4 = 0;
  FUN_00475014(0,1);
  uVar3 = param_3;
  while( true ) {
    uVar1 = DAT_0044558c;
    if (uVar3 == 0) {
      return 0;
    }
    uVar5 = uVar3;
    if (0x1000 < uVar3) {
      uVar5 = 0x1000;
    }
    (**(code **)(param_4 + 0x18))(DAT_0044558c,iVar4 + param_1,uVar5);
    iVar2 = FUN_004751c8(uVar1,iVar4 + param_2,uVar5);
    if (iVar2 != 0) break;
    iVar4 = uVar5 + iVar4;
    uVar3 = uVar3 - uVar5;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(1,DAT_00444dec,DAT_00444de8,DAT_00445594,0x2ac,DAT_00445590,param_1,param_3);
  }
  iVar4 = FUN_0043d0ce();
  if ((-1 < iVar4 << 0x1f) && (iVar4 = FUN_0043d0ce(), -1 < iVar4 << 0x1d)) {
    return iVar2;
  }
  compress_log_output(0x4800000,DAT_00445598,DAT_00445598,param_1,param_3);
  return iVar2;
}

