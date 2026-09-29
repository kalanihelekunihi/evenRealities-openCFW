
int FUN_0052e1ea(int param_1,int param_2,int *param_3,undefined4 param_4)

{
  int *piVar1;
  undefined1 uVar2;
  char cVar3;
  byte bVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  undefined1 *puVar8;
  byte bVar9;
  char local_68;
  byte local_67;
  undefined1 local_64;
  undefined1 local_63;
  int local_60;
  undefined4 local_58;
  undefined4 local_54;
  uint local_48;
  undefined1 local_44;
  undefined1 *local_40;
  undefined1 *local_3c;
  undefined1 local_38;
  undefined1 local_37;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 uStack_28;
  
  piVar1 = DAT_0052eba4;
  local_64 = 0x81;
  local_63 = 0;
  uStack_28 = param_4;
  if (*DAT_0052eaf4 == '\0') {
    if (*DAT_0052eba4 << 10 < 0) {
      iVar5 = FUN_0052e072(param_1);
      local_60 = param_2;
      if (iVar5 == 0) {
        do {
          iVar6 = FUN_0052dd1c();
          if (iVar6 == 0) {
            for (uVar7 = 0; uVar7 < 10; uVar7 = uVar7 + 1) {
              FUN_00480fd6(0x95,0);
              FUN_0043c0e4(&local_58,0x30,0);
              local_37 = 0;
              local_34 = 0;
              local_30 = 0;
              local_44 = 2;
              local_54 = 0;
              local_48 = 2;
              local_40 = &local_64;
              local_58 = 0;
              local_38 = 0;
              local_3c = &local_68;
              cVar3 = FUN_0055cf40(*(undefined4 *)(param_1 + 4),&local_58);
              if (cVar3 != '\0') {
                FUN_00480fd6(0x95,1);
                iVar5 = 10;
                break;
              }
              if ((local_68 == -0x40) && (local_67 != 0)) break;
              FUN_00480fd6(0x95,1);
            }
            bVar4 = local_67;
            if ((local_68 != -0x40) || (local_67 == 0)) {
              FUN_00480fd6(0x95,1);
              FUN_004733ee(DAT_0052ede8,0x3b4,local_68,local_67);
              iVar5 = 6;
              break;
            }
            uVar7 = (uint)local_67;
            if ((*piVar1 << 10 < 0) && (local_67 != 0)) {
              if (0x103 < *param_3 + uVar7) {
                FUN_00480fd6(0x95,1);
                FUN_004733ee(DAT_0052edec,local_68,local_67);
                iVar5 = 9;
                break;
              }
              FUN_0043c0e4(&local_58,0x30,0);
              local_54 = 0;
              local_44 = 1;
              local_48 = (uint)bVar4;
              local_3c = (undefined1 *)(local_60 + *param_3);
              local_38 = 0;
              local_37 = 0;
              local_34 = 0;
              local_30 = 0;
              local_58 = 0;
              cVar3 = FUN_0055cc1c(*(undefined4 *)(param_1 + 4),&local_58);
              if (cVar3 != '\0') {
                FUN_00480fd6(0x95,1);
                FUN_004733ee(DAT_0052f0dc,cVar3);
                iVar5 = 0xb;
                break;
              }
              *param_3 = *param_3 + uVar7;
            }
          }
          else {
            FUN_00480fd6(0x95,0);
            FUN_0052dc98(0x81);
            bVar4 = FUN_0052dcde();
            local_67 = bVar4;
            if ((bVar4 == 0) || (bVar4 == 0xff)) {
              FUN_00480fd6(0x95,1);
              FUN_004733ee(DAT_0052ede8,0x35e,local_68,local_67);
              iVar5 = 6;
              break;
            }
            if ((*piVar1 << 10 < 0) && (bVar4 != 0)) {
              if (0x103 < *param_3 + (uint)bVar4) {
                FUN_00480fd6(0x95,1);
                FUN_004733ee(DAT_0052edec,local_68,local_67);
                iVar5 = 9;
                break;
              }
              puVar8 = (undefined1 *)(local_60 + *param_3);
              for (bVar9 = 0; bVar9 < bVar4; bVar9 = bVar9 + 1) {
                uVar2 = FUN_0052dcde();
                *puVar8 = uVar2;
                puVar8 = puVar8 + 1;
              }
              *param_3 = *param_3 + (uint)bVar4;
            }
          }
          FUN_00480fd6(0x95,1);
        } while (*piVar1 << 10 < 0);
        FUN_0052e0a2(param_1);
      }
    }
    else {
      iVar5 = 7;
    }
  }
  else {
    FUN_004733ee(DAT_0052ede4);
    iVar5 = 3;
  }
  return iVar5;
}

