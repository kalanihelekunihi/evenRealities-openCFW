
undefined8
cmdq_update_indices_427754(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = critical_save();
  *(uint *)(param_1 + 0x1c) =
       **(uint **)(*(int *)(param_1 + 0x24) + 8) & 0xff | *(uint *)(param_1 + 0x20) & 0xffffff00;
  if (*(int *)(param_1 + 0x20) - *(int *)(param_1 + 0x1c) < 0) {
    *(int *)(param_1 + 0x1c) = *(int *)(param_1 + 0x1c) + -0x100;
  }
  *(undefined4 *)(param_1 + 0xc) = **(undefined4 **)(*(int *)(param_1 + 0x24) + 4);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return CONCAT44(param_4,uVar2);
}

