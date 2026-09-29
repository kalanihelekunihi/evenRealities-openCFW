
void FUN_005ca5ac(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  uint in_fpscr;
  int local_150;
  int local_14c;
  int local_148;
  int local_144;
  int local_140;
  int local_13c;
  int local_138;
  int local_134;
  undefined4 local_130;
  undefined4 uStack_12c;
  undefined1 auStack_128 [16];
  undefined4 local_118;
  undefined4 local_104;
  undefined4 local_100;
  int local_fc;
  int iStack_f8;
  undefined2 local_f4;
  undefined1 auStack_e8 [16];
  undefined4 local_d8;
  undefined4 local_c4;
  undefined4 local_c0;
  undefined4 local_bc;
  undefined4 uStack_b8;
  undefined2 local_b4;
  undefined1 auStack_a8 [16];
  undefined4 local_98;
  undefined4 local_8c;
  undefined4 local_88;
  undefined4 local_84;
  undefined4 local_80;
  undefined1 auStack_68 [16];
  undefined4 local_58;
  undefined8 local_4c;
  undefined8 local_44;
  int local_38;
  
  uVar1 = FUN_00451960(param_2);
  if (1 < (*(uint *)(param_1 + 0x48) & 0x7fff)) {
    if ((((*(char *)(param_1 + 0x3c) == '\x02') || (*(char *)(param_1 + 0x3c) == '\x04')) ||
        (*(char *)(param_1 + 0x3c) == '\x01')) || (*(char *)(param_1 + 0x3c) == '\0')) {
      FUN_005c6fbc(auStack_68);
      local_58 = uVar1;
      FUN_00452b0e(param_1,0,auStack_68);
      iVar2 = FUN_005c9de8(param_1,0);
      iVar3 = FUN_005c9db6(param_1,0);
      iVar3 = iVar2 + iVar3;
      iVar4 = FUN_005c9dc0(param_1,0);
      iVar5 = FUN_005c9dca(param_1,0);
      iVar5 = iVar2 + iVar5;
      iVar6 = FUN_005c9dd4(param_1,0);
      local_148 = 0;
      local_14c = 0;
      if (*(char *)(param_1 + 0x3c) == '\x02') {
        local_148 = (local_38 / 2 + *(int *)(param_1 + 0x1c)) - (iVar2 + iVar6);
        local_14c = iVar3 + *(int *)(param_1 + 0x18);
      }
      else if (*(char *)(param_1 + 0x3c) == '\x04') {
        local_148 = iVar5 + local_38 / 2 + *(int *)(param_1 + 0x14);
        local_14c = iVar3 + *(int *)(param_1 + 0x18);
      }
      if (*(char *)(param_1 + 0x3c) == '\x01') {
        local_148 = iVar2 + iVar6 + *(int *)(param_1 + 0x14);
        local_14c = iVar3 + local_38 / 2 + *(int *)(param_1 + 0x18);
      }
      else if (*(char *)(param_1 + 0x3c) == '\0') {
        local_148 = iVar5 + *(int *)(param_1 + 0x14);
        local_14c = (local_38 / 2 + *(int *)(param_1 + 0x20)) - (iVar2 + iVar4);
      }
      if ((*(char *)(param_1 + 0x3c) == '\x02') || (*(char *)(param_1 + 0x3c) == '\x04')) {
        local_150 = local_148 + -1;
        local_148 = local_148 + -1;
        local_14c = local_14c - *(int *)(param_1 + 0x5c) / 2;
        local_144 = *(int *)(param_1 + 0x60) / 2 + (*(int *)(param_1 + 0x20) - (iVar2 + iVar4));
      }
      else {
        local_150 = local_148 - *(int *)(param_1 + 0x5c) / 2;
        local_148 = *(int *)(param_1 + 0x60) / 2 + (*(int *)(param_1 + 0x1c) - iVar5);
        local_144 = local_14c;
      }
      local_4c = FUN_004515b0(&local_150);
      local_44 = FUN_004515b0(&local_148);
      FUN_005c6fea(uVar1,auStack_68);
      puVar7 = (undefined4 *)FUN_00482ce4(param_1 + 0x2c);
      while (puVar7 != (undefined4 *)0x0) {
        FUN_005c6fbc(auStack_a8);
        local_98 = uVar1;
        FUN_00452b0e(param_1,0,auStack_a8);
        if ((*(char *)(param_1 + 0x3c) == '\x02') || (*(char *)(param_1 + 0x3c) == '\x04')) {
          local_138 = local_150;
          local_134 = (int)puVar7[7] / 2 + puVar7[10];
          local_140 = local_150;
          local_13c = puVar7[0xc] - (int)puVar7[8] / 2;
        }
        else {
          local_138 = puVar7[9] - (int)puVar7[7] / 2;
          local_134 = local_14c;
          local_140 = (int)puVar7[8] / 2 + puVar7[0xb];
          local_13c = local_14c;
        }
        FUN_005caede(param_1,auStack_a8,*puVar7,0);
        local_8c = VectorSignedToFloat(local_138,(byte)(in_fpscr >> 0x16) & 3);
        local_88 = VectorSignedToFloat(local_134,(byte)(in_fpscr >> 0x16) & 3);
        local_84 = VectorSignedToFloat(local_140,(byte)(in_fpscr >> 0x16) & 3);
        local_80 = VectorSignedToFloat(local_13c,(byte)(in_fpscr >> 0x16) & 3);
        FUN_005c6fea(uVar1,auStack_a8);
        puVar7 = (undefined4 *)FUN_00482cfa(param_1 + 0x2c,puVar7);
      }
    }
    else if ((*(char *)(param_1 + 0x3c) == '\x10') || (*(char *)(param_1 + 0x3c) == '\b')) {
      FUN_005c1054(auStack_e8);
      local_d8 = uVar1;
      FUN_00452bca(param_1,0,auStack_e8);
      FUN_005ca934(param_1,&local_130,&local_13c);
      local_150 = *(int *)(param_1 + 0x50) + *(int *)(param_1 + 0x54);
      uVar8 = FUN_004888b4(*(undefined4 *)(param_1 + 0x40),*(undefined4 *)(param_1 + 0x40),
                           *(undefined4 *)(param_1 + 0x44),*(undefined4 *)(param_1 + 0x54));
      local_150 = *(int *)(param_1 + 0x50) + *(int *)(param_1 + 0x54);
      uVar9 = FUN_004888b4(*(undefined4 *)(param_1 + 0x44),*(undefined4 *)(param_1 + 0x40),
                           *(undefined4 *)(param_1 + 0x44),*(undefined4 *)(param_1 + 0x54));
      local_bc = local_130;
      uStack_b8 = uStack_12c;
      local_b4 = (undefined2)local_13c;
      local_c4 = VectorSignedToFloat(uVar8,(byte)(in_fpscr >> 0x16) & 3);
      local_c0 = VectorSignedToFloat(uVar9,(byte)(in_fpscr >> 0x16) & 3);
      FUN_005c1082(uVar1,auStack_e8);
      for (puVar7 = (undefined4 *)FUN_00482ce4(param_1 + 0x2c); puVar7 != (undefined4 *)0x0;
          puVar7 = (undefined4 *)FUN_00482cfa(param_1 + 0x2c,puVar7)) {
        FUN_005c1054(auStack_128);
        local_118 = uVar1;
        FUN_00452bca(param_1,0,auStack_128);
        FUN_005ca934(param_1,&local_138,&local_140);
        local_150 = *(int *)(param_1 + 0x50) + *(int *)(param_1 + 0x54);
        uVar8 = FUN_004888b4(puVar7[3],*(undefined4 *)(param_1 + 0x40),
                             *(undefined4 *)(param_1 + 0x44),*(undefined4 *)(param_1 + 0x54));
        local_150 = *(int *)(param_1 + 0x50) + *(int *)(param_1 + 0x54);
        uVar9 = FUN_004888b4(puVar7[4],*(undefined4 *)(param_1 + 0x40),
                             *(undefined4 *)(param_1 + 0x44),*(undefined4 *)(param_1 + 0x54));
        FUN_005caf94(param_1,auStack_128,*puVar7);
        local_fc = local_138;
        iStack_f8 = local_134;
        local_f4 = (undefined2)local_140;
        local_104 = VectorSignedToFloat(uVar8,(byte)(in_fpscr >> 0x16) & 3);
        local_100 = VectorSignedToFloat(uVar9,(byte)(in_fpscr >> 0x16) & 3);
        FUN_005c1082(uVar1,auStack_128);
      }
    }
  }
  return;
}

