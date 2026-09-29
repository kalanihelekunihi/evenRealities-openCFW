
int FUN_004cb5ac(undefined4 param_1,uint *param_2,uint param_3,uint param_4,uint *param_5,
                uint param_6,uint param_7,uint param_8,ushort param_9,ushort param_10,
                ushort param_11,code *param_12,uint *param_13)

{
  short sVar1;
  ushort uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint *puVar6;
  uint uVar7;
  uint *puVar8;
  uint local_130;
  uint local_12c;
  uint local_128;
  uint *local_124;
  uint local_120;
  uint local_11c;
  uint *local_118;
  uint local_114;
  uint local_110;
  uint local_10c;
  ushort local_108;
  ushort local_106;
  ushort local_104;
  code *local_100;
  uint *local_fc;
  uint local_f8;
  uint *local_f4;
  uint local_f0;
  uint uStack_ec;
  uint *local_e8;
  uint local_e4 [2];
  uint *local_dc;
  uint local_d8 [3];
  ushort local_cc [4];
  code *local_c4;
  uint *local_c0;
  uint auStack_bc [4];
  undefined1 auStack_ac [124];
  undefined4 local_30;
  uint *local_2c;
  uint local_28;
  
  uVar7 = 0;
  local_30 = param_1;
  local_2c = param_2;
  local_28 = param_4;
  FUN_0043c0e4(&local_12c,8,0);
LAB_004cb60e:
  do {
    while( true ) {
      do {
        iVar4 = FUN_004caebe(local_28);
        if (iVar4 + param_3 < local_2c[3]) {
          iVar4 = FUN_004caebe(local_28);
          param_3 = iVar4 + param_3;
          iVar4 = FUN_004ca83c(local_30,0,local_30,4,*local_2c,param_3,&local_130,4);
          if (iVar4 != 0) {
            return iVar4;
          }
          uVar3 = lfs_frombe32(local_130);
          local_130 = uVar3 ^ local_28 | 0x80000000;
          local_12c = *local_2c;
          local_128 = param_3 + 4;
          puVar6 = &local_12c;
          local_28 = local_130;
        }
        else {
          if ((int)param_6 < 1) {
            iVar4 = 0;
            goto LAB_004cb84e;
          }
          local_130 = *param_5;
          puVar6 = (uint *)param_5[1];
          param_5 = param_5 + 2;
          param_6 = param_6 - 1;
        }
      } while ((param_7 & DAT_004cc1e4 & local_130) != (param_8 & DAT_004cc1e4 & param_7));
      iVar4 = FUN_004caeb0(param_7);
      if (iVar4 == 0) break;
      if (2 < uVar7) {
        FUN_004d09b4(DAT_004cc1ec,DAT_004cc1e8,0x3c5);
      }
      local_124 = local_2c;
      local_11c = local_28;
      local_108 = param_9;
      local_104 = param_11;
      local_100 = param_12;
      local_fc = param_13;
      local_f8 = local_130;
      local_f0 = local_12c;
      uStack_ec = local_128;
      local_120 = param_3;
      local_118 = param_5;
      local_114 = param_6;
      local_110 = param_7;
      local_10c = param_8;
      local_106 = param_10;
      local_f4 = puVar6;
      FUN_00439c04(auStack_ac + uVar7 * 0x3c,&local_124,0x3c);
      uVar7 = uVar7 + 1;
      param_7 = 0;
      param_8 = 0;
      param_9 = 0;
      param_10 = 0;
      param_11 = 0;
      param_12 = DAT_004cc1f8;
      param_13 = auStack_bc + uVar7 * 0xf;
    }
    while( true ) {
      iVar4 = FUN_004caeb0(param_7);
      if (((iVar4 != 0) &&
          ((uVar3 = FUN_004caeb0(local_130), uVar3 < param_9 ||
           (uVar3 = FUN_004caeb0(local_130), param_10 <= uVar3)))) ||
         (iVar4 = FUN_004cae98(local_130), iVar4 == 0)) goto LAB_004cb60e;
      iVar4 = FUN_004cae98(local_130);
      if (iVar4 == 0x101) break;
      iVar4 = FUN_004cae98(local_130);
      if (iVar4 == 0x102) {
        uVar3 = 0;
        goto LAB_004cb7d8;
      }
      iVar4 = (*param_12)(param_13,local_130 + (short)param_11 * 0x400,puVar6);
      if (iVar4 < 0) {
        return iVar4;
      }
      if (iVar4 == 0) goto LAB_004cb60e;
LAB_004cb84e:
      if (uVar7 == 0) {
        return iVar4;
      }
      local_2c = (&local_e8)[uVar7 * 0xf];
      param_3 = local_e4[uVar7 * 0xf];
      local_28 = local_e4[uVar7 * 0xf + 1];
      param_5 = (&local_dc)[uVar7 * 0xf];
      param_6 = local_d8[uVar7 * 0xf];
      param_7 = local_d8[uVar7 * 0xf + 1];
      param_8 = local_d8[uVar7 * 0xf + 2];
      param_9 = local_cc[uVar7 * 0x1e];
      param_10 = local_cc[uVar7 * 0x1e + 1];
      param_11 = local_cc[uVar7 * 0x1e + 2];
      param_12 = (&local_c4)[uVar7 * 0xf];
      param_13 = (uint *)auStack_bc[uVar7 * 0xf + -1];
      local_130 = auStack_bc[uVar7 * 0xf];
      puVar6 = (uint *)auStack_bc[uVar7 * 0xf + 1];
      local_12c = auStack_bc[uVar7 * 0xf + 2];
      local_128 = auStack_bc[uVar7 * 0xf + 3];
      uVar7 = uVar7 - 1;
    }
    if (param_12 != DAT_004cc1f8) {
      FUN_0048949c(&local_e8,0x3c);
      local_e8 = local_2c;
      local_e4[1] = local_28;
      local_cc[0] = param_9;
      local_cc[2] = param_11;
      local_c4 = param_12;
      local_c0 = param_13;
      local_e4[0] = param_3;
      local_dc = param_5;
      local_d8[0] = param_6;
      local_d8[1] = param_7;
      local_d8[2] = param_8;
      local_cc[1] = param_10;
      FUN_00439c04(auStack_ac + uVar7 * 0x3c,&local_e8,0x3c);
      uVar7 = uVar7 + 1;
      param_9 = FUN_004caeb8(local_130);
      sVar1 = FUN_004caeb0(local_130);
      param_3 = 0;
      local_28 = 0xffffffff;
      param_5 = (uint *)0x0;
      param_6 = 0;
      param_8 = 0x20000000;
      param_10 = param_9 + 1;
      param_11 = param_11 + (sVar1 - param_9);
      param_7 = DAT_004cc1fc;
      local_2c = puVar6;
    }
  } while( true );
LAB_004cb7d8:
  uVar5 = FUN_004caeb8(local_130);
  if (uVar5 <= uVar3) goto LAB_004cb60e;
  puVar8 = puVar6;
  uVar2 = FUN_004caeb0(local_130);
  iVar4 = (*param_12)(param_13,((int)(short)param_11 + (uint)uVar2) * 0x400 |
                               ((byte)puVar8[uVar3 * 3] + 0x300) * 0x100000 | puVar8[uVar3 * 3 + 2],
                      puVar8[uVar3 * 3 + 1]);
  if (iVar4 < 0) {
    return iVar4;
  }
  if (iVar4 != 0) goto LAB_004cb60e;
  uVar3 = uVar3 + 1;
  goto LAB_004cb7d8;
}

