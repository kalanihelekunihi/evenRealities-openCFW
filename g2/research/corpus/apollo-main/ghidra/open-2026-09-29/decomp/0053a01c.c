
undefined8 FUN_0053a01c(undefined4 param_1,int param_2,undefined4 param_3,int param_4)

{
  byte bVar1;
  byte *pbVar2;
  int iVar3;
  uint uVar4;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  int iStack_1c;
  
  iVar3 = DAT_0053a3c4;
  pbVar2 = DAT_0053a3c0;
  uStack_20 = (undefined2)param_3;
  uStack_1e = (undefined2)((uint)param_3 >> 0x10);
  iStack_1c = param_4;
  if (param_2 - 3U < 0x3fe) {
    bVar1 = *DAT_0053a3c0;
    FUN_00439be4(DAT_0053a3c4 + (uint)bVar1 * 0x400,param_1,param_2);
    FUN_0043c0e4((uint)bVar1 * 0x400 + iVar3 + param_2,0x400 - param_2,0);
    uVar4 = *pbVar2 + 1;
    *pbVar2 = (char)uVar4 + (char)(uVar4 / 5) * -5;
    uStack_20 = 1;
    uStack_1e = (undefined2)param_2;
    iStack_1c = iVar3 + (uint)bVar1 * 0x400;
    device_mgr_fn_004c659a(&uStack_20);
  }
  return CONCAT44(iStack_1c,CONCAT22(uStack_1e,uStack_20));
}

