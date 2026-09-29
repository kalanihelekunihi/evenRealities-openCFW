
undefined8 FUN_004bfa3c(int param_1,char param_2,int *param_3,uint *param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar1 = DAT_004c0754;
  iVar4 = *(int *)(param_1 + 4);
  if (param_2 == '\0') {
    if (0xffff < *param_4) {
      uVar3 = 5;
      goto LAB_004bfb70;
    }
    if (*(byte *)((int)param_4 + 0x12) != 0) {
      uVar3 = 7;
      goto LAB_004bfb70;
    }
    *param_3 = DAT_004c0754 + iVar4 * 0x1000 + 8;
    param_3[1] = param_4[2];
    param_3[2] = iVar1 + iVar4 * 0x1000 + 0xc;
    param_3[3] = (uint)*(ushort *)((int)param_4 + 0xe);
    param_3[4] = iVar1 + iVar4 * 0x1000;
    param_3[5] = (uint)*(byte *)((int)param_4 + 5) << 0xb | *param_4 << 0x10 |
                 (uint)(byte)param_4[1] << 9 | (*(byte *)((int)param_4 + 6) & 1) << 7 |
                 (uint)(byte)param_4[3] << 6 | (uint)*(byte *)((int)param_4 + 7) << 5 |
                 (uint)(byte)param_4[4] << 10 | (uint)*(byte *)(param_1 + 0xd) << 8 |
                 (uint)*(byte *)((int)param_4 + 0x11) << 0xc | 1;
  }
  else if (param_2 == '\x01') {
    if (0xffffff < param_4[1]) {
      uVar3 = 5;
      goto LAB_004bfb70;
    }
    if ((*(int *)(param_1 + 0x838) != 0) && (param_4[4] != 0)) {
      uVar3 = 7;
      goto LAB_004bfb70;
    }
    param_3[0xc] = DAT_004c0754 + iVar4 * 0x1000 + 0x100;
    param_3[0xd] = 0;
    param_3[4] = iVar1 + iVar4 * 0x1000 + 0x108;
    param_3[5] = param_4[3];
    param_3[6] = iVar1 + iVar4 * 0x1000 + 0x10c;
    param_3[7] = param_4[2];
    param_3[8] = iVar1 + iVar4 * 0x1000 + 0x110;
    param_3[9] = param_4[1];
    param_3[10] = iVar1 + iVar4 * 0x1000 + 0x100;
    param_3[0xb] = ((byte)*param_4 & 3) << 4 | (*(byte *)((int)param_4 + 1) & 1) << 2 | 3;
    param_3[2] = iVar1 + iVar4 * 0x1000 + 0x2b8;
    *param_3 = param_3[2];
    iVar2 = FUN_004bfa10(param_1,param_4[4]);
    param_3[1] = iVar2;
    param_3[3] = 0x4000;
    param_3[0xf] = param_4[5];
    param_3[0xe] = iVar1 + iVar4 * 0x1000 + 0x2b4;
  }
  uVar3 = 0;
LAB_004bfb70:
  return CONCAT44(param_4,uVar3);
}

