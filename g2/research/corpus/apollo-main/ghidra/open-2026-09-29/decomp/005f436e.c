
undefined8 TT_Load_Context(int *param_1,int param_2,int param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int *extraout_r3;
  int *piVar6;
  uint local_14;
  
  *param_1 = param_2;
  param_1[1] = param_3;
  if (param_3 != 0) {
    param_1[100] = *(int *)(param_3 + 0x7c);
    param_1[0x65] = *(int *)(param_3 + 0x80);
    param_1[0x67] = *(int *)(param_3 + 0x88);
    param_1[0x68] = *(int *)(param_3 + 0x8c);
    param_1[0x66] = *(int *)(param_3 + 0x84);
    param_1[0x69] = *(int *)(param_3 + 0x90);
    param_1[0x36] = *(int *)(param_3 + 0x78);
    iVar3 = param_3;
    local_14 = param_4;
    FUN_00439c04(param_1 + 0x3e,param_3 + 0x4c,0x28,param_4,param_3);
    FUN_00439c04(param_1 + 0x37,*(undefined4 *)(param_3 + 0x2c),0x1c);
    param_1[0x6a] = *(int *)(param_3 + 0x94);
    param_1[0x6b] = *(int *)(param_3 + 0x98);
    piVar6 = extraout_r3;
    for (iVar5 = 0; iVar5 < 3; iVar5 = iVar5 + 1) {
      iVar1 = param_3 + iVar5 * 8;
      iVar4 = *(int *)(iVar1 + 0xa0);
      piVar6 = param_1 + iVar5 * 2 + 0x70;
      *piVar6 = *(int *)(iVar1 + 0x9c);
      param_1[iVar5 * 2 + 0x71] = iVar4;
    }
    FUN_00439c04(param_1 + 0x48,param_3 + 0xb4,0x44,piVar6,iVar3);
    param_1[0x60] = *(int *)(param_3 + 0xf8);
    param_1[0x61] = *(int *)(param_3 + 0xfc);
    *(undefined2 *)(param_1 + 0x76) = *(undefined2 *)(param_3 + 0x100);
    param_1[0x77] = *(int *)(param_3 + 0x104);
    FUN_00439c04(param_1 + 0x2d,param_3 + 0x108,0x24);
    FUN_0043c0e4(param_1 + 9,0x24,0);
    FUN_00439c04(param_1 + 0x12,param_1 + 9,0x24);
    FUN_00439c04(param_1 + 0x1b,param_1 + 9,0x24);
  }
  local_14 = param_1[5];
  uVar2 = *(ushort *)(param_2 + 0x11c) + 0x20;
  iVar3 = Update_Max(param_1[2],&local_14,4,param_1 + 6);
  param_1[5] = local_14;
  if (iVar3 == 0) {
    local_14 = param_1[0x62];
    uVar2 = (uint)*(ushort *)(param_2 + 0x11e);
    iVar3 = Update_Max(param_1[2],&local_14,1,param_1 + 99);
    param_1[0x62] = local_14 & 0xffff;
    if (iVar3 == 0) {
      *(undefined2 *)(param_1 + 0x26) = 0;
      *(undefined2 *)((int)param_1 + 0x9a) = 0;
      FUN_00439c04(param_1 + 0x12,param_1 + 0x24,0x24);
      FUN_00439c04(param_1 + 0x1b,param_1 + 0x24,0x24);
      FUN_00439c04(param_1 + 9,param_1 + 0x24,0x24);
      *(undefined1 *)(param_1 + 0x7b) = 0;
      iVar3 = 0;
    }
  }
  return CONCAT44(uVar2,iVar3);
}

