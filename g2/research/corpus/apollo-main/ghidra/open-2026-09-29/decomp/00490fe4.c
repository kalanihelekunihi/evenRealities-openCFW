
undefined8 FUN_00490fe4(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  char *pcVar3;
  uint uVar4;
  char *pcVar5;
  
  uVar2 = 0;
  pcVar3 = *(char **)(param_2 + 0x1c);
  if ((*(byte *)(param_2 + 0x16) & 0xc0) == 0x80) {
    uVar4 = 0xffffffff;
  }
  else {
    if (*(ushort *)(param_2 + 0x12) == 0) {
      uVar1 = DAT_004910dc;
      if (*(int *)(param_1 + 0x10) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0x10);
      }
      *(undefined4 *)(param_1 + 0x10) = uVar1;
      uVar1 = 0;
      goto LAB_00491020;
    }
    uVar4 = *(ushort *)(param_2 + 0x12) - 1;
  }
  pcVar5 = pcVar3;
  if (pcVar3 == (char *)0x0) {
    uVar2 = 0;
  }
  else {
    for (; (uVar2 < uVar4 && (*pcVar5 != '\0')); pcVar5 = pcVar5 + 1) {
      uVar2 = uVar2 + 1;
    }
    if (*pcVar5 != '\0') {
      uVar1 = DAT_004910e0;
      if (*(int *)(param_1 + 0x10) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0x10);
      }
      *(undefined4 *)(param_1 + 0x10) = uVar1;
      uVar1 = 0;
      goto LAB_00491020;
    }
  }
  uVar1 = FUN_00490db6(param_1,pcVar3,uVar2);
LAB_00491020:
  return CONCAT44(param_4,uVar1);
}

