
undefined4 Ins_MSIRP(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  uint uVar5;
  
  uVar5 = *param_2;
  if (((uVar5 & 0xffff) < (uint)*(ushort *)(param_1 + 0x50)) &&
     (*(ushort *)(param_1 + 0x120) < *(ushort *)(param_1 + 0x2c))) {
    if (*(short *)(param_1 + 0x15e) == 0) {
      puVar3 = (undefined4 *)(*(int *)(param_1 + 0x30) + (uint)*(ushort *)(param_1 + 0x120) * 8);
      uVar2 = puVar3[1];
      puVar4 = (undefined4 *)(*(int *)(param_1 + 0x54) + (uVar5 & 0xffff) * 8);
      *puVar4 = *puVar3;
      puVar4[1] = uVar2;
      (**(code **)(param_1 + 0x250))(param_1,param_1 + 0x48,uVar5 & 0xffff,param_2[1]);
      puVar3 = (undefined4 *)(*(int *)(param_1 + 0x54) + (uVar5 & 0xffff) * 8);
      uVar2 = puVar3[1];
      puVar4 = (undefined4 *)(*(int *)(param_1 + 0x58) + (uVar5 & 0xffff) * 8);
      *puVar4 = *puVar3;
      puVar4[1] = uVar2;
    }
    iVar1 = (**(code **)(param_1 + 0x240))
                      (param_1,*(int *)(*(int *)(param_1 + 0x58) + (uVar5 & 0xffff) * 8) -
                               *(int *)(*(int *)(param_1 + 0x34) +
                                       (uint)*(ushort *)(param_1 + 0x120) * 8),
                       *(int *)(*(int *)(param_1 + 0x58) + (uVar5 & 0xffff) * 8 + 4) -
                       *(int *)(*(int *)(param_1 + 0x34) + (uint)*(ushort *)(param_1 + 0x120) * 8 +
                               4));
    (**(code **)(param_1 + 0x24c))(param_1,param_1 + 0x48,uVar5 & 0xffff,param_2[1] - iVar1);
    *(undefined2 *)(param_1 + 0x122) = *(undefined2 *)(param_1 + 0x120);
    *(short *)(param_1 + 0x124) = (short)uVar5;
    if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1f) < 0) {
      *(short *)(param_1 + 0x120) = (short)uVar5;
    }
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return param_4;
}

