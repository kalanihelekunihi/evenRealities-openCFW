
void FUN_005c5370(int param_1,undefined4 param_2,int param_3,uint param_4)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 local_a8;
  int local_a4;
  undefined4 local_a0;
  int local_9c;
  undefined1 auStack_98 [16];
  undefined4 local_88;
  uint uStack_28;
  
  if (param_3 != 0xffff) {
    iVar5 = *(int *)(param_1 + 0x2c);
    uVar1 = *(undefined2 *)(iVar5 + 0x28);
    if ((param_4 & 0xffff) != (uint)*(ushort *)(iVar5 + 0x28)) {
      *(short *)(iVar5 + 0x28) = (short)param_4;
      *(ushort *)(iVar5 + 0x2a) = *(ushort *)(iVar5 + 0x2a) | 8;
    }
    uStack_28 = param_4;
    iVar2 = FUN_005c45d8(iVar5,0x40000);
    iVar3 = FUN_005c45e2(iVar5,0x40000);
    iVar2 = *(int *)(iVar2 + 0xc);
    iVar4 = FUN_005c5722(param_1);
    local_a4 = ((iVar3 + iVar2) * param_3 + *(int *)(iVar4 + 0x18)) - iVar3 / 2;
    local_9c = iVar3 + iVar2 + local_a4 + -1;
    local_a8 = *(undefined4 *)(*(int *)(param_1 + 0x2c) + 0x14);
    local_a0 = *(undefined4 *)(*(int *)(param_1 + 0x2c) + 0x1c);
    FUN_00451b9c(auStack_98);
    local_88 = param_2;
    FUN_00452616(iVar5,0x40000,auStack_98);
    FUN_00451c6e(param_2,auStack_98,&local_a8);
    *(undefined2 *)(iVar5 + 0x28) = uVar1;
    *(ushort *)(iVar5 + 0x2a) = *(ushort *)(iVar5 + 0x2a) & 0xfff7;
  }
  return;
}

