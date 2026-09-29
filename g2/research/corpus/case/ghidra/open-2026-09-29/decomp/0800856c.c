
void FUN_0800856c(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined2 uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  iVar1 = DAT_080085ac;
  if (param_1[0x19] == 0) {
    uVar2 = 1;
    *(undefined2 *)((int)param_1 + 0x6a) = 1;
  }
  else {
    uVar4 = (*(uint *)(*param_1 + 8) & 0xfffffff) >> 0x19;
    uVar3 = *(uint *)(*param_1 + 8) >> 0x1d;
    iVar5 = DAT_080085ac + -8;
    uVar2 = __aeabi_uidiv((uint)*(byte *)(iVar5 + uVar3) << 3,*(undefined1 *)(DAT_080085ac + uVar3),
                          param_3,param_4,param_4);
    *(undefined2 *)((int)param_1 + 0x6a) = uVar2;
    uVar2 = __aeabi_uidiv((uint)*(byte *)(iVar5 + uVar4) << 3,*(undefined1 *)(iVar1 + uVar4));
  }
  *(undefined2 *)(param_1 + 0x1a) = uVar2;
  return;
}

