
undefined4 FUN_0044cd9e(undefined4 param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0044b88e(param_1,0);
  if (iVar1 == 0) {
    iVar1 = FUN_0044b87a(param_1,0);
    if (iVar1 == 0x100) {
      iVar1 = FUN_0044b884(param_1,0);
      if (iVar1 == 0x100) {
        iVar1 = FUN_0044b898(param_1,0);
        if (iVar1 == 0) {
          iVar1 = FUN_0044b8a2(param_1,0);
          if (iVar1 == 0) {
            iVar1 = FUN_0044b8c4(param_1,0);
            if (iVar1 == 0xff) {
              iVar1 = FUN_0044b902(param_1,0);
              if (iVar1 == 0) {
                iVar1 = FUN_0044b8ea(param_1,0);
                if (iVar1 == 0) {
                  uVar2 = 0;
                }
                else {
                  uVar2 = 1;
                }
              }
              else {
                uVar2 = 1;
              }
            }
            else {
              uVar2 = 1;
            }
          }
          else {
            uVar2 = 2;
          }
        }
        else {
          uVar2 = 2;
        }
      }
      else {
        uVar2 = 2;
      }
    }
    else {
      uVar2 = 2;
    }
  }
  else {
    uVar2 = 2;
  }
  return uVar2;
}

