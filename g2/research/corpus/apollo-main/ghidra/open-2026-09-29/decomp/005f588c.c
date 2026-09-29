
undefined4 Ins_PUSHW(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  ushort uVar2;
  ushort uVar3;
  
  uVar2 = *(byte *)(param_1 + 0x174) - 0xb7;
  if ((uint)uVar2 < (uint)((*(int *)(param_1 + 0x14) + 1) - *(int *)(param_1 + 0x10))) {
    *(int *)(param_1 + 0x16c) = *(int *)(param_1 + 0x16c) + 1;
    for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1) {
      uVar1 = GetShortIns(param_1);
      *(undefined4 *)(param_2 + (uint)uVar3 * 4) = uVar1;
    }
    *(undefined1 *)(param_1 + 0x17c) = 0;
  }
  else {
    *(undefined4 *)(param_1 + 0xc) = 0x82;
  }
  return param_4;
}

