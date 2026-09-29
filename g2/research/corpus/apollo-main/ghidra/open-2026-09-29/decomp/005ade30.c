
undefined8 cff_charset_compute_cids(int param_1,uint param_2,undefined4 param_3)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  ushort uVar4;
  int local_18;
  
  local_18 = 0;
  uVar4 = 0;
  uVar1 = param_2;
  if (*(int *)(param_1 + 0x10) == 0) {
    for (uVar1 = 0; uVar1 < param_2; uVar1 = uVar1 + 1) {
      if (uVar4 < *(ushort *)(*(int *)(param_1 + 8) + uVar1 * 2)) {
        uVar4 = *(ushort *)(*(int *)(param_1 + 8) + uVar1 * 2);
      }
    }
    uVar1 = 0;
    uVar2 = ft_mem_realloc(param_3,2,0,uVar4 + 1,0,&local_18);
    *(undefined4 *)(param_1 + 0xc) = uVar2;
    uVar3 = param_2;
    if (local_18 == 0) {
      while (uVar3 = uVar3 - 1, -1 < (int)uVar3) {
        *(short *)(*(int *)(param_1 + 0xc) +
                  (uint)*(ushort *)(*(int *)(param_1 + 8) + uVar3 * 2) * 2) = (short)uVar3;
      }
      *(uint *)(param_1 + 0x10) = (uint)uVar4;
      *(uint *)(param_1 + 0x14) = param_2;
    }
  }
  return CONCAT44(uVar1,local_18);
}

