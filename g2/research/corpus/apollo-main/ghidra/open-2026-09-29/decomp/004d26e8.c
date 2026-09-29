
void dmPrivHciHandler(undefined2 *param_1)

{
  byte bVar1;
  int iVar2;
  undefined1 uVar3;
  
  bVar1 = *(byte *)(param_1 + 1);
  if (bVar1 == 0x15) {
    *(undefined1 *)(param_1 + 1) = 0x3a;
    iVar2 = DAT_004d2920;
    *param_1 = *(undefined2 *)(DAT_004d2920 + 4);
    if (((*(char *)((int)param_1 + 3) == '\0') && (*(char *)(iVar2 + 8) != '\0')) &&
       (*(char *)(DAT_004d2924 + 0x16) == '\0')) {
      dmPrivSetAddrResEnable(1);
    }
  }
  else {
    if (bVar1 < 0x15) {
      return;
    }
    if (bVar1 == 0x17) {
      *(undefined1 *)(param_1 + 1) = 0x3c;
      if ((*(char *)((int)param_1 + 3) == '\0') && (*(char *)(DAT_004d2924 + 0x16) != '\0')) {
        dmPrivSetAddrResEnable(0);
      }
    }
    else if (bVar1 < 0x17) {
      *(undefined1 *)(param_1 + 1) = 0x3b;
      *param_1 = *(undefined2 *)(DAT_004d2920 + 6);
    }
    else if (bVar1 == 0x19) {
      *(undefined1 *)(param_1 + 1) = 0x3e;
    }
    else if (bVar1 < 0x19) {
      *(undefined1 *)(param_1 + 1) = 0x3d;
    }
    else {
      if (bVar1 != 0x1a) {
        return;
      }
      *(undefined1 *)(param_1 + 1) = 0x3f;
      iVar2 = DAT_004d2924;
      if (*(char *)((int)param_1 + 3) == '\0') {
        *(undefined1 *)(DAT_004d2924 + 0x16) = *(undefined1 *)(DAT_004d2920 + 9);
        if (*(char *)(iVar2 + 0x16) == '\0') {
          uVar3 = 0xc;
        }
        else {
          uVar3 = 0xd;
        }
        dmDevPassEvtToDevPriv(uVar3,*(char *)(iVar2 + 0x16) != '\0',0,0);
      }
    }
  }
  (**(code **)(DAT_004d2924 + 8))(param_1);
  return;
}

