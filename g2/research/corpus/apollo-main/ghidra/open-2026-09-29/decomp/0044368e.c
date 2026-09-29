
undefined4 FUN_0044368e(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = FUN_00460106();
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    iVar3 = FUN_0046cacc(iVar1,&DAT_0044373c);
    if (iVar3 == 0) {
      uVar2 = 1;
    }
    else {
      iVar3 = FUN_0046cacc(iVar1,DAT_004441e4);
      if (iVar3 == 0) {
        uVar2 = 0;
      }
      else {
        iVar3 = FUN_0046cacc(iVar1,&DAT_00443740);
        if (iVar3 == 0) {
          uVar2 = 2;
        }
        else {
          iVar3 = FUN_0046cacc(iVar1,&DAT_00443744);
          if (iVar3 == 0) {
            uVar2 = 4;
          }
          else {
            iVar3 = FUN_0046cacc(iVar1,&DAT_00443748);
            if (iVar3 == 0) {
              uVar2 = 3;
            }
            else {
              iVar3 = FUN_0046cacc(iVar1,&DAT_0044374c);
              if (iVar3 == 0) {
                uVar2 = 5;
              }
              else {
                iVar3 = FUN_0046cacc(iVar1,DAT_004441e8);
                if (iVar3 == 0) {
                  uVar2 = 6;
                }
                else {
                  iVar1 = FUN_0046cacc(iVar1,DAT_004443a0);
                  if (iVar1 == 0) {
                    uVar2 = 7;
                  }
                  else {
                    uVar2 = 0;
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  return uVar2;
}

