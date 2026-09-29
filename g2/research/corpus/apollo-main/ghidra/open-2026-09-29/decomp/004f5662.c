
undefined4 FUN_004f5662(int param_1,int param_2,int *param_3,char param_4)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  if (param_3 == (int *)0x0) {
    uVar2 = 2;
  }
  else {
    if (param_1 == 0) {
      param_1 = DAT_004f61f0;
    }
    *param_3 = 0;
    iVar4 = 0;
    while ((iVar4 < 0x14 && (*param_3 < param_2))) {
      if ((*(char *)(iVar4 * 0xe8 + DAT_004f62f0 + 0xe4) != '\0') &&
         (*(char *)(DAT_004f62f0 + 0x1222) == param_4)) {
        bVar1 = false;
        for (iVar3 = 0; iVar3 < (int)(uint)*DAT_004f5c3c; iVar3 = iVar3 + 1) {
          if (*(int *)(DAT_004f5c3c + iVar3 * 0x94 + 0x8a) == *(int *)(DAT_004f62f0 + iVar4 * 0xe8))
          {
            bVar1 = true;
            break;
          }
        }
        if (!bVar1) {
          FUN_00439c04(*param_3 * 0xe8 + param_1,DAT_004f62f0 + iVar4 * 0xe8,0xe8);
          *param_3 = *param_3 + 1;
        }
      }
      iVar4 = iVar4 + 1;
    }
    uVar2 = 0;
  }
  return uVar2;
}

