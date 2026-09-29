
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void DmRegister(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  undefined2 uStack_90;
  undefined1 uStack_8e;
  undefined1 uStack_8d;
  
  iVar1 = DAT_004d2ae8;
  *(undefined4 *)(DAT_004d2ae8 + 8) = param_1;
  if ((*(int *)(DAT_004d2aec + 0x20) != _DAT_004d2af4) &&
     (iVar2 = HciGetMaxRxAclLen(), iVar2 + -4 < 0x41)) {
    uStack_90 = 0;
    uStack_8e = 0x78;
    uStack_8d = 1;
    (**(code **)(iVar1 + 8))(&uStack_90);
  }
  return;
}

