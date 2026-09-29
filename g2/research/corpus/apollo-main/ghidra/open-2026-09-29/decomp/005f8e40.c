
undefined8
tt_size_ready_bytecode(int *param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if (param_1[0x4c] < 0) {
    iVar1 = tt_size_init_bytecode(param_1,param_2);
  }
  else {
    iVar1 = param_1[0x4c];
  }
  if (iVar1 == 0) {
    if (param_1[0x4d] < 0) {
      iVar1 = *param_1;
      for (uVar3 = 0; uVar3 < (uint)param_1[0x3e]; uVar3 = uVar3 + 1) {
        uVar2 = FT_MulFix((int)*(short *)(*(int *)(iVar1 + 0x29c) + uVar3 * 2),param_1[0x17]);
        *(undefined4 *)(param_1[0x3f] + uVar3 * 4) = uVar2;
      }
      for (uVar3 = 0; uVar3 < *(ushort *)(param_1 + 0x44); uVar3 = uVar3 + 1) {
        *(undefined4 *)(param_1[0x45] + uVar3 * 8) = 0;
        *(undefined4 *)(param_1[0x45] + uVar3 * 8 + 4) = 0;
        *(undefined4 *)(param_1[0x46] + uVar3 * 8) = 0;
        *(undefined4 *)(param_1[0x46] + uVar3 * 8 + 4) = 0;
      }
      for (uVar3 = 0; uVar3 < *(ushort *)(param_1 + 0x40); uVar3 = uVar3 + 1) {
        *(undefined4 *)(param_1[0x41] + uVar3 * 4) = 0;
      }
      FUN_00439c04(param_1 + 0x2d,DAT_005f9500,0x44);
      iVar1 = tt_size_run_prep(param_1,param_2);
    }
    else {
      iVar1 = param_1[0x4d];
    }
  }
  return CONCAT44(param_4,iVar1);
}

