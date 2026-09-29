
undefined4 FUN_004c91e0(undefined4 param_1,int param_2,uint *param_3)

{
  undefined4 uVar1;
  int iVar2;
  short local_50 [2];
  int local_4c;
  uint local_48;
  undefined1 auStack_44 [18];
  undefined1 auStack_32 [4];
  undefined1 auStack_2e [6];
  undefined1 auStack_28 [28];
  
  if (*(char *)(param_2 + 0x10) == '\x01') {
    uVar1 = FUN_004c70e4(*(undefined4 *)(param_2 + 0xc));
    iVar2 = FUN_004547be(uVar1,&DAT_004c9480);
    if (iVar2 == 0) {
      FUN_004c6f46(param_2 + 0x14,auStack_44,0x36,0);
      FUN_00454738(&local_48,auStack_32,4);
      FUN_00454738(&local_4c,auStack_2e,4);
      param_3[1] = param_3[1] & 0xffff0000 | local_48 & 0xffff;
      param_3[1] = param_3[1] & 0xffff | local_4c << 0x10;
      FUN_00454738(local_50,auStack_28,2);
      if (local_50[0] == 0x10) {
        *param_3 = *param_3 & 0xffff00ff | 0x1200;
      }
      else if (local_50[0] == 0x18) {
        *param_3 = *param_3 & 0xffff00ff | 0xf00;
      }
      else {
        if (local_50[0] != 0x20) {
          FUN_0044d25c(2,DAT_004c948c,0x7e,DAT_004c9488,DAT_004c9484,local_50[0]);
          return 1;
        }
        *param_3 = *param_3 & 0xffff00ff | 0x1000;
      }
      return 1;
    }
  }
  else if (*(char *)(param_2 + 0x10) == '\0') {
    return 0;
  }
  return 0;
}

