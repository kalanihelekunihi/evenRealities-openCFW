
char FUN_005598cc(char *param_1)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  if (param_1 == (char *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00559fb0,DAT_00559fac,DAT_0055a208,0x76,DAT_0055a204);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055a20c,DAT_0055a20c);
    }
    return '\x01';
  }
  if ((*param_1 == '\0') || (*param_1 == '\x01')) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00559fb0,DAT_00559fac,DAT_0055a208,0x7c,DAT_00559fa8,*param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00559fb4,DAT_00559fb4,*param_1);
    }
    return '\x03';
  }
  iVar2 = FUN_00559836(*param_1);
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00559fb0,DAT_00559fac,DAT_0055a208,0x83,DAT_00559fa8,*param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00559fb4,DAT_00559fb4,*param_1);
    }
    return '\x03';
  }
  health_lock_storage();
  cVar1 = FUN_00559d82(param_1,iVar2);
  if (cVar1 != '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00559fb0,DAT_00559fac,DAT_0055a208,0x8c,DAT_0055a210);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055a214,DAT_0055a214);
    }
    health_unlock_storage();
    return cVar1;
  }
  health_unlock_storage();
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar3 = FUN_00559854(*param_1);
    FUN_0043d574(4,DAT_00559fb0,DAT_00559fac,DAT_0055a208,0x96,DAT_0055a218,uVar3,
                 *(undefined4 *)(param_1 + 4),(double)*(float *)(param_1 + 8),
                 (double)*(float *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x10),param_1[0x15]);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    uVar3 = FUN_00559854(*param_1);
    compress_log_output(0x11800000,DAT_0055a2b0,DAT_0055a2b0,uVar3,*(undefined4 *)(param_1 + 4));
  }
  return '\0';
}

