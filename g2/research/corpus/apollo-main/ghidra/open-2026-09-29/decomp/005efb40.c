
int TT_Hint_Glyph(int *param_1,char param_2)

{
  int iVar1;
  int iVar2;
  undefined1 auStack_30 [8];
  byte *local_28;
  
  iVar1 = *(int *)(*param_1 + 0x60);
  iVar2 = *(int *)(param_1[2] + 0x8c);
  if (0 < iVar2) {
    FUN_00439be4(param_1[0x21],param_1[0x22],(uint)*(ushort *)(param_1 + 0x20) << 3);
  }
  FUN_00439c04(param_1[0x27] + 0x120,param_1[1] + 0xb4,0x44);
  if (param_2 == '\0') {
    *(undefined4 *)(param_1[0x27] + 0xe0) = *(undefined4 *)(*(int *)(param_1[1] + 0x2c) + 4);
    *(undefined4 *)(param_1[0x27] + 0xe4) = *(undefined4 *)(*(int *)(param_1[1] + 0x2c) + 8);
  }
  else {
    *(undefined4 *)(param_1[0x27] + 0xe0) = 0x10000;
    *(undefined4 *)(param_1[0x27] + 0xe4) = 0x10000;
    FUN_00439be4(param_1[0x23],param_1[0x22],(uint)*(ushort *)(param_1 + 0x20) << 3);
  }
  *(uint *)(param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8 + -0x20) =
       *(int *)(param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8 + -0x20) + 0x20U & 0xffffffc0;
  *(uint *)(param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8 + -0x18) =
       *(int *)(param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8 + -0x18) + 0x20U & 0xffffffc0;
  *(uint *)(param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8 + -0xc) =
       *(int *)(param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8 + -0xc) + 0x20U & 0xffffffc0;
  *(uint *)(param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8 + -4) =
       *(int *)(param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8 + -4) + 0x20U & 0xffffffc0;
  if (0 < iVar2) {
    FUN_00439c04(auStack_30,param_1[3] + 0x38,0x14);
    TT_Set_CodeRange(param_1[0x27],3,*(undefined4 *)(param_1[0x27] + 0x18c),iVar2);
    *(char *)(param_1[0x27] + 0x234) = param_2;
    FUN_00439c04(param_1[0x27] + 0x90,param_1 + 0x1e,0x24);
    iVar2 = TT_Run_Context(param_1[0x27]);
    if ((iVar2 != 0) && (*(char *)(param_1[0x27] + 0x235) != '\0')) {
      return iVar2;
    }
    *local_28 = *local_28 | (byte)(*(int *)(param_1[0x27] + 0x158) << 5) | 4;
  }
  if ((*(int *)(iVar1 + 0x40) != 0x28) || (*(char *)(param_1[0x27] + 0x267) == '\0')) {
    iVar1 = param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8;
    iVar2 = *(int *)(iVar1 + -0x1c);
    param_1[0x11] = *(int *)(iVar1 + -0x20);
    param_1[0x12] = iVar2;
    iVar1 = param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8;
    iVar2 = *(int *)(iVar1 + -0x14);
    param_1[0x13] = *(int *)(iVar1 + -0x18);
    param_1[0x14] = iVar2;
    iVar1 = param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8;
    iVar2 = *(int *)(iVar1 + -0xc);
    param_1[0x2d] = *(int *)(iVar1 + -0x10);
    param_1[0x2e] = iVar2;
    iVar1 = param_1[0x22] + (uint)*(ushort *)(param_1 + 0x20) * 8;
    iVar2 = *(int *)(iVar1 + -4);
    param_1[0x2f] = *(int *)(iVar1 + -8);
    param_1[0x30] = iVar2;
  }
  return 0;
}

