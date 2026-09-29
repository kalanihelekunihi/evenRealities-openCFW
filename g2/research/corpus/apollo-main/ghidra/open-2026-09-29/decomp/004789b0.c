
void FUN_004789b0(undefined4 param_1,byte param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 *puVar4;
  
  puVar4 = (undefined1 *)(DAT_004793f0 + (uint)param_2 * 0x100);
  if (puVar4 == (undefined1 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00479574,DAT_00479570,DAT_0047956c,0xb5,DAT_004793f4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004793f8,DAT_004793f8);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xb9,DAT_004793fc,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00479400,DAT_00479400,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xbd,DAT_00479404,puVar4[5],puVar4[4],
                   puVar4[3],puVar4[2],puVar4[1],*puVar4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x11800000,DAT_00479408,DAT_00479408,puVar4[5],puVar4[4],puVar4[3],
                          puVar4[2],puVar4[1],*puVar4);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = DAT_0047940c;
      if ((puVar4[6] != '\0') && (uVar3 = DAT_00479414, puVar4[6] == '\x01')) {
        uVar3 = DAT_00479410;
      }
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xc1,DAT_00479578,uVar3,puVar4[6]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar3 = DAT_0047940c;
      if ((puVar4[6] != '\0') && (uVar3 = DAT_00479414, puVar4[6] == '\x01')) {
        uVar3 = DAT_00479410;
      }
      compress_log_output(0x10800000,DAT_0047957c,DAT_0047957c,uVar3,puVar4[6]);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = DAT_00479584;
      if (puVar4[0x2f] != '\0') {
        uVar3 = DAT_00479580;
      }
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xc2,DAT_00479588,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar3 = DAT_00479584;
      if (puVar4[0x2f] != '\0') {
        uVar3 = DAT_00479580;
      }
      compress_log_output(0x10400000,DAT_0047958c,DAT_0047958c,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = DAT_00479584;
      if (puVar4[0x30] != '\0') {
        uVar3 = DAT_00479580;
      }
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xc3,DAT_00479590,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar3 = DAT_00479584;
      if (puVar4[0x30] != '\0') {
        uVar3 = DAT_00479580;
      }
      compress_log_output(0x10400000,DAT_00479594,DAT_00479594,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xc4,DAT_00479598,
                   *(undefined4 *)(puVar4 + 0xc4));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0047959c,DAT_0047959c,*(undefined4 *)(puVar4 + 0xc4));
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xc5,DAT_004795a0,puVar4[0x2e]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004795a4,DAT_004795a4,puVar4[0x2e]);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = DAT_00479584;
      if (puVar4[0x31] != '\0') {
        uVar3 = DAT_00479580;
      }
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xc6,DAT_004795a8,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar3 = DAT_00479584;
      if (puVar4[0x31] != '\0') {
        uVar3 = DAT_00479580;
      }
      compress_log_output(0x10400000,DAT_004795ac,DAT_004795ac,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = DAT_00479584;
      if (puVar4[0x32] != '\0') {
        uVar3 = DAT_00479580;
      }
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,199,DAT_004795b0,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar3 = DAT_00479584;
      if (puVar4[0x32] != '\0') {
        uVar3 = DAT_00479580;
      }
      compress_log_output(0x10400000,DAT_004795b4,DAT_004795b4,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,200,DAT_004795b8,puVar4[0x2e]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004795bc,DAT_004795bc,puVar4[0x2e]);
    }
    FUN_0043dacc(DAT_004795c0,0x10,puVar4 + 7,0x10);
    FUN_0043dacc(DAT_004795c4,0x10,puVar4 + 0x1e,0x10);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xd0,DAT_004795c8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004795cc,DAT_004795cc);
    }
    FUN_0043dacc(DAT_004795d0,0x10,puVar4 + 0x34,0x10);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xd3,DAT_004795d4,puVar4[0x4e]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004795d8,DAT_004795d8,puVar4[0x4e]);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = DAT_00479988;
      if (puVar4[0x4f] != '\0') {
        uVar3 = DAT_00479984;
      }
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xd4,DAT_0047998c,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar3 = DAT_00479988;
      if (puVar4[0x4f] != '\0') {
        uVar3 = DAT_00479984;
      }
      compress_log_output(0x10400000,DAT_00479990,DAT_00479990,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xd7,DAT_00479994);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00479998,DAT_00479998);
    }
    FUN_0043dacc(DAT_0047999c,0x10,puVar4 + 0x50,0x10);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xd9,DAT_004799a0,puVar4[0x6a]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004799a4,DAT_004799a4,puVar4[0x6a]);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xdc,DAT_00479ab4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00479ab8,DAT_00479ab8);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xdd,DAT_00479abc,
                   *(undefined4 *)(puVar4 + 0x80));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00479ac0,DAT_00479ac0,*(undefined4 *)(puVar4 + 0x80));
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xde,DAT_00479ac4,puVar4[0x84]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00479ac8,DAT_00479ac8,puVar4[0x84]);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xe0,DAT_00479acc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00479ad0,DAT_00479ad0);
    }
    for (iVar1 = 0; iVar1 < 10; iVar1 = iVar1 + 1) {
      if (*(short *)(puVar4 + iVar1 * 2 + 0x6c) != 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xe3,DAT_00479ad4,iVar1,
                       *(undefined2 *)(puVar4 + iVar1 * 2 + 0x6c));
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_00479ad8,DAT_00479ad8,iVar1,
                              *(undefined2 *)(puVar4 + iVar1 * 2 + 0x6c));
        }
      }
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xe7,DAT_00479adc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00479ae0,DAT_00479ae0);
    }
    for (iVar1 = 0; iVar1 < 1; iVar1 = iVar1 + 1) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xe9,DAT_00479ae4,puVar4[iVar1 + 0x85]
                    );
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00479ae8,DAT_00479ae8,puVar4[iVar1 + 0x85]);
      }
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xed,DAT_00479aec);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00479af0,DAT_00479af0);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = DAT_00479584;
      if (puVar4[0x86] != '\0') {
        uVar3 = DAT_00479580;
      }
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xee,DAT_00479af4,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar3 = DAT_00479584;
      if (puVar4[0x86] != '\0') {
        uVar3 = DAT_00479580;
      }
      compress_log_output(0x10400000,DAT_00479af8,DAT_00479af8,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xf2,DAT_00479afc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00479b00,DAT_00479b00);
    }
    for (iVar1 = 0; iVar1 < 0x15; iVar1 = iVar1 + 1) {
      if (*(short *)(puVar4 + iVar1 * 2 + 0x98) != 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xf5,DAT_00479b04,
                       *(undefined2 *)(puVar4 + iVar1 * 2 + 0x98));
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00479b08,DAT_00479b08,
                              *(undefined2 *)(puVar4 + iVar1 * 2 + 0x98));
        }
      }
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xf9,DAT_00479b0c,puVar4[0xc2]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00479b10,DAT_00479b10,puVar4[0xc2]);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = DAT_00479584;
      if (puVar4[0xc3] != '\0') {
        uVar3 = DAT_00479580;
      }
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xfa,DAT_00479b14,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar3 = DAT_00479584;
      if (puVar4[0xc3] != '\0') {
        uVar3 = DAT_00479580;
      }
      compress_log_output(0x10400000,DAT_00479b18,DAT_00479b18,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_0047956c,0xfb,DAT_00479b1c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00479b20,DAT_00479b20);
    }
  }
  return;
}

