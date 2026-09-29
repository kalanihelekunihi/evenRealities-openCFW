
/* WARNING: Heritage AFTER dead removal. Example location: s1 : 0x004ea9a6 */
/* WARNING: Restarted to delay deadcode elimination for space: register */

void FUN_004ea800(int param_1,uint param_2)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  undefined4 uVar6;
  uint local_d50;
  uint local_d4c;
  uint local_d48;
  uint local_d44;
  uint local_d40;
  uint local_d3c;
  undefined1 auStack_d30 [32];
  undefined1 auStack_d10 [128];
  undefined1 auStack_c90 [136];
  float local_c08;
  float local_c04;
  undefined4 local_c00;
  int local_bdc;
  undefined4 local_bd8;
  undefined4 local_bd4;
  undefined1 auStack_bd0 [744];
  undefined1 auStack_8e8 [32];
  undefined1 auStack_8c8 [32];
  undefined1 auStack_8a8 [128];
  undefined1 auStack_828 [136];
  float local_7a0;
  float local_79c;
  undefined4 local_798;
  int local_774;
  undefined4 local_770;
  undefined4 local_76c;
  undefined1 auStack_768 [744];
  undefined1 auStack_480 [32];
  undefined1 auStack_460 [32];
  undefined1 auStack_440 [128];
  undefined1 auStack_3c0 [136];
  float local_338;
  float local_334;
  undefined4 local_330;
  int local_30c;
  undefined4 local_308;
  undefined4 local_304;
  undefined1 auStack_300 [744];
  
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_d4c = DAT_004eb320;
      local_d50 = 0x1c6;
      FUN_0043d574(1,DAT_004eb32c,DAT_004eb328,DAT_004eb324);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004eb330);
    }
  }
  else {
    uVar5 = param_2 * 3;
    uVar4 = param_2 * 3 + 1;
    uVar3 = param_2 * 3 + 2;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_d4c = DAT_004eb334;
      local_d50 = 0x1d0;
      local_d48 = param_2;
      local_d44 = uVar5;
      local_d40 = uVar4;
      local_d3c = uVar3;
      FUN_0043d574(4,DAT_004eb32c,DAT_004eb328,DAT_004eb324);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      local_d50 = uVar5;
      local_d4c = uVar4;
      local_d48 = uVar3;
      compress_log_output(0x11000000,DAT_004eb338,DAT_004eb338,param_2);
    }
    iVar2 = FUN_004e9fd6();
    if (((int)uVar5 < iVar2) && (iVar2 = FUN_004e9eb8(auStack_440,uVar5 & 0xffff), iVar2 != 0)) {
      if (local_30c == 1) {
        FUN_00498680(*(undefined4 *)(param_1 + 4),DAT_004eb494);
      }
      else if (local_30c == 2) {
        FUN_00498680(*(undefined4 *)(param_1 + 4),DAT_004eb498);
      }
      else {
        FUN_00498680(*(undefined4 *)(param_1 + 4),DAT_004eb49c);
      }
      FUN_0043f4c0(*(undefined4 *)(param_1 + 8),0xe4,0x1e);
      FUN_00499678(*(undefined4 *)(param_1 + 8),1);
      FUN_0049942e(*(undefined4 *)(param_1 + 8),auStack_440);
      FUN_0043f4c0(*(undefined4 *)(param_1 + 0xc),0xf0,0x1c);
      FUN_00499678(*(undefined4 *)(param_1 + 0xc),1);
      FUN_0049942e(*(undefined4 *)(param_1 + 0xc),auStack_3c0);
      FUN_004ecee8(SUB84((double)local_334,0),auStack_460,0x20);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x14),auStack_460);
      uVar6 = (undefined4)((ulonglong)(double)local_334 >> 0x20);
      FUN_004ecf3c(SUB84((double)local_334,0),uVar6,SUB84((double)local_338,0),auStack_480,0x20);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x18),auStack_480);
      cVar1 = FUN_004ff4c0(local_330,uVar6,local_304,uVar5,auStack_300,local_308);
      if (cVar1 != '\0') {
        FUN_00498680(*(undefined4 *)(param_1 + 0x10),DAT_004eb4a0 + param_2 * 0x3c);
      }
    }
    iVar2 = FUN_004e9fd6();
    if (((int)uVar4 < iVar2) && (iVar2 = FUN_004e9eb8(auStack_8a8,uVar4 & 0xffff), iVar2 != 0)) {
      if (local_774 == 1) {
        FUN_00498680(*(undefined4 *)(param_1 + 0x1c),DAT_004eb494);
      }
      else if (local_774 == 2) {
        FUN_00498680(*(undefined4 *)(param_1 + 0x1c),DAT_004eb498);
      }
      else {
        FUN_00498680(*(undefined4 *)(param_1 + 0x1c),DAT_004eb49c);
      }
      FUN_0043f4c0(*(undefined4 *)(param_1 + 0x20),0xe4,0x1e);
      FUN_00499678(*(undefined4 *)(param_1 + 0x20),1);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x20),auStack_8a8);
      FUN_0043f4c0(*(undefined4 *)(param_1 + 0x24),0xf0,0x1c);
      FUN_00499678(*(undefined4 *)(param_1 + 0x24),1);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x24),auStack_828);
      FUN_004ecee8(SUB84((double)local_79c,0),auStack_8c8,0x20);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x2c),auStack_8c8);
      uVar6 = (undefined4)((ulonglong)(double)local_79c >> 0x20);
      FUN_004ecf3c(SUB84((double)local_79c,0),uVar6,SUB84((double)local_7a0,0),auStack_8e8,0x20);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x30),auStack_8e8);
      cVar1 = FUN_004ff4c0(local_798,uVar6,local_76c,uVar4,auStack_768,local_770);
      if (cVar1 != '\0') {
        FUN_00498680(*(undefined4 *)(param_1 + 0x28),DAT_004eb4a0 + uVar4 * 0x14);
      }
    }
    iVar2 = FUN_004e9fd6();
    if (((int)uVar3 < iVar2) && (iVar2 = FUN_004e9eb8(auStack_d10,uVar3 & 0xffff), iVar2 != 0)) {
      if (local_bdc == 1) {
        FUN_00498680(*(undefined4 *)(param_1 + 0x34),DAT_004eb494);
      }
      else if (local_bdc == 2) {
        FUN_00498680(*(undefined4 *)(param_1 + 0x34),DAT_004eb498);
      }
      else {
        FUN_00498680(*(undefined4 *)(param_1 + 0x34),DAT_004eb49c);
      }
      FUN_0043f4c0(*(undefined4 *)(param_1 + 0x38),0xe4,0x1e);
      FUN_00499678(*(undefined4 *)(param_1 + 0x38),1);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x38),auStack_d10);
      FUN_0043f4c0(*(undefined4 *)(param_1 + 0x3c),0xf0,0x1c);
      FUN_00499678(*(undefined4 *)(param_1 + 0x3c),1);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x3c),auStack_c90);
      FUN_004ecee8(SUB84((double)local_c04,0),auStack_d30,0x20);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x44),auStack_d30);
      uVar6 = (undefined4)((ulonglong)(double)local_c04 >> 0x20);
      FUN_004ecf3c(SUB84((double)local_c04,0),uVar6,SUB84((double)local_c08,0),&local_d50,0x20);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x48),&local_d50);
      cVar1 = FUN_004ff4c0(local_c00,uVar6,local_bd4,uVar3,auStack_bd0,local_bd8);
      if (cVar1 != '\0') {
        FUN_00498680(*(undefined4 *)(param_1 + 0x40),DAT_004eb4a0 + uVar3 * 0x14);
      }
    }
    FUN_004ed058(param_1,param_2);
    *(undefined1 *)(param_1 + 0x5c) = 1;
  }
  return;
}

