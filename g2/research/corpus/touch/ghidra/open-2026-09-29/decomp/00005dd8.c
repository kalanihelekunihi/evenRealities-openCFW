
undefined4 touch_sub_2ad8(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint local_14;
  
  local_14 = 500;
  if (param_1 == (int *)0x0) {
    uVar2 = 1;
  }
  else {
    Cy_SysClk_IloStartMeasurement();
    do {
      iVar1 = Cy_SysClk_IloCompensate(local_14,&local_14);
    } while (iVar1 != 0);
    iVar1 = *DAT_00005e5c;
    Cy_SysClk_IloStopMeasurement();
    iVar3 = param_1[2];
    uVar2 = __aeabi_uidiv(iVar1 << 0x18,DAT_00005e60);
    *(undefined4 *)(iVar3 + 0x2c) = uVar2;
    iVar1 = param_1[2];
    uVar2 = touch_sub_2a70(*(undefined4 *)(iVar1 + 0x1c),param_1);
    *(undefined4 *)(iVar1 + 0x20) = uVar2;
    iVar1 = param_1[2];
    uVar2 = touch_sub_2a70(*(undefined4 *)(iVar1 + 0x24),param_1);
    *(undefined4 *)(iVar1 + 0x28) = uVar2;
    local_14 = *(uint *)(param_1[2] + 0x20);
    if (*(int *)(param_1[1] + 8) << 0x1a < 0) {
      local_14 = *(uint *)(param_1[2] + 0x28);
    }
    *(uint *)(**(int **)(*param_1 + 8) + 0x70) =
         *(uint *)(**(int **)(*param_1 + 8) + 0x70) & 0xffff0000;
    *(uint *)(**(int **)(*param_1 + 8) + 0x70) =
         *(uint *)(**(int **)(*param_1 + 8) + 0x70) | local_14;
    uVar2 = 0;
  }
  return uVar2;
}

