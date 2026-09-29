
undefined4 FUN_0050f8cc(int param_1,char param_2)

{
  char *pcVar1;
  int *piVar2;
  int *piVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 local_c8;
  int local_c4;
  int local_c0;
  int local_b4;
  int local_b0;
  undefined1 auStack_a8 [3];
  undefined1 local_a5;
  int local_a4;
  int local_a0;
  int local_94;
  int local_90;
  undefined1 auStack_88 [3];
  undefined1 local_85;
  int local_84;
  int local_80;
  int local_74;
  int local_70;
  undefined1 auStack_68 [3];
  undefined1 local_65;
  int local_64;
  int local_60;
  int local_54;
  int local_50;
  undefined1 auStack_48 [3];
  undefined1 local_45;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined1 auStack_18 [3];
  undefined1 local_15;
  
  pcVar1 = DAT_0050fe7c;
  if (param_1 == 0) {
    uVar4 = 0xffffffff;
  }
  else {
    if (*DAT_0050fe7c != '\0') {
      if (param_2 != '\x01') {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_c4 = DAT_0050fec4;
          local_c8 = 0x5f;
          FUN_0043d574(3,DAT_0050febc,DAT_0050feb8,DAT_0050feb4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_0050fec8,DAT_0050fec8);
        }
        return 0;
      }
      FUN_0050fbb6();
    }
    *DAT_0050fe80 = param_1;
    FUN_0048949c(&local_44,0x30);
    local_44 = DAT_0050fe84;
    local_40 = 0xf;
    local_3c = DAT_0050fe88;
    local_38 = 0x23;
    local_34 = DAT_0050fe8c;
    local_30 = 0xb;
    local_2c = DAT_0050fe90;
    local_28 = 0x36;
    local_24 = 0x32;
    local_20 = 0x18;
    local_1c = 0x18;
    local_c8 = FUN_0044104c(0);
    FUN_00439be4(auStack_18,&local_c8,3);
    piVar2 = DAT_0050fe94;
    local_15 = 0;
    FUN_00439be4(DAT_0050fe94,&local_44,0x30);
    if ((*piVar2 != 0) && (piVar2[1] != 0)) {
      FUN_00439c04(&local_64,DAT_0050fe98,0x20);
      local_64 = *piVar2;
      local_60 = piVar2[1];
      local_54 = piVar2[9];
      local_50 = piVar2[10];
      FUN_00439be4(auStack_48,piVar2 + 0xb,3);
      piVar3 = DAT_0050fe9c;
      local_45 = *(undefined1 *)((int)piVar2 + 0x2f);
      iVar5 = FUN_00463c68(param_1,&local_64);
      *piVar3 = iVar5;
      if ((*piVar3 != 0) && (iVar5 = FUN_00463e9a(*piVar3), iVar5 != 0)) {
        FUN_0043f6b8(iVar5,7,0,0);
        FUN_0043ded4(iVar5,1);
      }
    }
    if ((piVar2[2] != 0) && (piVar2[3] != 0)) {
      FUN_00439c04(&local_84,DAT_0050fea0,0x20);
      local_84 = piVar2[2];
      local_80 = piVar2[3];
      local_74 = piVar2[9];
      local_70 = piVar2[10];
      FUN_00439be4(auStack_68,piVar2 + 0xb,3);
      piVar3 = DAT_0050fe9c;
      local_65 = *(undefined1 *)((int)piVar2 + 0x2f);
      iVar5 = FUN_00463c68(param_1,&local_84);
      piVar3[1] = iVar5;
      if ((piVar3[1] != 0) && (iVar5 = FUN_00463e9a(piVar3[1]), iVar5 != 0)) {
        FUN_0043f6b8(iVar5,7,0,0);
        FUN_0043ded4(iVar5,1);
      }
    }
    if ((piVar2[4] != 0) && (piVar2[5] != 0)) {
      FUN_00439c04(&local_a4,DAT_0050fea4,0x20);
      local_a4 = piVar2[4];
      local_a0 = piVar2[5];
      local_94 = piVar2[9];
      local_90 = piVar2[10];
      FUN_00439be4(auStack_88,piVar2 + 0xb,3);
      piVar3 = DAT_0050fe9c;
      local_85 = *(undefined1 *)((int)piVar2 + 0x2f);
      iVar5 = FUN_00463c68(param_1,&local_a4);
      piVar3[2] = iVar5;
      if ((piVar3[2] != 0) && (iVar5 = FUN_00463e9a(piVar3[2]), iVar5 != 0)) {
        FUN_0043f6b8(iVar5,7,0,0);
        FUN_0043ded4(iVar5,1);
      }
    }
    if ((piVar2[6] != 0) && (piVar2[7] != 0)) {
      FUN_00439c04(&local_c4,DAT_0050fea8,0x20);
      local_c4 = piVar2[6];
      local_c0 = piVar2[7];
      local_b4 = piVar2[9];
      local_b0 = piVar2[10];
      FUN_00439be4(auStack_a8,piVar2 + 0xb,3);
      piVar3 = DAT_0050fe9c;
      local_a5 = *(undefined1 *)((int)piVar2 + 0x2f);
      iVar5 = FUN_00463c68(param_1,&local_c4);
      piVar3[3] = iVar5;
      if ((piVar3[3] != 0) && (iVar5 = FUN_00463e9a(piVar3[3]), iVar5 != 0)) {
        FUN_0043f6b8(iVar5,7,0,0);
        FUN_0043ded4(iVar5,1);
      }
    }
    *pcVar1 = '\x01';
    *DAT_0050feac = 0;
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      local_c4 = DAT_0050feb0;
      local_c8 = 0xd7;
      FUN_0043d574(3,DAT_0050febc,DAT_0050feb8,DAT_0050feb4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0050fec0,DAT_0050fec0);
    }
    uVar4 = 0;
  }
  return uVar4;
}

