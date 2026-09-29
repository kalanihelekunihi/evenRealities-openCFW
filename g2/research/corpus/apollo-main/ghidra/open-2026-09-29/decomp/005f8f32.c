
undefined8 tt_size_reset(int *param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  ushort *puVar4;
  
  iVar3 = *param_1;
  if (*(char *)(iVar3 + 0x2b8) == '\0') {
    *(undefined1 *)(param_1 + 0x1c) = 0;
    puVar4 = (ushort *)(param_1 + 0xc);
    FUN_00439c04(puVar4,param_1 + 3,0x1c);
    if ((*puVar4 == 0) || (*(short *)((int)param_1 + 0x32) == 0)) {
      uVar1 = 0x97;
    }
    else {
      if ((int)((uint)*(byte *)(iVar3 + 0xb0) << 0x1c) < 0) {
        iVar2 = FT_MulFix((int)*(short *)(iVar3 + 0x46),param_1[0xe]);
        param_1[0xf] = iVar2 + 0x20U & 0xffffffc0;
        iVar2 = FT_MulFix((int)*(short *)(iVar3 + 0x48),param_1[0xe]);
        param_1[0x10] = iVar2 + 0x20U & 0xffffffc0;
        iVar2 = FT_MulFix((int)*(short *)(iVar3 + 0x4a),param_1[0xe]);
        param_1[0x11] = iVar2 + 0x20U & 0xffffffc0;
      }
      *(undefined1 *)(param_1 + 0x1c) = 1;
      if (param_2 == '\0') {
        if ((int)((uint)*(byte *)(iVar3 + 0xb0) << 0x1c) < 0) {
          iVar2 = FT_DivFix((uint)*puVar4 << 6,*(undefined2 *)(iVar3 + 0x44));
          param_1[0xd] = iVar2;
          iVar2 = FT_DivFix((uint)*(ushort *)((int)param_1 + 0x32) << 6,
                            *(undefined2 *)(iVar3 + 0x44));
          param_1[0xe] = iVar2;
          iVar3 = FT_MulFix((int)*(short *)(iVar3 + 0x4c),param_1[0xd]);
          param_1[0x12] = iVar3 + 0x20U & 0xffffffc0;
        }
        if (*puVar4 < *(ushort *)((int)param_1 + 0x32)) {
          param_1[0x17] = param_1[0xe];
          *(undefined2 *)(param_1 + 0x15) = *(undefined2 *)((int)param_1 + 0x32);
          iVar3 = FT_DivFix(*puVar4,*(undefined2 *)((int)param_1 + 0x32));
          param_1[0x13] = iVar3;
          param_1[0x14] = 0x10000;
        }
        else {
          param_1[0x17] = param_1[0xd];
          *(ushort *)(param_1 + 0x15) = *puVar4;
          param_1[0x13] = 0x10000;
          iVar3 = FT_DivFix(*(undefined2 *)((int)param_1 + 0x32),*puVar4);
          param_1[0x14] = iVar3;
        }
        param_1[0xb] = (int)puVar4;
        param_1[0x4d] = -1;
        uVar1 = 0;
      }
      else {
        uVar1 = 0;
      }
    }
  }
  else {
    uVar1 = 0;
  }
  return CONCAT44(param_4,uVar1);
}

