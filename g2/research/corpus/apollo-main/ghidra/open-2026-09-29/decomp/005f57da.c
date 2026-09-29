
undefined4 Ins_NPUSHW(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  bVar1 = *(byte *)(*(int *)(param_1 + 0x168) + *(int *)(param_1 + 0x16c) + 1);
  if ((uint)bVar1 < (uint)((*(int *)(param_1 + 0x14) + 1) - *(int *)(param_1 + 0x10))) {
    *(int *)(param_1 + 0x16c) = *(int *)(param_1 + 0x16c) + 2;
    for (uVar3 = 0; uVar3 < bVar1; uVar3 = uVar3 + 1) {
      uVar2 = GetShortIns(param_1);
      *(undefined4 *)(param_2 + (uint)uVar3 * 4) = uVar2;
    }
    *(undefined1 *)(param_1 + 0x17c) = 0;
    *(uint *)(param_1 + 0x20) = *(int *)(param_1 + 0x20) + (uint)bVar1;
  }
  else {
    *(undefined4 *)(param_1 + 0xc) = 0x82;
  }
  return param_4;
}

