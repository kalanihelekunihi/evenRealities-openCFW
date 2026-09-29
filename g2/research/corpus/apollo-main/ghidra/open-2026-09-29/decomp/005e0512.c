
undefined8 FUN_005e0512(int param_1,uint param_2,ushort *param_3,undefined4 param_4)

{
  undefined2 uVar1;
  char cVar2;
  ushort uVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  
  if (*(int *)(param_1 + 0x300) == 0) {
    if (*(uint *)(param_1 + 0x2fc) <= param_2) {
      iVar4 = 6;
      goto LAB_005e0726;
    }
  }
  else {
    if (*(uint *)(param_1 + 0x1c) <= param_2) {
      iVar4 = 6;
      goto LAB_005e0726;
    }
    param_2 = *(uint *)(*(int *)(param_1 + 0x300) + param_2 * 4);
  }
  uVar5 = *(byte *)(param_1 + 0x2f8) - 1;
  if (uVar5 < 2) {
    iVar4 = *(int *)(param_1 + 0x2f0) + param_2 * 0x30;
    *param_3 = (ushort)*(byte *)(iVar4 + 0x34);
    param_3[1] = (ushort)*(byte *)(iVar4 + 0x35);
    *(int *)(param_3 + 6) = (int)*(char *)(iVar4 + 0x18) << 6;
    *(int *)(param_3 + 8) = (int)*(char *)(iVar4 + 0x19) << 6;
    cVar2 = *(char *)(iVar4 + 0x21);
    if (*(int *)(param_3 + 8) < 1) {
      if ((*(int *)(param_3 + 8) == 0) && (*(int *)(param_3 + 6) == 0)) {
        if ((*(char *)(iVar4 + 0x20) == '\0') && (cVar2 == '\0')) {
          *(uint *)(param_3 + 6) = (uint)param_3[1] << 6;
          param_3[8] = 0;
          param_3[9] = 0;
        }
        else {
          *(int *)(param_3 + 6) = (int)*(char *)(iVar4 + 0x20) << 6;
          *(int *)(param_3 + 8) = (int)cVar2 << 6;
        }
      }
    }
    else if (cVar2 < '\0') {
      *(int *)(param_3 + 8) = -*(int *)(param_3 + 8);
    }
    *(int *)(param_3 + 10) = *(int *)(param_3 + 6) - *(int *)(param_3 + 8);
    if (*(int *)(param_3 + 10) == 0) {
      *(uint *)(param_3 + 10) = (uint)param_3[1] << 6;
      *(int *)(param_3 + 8) = *(int *)(param_3 + 6) - *(int *)(param_3 + 10);
    }
    *(uint *)(param_3 + 0xc) =
         ((int)*(char *)(iVar4 + 0x1f) +
         (int)*(char *)(iVar4 + 0x1e) + (uint)*(byte *)(iVar4 + 0x1a)) * 0x40;
    uVar6 = FT_MulDiv(*param_3,0x400000,*(undefined2 *)(param_1 + 0xb2));
    *(undefined4 *)(param_3 + 2) = uVar6;
    uVar6 = FT_MulDiv(param_3[1],0x400000,*(undefined2 *)(param_1 + 0xb2));
    *(undefined4 *)(param_3 + 4) = uVar6;
    iVar4 = 0;
  }
  else if (uVar5 == 2) {
    uVar6 = *(undefined4 *)(param_1 + 0x68);
    iVar4 = *(int *)(param_1 + 0x2f0) + param_2 * 4;
    uVar5 = (uint)*(byte *)(iVar4 + 0xb) |
            (uint)*(byte *)(iVar4 + 9) << 0x10 | (uint)*(byte *)(iVar4 + 8) << 0x18 |
            (uint)*(byte *)(iVar4 + 10) << 8;
    if (*(uint *)(param_1 + 0x33c) < uVar5 + 4) {
      iVar4 = 3;
    }
    else {
      iVar4 = FT_Stream_Seek(uVar6,uVar5 + *(int *)(param_1 + 0x338));
      if ((iVar4 == 0) && (iVar4 = FT_Stream_EnterFrame(uVar6,4), iVar4 == 0)) {
        uVar3 = FT_Stream_GetUShort(uVar6);
        FT_Stream_GetUShort(uVar6);
        FT_Stream_ExitFrame(uVar6);
        uVar1 = *(undefined2 *)(param_1 + 0xb2);
        *param_3 = uVar3;
        param_3[1] = uVar3;
        uVar5 = (uint)uVar3;
        uVar6 = FT_MulDiv((int)*(short *)(param_1 + 0xdc),uVar5 << 6,uVar1);
        *(undefined4 *)(param_3 + 6) = uVar6;
        uVar6 = FT_MulDiv((int)*(short *)(param_1 + 0xde),uVar5 << 6,uVar1);
        *(undefined4 *)(param_3 + 8) = uVar6;
        uVar6 = FT_MulDiv(((int)*(short *)(param_1 + 0xdc) - (int)*(short *)(param_1 + 0xde)) +
                          (int)*(short *)(param_1 + 0xe0),uVar5 << 6,uVar1);
        *(undefined4 *)(param_3 + 10) = uVar6;
        uVar6 = FT_MulDiv(*(undefined2 *)(param_1 + 0xe2),uVar5 << 6,uVar1);
        *(undefined4 *)(param_3 + 0xc) = uVar6;
        uVar6 = FT_MulDiv(*param_3,0x400000,*(undefined2 *)(param_1 + 0xb2));
        *(undefined4 *)(param_3 + 2) = uVar6;
        uVar6 = FT_MulDiv(param_3[1],0x400000,*(undefined2 *)(param_1 + 0xb2));
        *(undefined4 *)(param_3 + 4) = uVar6;
      }
    }
  }
  else {
    iVar4 = 2;
  }
LAB_005e0726:
  return CONCAT44(param_4,iVar4);
}

