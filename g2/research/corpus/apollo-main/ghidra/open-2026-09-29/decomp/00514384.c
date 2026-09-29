
void FUN_00514384(int param_1)

{
  if (param_1 == 0) {
    FUN_004b127c(0x2000);
    return;
  }
  if (*(int *)(param_1 + 0x24) != 0) {
    param_1 = *(int *)(param_1 + 0x24);
  }
  do {
    if ((*(int *)(param_1 + 0x24) != 0) && (param_1 == *(int *)(*DAT_00514b78 + 4))) {
      *(int *)(*DAT_00514b78 + 4) = *(int *)(param_1 + 0x24);
    }
    *(undefined4 *)(param_1 + 0x14) = 0;
    *(undefined4 *)(param_1 + 0x30) = 0;
    if (param_1 == 0) {
      FUN_004b127c(0x2000);
    }
    else {
      *(uint *)(param_1 + 0x18) = *(uint *)(param_1 + 0x18) & 0xfffffffb;
    }
    param_1 = *(int *)(param_1 + 0x20);
  } while (param_1 != 0);
  return;
}

