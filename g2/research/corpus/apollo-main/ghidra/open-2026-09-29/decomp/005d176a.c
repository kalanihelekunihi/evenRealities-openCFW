
undefined4 FUN_005d176a(undefined4 *param_1,undefined4 *param_2,char param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  FUN_0043c0e4(param_1,0x3c,0);
  if (param_3 == '\0') {
    *param_1 = *param_2;
    param_1[1] = param_2[1];
    param_1[2] = param_2[2];
    param_1[3] = param_2[3];
    param_1[4] = param_2[4];
    param_1[5] = param_2[5];
    param_1[6] = param_2 + 6;
    param_1[7] = param_2 + 7;
    param_1[8] = param_2 + 8;
    param_1[9] = param_2 + 10;
    param_1[10] = param_2 + 0xc;
    *(undefined1 *)(param_1 + 0xb) = *(undefined1 *)(param_2 + 0x10);
    *(undefined1 *)((int)param_1 + 0x2d) = *(undefined1 *)((int)param_2 + 0x41);
    *(undefined1 *)((int)param_1 + 0x2e) = *(undefined1 *)((int)param_2 + 0x42);
    *(undefined1 *)((int)param_1 + 0x2f) = *(undefined1 *)((int)param_2 + 0x43);
  }
  else {
    *param_1 = *param_2;
    param_1[1] = param_2[1];
    param_1[2] = param_2[2];
    param_1[3] = param_2[3];
    param_1[4] = param_2[4];
    param_1[5] = param_2[5];
    param_1[6] = param_2 + 6;
    param_1[7] = param_2 + 7;
    param_1[8] = param_2 + 8;
    param_1[9] = param_2 + 10;
    param_1[10] = param_2 + 0xc;
    *(undefined1 *)(param_1 + 0xb) = 0;
    *(undefined1 *)((int)param_1 + 0x2d) = *(undefined1 *)((int)param_2 + 0x41);
    *(undefined1 *)((int)param_1 + 0x2e) = *(undefined1 *)((int)param_2 + 0x42);
    *(undefined1 *)((int)param_1 + 0x2f) = *(undefined1 *)((int)param_2 + 0x43);
  }
  *(char *)(param_1 + 0xc) = param_3;
  uVar1 = DAT_005d213c[1];
  param_1[0xd] = *DAT_005d213c;
  param_1[0xe] = uVar1;
  return param_4;
}

