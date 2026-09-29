
uint FUN_00505aa2(int param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  char cVar7;
  char cVar8;
  uint uVar9;
  byte local_38;
  byte local_37;
  byte local_36;
  byte local_35;
  byte local_34;
  undefined1 local_33;
  undefined1 local_32;
  byte local_31;
  byte local_30;
  byte local_2f [3];
  byte local_2c [4];
  undefined4 uStack_28;
  
  cVar8 = '\0';
  if ((param_2[10] == 0) && (param_2[0xb] == 0)) {
    cVar7 = '\0';
  }
  else {
    cVar7 = '\x01';
  }
  if ((byte)(param_2[2] + param_2[0xd] + cVar7) < 2) {
    uStack_28 = param_4;
    uVar2 = FUN_00508e5c(param_1,0x1d,6,&local_34);
    uVar3 = FUN_00508e5c(param_1,0x28,1,&local_37);
    uVar2 = uVar2 | uVar3;
    if ((local_2f[0] & 7) >> 2 != 0) {
      uVar9 = 0xffffffff;
      uVar3 = 0xffffffff;
      uVar1 = FUN_00508e5c(param_1,0x10,1,&local_36);
      uVar2 = uVar2 | uVar1;
      if ((local_36 & 3) != 0) {
        uVar3 = FUN_00508e5c(param_1,0x1b,1,local_2c);
        uVar2 = uVar2 | uVar3;
        uVar3 = FUN_0050594a(local_2c[0] & 0xf);
      }
      if ((local_36 & 0xf) >> 2 != 0) {
        uVar1 = FUN_00508e5c(param_1,0x1c,1,&local_35);
        uVar2 = uVar2 | uVar1;
        uVar9 = FUN_0050594a(local_35 & 0xf);
      }
      local_2f[0] = local_2f[0] & 0xfb;
      uVar1 = FUN_00508e74(param_1,0x22,1,local_2f);
      uVar2 = uVar1 | uVar2;
      if ((uVar3 != 0xffffffff) || (uVar9 != 0xffffffff)) {
        if (uVar9 <= uVar3) {
          uVar3 = uVar9;
        }
        FUN_00505f10(param_1,uVar3 << 1);
      }
    }
    local_30 = local_30 & 0xfe;
    uVar3 = FUN_00508e74(param_1,0x21,1,&local_30);
    local_34 = local_34 & 0x3f;
    uVar1 = FUN_00508e74(param_1,0x1d,1,&local_34);
    local_34 = param_2[7] & 0x3f | local_34 & 0xc0;
    local_33 = (undefined1)*(undefined2 *)(param_2 + 4);
    local_32 = (undefined1)((ushort)*(undefined2 *)(param_2 + 4) >> 8);
    local_31 = local_31 & 0xf7 | (param_2[8] & 1) << 3;
    local_30 = local_30 & 0xc1 | (param_2[10] & 1) << 5 | (param_2[0xb] & 1) << 4 |
               (param_2[2] & 1) << 3 | (*param_2 & 1) << 2 | (param_2[1] & 1) << 1;
    local_2f[0] = param_2[0xc] & 1 |
                  local_2f[0] & 0xc4 | (param_2[0xe] & 7) << 3 | (param_2[9] & 1) << 1;
    local_37 = param_2[0x10] & 0xf | param_2[0xf] << 4;
    uVar9 = FUN_00508e74(param_1,0x1d,6,&local_34);
    uVar4 = FUN_00508e74(param_1,0x28,1,&local_37);
    uVar5 = FUN_00508e5c(param_1,0xa258,1,&local_38);
    if (param_2[9] == 0) {
      local_38 = local_38 & 0xfc;
    }
    else {
      local_38 = local_38 | 3;
    }
    uVar6 = FUN_00508e74(param_1,0xa258,1,&local_38);
    uVar6 = uVar2 | uVar3 | uVar1 | uVar9 | uVar4 | uVar5 | uVar6;
    local_34 = local_34 & 0x3f | param_2[6] << 6;
    if (param_2[6] == 0) {
      local_30 = local_30 & 0xfe;
      uVar2 = FUN_00508e74(param_1,0x21,1,&local_30);
      uVar1 = FUN_00508e74(param_1,0x1d,1,&local_34);
      uVar1 = uVar6 | uVar2 | uVar1;
      *(undefined1 *)(param_1 + 0x1d) = 0;
      *(undefined1 *)(param_1 + 0x1c) = 0;
    }
    else {
      uVar2 = FUN_00508e74(param_1,0x1d,1,&local_34);
      local_30 = local_30 | 1;
      uVar3 = FUN_00508e74(param_1,0x21,1,&local_30);
      local_2f[0] = local_2f[0] & 0xfb | (param_2[0xd] & 1) << 2;
      uVar1 = FUN_00508e74(param_1,0x22,1,local_2f);
      uVar1 = uVar6 | uVar2 | uVar3 | uVar1;
      *(byte *)(param_1 + 0x1d) = param_2[0xd];
      *(undefined1 *)(param_1 + 0x1c) = 1;
    }
    if ((param_2[10] == 0) && (param_2[0xb] == 0)) {
      if (param_2[2] == 0) {
        if (param_2[1] != 0) {
          cVar8 = '\b';
        }
        if (*param_2 != 0) {
          cVar8 = cVar8 + '\b';
        }
      }
      else {
        cVar8 = '\x14';
      }
    }
    else if ((param_2[1] == 0) && (*param_2 == 0)) {
      if ((param_2[10] == 0) || (param_2[0xb] == 0)) {
        cVar8 = '\x10';
      }
      else {
        cVar8 = '\x14';
      }
    }
    else {
      cVar8 = ' ';
    }
    *(char *)(param_1 + 0x10) = cVar8;
    uVar2 = FUN_00505ea8(param_1);
    uVar1 = uVar1 | uVar2;
  }
  else {
    uVar1 = 0xfffffff5;
  }
  return uVar1;
}

