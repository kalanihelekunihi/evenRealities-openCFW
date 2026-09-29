
undefined4 FUN_005056d2(int param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  ushort uVar2;
  uint local_40;
  undefined2 local_3c;
  short local_3a;
  short local_38;
  short local_36;
  short local_34;
  short local_32;
  short local_30;
  short local_2e;
  undefined4 uStack_14;
  
  uVar2 = 1;
  if ((char)*param_2 < '\0') {
    uVar1 = 0xffffffff;
  }
  else {
    local_40 = 0;
    local_3c = 0;
    if ((*param_2 & 0x7f) >> 6 != 0) {
      local_3a = *(short *)(param_2 + 1);
      local_38 = *(short *)(param_2 + 3);
      local_36 = *(short *)(param_2 + 5);
      uVar2 = 7;
      if (((local_3a != DAT_00505ed8) && (local_38 != DAT_00505ed8)) && (local_36 != DAT_00505ed8))
      {
        *(short *)(param_1 + 0x1e) = local_3a;
        *(short *)(param_1 + 0x20) = local_38;
        *(short *)(param_1 + 0x22) = local_36;
        *(undefined1 *)(param_1 + 0x2c) = 1;
        local_40 = 1;
      }
    }
    if ((*param_2 & 0x3f) >> 5 != 0) {
      local_34 = CONCAT11(param_2[uVar2 + 1],param_2[uVar2]);
      local_32 = CONCAT11(param_2[uVar2 + 3],param_2[uVar2 + 2]);
      local_30 = CONCAT11(param_2[uVar2 + 5],param_2[uVar2 + 4]);
      uVar2 = uVar2 + 6;
      if (((local_34 != DAT_00505ed8) && (local_32 != DAT_00505ed8)) && (local_30 != DAT_00505ed8))
      {
        *(short *)(param_1 + 0x24) = local_34;
        *(short *)(param_1 + 0x26) = local_32;
        *(short *)(param_1 + 0x28) = local_30;
        *(undefined1 *)(param_1 + 0x2d) = 1;
        local_40 = local_40 | 2;
      }
    }
    if ((*param_2 & 0x60) != 0) {
      local_2e = (short)(char)param_2[uVar2];
      uVar2 = uVar2 + 1;
      if (local_2e != -0x80) {
        *(short *)(param_1 + 0x2a) = local_2e;
        *(undefined1 *)(param_1 + 0x2e) = 1;
        local_40 = local_40 | 8;
      }
    }
    if ((*param_2 & 0x60) == 0x60) {
      local_3c = CONCAT11(param_2[uVar2 + 1],param_2[uVar2]);
    }
    if (*(int *)(param_1 + 0x18) != 0) {
      uStack_14 = param_4;
      (**(code **)(param_1 + 0x18))(&local_40);
    }
    uVar1 = 0;
  }
  return uVar1;
}

