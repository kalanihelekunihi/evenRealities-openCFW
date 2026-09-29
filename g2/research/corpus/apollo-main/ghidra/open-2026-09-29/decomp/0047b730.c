
char FUN_0047b730(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  char cVar4;
  
  iVar3 = DAT_0047c158;
  cVar4 = '\x01';
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x779,DAT_0047c15c,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047c160,DAT_0047c160);
  }
  FUN_00475014(0,1);
  iVar1 = 0;
  do {
    if (9 < iVar1) {
LAB_0047bb64:
      if (cVar4 == '\0') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x7c4,DAT_0047c538);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0047c8a4,DAT_0047c8a4);
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x7c2,DAT_0047c530);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0047c534,DAT_0047c534);
        }
      }
      return cVar4;
    }
    iVar2 = FUN_004d294a(param_1,iVar3);
    if ((iVar2 != 0) && (*(char *)(param_1 + 6) == *(char *)(iVar3 + 6))) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x782,DAT_0047c280,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0047c284,DAT_0047c284,iVar1);
      }
      if (*(char *)(param_1 + 0x30) != *(char *)(iVar3 + 0x30)) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x787,DAT_0047c288,
                       *(undefined1 *)(param_1 + 0x30),*(undefined1 *)(iVar3 + 0x30));
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_0047c28c,DAT_0047c28c,*(undefined1 *)(param_1 + 0x30),
                              *(undefined1 *)(iVar3 + 0x30));
        }
        cVar4 = '\0';
      }
      if (*(char *)(param_1 + 0x2f) != *(char *)(iVar3 + 0x2f)) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x78d,DAT_0047c290,
                       *(undefined1 *)(param_1 + 0x2f),*(undefined1 *)(iVar3 + 0x2f));
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_0047c294,DAT_0047c294,*(undefined1 *)(param_1 + 0x2f),
                              *(undefined1 *)(iVar3 + 0x2f));
        }
        cVar4 = '\0';
      }
      if (*(char *)(param_1 + 0x2e) != *(char *)(iVar3 + 0x2e)) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x793,DAT_0047c298,
                       *(undefined1 *)(param_1 + 0x2e),*(undefined1 *)(iVar3 + 0x2e));
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_0047c29c,DAT_0047c29c,*(undefined1 *)(param_1 + 0x2e),
                              *(undefined1 *)(iVar3 + 0x2e));
        }
        cVar4 = '\0';
      }
      if ((int)((uint)*(byte *)(param_1 + 0x2e) << 0x1f) < 0) {
        iVar1 = FUN_004751c8(param_1 + 0x34,iVar3 + 0x34,0x10);
        if (iVar1 == 0) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x79f,DAT_0047c2b0);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0047c2b4,DAT_0047c2b4);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x79a,DAT_0047c2a0);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_0047c2a4,DAT_0047c2a4);
          }
          FUN_0043dacc(DAT_0047c2a8,0x10,param_1 + 0x34,0x10);
          FUN_0043dacc(DAT_0047c2ac,0x10,iVar3 + 0x34,0x10);
          cVar4 = '\0';
        }
      }
      if ((int)((uint)*(byte *)(param_1 + 0x2e) << 0x1d) < 0) {
        iVar1 = FUN_004751c8(param_1 + 7,iVar3 + 7,0x10);
        if (iVar1 == 0) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x7ab,DAT_0047c510);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0047c514,DAT_0047c514);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x7a6,DAT_0047c2b8);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_0047c504,DAT_0047c504);
          }
          FUN_0043dacc(DAT_0047c508,0x10,param_1 + 7,0x10);
          FUN_0043dacc(DAT_0047c50c,0x10,iVar3 + 7,0x10);
          cVar4 = '\0';
        }
      }
      if ((int)((uint)*(byte *)(param_1 + 0x2e) << 0x1c) < 0) {
        iVar1 = FUN_004751c8(param_1 + 0x1e,iVar3 + 0x1e,0x10);
        if (iVar1 == 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x7b7,DAT_0047c528);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0047c52c,DAT_0047c52c);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0047bc24,DAT_0047bc20,DAT_0047c27c,0x7b2,DAT_0047c518);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_0047c51c,DAT_0047c51c);
          }
          FUN_0043dacc(DAT_0047c520,0x10,param_1 + 0x1e,0x10);
          FUN_0043dacc(DAT_0047c524,0x10,iVar3 + 0x1e,0x10);
          cVar4 = '\0';
        }
      }
      goto LAB_0047bb64;
    }
    iVar3 = iVar3 + 0x100;
    iVar1 = iVar1 + 1;
  } while( true );
}

