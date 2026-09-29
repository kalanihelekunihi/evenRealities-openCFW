
undefined8 FUN_005b7060(int param_1,int param_2,undefined4 param_3,int param_4)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  
  if (*(char *)(DAT_005b7604 + 0x98) == '\0') {
    if (param_1 != 10) {
      if (param_1 == 0x48) {
        FUN_005b02e4(10,0);
      }
      else if (((param_1 == 0x44) || (param_1 == 0x45)) && (*(int *)(DAT_005b7604 + 0x28) != 0)) {
        iVar2 = (*(undefined4 **)(param_2 + 0x10))[1];
        if (param_1 == 0x44) {
          iVar2 = -iVar2;
        }
        iVar2 = FUN_005b6a7e(iVar2,**(undefined4 **)(param_2 + 0x10));
        iVar3 = FUN_005b6a52();
        if (iVar2 != iVar3) {
          if (param_1 == 0x44) {
            uVar1 = 0xe;
          }
          else {
            uVar1 = 0xf;
          }
          FUN_005b02e4(uVar1,iVar2);
        }
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x132;
      param_3 = DAT_005b7650;
      param_4 = param_1;
      FUN_0043d574(3,PTR_s_conversate_prep_005b7614,DAT_005b7610,DAT_005b7654,0x132,DAT_005b7650,
                   param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_005b7658,DAT_005b7658,param_1,param_2,param_3,param_4);
    }
  }
  return CONCAT44(param_3,param_2);
}

