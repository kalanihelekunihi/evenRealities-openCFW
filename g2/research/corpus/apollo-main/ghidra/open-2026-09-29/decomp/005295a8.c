
undefined8 FUN_005295a8(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  
  iVar6 = param_2;
  FUN_004d4666(*(int *)(param_2 + 0x34) + 0x10);
  iVar5 = *(int *)(*(int *)(param_2 + 0x34) + 0xc);
  iVar2 = FT_Get_Char_Index(iVar5,*param_1);
  if ((int)((uint)*(byte *)(iVar5 + 8) << 0x1f) < 0) {
    iVar3 = FT_Set_Pixel_Sizes(iVar5,0,*(undefined4 *)(param_2 + 0x28));
  }
  else {
    iVar3 = FT_Select_Size(iVar5,0);
  }
  if (iVar3 == 0) {
    if (*(char *)(param_2 + 0x2d) == '\x01') {
      iVar3 = FT_Load_Glyph(iVar5,iVar2,DAT_0052976c);
    }
    else {
      iVar3 = 0;
      if (*(char *)(param_2 + 0x2d) == '\0') {
        iVar3 = FT_Load_Glyph(iVar5,iVar2,0x208000);
      }
    }
    if (iVar3 == 0) {
      iVar3 = *(int *)(iVar5 + 0x54);
      if (*(char *)(param_2 + 0x2d) == '\x01') {
        *(short *)(param_1 + 3) = (short)(*(int *)(iVar3 + 0x28) >> 6);
        *(short *)(param_1 + 4) = (short)(*(int *)(iVar3 + 0x1c) >> 6);
        *(short *)((int)param_1 + 0xe) = (short)(*(int *)(iVar3 + 0x18) >> 6);
        *(short *)((int)param_1 + 0x12) = (short)(*(int *)(iVar3 + 0x20) >> 6);
        *(short *)(param_1 + 5) = (short)(*(int *)(iVar3 + 0x24) - *(int *)(iVar3 + 0x1c) >> 6);
        *(undefined1 *)((int)param_1 + 0x16) = 0x1a;
        if ((int)((uint)*(byte *)(param_2 + 0x2c) << 0x1f) < 0) {
          uVar1 = FUN_004b201e(*(undefined2 *)((int)param_1 + 0xe),*(undefined2 *)(param_1 + 4));
          *(undefined2 *)((int)param_1 + 0xe) = uVar1;
        }
      }
      else if (*(char *)(param_2 + 0x2d) == '\0') {
        iVar5 = *(int *)(iVar5 + 0x54);
        *(short *)(param_1 + 3) = (short)(*(int *)(iVar3 + 0x40) >> 6);
        *(short *)(param_1 + 4) = (short)*(undefined4 *)(iVar5 + 0x4c);
        *(short *)((int)param_1 + 0xe) = (short)*(undefined4 *)(iVar5 + 0x50);
        *(short *)((int)param_1 + 0x12) = (short)*(undefined4 *)(iVar3 + 100);
        *(short *)(param_1 + 5) = (short)*(undefined4 *)(iVar3 + 0x68) - *(short *)(param_1 + 4);
        if (*(int *)(iVar3 + 0x48) == DAT_00529774) {
          *(undefined1 *)((int)param_1 + 0x16) = 0x19;
        }
        else {
          *(undefined1 *)((int)param_1 + 0x16) = 8;
        }
      }
      *(byte *)((int)param_1 + 0x17) = *(byte *)((int)param_1 + 0x17) & 0xfe | iVar2 == 0;
      param_1[8] = iVar2;
      FUN_004d4696(*(int *)(param_2 + 0x34) + 0x10);
      uVar4 = 1;
    }
    else {
      iVar6 = DAT_00529770;
      FUN_0044d25c(3,DAT_00529744,0xa2,DAT_00529768,DAT_00529770,iVar3);
      FUN_004d4696(*(int *)(param_2 + 0x34) + 0x10);
      uVar4 = 0;
    }
  }
  else {
    iVar6 = DAT_00529764;
    FUN_0044d25c(3,DAT_00529744,0x96,DAT_00529768,DAT_00529764,iVar3,param_4);
    FUN_004d4696(*(int *)(param_2 + 0x34) + 0x10);
    uVar4 = 0;
  }
  return CONCAT44(iVar6,uVar4);
}

