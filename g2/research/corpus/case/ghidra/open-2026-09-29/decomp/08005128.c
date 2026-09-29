
undefined8 FUN_08005128(ushort *param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  bool bVar7;
  uint local_20;
  
  iVar2 = DAT_080052d4;
  iVar1 = DAT_080052d0;
  uVar6 = 0;
  local_20 = param_2;
  if (-1 < *(int *)param_1 << 0xe) goto LAB_080051e4;
  bVar7 = -1 < *(int *)(DAT_080052d4 + 0x3c) << 3;
  if (bVar7) {
    *(uint *)(DAT_080052d4 + 0x3c) = *(uint *)(DAT_080052d4 + 0x3c) | DAT_080052d0 << 0x16;
  }
  local_20 = (uint)bVar7;
  *DAT_080052d8 = *DAT_080052d8 | (int)DAT_080052d8 >> 0x16;
  iVar3 = case_tick_word2();
  do {
    if ((int)(*DAT_080052d8 << 0x17) < 0) {
      uVar4 = *(uint *)(iVar1 + 0x1c) & 0x300;
      if ((uVar4 != 0) && (*(uint *)(param_1 + 0x12) != uVar4)) {
        uVar4 = *(uint *)(iVar1 + 0x1c) & 0xfffffcff;
        *(uint *)(iVar1 + 0x1c) = *(uint *)(iVar1 + 0x1c) | 0x10000;
        *(uint *)(iVar1 + 0x1c) = *(uint *)(iVar1 + 0x1c) & 0xfffeffff;
        *(uint *)(iVar1 + 0x1c) = uVar4;
      }
      if ((uVar4 & 1) == 0) goto LAB_080051c6;
      iVar3 = case_tick_word2();
      goto LAB_080051c0;
    }
    iVar5 = case_tick_word2();
  } while ((uint)(iVar5 - iVar3) < 3);
  goto LAB_080051bc;
LAB_080051c6:
  *(uint *)(iVar1 + 0x1c) = *(uint *)(iVar1 + 0x1c) & 0xfffffcff | *(uint *)(param_1 + 0x12);
  goto LAB_080051d4;
  while( true ) {
    iVar5 = case_tick_word2();
    if (DAT_080052dc < (uint)(iVar5 - iVar3)) break;
LAB_080051c0:
    if (*(int *)(iVar1 + 0x1c) << 0x1e < 0) goto LAB_080051c6;
  }
LAB_080051bc:
  uVar6 = 3;
LAB_080051d4:
  if (local_20 != 0) {
    *(uint *)(iVar2 + 0x3c) = *(uint *)(iVar2 + 0x3c) & 0xefffffff;
  }
LAB_080051e4:
  if ((*param_1 & 1) != 0) {
    *(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & 0xfffffffc | *(uint *)(param_1 + 2);
  }
  if ((int)((uint)(byte)*param_1 * 0x40000000) < 0) {
    *(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & 0xfffffff3 | *(uint *)(param_1 + 4);
  }
  if ((int)((uint)(byte)*param_1 << 0x1d) < 0) {
    *(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & 0xffffffcf | *(uint *)(param_1 + 6);
  }
  uVar4 = DAT_080052e0;
  if ((int)((uint)(byte)*param_1 << 0x1a) < 0) {
    *(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & ~DAT_080052e0 | *(uint *)(param_1 + 8);
  }
  if ((int)((uint)(byte)*param_1 << 0x19) < 0) {
    *(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & 0xffff3fff | *(uint *)(param_1 + 10);
  }
  if (((int)((uint)*param_1 << 0x11) < 0) &&
     (*(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & 0x3fffffff | *(uint *)(param_1 + 0x10),
     *(int *)(param_1 + 0x10) == 0x40000000)) {
    *(uint *)(iVar2 + 0xc) = *(uint *)(iVar2 + 0xc) | 0x10000;
  }
  if (((int)((uint)*param_1 << 0x14) < 0) &&
     (*(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & 0xfffffffc | *(uint *)(param_1 + 0xc),
     *(int *)(param_1 + 0xc) == 1)) {
    *(uint *)(iVar2 + 0xc) = *(uint *)(iVar2 + 0xc) | 0x10000;
  }
  if (((int)((uint)*param_1 << 0x12) < 0) &&
     (*(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & 0xfffffff3 | *(uint *)(param_1 + 0xe),
     *(int *)(param_1 + 0xe) == 4)) {
    *(uint *)(iVar2 + 0xc) = *(uint *)(iVar2 + 0xc) | 0x10000;
  }
  if ((*(int *)param_1 << 7 < 0) &&
     (*(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & ~uVar4 | *(uint *)(param_1 + 0x14),
     *(int *)(param_1 + 0x14) == 0x2000)) {
    *(uint *)(iVar2 + 0xc) = *(uint *)(iVar2 + 0xc) | 0x1000000;
  }
  return CONCAT44(local_20,uVar6);
}

