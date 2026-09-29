
undefined4 FUN_0055c2bc(uint param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint *puVar3;
  
  iVar1 = DAT_0055cc18;
  if (param_1 < 8) {
    if (param_2 == (int *)0x0) {
      uVar2 = 6;
    }
    else if (*(int *)(DAT_0055cc18 + param_1 * 0x8a8) << 7 < 0) {
      uVar2 = 7;
    }
    else {
      puVar3 = (uint *)(param_1 * 0x8a8 + DAT_0055cc18);
      *puVar3 = *puVar3 | 0x1000000;
      puVar3 = (uint *)(param_1 * 0x8a8 + iVar1);
      *puVar3 = *puVar3 & 0xfdffffff;
      puVar3 = (uint *)(iVar1 + param_1 * 0x8a8);
      *puVar3 = *puVar3 & 0xff000000 | DAT_0055cf30;
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

