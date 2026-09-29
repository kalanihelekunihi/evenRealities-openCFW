
void AT_Handler(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  byte bVar4;
  undefined2 local_1c [2];
  undefined4 local_18;
  
  iVar1 = DAT_005415a4;
  local_1c[0] = *DAT_005415a0;
  local_18 = 0;
  FUN_0043c0e4(DAT_005415a4,0x300,0);
  iVar2 = FUN_0057deb0(param_1,local_1c,&local_18);
  for (bVar4 = 0; (iVar2 != 0 && (bVar4 < 3)); bVar4 = bVar4 + 1) {
    FUN_0044b728((uint)bVar4 * 0x100 + iVar1,0x100,&DAT_0054157c);
    iVar2 = FUN_0057deb0(0,local_1c,&local_18);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00541598,DAT_00541594,DAT_005415ac,0xab,DAT_005415a8,param_1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005415b0,DAT_005415b0,param_1);
  }
  if (bVar4 < 3) {
    iVar2 = 0;
  }
  else {
    iVar2 = iVar1 + 0x200;
  }
  if (bVar4 < 2) {
    iVar3 = 0;
  }
  else {
    iVar3 = iVar1 + 0x100;
  }
  at_core_dispatch_command(iVar1,iVar3,iVar2);
  return;
}

