
void Ins_GC(int param_1,uint *param_2)

{
  uint uVar1;
  
  uVar1 = *param_2;
  if (uVar1 < *(ushort *)(param_1 + 0x74)) {
    if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1f) < 0) {
      uVar1 = (**(code **)(param_1 + 0x244))
                        (param_1,*(undefined4 *)(*(int *)(param_1 + 0x78) + uVar1 * 8),
                         *(undefined4 *)(*(int *)(param_1 + 0x78) + uVar1 * 8 + 4));
    }
    else {
      uVar1 = (**(code **)(param_1 + 0x240))
                        (param_1,*(undefined4 *)(*(int *)(param_1 + 0x7c) + uVar1 * 8),
                         *(undefined4 *)(*(int *)(param_1 + 0x7c) + uVar1 * 8 + 4));
    }
  }
  else {
    if (*(char *)(param_1 + 0x235) != '\0') {
      *(undefined4 *)(param_1 + 0xc) = 0x86;
    }
    uVar1 = 0;
  }
  *param_2 = uVar1;
  return;
}

