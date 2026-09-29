
undefined8 FUN_00529936(undefined4 *param_1,int param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  undefined1 uVar8;
  int iVar9;
  int local_28;
  
  local_28 = param_4;
  FUN_004d4666(*(int *)(param_2 + 0x34) + 0x10);
  iVar3 = *(int *)(*(int *)(param_2 + 0x34) + 0xc);
  if ((int)((uint)*(byte *)(iVar3 + 8) << 0x1f) < 0) {
    iVar1 = FT_Set_Pixel_Sizes(iVar3,0,*(undefined4 *)(param_2 + 0x28));
  }
  else {
    iVar1 = FT_Select_Size(iVar3,0);
  }
  if (iVar1 == 0) {
    iVar1 = FT_Load_Glyph(iVar3,*param_1,DAT_00529ad0);
    if (iVar1 == 0) {
      iVar1 = FT_Render_Glyph(*(undefined4 *)(iVar3 + 0x54),0);
      if (iVar1 == 0) {
        iVar1 = FUN_00567ec8(*(undefined4 *)(iVar3 + 0x54),&local_28);
        iVar3 = local_28;
        if (iVar1 == 0) {
          uVar4 = *(uint *)(local_28 + 0x1c);
          uVar6 = *(uint *)(local_28 + 0x20);
          if (*(char *)(local_28 + 0x2e) == '\a') {
            uVar8 = 0x10;
          }
          else {
            uVar8 = 0xe;
          }
          iVar5 = *(int *)(local_28 + 0x24);
          iVar1 = FUN_0048aad8(uVar6 & 0xffff,uVar8);
          iVar9 = iVar1;
          uVar2 = FUN_0048b010(DAT_00529ae0,uVar6 & 0xffff,uVar4 & 0xffff,uVar8);
          param_1[2] = uVar2;
          for (iVar7 = 0; iVar7 < (int)(uVar4 & 0xffff); iVar7 = iVar7 + 1) {
            FUN_00454738(*(int *)(param_1[2] + 0x10) + iVar1 * iVar7,
                         iVar5 * iVar7 + *(int *)(iVar3 + 0x28),iVar5);
          }
          FUN_00567f88(local_28);
          FUN_004d4696(*(int *)(param_2 + 0x34) + 0x10);
          uVar2 = 1;
        }
        else {
          iVar9 = DAT_00529adc;
          FUN_0044d25c(3,DAT_00529aa8,0xa9,DAT_00529acc,DAT_00529adc,iVar1);
          FUN_004d4696(*(int *)(param_2 + 0x34) + 0x10);
          uVar2 = 0;
        }
      }
      else {
        iVar9 = DAT_00529ad8;
        FUN_0044d25c(3,DAT_00529aa8,0xa0,DAT_00529acc,DAT_00529ad8,iVar1);
        FUN_004d4696(*(int *)(param_2 + 0x34) + 0x10);
        uVar2 = 0;
      }
    }
    else {
      iVar9 = DAT_00529ad4;
      FUN_0044d25c(3,DAT_00529aa8,0x99,DAT_00529acc,DAT_00529ad4,iVar1);
      FUN_004d4696(*(int *)(param_2 + 0x34) + 0x10);
      uVar2 = 0;
    }
  }
  else {
    iVar9 = DAT_00529ac8;
    FUN_0044d25c(3,DAT_00529aa8,0x92,DAT_00529acc,DAT_00529ac8,iVar1);
    FUN_004d4696(*(int *)(param_2 + 0x34) + 0x10);
    uVar2 = 0;
  }
  return CONCAT44(iVar9,uVar2);
}

