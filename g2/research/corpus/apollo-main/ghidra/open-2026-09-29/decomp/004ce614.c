
int FUN_004ce614(int param_1,undefined4 param_2,undefined4 param_3)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  bool bVar7;
  ushort local_d4 [2];
  undefined1 auStack_d0 [8];
  uint local_c8 [3];
  undefined2 local_bc;
  undefined1 local_ba;
  undefined1 auStack_b8 [20];
  short local_a4;
  char local_a1;
  undefined1 auStack_98 [32];
  undefined1 auStack_78 [32];
  uint local_58 [2];
  uint local_50;
  uint local_48;
  undefined4 local_44;
  uint local_40;
  undefined1 *local_3c;
  uint local_38;
  int iStack_30;
  undefined4 uStack_2c;
  undefined4 local_28;
  
  iStack_30 = param_1;
  uStack_2c = param_2;
  local_28 = param_3;
  iVar2 = FUN_004cf9e0(param_1);
  if (iVar2 == 0) {
    iVar3 = FUN_004cc04a(param_1,auStack_78,&uStack_2c,0);
    if ((iVar3 < 0) || (iVar2 = FUN_004caeb0(iVar3), iVar2 == 0x3ff)) {
      iVar2 = iVar3;
      if (-1 < iVar3) {
        iVar2 = -0x16;
      }
    }
    else {
      iVar2 = FUN_004cc04a(param_1,auStack_98,&local_28,local_d4);
      if (((iVar2 < 0) || (iVar4 = FUN_004caeb0(iVar2), iVar4 == 0x3ff)) &&
         ((iVar2 != -2 || (iVar4 = FUN_004cad80(local_28), iVar4 == 0)))) {
        if (-1 < iVar2) {
          iVar2 = -0x16;
        }
      }
      else {
        iVar4 = FUN_004cadea(auStack_78,auStack_98);
        bVar7 = iVar4 == 0;
        uVar1 = FUN_004caeb0(iVar3);
        local_c8[2] = *(undefined4 *)(param_1 + 0x28);
        if (iVar2 == -2) {
          iVar4 = FUN_004cadac(local_28);
          if ((iVar4 != 0) && (iVar4 = FUN_004cae98(iVar3), iVar4 != 2)) {
            return -0x14;
          }
          uVar5 = FUN_004cad76(local_28);
          if (*(uint *)(param_1 + 0x70) < uVar5) {
            return -0x24;
          }
          if ((bVar7) && (local_d4[0] <= uVar1)) {
            uVar1 = uVar1 + 1;
          }
        }
        else {
          uVar5 = FUN_004cae98(iVar2);
          uVar6 = FUN_004cae98(iVar3);
          if ((uVar5 & 0xffff) != uVar6) {
            iVar2 = FUN_004cae98(iVar2);
            if (iVar2 == 2) {
              return -0x15;
            }
            return -0x14;
          }
          if ((bVar7) && (local_d4[0] == uVar1)) {
            return 0;
          }
          iVar4 = FUN_004cae98(iVar2);
          if (iVar4 == 2) {
            iVar4 = FUN_004cb3c8(param_1,auStack_98,DAT_004cef6c,
                                 DAT_004cef68 | (uint)local_d4[0] << 10,auStack_d0);
            if (iVar4 < 0) {
              return iVar4;
            }
            FUN_004cae3e(auStack_d0);
            iVar4 = FUN_004cbedc(param_1,auStack_b8,auStack_d0);
            if (iVar4 != 0) {
              return iVar4;
            }
            if ((local_a4 != 0) || (local_a1 != '\0')) {
              return -0x27;
            }
            iVar4 = FUN_004cf570(param_1,1);
            if (iVar4 != 0) {
              return iVar4;
            }
            local_ba = 0;
            local_bc = 0;
            *(uint **)(param_1 + 0x28) = local_c8 + 2;
          }
        }
        if (!bVar7) {
          FUN_004cf5ec(param_1,uVar1,auStack_78);
        }
        FUN_0048949c(local_58,0x28);
        if (iVar2 == -2) {
          local_58[0] = 0;
        }
        else {
          local_58[0] = DAT_004cef70 | (uint)local_d4[0] << 10;
        }
        local_50 = DAT_004cf270 | (uint)local_d4[0] << 10;
        iVar4 = FUN_004cae98(iVar3);
        local_48 = FUN_004cad76(local_28);
        local_48 = local_48 | (uint)local_d4[0] << 10 | iVar4 << 0x14;
        local_44 = local_28;
        uVar5 = FUN_004caeb0(iVar3);
        local_40 = uVar5 | (uint)local_d4[0] << 10 | DAT_004cf280;
        local_3c = auStack_78;
        if (bVar7) {
          local_38 = DAT_004cef70 | (uint)uVar1 << 10;
        }
        else {
          local_38 = 0;
        }
        iVar4 = FUN_004cd388(param_1,auStack_98,local_58,5);
        if (iVar4 == 0) {
          if ((!bVar7) && (iVar4 = FUN_004caf2e(param_1 + 0x30), iVar4 != 0)) {
            FUN_004cf5ec(param_1,0x3ff,0);
            local_c8[0] = 0;
            local_c8[1] = 0;
            iVar3 = FUN_004caeb0(iVar3);
            local_c8[0] = DAT_004cef70 | iVar3 << 10;
            iVar3 = FUN_004cd388(param_1,auStack_78,local_c8,1);
            if (iVar3 != 0) {
              *(uint *)(param_1 + 0x28) = local_c8[2];
              return iVar3;
            }
          }
          *(uint *)(param_1 + 0x28) = local_c8[2];
          if (((iVar2 == -2) || (iVar2 = FUN_004cae98(iVar2), iVar2 != 2)) ||
             ((iVar2 = FUN_004cf570(param_1,0xffffffff), iVar2 == 0 &&
              ((iVar2 = FUN_004cf40a(param_1,auStack_b8,auStack_98), iVar2 == 0 &&
               (iVar2 = FUN_004cc5a2(param_1,auStack_98,auStack_b8), iVar2 == 0)))))) {
            iVar2 = 0;
          }
        }
        else {
          *(uint *)(param_1 + 0x28) = local_c8[2];
          iVar2 = iVar4;
        }
      }
    }
  }
  return iVar2;
}

