
void Ins_SCANCTRL(int param_1,byte *param_2)

{
  ushort uVar1;
  
  uVar1 = (ushort)*param_2;
  if (uVar1 == 0xff) {
    *(undefined1 *)(param_1 + 0x155) = 1;
  }
  else if (uVar1 == 0) {
    *(undefined1 *)(param_1 + 0x155) = 0;
  }
  else {
    if ((*(int *)param_2 << 0x17 < 0) && (*(ushort *)(param_1 + 0x100) <= uVar1)) {
      *(undefined1 *)(param_1 + 0x155) = 1;
    }
    if ((*(int *)param_2 << 0x16 < 0) && (*(char *)(param_1 + 0x11d) != '\0')) {
      *(undefined1 *)(param_1 + 0x155) = 1;
    }
    if ((*(int *)param_2 << 0x15 < 0) && (*(char *)(param_1 + 0x11e) != '\0')) {
      *(undefined1 *)(param_1 + 0x155) = 1;
    }
    if ((*(int *)param_2 << 0x14 < 0) && (uVar1 < *(ushort *)(param_1 + 0x100))) {
      *(undefined1 *)(param_1 + 0x155) = 0;
    }
    if ((*(int *)param_2 << 0x13 < 0) && (*(char *)(param_1 + 0x11d) != '\0')) {
      *(undefined1 *)(param_1 + 0x155) = 0;
    }
    if ((*(int *)param_2 << 0x12 < 0) && (*(char *)(param_1 + 0x11e) != '\0')) {
      *(undefined1 *)(param_1 + 0x155) = 0;
    }
  }
  return;
}

