
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
text_stream_animation_presets_init(int param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int *piVar2;
  int *piVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uStack_d0;
  int iStack_cc;
  int iStack_c8;
  int iStack_c4;
  int iStack_bc;
  int iStack_b8;
  undefined1 auStack_b0 [3];
  undefined1 uStack_ad;
  int iStack_ac;
  int iStack_a8;
  int iStack_a4;
  int iStack_9c;
  int iStack_98;
  undefined1 auStack_90 [3];
  undefined1 uStack_8d;
  int iStack_8c;
  int iStack_88;
  int iStack_84;
  int iStack_7c;
  int iStack_78;
  undefined1 auStack_70 [3];
  undefined1 uStack_6d;
  int iStack_6c;
  int iStack_68;
  int iStack_64;
  int iStack_5c;
  int iStack_58;
  undefined1 auStack_50 [3];
  undefined1 uStack_4d;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined1 auStack_1c [3];
  undefined1 uStack_19;
  undefined4 uStack_18;
  
  pcVar1 = DAT_00553d44;
  if (param_1 == 0) {
    uVar4 = 0xffffffff;
  }
  else {
    uStack_18 = param_4;
    if (*DAT_00553d44 != '\0') {
      if (param_2 != '\x01') {
        return 0;
      }
      text_stream_animation_presets_deinit();
    }
    *_DAT_00553d48 = param_1;
    FUN_0048949c(&uStack_4c,0x34);
    uStack_4c = _DAT_00553d4c;
    uStack_48 = 0x12;
    uStack_44 = _DAT_00553d50;
    uStack_40 = 0x13;
    uStack_3c = _DAT_00553d54;
    uStack_38 = 0x19;
    uStack_34 = _DAT_00553d58;
    uStack_30 = 0x10;
    uStack_2c = 0x32;
    uStack_28 = 0x24;
    uStack_24 = 0x14;
    uStack_d0 = FUN_0044104c(0);
    FUN_00439be4(auStack_1c,&uStack_d0,3);
    piVar2 = DAT_00553d5c;
    uStack_19 = 0xff;
    FUN_00439be4(DAT_00553d5c,&uStack_4c,0x34);
    if ((*piVar2 != 0) && (piVar2[1] != 0)) {
      FUN_0048949c(&iStack_6c,0x20);
      iStack_6c = *piVar2;
      iStack_68 = piVar2[1];
      if (piVar2[8] == 0) {
        iStack_64 = 0x32;
      }
      else {
        iStack_64 = piVar2[8];
      }
      iStack_5c = piVar2[9];
      iStack_58 = piVar2[10];
      FUN_00439be4(auStack_50,piVar2 + 0xc,3);
      piVar3 = DAT_00553d60;
      uStack_4d = *(undefined1 *)((int)piVar2 + 0x33);
      iVar5 = FUN_00463c68(param_1,&iStack_6c);
      *piVar3 = iVar5;
      if ((*piVar3 != 0) && (iVar5 = FUN_00463e9a(*piVar3), iVar5 != 0)) {
        text_stream_apply_animation_bounds(iVar5,0,0);
        FUN_0044122a(iVar5,8,0);
        FUN_00441238(iVar5,8,0);
        FUN_0043ded4(iVar5,1);
      }
    }
    if ((piVar2[2] != 0) && (piVar2[3] != 0)) {
      FUN_0048949c(&iStack_8c,0x20);
      iStack_8c = piVar2[2];
      iStack_88 = piVar2[3];
      if (piVar2[8] == 0) {
        iStack_84 = 0x32;
      }
      else {
        iStack_84 = piVar2[8];
      }
      iStack_7c = piVar2[9];
      iStack_78 = piVar2[10];
      FUN_00439be4(auStack_70,piVar2 + 0xc,3);
      piVar3 = DAT_00553d60;
      uStack_6d = *(undefined1 *)((int)piVar2 + 0x33);
      iVar5 = FUN_00463c68(param_1,&iStack_8c);
      piVar3[1] = iVar5;
      if ((piVar3[1] != 0) && (iVar5 = FUN_00463e9a(piVar3[1]), iVar5 != 0)) {
        text_stream_apply_animation_bounds(iVar5,0,0);
        FUN_0044122a(iVar5,8,0);
        FUN_00441238(iVar5,8,0);
        FUN_0043ded4(iVar5,1);
      }
    }
    if ((piVar2[4] != 0) && (piVar2[5] != 0)) {
      FUN_0048949c(&iStack_ac,0x20);
      iStack_ac = piVar2[4];
      iStack_a8 = piVar2[5];
      if (piVar2[8] == 0) {
        iStack_a4 = 0x32;
      }
      else {
        iStack_a4 = piVar2[8];
      }
      iStack_9c = piVar2[9];
      iStack_98 = piVar2[10];
      FUN_00439be4(auStack_90,piVar2 + 0xc,3);
      piVar3 = DAT_00553d60;
      uStack_8d = *(undefined1 *)((int)piVar2 + 0x33);
      iVar5 = FUN_00463c68(param_1,&iStack_ac);
      piVar3[2] = iVar5;
      if ((piVar3[2] != 0) && (iVar5 = FUN_00463e9a(piVar3[2]), iVar5 != 0)) {
        text_stream_apply_animation_bounds(iVar5,0,0);
        FUN_0044122a(iVar5,8,0);
        FUN_00441238(iVar5,8,0);
        FUN_0043ded4(iVar5,1);
      }
    }
    if ((piVar2[6] != 0) && (piVar2[7] != 0)) {
      FUN_0048949c(&iStack_cc,0x20);
      iStack_cc = piVar2[6];
      iStack_c8 = piVar2[7];
      if (piVar2[8] == 0) {
        iStack_c4 = 0x32;
      }
      else {
        iStack_c4 = piVar2[8];
      }
      iStack_bc = piVar2[9];
      iStack_b8 = piVar2[10];
      FUN_00439be4(auStack_b0,piVar2 + 0xc,3);
      piVar3 = DAT_00553d60;
      uStack_ad = *(undefined1 *)((int)piVar2 + 0x33);
      iVar5 = FUN_00463c68(param_1,&iStack_cc);
      piVar3[3] = iVar5;
      if ((piVar3[3] != 0) && (iVar5 = FUN_00463e9a(piVar3[3]), iVar5 != 0)) {
        text_stream_apply_animation_bounds(iVar5,0,0);
        FUN_0044122a(iVar5,8,0);
        FUN_00441238(iVar5,8,0);
        FUN_0043ded4(iVar5,1);
      }
    }
    *pcVar1 = '\x01';
    *DAT_00553fe8 = 0;
    FUN_0043c0e4(DAT_00553fec,0x40,0);
    uVar4 = 0;
  }
  return uVar4;
}

