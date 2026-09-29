
undefined4 Cy_SysClk_ImoSetFrequency(int param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  
  uVar4 = DAT_00009d8c;
  if ((*(int *)(DAT_00009d4c + 0x30) < 0) &&
     ((((param_1 == DAT_00009d50 || (param_1 == DAT_00009d54)) || (param_1 == DAT_00009d58)) ||
      (((param_1 == DAT_00009d5c || (param_1 == DAT_00009d60)) ||
       ((param_1 == DAT_00009d64 || (uVar4 = DAT_00009d6c, param_1 == DAT_00009d68)))))))) {
    iVar2 = Cy_SysClk_ImoGetFrequency();
    if (iVar2 == param_1) {
      uVar4 = 0;
    }
    else {
      uVar3 = __aeabi_uidiv(param_1 + DAT_00009d70,DAT_00009d74);
      uVar4 = Cy_SysLib_EnterCriticalSection();
      iVar2 = DAT_00009d4c;
      *(undefined4 *)(DAT_00009d4c + DAT_00009d78) = 0;
      *(uint *)(iVar2 + DAT_00009d80) = (uint)*(byte *)(uVar3 + DAT_00009d7c);
      *(undefined4 *)(iVar2 + 0xf10) = 0;
      *(uint *)(iVar2 + DAT_00009d88) = (uint)*(byte *)(uVar3 + DAT_00009d84);
      uVar3 = uVar3 >> 2;
      Cy_SysLib_DelayCycles(0x32);
      iVar1 = DAT_00009d78;
      iVar2 = DAT_00009d4c;
      if (uVar3 != 0) {
        *(uint *)(DAT_00009d4c + DAT_00009d78) =
             *(uint *)(DAT_00009d4c + DAT_00009d78) & 0xfffffff8 | uVar3 - 1 & 7;
        Cy_SysLib_DelayCycles(0x32);
        *(uint *)(iVar2 + iVar1) = *(uint *)(iVar2 + iVar1) & 0xfffffff8 | uVar3 & 7;
      }
      Cy_SysLib_ExitCriticalSection(uVar4);
      uVar4 = 0;
    }
  }
  return uVar4;
}

