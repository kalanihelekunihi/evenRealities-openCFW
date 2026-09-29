
undefined4 Ins_ALIGNPTS(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = *param_2;
  uVar3 = param_2[1];
  if (((uVar2 & 0xffff) < (uint)*(ushort *)(param_1 + 0x50)) &&
     ((uVar3 & 0xffff) < (uint)*(ushort *)(param_1 + 0x2c))) {
    iVar1 = (**(code **)(param_1 + 0x240))
                      (param_1,*(int *)(*(int *)(param_1 + 0x34) + (uVar3 & 0xffff) * 8) -
                               *(int *)(*(int *)(param_1 + 0x58) + (uVar2 & 0xffff) * 8),
                       *(int *)(*(int *)(param_1 + 0x34) + (uVar3 & 0xffff) * 8 + 4) -
                       *(int *)(*(int *)(param_1 + 0x58) + (uVar2 & 0xffff) * 8 + 4));
    (**(code **)(param_1 + 0x24c))(param_1,param_1 + 0x48,uVar2 & 0xffff,iVar1 / 2);
    (**(code **)(param_1 + 0x24c))(param_1,param_1 + 0x24,uVar3 & 0xffff,-(iVar1 / 2));
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return param_4;
}

