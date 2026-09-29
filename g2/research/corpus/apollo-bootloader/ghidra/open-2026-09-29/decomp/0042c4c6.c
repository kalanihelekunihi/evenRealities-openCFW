
undefined4 hw_context_claim_42c4c6(uint param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint *puVar3;
  
  iVar1 = DAT_0042cdb4;
  if (param_1 < 8) {
    if (param_2 == (int *)0x0) {
      uVar2 = 6;
    }
    else if (*(int *)(DAT_0042cdb4 + param_1 * 0x8a8) << 7 < 0) {
      uVar2 = 7;
    }
    else {
      puVar3 = (uint *)(param_1 * 0x8a8 + DAT_0042cdb4);
      *puVar3 = *puVar3 | 0x1000000;
      puVar3 = (uint *)(param_1 * 0x8a8 + iVar1);
      *puVar3 = *puVar3 & 0xfdffffff;
      puVar3 = (uint *)(iVar1 + param_1 * 0x8a8);
      *puVar3 = *puVar3 & 0xff000000 | DAT_0042cdb8;
      *(uint *)(param_1 * 0x8a8 + iVar1 + 4) = param_1;
      *param_2 = param_1 * 0x8a8 + iVar1;
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 5;
  }
  return uVar2;
}

