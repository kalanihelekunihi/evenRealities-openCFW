
/* WARNING: Type propagation algorithm not settling */

void FUN_005944bc(uint param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  byte *pbVar4;
  undefined4 *puVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  uint uVar9;
  uint local_44;
  int local_40 [3];
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  
  local_40[1] = 0;
  FUN_00439c04(local_40 + 2,DAT_00594824,0x20);
  uVar3 = DAT_00594840;
  uVar2 = DAT_00594838;
  uVar1 = DAT_00594834;
  uVar7 = DAT_005947c4;
  local_44 = *DAT_00594828;
  local_40[0] = *DAT_0059482c;
  if (*DAT_00594830 == '\0') {
    FUN_0047da78(DAT_00594834,DAT_005947c4,DAT_00594838);
    FUN_0047da78(&DAT_005947b0);
    FUN_004733ee(uVar1,uVar7,uVar2);
    FUN_004733ee(&DAT_005947b0);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (*DAT_0059483c == '\0') {
    *DAT_0059483c = '\x01';
    FUN_0047da78(&DAT_005947b4);
    FUN_0047da78(&DAT_005947b0);
    FUN_004733ee(&DAT_005947b4);
    FUN_004733ee(&DAT_005947b0);
    FUN_00593a38();
    pbVar4 = DAT_00594844;
    *DAT_00594844 = (byte)(param_1 >> 2) & 1;
    iVar6 = DAT_005947c8;
    if (*pbVar4 == 0) {
      FUN_0047da78(*(undefined4 *)(DAT_005947c8 + 0x2c));
      FUN_0047da78(&DAT_005947b0);
      FUN_004733ee(*(undefined4 *)(iVar6 + 0x2c));
      FUN_004733ee(&DAT_005947b0);
    }
    else {
      iVar6 = FUN_00593af6();
      uVar7 = DAT_00594848;
      if (iVar6 != 0) {
        uVar7 = FUN_00593af6();
      }
      iVar6 = DAT_005947c8;
      FUN_0047da78(*(undefined4 *)(DAT_005947c8 + 0x28),uVar7);
      FUN_0047da78(&DAT_005947b0);
      iVar8 = FUN_00593af6();
      uVar7 = DAT_00594848;
      if (iVar8 != 0) {
        uVar7 = FUN_00593af6();
      }
      FUN_004733ee(*(undefined4 *)(iVar6 + 0x28),uVar7);
      FUN_004733ee(&DAT_005947b0);
      param_2 = (undefined4 *)FUN_005939a0();
      FUN_00593a78(local_40 + 1,&local_44,local_40);
    }
    uVar9 = FUN_005942aa(param_1,param_2 + 8);
    uVar7 = DAT_0059484c;
    if ((uVar9 < local_44) || (local_40[0] + local_44 < uVar9)) {
      FUN_0047da78(DAT_0059484c,uVar9,local_44,local_40[0] + local_44);
      FUN_0047da78(&DAT_005947b0);
      FUN_004733ee(uVar7,uVar9,local_44,local_40[0] + local_44);
      FUN_004733ee(&DAT_005947b0);
      *DAT_00594850 = 1;
    }
    FUN_00593afe(local_44,local_40[0],uVar9);
    iVar6 = DAT_005947c8;
    FUN_0047da78(*(undefined4 *)(DAT_005947c8 + 0x30));
    FUN_0047da78(&DAT_005947b0);
    FUN_004733ee(*(undefined4 *)(iVar6 + 0x30));
    FUN_004733ee(&DAT_005947b0);
    puVar5 = DAT_00594854;
    *DAT_00594854 = *param_2;
    puVar5[1] = param_2[1];
    puVar5[2] = param_2[2];
    puVar5[3] = param_2[3];
    puVar5[4] = param_2[4];
    puVar5[5] = param_2[5];
    puVar5[6] = param_2[6];
    puVar5[7] = param_2[7];
    uVar7 = DAT_00594858;
    FUN_0047da78(DAT_00594858,local_40[2],*puVar5,local_34,puVar5[1],local_30,puVar5[2],local_2c,
                 puVar5[3]);
    FUN_0047da78(&DAT_005947b0);
    FUN_004733ee(uVar7,local_40[2],*puVar5,local_34,puVar5[1],local_30,puVar5[2],local_2c,puVar5[3])
    ;
    FUN_004733ee(&DAT_005947b0);
    FUN_0047da78(uVar7,local_28,puVar5[4],local_24,puVar5[5],local_20,puVar5[6],local_1c,puVar5[7]);
    FUN_0047da78(&DAT_005947b0);
    FUN_004733ee(uVar7,local_28,puVar5[4],local_24,puVar5[5],local_20,puVar5[6],local_1c,puVar5[7]);
    FUN_004733ee(&DAT_005947b0);
    uVar7 = DAT_0059485c;
    FUN_0047da78(DAT_0059485c);
    FUN_0047da78(&DAT_005947b0);
    FUN_004733ee(uVar7);
    FUN_004733ee(&DAT_005947b0);
    puVar5[8] = *DAT_00594860;
    *(undefined1 *)(puVar5 + 9) = *DAT_00594864;
    puVar5[10] = *DAT_00594868;
    *(undefined1 *)(puVar5 + 0xb) = *DAT_0059486c;
    puVar5[0xc] = *DAT_00594870;
    *(undefined2 *)(puVar5 + 0xd) = *DAT_00594874;
    puVar5[0xe] = *DAT_00594878;
    puVar5[0xf] = (uint)*DAT_0059487c;
    puVar5[0x10] = (uint)*DAT_00594880;
    FUN_00593e0c();
    FUN_00593d4a(uVar9);
    FUN_00594334();
    FUN_0047dac0();
    return;
  }
  FUN_0047da78(DAT_00594834,DAT_00594840,DAT_00594838);
  FUN_0047da78(&DAT_005947b0);
  FUN_004733ee(uVar1,uVar3,uVar2);
  FUN_004733ee(&DAT_005947b0);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

