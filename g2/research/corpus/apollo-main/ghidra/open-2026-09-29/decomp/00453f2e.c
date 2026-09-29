
undefined8 FUN_00453f2e(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint local_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  uVar2 = 0;
  local_20 = param_2;
  local_1c = param_3;
  uStack_18 = param_4;
  iVar1 = FUN_00450f28(param_1,param_2 + 0x14,0);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043e0e0(param_2,1);
    if (iVar1 == 0) {
      iVar1 = FUN_00452dd8(param_2);
      if (iVar1 == 0) {
        iVar1 = FUN_00453180(param_2,0);
        if (iVar1 < 0xfd) {
          uVar2 = 0;
        }
        else {
          local_20 = local_20 & 0xffffff00;
          local_1c = param_1;
          FUN_00451670(param_2,0x1a,&local_20);
          if ((char)local_20 == '\x02') {
            uVar2 = 0;
          }
          else {
            iVar1 = FUN_0044ddea(param_2);
            do {
              iVar1 = iVar1 + -1;
              if (iVar1 < 0) break;
              uVar2 = FUN_00453f2e(param_1,*(undefined4 *)(**(int **)(param_2 + 8) + iVar1 * 4));
            } while (uVar2 == 0);
            if ((uVar2 == 0) && ((char)local_20 == '\0')) {
              uVar2 = param_2;
            }
          }
        }
      }
      else {
        uVar2 = 0;
      }
    }
    else {
      uVar2 = 0;
    }
  }
  return CONCAT44(local_20,uVar2);
}

