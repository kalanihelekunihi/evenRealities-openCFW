
void FUN_1000a080(uint param_1,int param_2)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  uint uVar7;
  
  uVar2 = FUN_1000a05c(param_2);
  uVar3 = FUN_1000a034(param_2);
  iVar4 = FUN_1000324c();
  if (param_2 == 1) {
    bVar1 = *(byte *)(iVar4 + 5) >> 3;
    if (((param_1 & 9) == 0) && ((bVar1 & 1) != 0)) {
      uVar7 = (uVar3 >> 8) << 7;
    }
    else {
      uVar7 = uVar3 & 0xffffff80;
    }
    if ((param_1 & 8) == 0) {
      *(uint *)(iVar4 + 0x7c) = uVar2 & 0xffffff8;
      uVar3 = bVar1 & 1;
      if ((bVar1 & 1) != 0) {
        uVar3 = (uVar2 & 0xffffff8) + uVar7;
      }
      *(uint *)(iVar4 + 0x80) = uVar3;
      *(uint *)(iVar4 + 0x84) = uVar7;
      *(undefined4 *)(iVar4 + 0x8c) = 0;
      uVar6 = 0x100;
    }
    else {
      *(uint *)(iVar4 + 0xe0) = uVar3;
      *(uint *)(iVar4 + 0x84) = uVar7;
      *(uint *)(iVar4 + 0x7c) = uVar2 & 0xffffff8;
      *(uint *)(iVar4 + 0xdc) = uVar2 & 0xffffff8;
      *(uint *)(iVar4 + 0xe4) = uVar3 >> 3;
      gx_audio_in_set_logfbank_enable(1);
      FUN_1000568c(1,*(undefined4 *)(iVar4 + 0xdc),*(undefined4 *)(iVar4 + 0xe0),
                   *(undefined4 *)(iVar4 + 0xe4),*(undefined4 *)(iVar4 + 0xe8),
                   *(undefined4 *)(iVar4 + 0xec));
      uVar6 = 0x400;
    }
    *(undefined4 *)(iVar4 + 0x88) = uVar6;
    FUN_100054cc(1,*(undefined4 *)(iVar4 + 0x7c),*(undefined4 *)(iVar4 + 0x80),
                 *(undefined4 *)(iVar4 + 0x84),uVar6,*(undefined4 *)(iVar4 + 0x8c),
                 *(undefined4 *)(iVar4 + 0x90));
    return;
  }
  if (param_2 != 2) {
    if (param_2 == 4) {
      *(uint *)(iVar4 + 0xac) = uVar2 & 0xffffff8;
      *(uint *)(iVar4 + 0xb0) = uVar3;
      *(undefined4 *)(iVar4 + 0xb4) = 1;
      gx_audio_in_set_logfbank_enable(1);
      FUN_100055e0(*(undefined4 *)(iVar4 + 0xac),*(undefined4 *)(iVar4 + 0xb0),
                   *(undefined4 *)(iVar4 + 0xb4),*(undefined4 *)(iVar4 + 0xb8),
                   *(undefined4 *)(iVar4 + 0xbc));
    }
    else if (param_2 == 8) {
      FUN_10005794(*(undefined4 *)(iVar4 + 0xc0),*(undefined4 *)(iVar4 + 0xc4),
                   *(undefined4 *)(iVar4 + 200),*(undefined4 *)(iVar4 + 0xcc),
                   *(undefined4 *)(iVar4 + 0xd0),*(undefined4 *)(iVar4 + 0xd4),
                   *(undefined4 *)(iVar4 + 0xd8));
      gx_audio_in_set_i2sout_mode(0);
    }
    return;
  }
  bVar1 = *(byte *)(iVar4 + 0x21) >> 3;
  uVar7 = bVar1 & 1;
  if ((param_1 & 1) == 0) {
    if ((bVar1 & 1) == 0) {
      uVar5 = FUN_10009f5c();
      if ((int)uVar5 < 0) {
        uVar5 = uVar5 + 0x3f;
      }
      uVar5 = uVar5 & 0xffffffc0;
      *(uint *)(iVar4 + 0x9c) = uVar3 & 0xffffff80;
      *(uint *)(iVar4 + 0x94) = uVar2 & 0xffffff8;
      goto LAB_1000a152;
    }
    uVar3 = (uVar3 >> 8) << 7;
    uVar5 = FUN_10009f5c();
    if ((int)uVar5 < 0) {
      uVar5 = uVar5 + 0x3f;
    }
    uVar5 = uVar5 & 0xffffffc0;
    *(uint *)(iVar4 + 0x9c) = uVar3;
    *(uint *)(iVar4 + 0x94) = uVar2 & 0xffffff8;
  }
  else {
    uVar3 = uVar3 & 0xffffff80;
    uVar5 = FUN_10009f5c();
    if ((int)uVar5 < 0) {
      uVar5 = uVar5 + 0x3f;
    }
    uVar5 = uVar5 & 0xffffffc0;
    *(uint *)(iVar4 + 0x9c) = uVar3;
    *(uint *)(iVar4 + 0x94) = uVar2 & 0xffffff8;
    if ((bVar1 & 1) == 0) goto LAB_1000a152;
  }
  uVar7 = uVar3 + (uVar2 & 0xffffff8);
LAB_1000a152:
  *(undefined4 *)(iVar4 + 0xa4) = 0;
  *(uint *)(iVar4 + 0x98) = uVar7;
  *(uint *)(iVar4 + 0xa0) = uVar5;
  FUN_100054cc(2,*(undefined4 *)(iVar4 + 0x94),*(undefined4 *)(iVar4 + 0x98),
               *(undefined4 *)(iVar4 + 0x9c),uVar5,*(undefined4 *)(iVar4 + 0xa4),
               *(undefined4 *)(iVar4 + 0xa8));
  return;
}

