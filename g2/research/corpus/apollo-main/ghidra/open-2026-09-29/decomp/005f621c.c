
undefined4
Compute_Point_Displacement
          (int param_1,undefined4 *param_2,undefined4 *param_3,undefined4 param_4,ushort *param_5)

{
  ushort uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined1 auStack_40 [8];
  ushort local_38;
  int local_34;
  int local_30;
  
  if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1f) < 0) {
    FUN_00439c04(auStack_40,param_1 + 0x24,0x24);
    uVar1 = *(ushort *)(param_1 + 0x122);
  }
  else {
    FUN_00439c04(auStack_40,param_1 + 0x48,0x24);
    uVar1 = *(ushort *)(param_1 + 0x124);
  }
  if (uVar1 < local_38) {
    FUN_00439c04(param_4,auStack_40,0x24);
    *param_5 = uVar1;
    uVar2 = (**(code **)(param_1 + 0x240))
                      (param_1,*(int *)(local_30 + (uint)uVar1 * 8) -
                               *(int *)(local_34 + (uint)uVar1 * 8),
                       *(int *)(local_30 + (uint)uVar1 * 8 + 4) -
                       *(int *)(local_34 + (uint)uVar1 * 8 + 4));
    uVar3 = FT_MulDiv(uVar2,(int)*(short *)(param_1 + 0x12e),*(undefined4 *)(param_1 + 0x238));
    *param_2 = uVar3;
    uVar2 = FT_MulDiv(uVar2,(int)*(short *)(param_1 + 0x130),*(undefined4 *)(param_1 + 0x238));
    *param_3 = uVar2;
    uVar2 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x235) != '\0') {
      *(undefined4 *)(param_1 + 0xc) = 0x86;
    }
    *param_5 = 0;
    uVar2 = 1;
  }
  return uVar2;
}

