
void touch_sub_3480(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  ushort uVar2;
  uint *puVar3;
  int iVar4;
  
  puVar3 = (uint *)**(undefined4 **)(*param_1 + 8);
  iVar4 = param_1[2];
  if ((int)((puVar3[0x4a] & puVar3[0x48]) << 0xf) < 0) {
    puVar3[0x48] = DAT_00006858;
    touch_sub_3162(*(undefined2 *)(iVar4 + 0x34),*(undefined2 *)(iVar4 + 0x46),param_1,puVar3[0x48],
                   param_4);
    uVar2 = *(short *)(iVar4 + 0x34) + *(short *)(iVar4 + 0x46);
    *(ushort *)(iVar4 + 0x34) = uVar2;
    uVar1 = *(ushort *)(iVar4 + 0x36);
    if ((uint)uVar1 < (uint)uVar2) {
      *puVar3 = *puVar3 & 0x7fffffff;
      puVar3[0x51] = 0x100;
      *(short *)(param_1[1] + 4) = *(short *)(param_1[1] + 4) + 1;
      touch_sub_2e4c(param_1);
    }
    else {
      puVar3[0x1c] = puVar3[0x1c] & 0xffff0000;
      *(undefined1 *)(iVar4 + 0x61) = 0;
      touch_sub_334c(*(undefined2 *)(iVar4 + 0x34),((uint)uVar1 - (uint)uVar2) + 1,param_1);
    }
  }
  else {
    if ((int)(puVar3[0x48] << 0x1f) < 0) {
      *(uint *)(param_1[1] + 8) = *(uint *)(param_1[1] + 8) | 0x400;
    }
    if ((int)((uint)*(ushort *)(param_1[1] + 0x16) << 0x1f) < 0) {
      touch_sub_3230(*(undefined2 *)(iVar4 + 0x34),*(undefined2 *)(iVar4 + 0x46),param_1);
      *(char *)(param_1[1] + 0x1b) = *(char *)(param_1[1] + 0x1b) + '\x01';
    }
    *puVar3 = *puVar3 & 0x7fffffff;
    puVar3[0x48] = DAT_00006858;
    puVar3[0x51] = 0x100;
    touch_sub_2e4c(param_1);
  }
  return;
}

