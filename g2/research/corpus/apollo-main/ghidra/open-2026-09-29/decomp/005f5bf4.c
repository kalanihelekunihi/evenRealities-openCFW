
void Ins_SCFS(int param_1,uint *param_2)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  uVar5 = *param_2;
  if ((uVar5 & 0xffff) < (uint)*(ushort *)(param_1 + 0x74)) {
    iVar1 = (**(code **)(param_1 + 0x240))
                      (param_1,*(undefined4 *)(*(int *)(param_1 + 0x7c) + (uVar5 & 0xffff) * 8),
                       *(undefined4 *)(*(int *)(param_1 + 0x7c) + (uVar5 & 0xffff) * 8 + 4));
    (**(code **)(param_1 + 0x24c))(param_1,param_1 + 0x6c,uVar5 & 0xffff,param_2[1] - iVar1);
    if (*(short *)(param_1 + 0x160) == 0) {
      puVar2 = (undefined4 *)(*(int *)(param_1 + 0x7c) + (uVar5 & 0xffff) * 8);
      uVar4 = puVar2[1];
      puVar3 = (undefined4 *)(*(int *)(param_1 + 0x78) + (uVar5 & 0xffff) * 8);
      *puVar3 = *puVar2;
      puVar3[1] = uVar4;
    }
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return;
}

