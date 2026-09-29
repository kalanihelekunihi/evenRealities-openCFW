
undefined4 af_loader_embolden_glyph_in_slot(int param_1,int param_2,int *param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  bool bVar8;
  int local_48;
  int local_44;
  short *local_40;
  int local_3c;
  undefined1 auStack_38 [12];
  undefined4 local_2c;
  undefined4 uStack_28;
  
  uVar4 = 0;
  local_3c = *(int *)(param_2 + 0x54);
  iVar5 = *(int *)(param_1 + 4);
  local_40 = (short *)(*(int *)(*(int *)(param_2 + 0x58) + 0x28) + 8);
  local_44 = 0;
  local_48 = 0;
  bVar8 = *local_40 != *(short *)(iVar5 + 0x160);
  iVar6 = (uint)*(ushort *)(param_2 + 0x44) * 0x10000;
  uStack_28 = param_4;
  uVar1 = FT_DivFix(0x3e80000,iVar6);
  FUN_00439c04(auStack_38,DAT_005abc30,0x10);
  if (*(short *)(param_2 + 0x44) == 0) {
    uVar4 = 0xb9;
  }
  else {
    iVar7 = *(int *)(DAT_005abc34 + (uint)*(byte *)(*param_3 + 1) * 4);
    if (*(int *)(iVar7 + 0x14) == 0) {
      uVar4 = 7;
    }
    else {
      (**(code **)(iVar7 + 0x14))(param_3,&local_48,&local_44);
      if ((bVar8) || ((0 < local_44 && (local_44 != *(int *)(iVar5 + 0x164))))) {
        iVar7 = af_loader_compute_darkening(param_1,param_2,local_44);
        uVar2 = FT_MulFix(iVar7 << 0x10,*(undefined4 *)(local_40 + 2));
        iVar7 = FT_DivFix(uVar2,uVar1);
        *(int *)(iVar5 + 0x164) = local_44;
        *(short *)(iVar5 + 0x160) = *local_40;
        *(int *)(iVar5 + 0x16c) = (int)(short)((uint)(iVar7 + 0x8000) >> 0x10);
      }
      if ((bVar8) || ((0 < local_48 && (local_48 != *(int *)(iVar5 + 0x168))))) {
        iVar7 = af_loader_compute_darkening(param_1,param_2,local_48);
        uVar2 = FT_MulFix(iVar7 * 0x10000,*(undefined4 *)(local_40 + 4));
        iVar3 = FT_DivFix(uVar2,uVar1);
        *(int *)(iVar5 + 0x168) = local_48;
        *(short *)(iVar5 + 0x160) = *local_40;
        *(int *)(iVar5 + 0x170) = (int)(short)((uint)(iVar3 + 0x8000) >> 0x10);
        uVar1 = FT_DivFix(iVar6 + iVar7 * -0x10000 + -0x80000,iVar6);
        *(undefined4 *)(iVar5 + 0x174) = uVar1;
      }
      FT_Outline_EmboldenXY
                (local_3c + 0x6c,*(undefined4 *)(iVar5 + 0x16c),*(undefined4 *)(iVar5 + 0x170));
      local_2c = *(undefined4 *)(iVar5 + 0x174);
      FT_Outline_Transform(local_3c + 0x6c,auStack_38);
    }
  }
  return uVar4;
}

