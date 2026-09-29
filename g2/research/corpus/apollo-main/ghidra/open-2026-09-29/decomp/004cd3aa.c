
int FUN_004cd3aa(int param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  ushort local_b0 [2];
  undefined4 local_ac;
  undefined1 *local_a8;
  undefined4 local_a4;
  undefined1 *local_a0;
  undefined1 auStack_9c [23];
  char local_85;
  undefined1 auStack_84 [8];
  undefined1 auStack_7c [32];
  undefined4 local_5c;
  undefined2 local_58;
  undefined1 local_56;
  undefined1 auStack_54 [23];
  char local_3d;
  uint local_34 [2];
  uint local_2c;
  undefined4 local_28;
  uint local_24;
  undefined1 *local_20;
  undefined4 local_1c;
  undefined1 *local_18;
  undefined4 local_14;
  
  local_14 = param_2;
  iVar1 = FUN_004cf9e0(param_1);
  if (iVar1 == 0) {
    local_5c = *(undefined4 *)(param_1 + 0x28);
    iVar1 = FUN_004cc04a(param_1,auStack_54,&local_14,local_b0);
    if ((iVar1 == -2) && (iVar2 = FUN_004cad80(local_14), iVar2 != 0)) {
      uVar3 = FUN_004cad76(local_14);
      if (*(uint *)(param_1 + 0x70) < uVar3) {
        iVar1 = -0x24;
      }
      else {
        lfs_alloc_ckpoint(param_1);
        iVar1 = FUN_004cc502(param_1,auStack_7c);
        if (iVar1 == 0) {
          FUN_00439c04(auStack_9c,auStack_54,0x20);
          do {
            if (local_85 == '\0') {
              FUN_004cae54(auStack_84);
              local_a4 = *DAT_004cdf64;
              local_a0 = auStack_84;
              iVar1 = FUN_004cd388(param_1,auStack_7c,&local_a4,1);
              FUN_004cae3e(auStack_84);
              if (iVar1 != 0) {
                return iVar1;
              }
              if (local_3d != '\0') {
                iVar1 = FUN_004cf570(param_1,1);
                if (iVar1 != 0) {
                  return iVar1;
                }
                local_56 = 0;
                local_58 = 0;
                *(undefined4 **)(param_1 + 0x28) = &local_5c;
                FUN_004cae54(auStack_7c);
                local_ac = *DAT_004cdf68;
                local_a8 = auStack_7c;
                iVar1 = FUN_004cd388(param_1,auStack_9c,&local_ac,1);
                FUN_004cae3e(auStack_7c);
                if (iVar1 != 0) {
                  *(undefined4 *)(param_1 + 0x28) = local_5c;
                  return iVar1;
                }
                *(undefined4 *)(param_1 + 0x28) = local_5c;
                iVar1 = FUN_004cf570(param_1,0xffffffff);
                if (iVar1 != 0) {
                  return iVar1;
                }
              }
              FUN_004cae54(auStack_7c);
              FUN_0048949c(local_34,0x20);
              local_34[0] = DAT_004cdf6c | (uint)local_b0[0] << 10;
              local_2c = uVar3 | (uint)local_b0[0] << 10 | 0x200000;
              local_28 = local_14;
              local_24 = DAT_004cdf70 | (uint)local_b0[0] << 10;
              local_20 = auStack_7c;
              local_1c = DAT_004ce154;
              if (local_3d != '\0') {
                local_1c = 0;
              }
              local_18 = auStack_7c;
              iVar1 = FUN_004cd388(param_1,auStack_54,local_34,4);
              FUN_004cae3e(auStack_7c);
              if (iVar1 != 0) {
                return iVar1;
              }
              return 0;
            }
            iVar1 = FUN_004cbedc(param_1,auStack_9c,auStack_84);
          } while (iVar1 == 0);
        }
      }
    }
    else if (-1 < iVar1) {
      iVar1 = -0x11;
    }
  }
  return iVar1;
}

