
undefined4 ui_onboarding_stock_sub_0050E534(void)

{
  int iVar1;
  undefined4 in_r3;
  int iVar2;
  int *piVar3;
  
  for (iVar2 = 0; iVar1 = DAT_0050e928, iVar2 < 3; iVar2 = iVar2 + 1) {
    piVar3 = (int *)(DAT_0050e928 + iVar2 * 0x60);
    if (piVar3[1] != 0) {
      FUN_00498680(piVar3[1],0);
      piVar3[1] = 0;
    }
    if (piVar3[2] != 0) {
      FUN_0049942e(piVar3[2],&DAT_0050e71c);
      piVar3[2] = 0;
    }
    if (piVar3[3] != 0) {
      FUN_0049942e(piVar3[3],&DAT_0050e71c);
      piVar3[3] = 0;
    }
    if (piVar3[4] != 0) {
      FUN_00498680(piVar3[4],0);
      piVar3[4] = 0;
    }
    if (piVar3[5] != 0) {
      FUN_0049942e(piVar3[5],&DAT_0050e71c);
      piVar3[5] = 0;
    }
    if (piVar3[6] != 0) {
      FUN_0049942e(piVar3[6],&DAT_0050e71c);
      piVar3[6] = 0;
    }
    if (piVar3[7] != 0) {
      FUN_00498680(piVar3[7],0);
      piVar3[7] = 0;
    }
    if (piVar3[8] != 0) {
      FUN_0049942e(piVar3[8],&DAT_0050e71c);
      piVar3[8] = 0;
    }
    if (piVar3[9] != 0) {
      FUN_0049942e(piVar3[9],&DAT_0050e71c);
      piVar3[9] = 0;
    }
    if (piVar3[10] != 0) {
      FUN_00498680(piVar3[10],0);
      piVar3[10] = 0;
    }
    if (piVar3[0xb] != 0) {
      FUN_0049942e(piVar3[0xb],&DAT_0050e71c);
      piVar3[0xb] = 0;
    }
    if (piVar3[0xc] != 0) {
      FUN_0049942e(piVar3[0xc],&DAT_0050e71c);
      piVar3[0xc] = 0;
    }
    if (piVar3[0xd] != 0) {
      FUN_00498680(piVar3[0xd],0);
      piVar3[0xd] = 0;
    }
    if (piVar3[0xe] != 0) {
      FUN_0049942e(piVar3[0xe],&DAT_0050e71c);
      piVar3[0xe] = 0;
    }
    if (piVar3[0xf] != 0) {
      FUN_0049942e(piVar3[0xf],&DAT_0050e71c);
      piVar3[0xf] = 0;
    }
    if (piVar3[0x10] != 0) {
      FUN_00498680(piVar3[0x10],0);
      piVar3[0x10] = 0;
    }
    if (piVar3[0x11] != 0) {
      FUN_0049942e(piVar3[0x11],&DAT_0050e71c);
      piVar3[0x11] = 0;
    }
    if (piVar3[0x12] != 0) {
      FUN_0049942e(piVar3[0x12],&DAT_0050e71c);
      piVar3[0x12] = 0;
    }
    if (piVar3[0x13] != 0) {
      piVar3[0x13] = 0;
    }
    if (piVar3[0x14] != 0) {
      piVar3[0x14] = 0;
    }
    if (*piVar3 != 0) {
      *piVar3 = 0;
    }
    *(undefined1 *)(piVar3 + 0x17) = 0;
    piVar3[0x15] = 0;
    piVar3[0x16] = 0;
  }
  if (*(int *)(DAT_0050e928 + 0x128) != 0) {
    *(undefined4 *)(DAT_0050e928 + 0x128) = 0;
  }
  if (*DAT_0050e92c != 0) {
    *DAT_0050e92c = 0;
  }
  *DAT_0050e930 = 0;
  *DAT_0050e934 = 0;
  *DAT_0050e938 = 0;
  *DAT_0050e93c = 0;
  *(undefined1 *)(iVar1 + 0x124) = 0;
  *(undefined4 *)(iVar1 + 0x120) = 0;
  *DAT_0050e940 = 0;
  FUN_0043c0e4(DAT_0050e944,0x14,0);
  *DAT_0050e948 = 0;
  return in_r3;
}

