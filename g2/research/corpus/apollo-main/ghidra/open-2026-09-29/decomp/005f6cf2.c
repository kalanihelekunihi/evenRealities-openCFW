
undefined4 Ins_ALIGNRP(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  if ((*(int *)(param_1 + 0x10) < *(int *)(param_1 + 0x134)) ||
     (*(ushort *)(param_1 + 0x2c) <= *(ushort *)(param_1 + 0x120))) {
    if (*(char *)(param_1 + 0x235) != '\0') {
      *(undefined4 *)(param_1 + 0xc) = 0x86;
    }
  }
  else {
    while (0 < *(int *)(param_1 + 0x134)) {
      *(int *)(param_1 + 0x1c) = *(int *)(param_1 + 0x1c) + -1;
      uVar2 = *(uint *)(*(int *)(param_1 + 0x18) + *(int *)(param_1 + 0x1c) * 4);
      if ((uVar2 & 0xffff) < (uint)*(ushort *)(param_1 + 0x50)) {
        iVar1 = (**(code **)(param_1 + 0x240))
                          (param_1,*(int *)(*(int *)(param_1 + 0x58) + (uVar2 & 0xffff) * 8) -
                                   *(int *)(*(int *)(param_1 + 0x34) +
                                           (uint)*(ushort *)(param_1 + 0x120) * 8),
                           *(int *)(*(int *)(param_1 + 0x58) + (uVar2 & 0xffff) * 8 + 4) -
                           *(int *)(*(int *)(param_1 + 0x34) +
                                    (uint)*(ushort *)(param_1 + 0x120) * 8 + 4));
        (**(code **)(param_1 + 0x24c))(param_1,param_1 + 0x48,uVar2 & 0xffff,-iVar1);
      }
      else if (*(char *)(param_1 + 0x235) != '\0') {
        *(undefined4 *)(param_1 + 0xc) = 0x86;
        return param_4;
      }
      *(int *)(param_1 + 0x134) = *(int *)(param_1 + 0x134) + -1;
    }
  }
  *(undefined4 *)(param_1 + 0x134) = 1;
  *(undefined4 *)(param_1 + 0x20) = *(undefined4 *)(param_1 + 0x1c);
  return param_4;
}

