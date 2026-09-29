
undefined4 FUN_005904ce(uint *param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint *puVar3;
  uint uVar4;
  
  iVar1 = DAT_00590814;
  uVar4 = param_1[1];
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00590a20)) {
    uVar2 = 2;
  }
  else if ((*(uint *)(DAT_00590814 + uVar4 * 0x1000 + 0x28) & 0xfffffff) == 0 &&
           -1 < *(int *)(DAT_00590814 + uVar4 * 0x1000 + 0x28) << 3) {
    if (*(char *)(param_2 + 1) == '\0') {
      puVar3 = (uint *)(DAT_00590814 + uVar4 * 0x1000 + 0x200);
      *puVar3 = *puVar3 | 1;
      *(undefined4 *)(iVar1 + uVar4 * 0x1000 + 0x48) = 0x10;
    }
    else if (*(char *)(param_2 + 1) == '\x01') {
      puVar3 = (uint *)(DAT_00590814 + uVar4 * 0x1000 + 0x200);
      *puVar3 = *puVar3 | 0x10;
      *(undefined4 *)(iVar1 + uVar4 * 0x1000 + 0x48) = 1;
    }
    else if (*(char *)(param_2 + 1) == '\x02') {
      puVar3 = (uint *)(DAT_00590814 + uVar4 * 0x1000 + 0x200);
      *puVar3 = *puVar3 | 1;
      puVar3 = (uint *)(iVar1 + uVar4 * 0x1000 + 0x200);
      *puVar3 = *puVar3 | 0x10;
      *(undefined4 *)(iVar1 + uVar4 * 0x1000 + 0x48) = 0x11;
    }
    if ((*(char *)(param_2 + 1) == '\0') && (param_1[0x10] != 0xffffffff)) {
      param_1[0x13] = param_1[0x10];
      *(uint *)(iVar1 + uVar4 * 0x1000 + 0x224) = param_1[0x13];
      *(uint *)(iVar1 + uVar4 * 0x1000 + 0x220) = param_1[0x15] >> 2;
      *(undefined4 *)(iVar1 + uVar4 * 0x1000 + 0x21c) = 1;
    }
    else if ((*(char *)(param_2 + 1) == '\x01') && (param_1[0x12] != 0xffffffff)) {
      param_1[0x14] = param_1[0x12];
      *(uint *)(iVar1 + uVar4 * 0x1000 + 0x22c) = param_1[0x14];
      *(uint *)(iVar1 + uVar4 * 0x1000 + 0x228) = param_1[0x16] >> 2;
      *(undefined4 *)(iVar1 + uVar4 * 0x1000 + 0x21c) = 2;
    }
    else if (((*(char *)(param_2 + 1) == '\x02') && (param_1[0x12] != 0xffffffff)) &&
            (param_1[0x10] != 0xffffffff)) {
      param_1[0x14] = param_1[0x12];
      *(uint *)(iVar1 + uVar4 * 0x1000 + 0x22c) = param_1[0x14];
      *(uint *)(iVar1 + uVar4 * 0x1000 + 0x228) = param_1[0x16] >> 2;
      param_1[0x13] = param_1[0x10];
      *(uint *)(iVar1 + uVar4 * 0x1000 + 0x224) = param_1[0x13];
      *(uint *)(iVar1 + uVar4 * 0x1000 + 0x220) = param_1[0x15] >> 2;
      *(undefined4 *)(iVar1 + uVar4 * 0x1000 + 0x21c) = 3;
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

