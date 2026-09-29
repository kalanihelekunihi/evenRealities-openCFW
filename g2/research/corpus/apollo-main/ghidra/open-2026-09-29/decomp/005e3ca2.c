
undefined4 smprActSendKey(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  if ((*(char *)(param_1 + 0x3f) == '\0') &&
     (iVar1 = smpSendKey(param_1,*(byte *)(param_1 + 0x2d) & *(byte *)(param_1 + 0x26)), iVar1 != 0)
     ) {
    *(undefined1 *)(param_1 + 0x3f) = 0;
    uVar2 = (uint)(*(byte *)(param_1 + 0x2c) & *(byte *)(param_1 + 0x25));
    if ((int)(uVar2 << 0x1f) < 0) {
      if ((*(char *)(DAT_005e3d48 + 0xf8) == '\0') || (**(char **)(param_1 + 0x48) == '\0')) {
        *(undefined1 *)(param_1 + 0x3f) = 6;
      }
      else if ((int)(uVar2 << 0x1e) < 0) {
        *(undefined1 *)(param_1 + 0x3f) = 8;
      }
    }
    else if ((int)(uVar2 << 0x1e) < 0) {
      *(undefined1 *)(param_1 + 0x3f) = 8;
    }
    else if ((int)(uVar2 << 0x1d) < 0) {
      *(undefined1 *)(param_1 + 0x3f) = 10;
    }
    if (*(char *)(param_1 + 0x3f) == '\0') {
      *(undefined1 *)(param_2 + 2) = 0xe;
      smpSmExecute(param_1,param_2);
    }
  }
  return param_4;
}

