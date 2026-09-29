
int FUN_004ce4dc(int param_1,undefined4 param_2)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_6c [8];
  uint local_64 [3];
  undefined2 local_58;
  undefined1 local_56;
  undefined1 auStack_54 [20];
  short local_40;
  char local_3d;
  undefined1 auStack_34 [32];
  int iStack_14;
  undefined4 uStack_10;
  
  iStack_14 = param_1;
  uStack_10 = param_2;
  iVar2 = FUN_004cf9e0(param_1);
  if (iVar2 == 0) {
    iVar2 = FUN_004cc04a(param_1,auStack_34,&uStack_10,0);
    if ((iVar2 < 0) || (iVar3 = FUN_004caeb0(iVar2), iVar3 == 0x3ff)) {
      if (-1 < iVar2) {
        iVar2 = -0x16;
      }
    }
    else {
      local_64[2] = *(undefined4 *)(param_1 + 0x28);
      iVar3 = FUN_004cae98(iVar2);
      if (iVar3 == 2) {
        uVar1 = FUN_004caeb0(iVar2);
        iVar3 = FUN_004cb3c8(param_1,auStack_34,DAT_004cef6c,DAT_004cef68 | (uint)uVar1 << 10,
                             auStack_6c);
        if (iVar3 < 0) {
          return iVar3;
        }
        FUN_004cae3e(auStack_6c);
        iVar3 = FUN_004cbedc(param_1,auStack_54,auStack_6c);
        if (iVar3 != 0) {
          return iVar3;
        }
        if ((local_40 != 0) || (local_3d != '\0')) {
          return -0x27;
        }
        iVar3 = FUN_004cf570(param_1,1);
        if (iVar3 != 0) {
          return iVar3;
        }
        local_56 = 0;
        local_58 = 0;
        *(uint **)(param_1 + 0x28) = local_64 + 2;
      }
      local_64[0] = 0;
      local_64[1] = 0;
      iVar3 = FUN_004caeb0(iVar2);
      local_64[0] = DAT_004cef70 | iVar3 << 10;
      iVar3 = FUN_004cd388(param_1,auStack_34,local_64,1);
      if (iVar3 == 0) {
        *(uint *)(param_1 + 0x28) = local_64[2];
        iVar2 = FUN_004cae98(iVar2);
        if ((iVar2 != 2) ||
           (((iVar2 = FUN_004cf570(param_1,0xffffffff), iVar2 == 0 &&
             (iVar2 = FUN_004cf40a(param_1,auStack_54,auStack_34), iVar2 == 0)) &&
            (iVar2 = FUN_004cc5a2(param_1,auStack_34,auStack_54), iVar2 == 0)))) {
          iVar2 = 0;
        }
      }
      else {
        *(uint *)(param_1 + 0x28) = local_64[2];
        iVar2 = iVar3;
      }
    }
  }
  return iVar2;
}

