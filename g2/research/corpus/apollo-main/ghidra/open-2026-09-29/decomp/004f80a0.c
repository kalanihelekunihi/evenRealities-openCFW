
void FUN_004f80a0(char param_1,char param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = -1;
  if (param_2 == '\x02') {
    if (param_1 == '\0') {
      iVar2 = 0;
    }
    else {
      iVar2 = param_3 + -1;
    }
  }
  else if (param_2 == '\x03') {
    if (param_1 == '\0') {
      iVar2 = (uint)*DAT_004f8628 - param_3;
      if (iVar2 < 0) {
        iVar2 = 0;
      }
    }
    else {
      iVar2 = *DAT_004f8628 - 1;
    }
  }
  if (((iVar2 < 0) || ((int)(uint)*DAT_004f8628 <= iVar2)) ||
     (*(int *)(DAT_004f8638 + iVar2 * 0x10) == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004f81e0,DAT_004f81dc,DAT_004f88f0,0xba1,DAT_004f88f8,iVar2,param_2,param_3
                  );
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8c00000,DAT_004f88fc,DAT_004f88fc,iVar2,param_2,param_3);
    }
  }
  else {
    FUN_00441488(*(undefined4 *)(DAT_004f8638 + iVar2 * 0x10),0,0);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f81e0,DAT_004f81dc,DAT_004f88f0,0xb9e,DAT_004f88ec,iVar2,param_2,param_1
                   ,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x11000000,DAT_004f88f4,DAT_004f88f4,iVar2,param_2,param_1,param_3);
    }
  }
  FUN_004f74f8(0,100,DAT_004f8900);
  return;
}

