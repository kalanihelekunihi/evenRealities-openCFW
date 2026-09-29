
void Ins_MDAP(int param_1,uint *param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = *param_2;
  if ((uVar3 & 0xffff) < (uint)*(ushort *)(param_1 + 0x2c)) {
    if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1f) < 0) {
      iVar1 = (**(code **)(param_1 + 0x240))
                        (param_1,*(undefined4 *)(*(int *)(param_1 + 0x34) + (uVar3 & 0xffff) * 8),
                         *(undefined4 *)(*(int *)(param_1 + 0x34) + (uVar3 & 0xffff) * 8 + 4));
      iVar2 = (**(code **)(param_1 + 0x23c))(param_1,iVar1,*(undefined4 *)(param_1 + 0x10c));
      iVar2 = iVar2 - iVar1;
    }
    else {
      iVar2 = 0;
    }
    (**(code **)(param_1 + 0x24c))(param_1,param_1 + 0x24,uVar3 & 0xffff,iVar2);
    *(short *)(param_1 + 0x120) = (short)uVar3;
    *(short *)(param_1 + 0x122) = (short)uVar3;
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return;
}

