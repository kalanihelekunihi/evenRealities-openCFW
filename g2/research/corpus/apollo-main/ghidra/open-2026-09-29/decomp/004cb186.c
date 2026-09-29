
undefined8 FUN_004cb186(int param_1,int *param_2,undefined4 param_3,undefined *param_4)

{
  uint uVar1;
  int iVar2;
  undefined *local_10;
  
  do {
    while (local_10 = param_4, *(uint *)(param_1 + 0x5c) < *(uint *)(param_1 + 0x58)) {
      if (-1 < (int)((uint)(*(byte *)(*(int *)(param_1 + 100) + (*(uint *)(param_1 + 0x5c) >> 3)) >>
                           (*(byte *)(param_1 + 0x5c) & 7)) << 0x1f)) {
        uVar1 = *(int *)(param_1 + 0x5c) + *(int *)(param_1 + 0x54);
        *param_2 = uVar1 - *(uint *)(param_1 + 0x6c) * (uVar1 / *(uint *)(param_1 + 0x6c));
        goto LAB_004cb1cc;
      }
      *(int *)(param_1 + 0x5c) = *(int *)(param_1 + 0x5c) + 1;
      *(int *)(param_1 + 0x60) = *(int *)(param_1 + 0x60) + -1;
    }
    if (*(int *)(param_1 + 0x60) == 0) {
      uVar1 = *(int *)(param_1 + 0x5c) + *(int *)(param_1 + 0x54);
      local_10 = &DAT_004cb3c4;
      FUN_004733ee(DAT_004cbf34,DAT_004cb594,0x2c2,
                   uVar1 - *(uint *)(param_1 + 0x6c) * (uVar1 / *(uint *)(param_1 + 0x6c)));
      iVar2 = -0x1c;
      break;
    }
    iVar2 = FUN_004cb12e(param_1);
  } while (iVar2 == 0);
  goto LAB_004cb238;
  while ((int)((uint)(*(byte *)(*(int *)(param_1 + 100) + (*(uint *)(param_1 + 0x5c) >> 3)) >>
                     (*(byte *)(param_1 + 0x5c) & 7)) << 0x1f) < 0) {
LAB_004cb1cc:
    *(int *)(param_1 + 0x5c) = *(int *)(param_1 + 0x5c) + 1;
    *(int *)(param_1 + 0x60) = *(int *)(param_1 + 0x60) + -1;
    if (*(uint *)(param_1 + 0x58) <= *(uint *)(param_1 + 0x5c)) break;
  }
  iVar2 = 0;
LAB_004cb238:
  return CONCAT44(local_10,iVar2);
}

