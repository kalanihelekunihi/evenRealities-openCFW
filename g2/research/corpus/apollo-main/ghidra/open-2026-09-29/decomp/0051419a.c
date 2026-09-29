
undefined8 FUN_0051419a(byte param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  iVar1 = FUN_0047f90c(0x14,&local_18);
  if (iVar1 == 0) {
    if (param_1 == 0) {
      if ((char)local_18 == '\0') {
        iVar1 = FUN_0047f5b8(0x14);
        if ((iVar1 == 0) && (param_2 != '\0')) {
          FUN_004b128a();
          FUN_00514184();
          FUN_004b11b0();
          iVar2 = FUN_004b128a();
          if (iVar2 == 0) {
            if (*DAT_00514274 != 0) {
              FUN_0051564c();
              FUN_005224b6();
              iVar2 = FUN_0051564c();
              if (iVar2 != 0) {
                iVar1 = 1;
              }
            }
          }
          else {
            iVar1 = 1;
          }
        }
      }
      else {
        iVar1 = 0;
      }
    }
    else if ((param_1 == 2) || (param_1 < 2)) {
      if ((char)local_18 == '\0') {
        iVar1 = 0;
      }
      else {
        iVar1 = FUN_0051403c(0xfc);
        if (iVar1 == 0) {
          iVar1 = FUN_0047f7ae(0x14);
        }
        else {
          iVar1 = 3;
        }
      }
    }
    else {
      iVar1 = 7;
    }
  }
  return CONCAT44(local_18,iVar1);
}

