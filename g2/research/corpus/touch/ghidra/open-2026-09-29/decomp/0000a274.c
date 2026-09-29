
undefined4 Cy_SysInt_SetVector(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if (*(int *)(DAT_0000a29c + 8) == DAT_0000a2a0) {
    if (param_2 == 0) {
      software_bkpt(1);
    }
    iVar2 = (param_1 + 0x10) * 4;
    uVar1 = *(undefined4 *)(iVar2 + DAT_0000a2a0);
    *(int *)(iVar2 + DAT_0000a2a0) = param_2;
  }
  else {
    uVar1 = *(undefined4 *)((param_1 + 0x10) * 4 + DAT_0000a2a4);
  }
  return uVar1;
}

