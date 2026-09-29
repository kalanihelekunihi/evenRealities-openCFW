
undefined4 FUN_00460638(int param_1,char *param_2,uint param_3)

{
  byte bVar1;
  byte bVar2;
  ushort uVar3;
  byte *pbVar4;
  char cVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  uint *puVar10;
  int iVar11;
  uint local_40;
  uint local_3c;
  uint local_38;
  uint local_34;
  uint local_30;
  undefined1 auStack_2c [12];
  uint local_20;
  
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    local_3c = DAT_004611b4;
    local_40 = 0x182;
    local_38 = param_3;
    FUN_0043d574(4,DAT_004611c0,DAT_004611bc,DAT_004611b8);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004611c4,DAT_004611c4,param_3);
  }
  FUN_00460178();
  if (param_1 == 4) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_3c = DAT_004611c8;
      local_40 = 0x185;
      local_38 = param_3;
      FUN_0043d574(4,DAT_004611c0,DAT_004611bc,DAT_004611b8);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004611cc,DAT_004611cc,param_3);
    }
    if ((param_3 == 2) && (bVar1 = param_2[1], *param_2 == '\0')) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        local_38 = (uint)bVar1;
        local_3c = DAT_004611d0;
        local_40 = 0x18b;
        FUN_0043d574(4,DAT_004611c0,DAT_004611bc,DAT_004611b8);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004612f0,DAT_004612f0,bVar1);
      }
      FUN_0046036a(bVar1);
    }
  }
  else if (param_1 == 0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_3c = DAT_004612f4;
      local_40 = 0x193;
      local_38 = param_3;
      FUN_0043d574(4,DAT_004611c0,DAT_004611bc,DAT_004611b8);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00461348,DAT_00461348,param_3);
    }
    pbVar4 = DAT_0046134c;
    FUN_0043c0e4(DAT_0046134c,0x37c,0);
    FUN_0048f49c(&local_40,param_2,param_3);
    FUN_00439c04(auStack_2c,&local_40,0x10);
    cVar5 = FUN_00490120(auStack_2c,DAT_00460e1c,pbVar4);
    if (cVar5 == '\0') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        local_38 = DAT_00461350;
        if (local_20 != 0) {
          local_38 = local_20;
        }
        local_3c = DAT_00461354;
        local_40 = 0x198;
        FUN_0043d574(1,DAT_004611c0,DAT_004611bc,DAT_004611b8);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        uVar9 = DAT_00461350;
        if (local_20 != 0) {
          uVar9 = local_20;
        }
        compress_log_output(0x4400000,DAT_00461358,DAT_00461358,uVar9);
      }
      return 0xffffffff;
    }
    bVar1 = *pbVar4;
    bVar2 = pbVar4[1];
    uVar3 = *(ushort *)(pbVar4 + 2);
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_30 = (uint)uVar3;
      local_34 = (uint)bVar2;
      local_38 = (uint)bVar1;
      local_3c = DAT_0046135c;
      local_40 = 0x19e;
      FUN_0043d574(4,DAT_004611c0,DAT_004611bc,DAT_004611b8);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      local_3c = (uint)uVar3;
      local_40 = (uint)bVar2;
      compress_log_output(0x10c00000,DAT_00461360,DAT_00461360,bVar1);
    }
    if (bVar1 == 0) {
      if (uVar3 != 3) {
        FUN_004604c2(bVar2,1);
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          local_38 = (uint)uVar3;
          local_3c = DAT_00461578;
          local_40 = 0x1c9;
          FUN_0043d574(1,DAT_004611c0,DAT_004611bc,DAT_004611b8);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0046157c,DAT_0046157c,uVar3);
        }
        return 0xffffffff;
      }
      puVar10 = (uint *)(pbVar4 + 4);
      if ((uint)*(ushort *)(pbVar4 + 8) != *puVar10) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          local_34 = *puVar10;
          local_38 = (uint)*(ushort *)(pbVar4 + 8);
          local_3c = DAT_00461364;
          local_40 = 0x1a6;
          FUN_0043d574(1,DAT_004611c0,DAT_004611bc,DAT_004611b8);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          local_40 = *puVar10;
          compress_log_output(0x4800000,DAT_00461368,DAT_00461368,*(undefined2 *)(pbVar4 + 8));
        }
        FUN_004604c2(bVar2,1);
        return 0xffffffff;
      }
      FUN_0046018e();
      iVar6 = DAT_0046136c;
      FUN_0043c0e4(DAT_0046136c,0x410,0);
      for (iVar11 = 0; iVar11 < (int)(uint)*(ushort *)(pbVar4 + 8); iVar11 = iVar11 + 1) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          uVar8 = FUN_00460084(iVar11 * 0x34 + iVar6 + 4);
          local_38 = FUN_0045fffe(iVar11 * 0x34 + iVar6 + 4,uVar8);
          local_30 = (uint)*(byte *)(iVar11 * 0x34 + iVar6 + 0x28);
          local_34 = *(uint *)(iVar6 + iVar11 * 0x34 + 0x30);
          local_3c = DAT_0046155c;
          local_40 = 0x1ad;
          FUN_0043d574(3,DAT_004611c0,DAT_004611bc,DAT_004611b8);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          uVar8 = FUN_00460084(iVar11 * 0x34 + iVar6 + 4);
          uVar8 = FUN_0045fffe(iVar11 * 0x34 + iVar6 + 4,uVar8);
          local_3c = (uint)*(byte *)(iVar11 * 0x34 + iVar6 + 0x28);
          local_40 = *(uint *)(iVar6 + iVar11 * 0x34 + 0x30);
          compress_log_output(0xcc00000,DAT_00461560,DAT_00461560,uVar8);
        }
        if (puVar10[iVar11 * 0xb + 2] == 0) {
          local_40 = iVar11 * 0x34 + iVar6 + 0x28;
          iVar7 = FUN_00460450(puVar10[iVar11 * 0xb + 0xc],iVar6 + iVar11 * 0x34,
                               iVar11 * 0x34 + iVar6 + 4,iVar11 * 0x34 + iVar6 + 0x24);
          if (iVar7 != 0) {
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              local_38 = puVar10[iVar11 * 0xb + 0xc];
              local_3c = DAT_00461564;
              local_40 = 0x1b1;
              FUN_0043d574(1,DAT_004611c0,DAT_004611bc,DAT_004611b8);
            }
            iVar6 = FUN_0043d0ce();
            if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_00461568,DAT_00461568,puVar10[iVar11 * 0xb + 0xc]);
            }
            FUN_004604c2(bVar2,1);
            FUN_004601ea();
            return 0xffffffff;
          }
          *(uint *)(iVar11 * 0x34 + iVar6 + 0x30) = puVar10[iVar11 * 0xb + 0xc];
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            uVar8 = FUN_00460084(iVar11 * 0x34 + iVar6 + 4);
            local_38 = FUN_0045fffe(iVar11 * 0x34 + iVar6 + 4,uVar8);
            local_30 = (uint)*(byte *)(iVar11 * 0x34 + iVar6 + 0x28);
            local_34 = *(uint *)(iVar11 * 0x34 + iVar6 + 0x30);
            local_3c = DAT_0046155c;
            local_40 = 0x1b7;
            FUN_0043d574(3,DAT_004611c0,DAT_004611bc,DAT_004611b8);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            uVar8 = FUN_00460084(iVar11 * 0x34 + iVar6 + 4);
            uVar8 = FUN_0045fffe(iVar11 * 0x34 + iVar6 + 4,uVar8);
            local_3c = (uint)*(byte *)(iVar11 * 0x34 + iVar6 + 0x28);
            local_40 = *(uint *)(iVar6 + iVar11 * 0x34 + 0x30);
            compress_log_output(0xcc00000,DAT_00461560,DAT_00461560,uVar8);
          }
        }
        else {
          *(uint *)(iVar11 * 0x34 + iVar6 + 0x30) = puVar10[iVar11 * 0xb + 0xc];
          *(undefined4 *)(iVar11 * 0x34 + iVar6 + 0x24) = 0xffe;
          *(undefined1 *)(iVar11 * 0x34 + iVar6 + 0x28) = 1;
          *(undefined4 *)(iVar6 + iVar11 * 0x34) = DAT_00461370;
          uVar8 = FUN_0044a43c(puVar10 + iVar11 * 0xb + 4);
          FUN_00439be4(iVar11 * 0x34 + iVar6 + 4,puVar10 + iVar11 * 0xb + 4,uVar8);
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            uVar8 = FUN_00460084(iVar11 * 0x34 + iVar6 + 4);
            local_38 = FUN_0045fffe(iVar11 * 0x34 + iVar6 + 4,uVar8);
            local_30 = (uint)*(byte *)(iVar11 * 0x34 + iVar6 + 0x28);
            local_34 = *(uint *)(iVar11 * 0x34 + iVar6 + 0x30);
            local_3c = DAT_0046155c;
            local_40 = 0x1be;
            FUN_0043d574(3,DAT_004611c0,DAT_004611bc,DAT_004611b8);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            uVar8 = FUN_00460084(iVar11 * 0x34 + iVar6 + 4);
            uVar8 = FUN_0045fffe(iVar11 * 0x34 + iVar6 + 4,uVar8);
            local_3c = (uint)*(byte *)(iVar11 * 0x34 + iVar6 + 0x28);
            local_40 = *(uint *)(iVar6 + iVar11 * 0x34 + 0x30);
            compress_log_output(0xcc00000,DAT_00461560,DAT_00461560,uVar8);
          }
        }
      }
      *DAT_0046156c = 1;
      *DAT_00461570 = (uint)*(ushort *)(pbVar4 + 8);
      *DAT_00460fb0 = 1;
      osEventFlagsSet(*DAT_00461574,4);
      FUN_004601ea();
      FUN_004604c2(bVar2,0);
    }
    else {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        local_38 = (uint)bVar1;
        local_3c = DAT_00461580;
        local_40 = 0x1cf;
        FUN_0043d574(1,DAT_004611c0,DAT_004611bc,DAT_004611b8);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00461584,DAT_00461584,bVar1);
      }
    }
  }
  return 0;
}

