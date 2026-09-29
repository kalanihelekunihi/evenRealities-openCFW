
undefined4 FUN_00484014(undefined4 param_1,undefined4 param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  
  puVar1 = (undefined4 *)FUN_0044f718(8);
  if (puVar1 == (undefined4 *)0x0) {
    uVar2 = 0;
  }
  else {
    iVar3 = FUN_00464466(&LAB_004840ac_1,0,puVar1);
    if (iVar3 == 0) {
      FUN_0044f758(puVar1);
      uVar2 = 0;
    }
    else {
      *puVar1 = param_1;
      puVar1[1] = param_2;
      FUN_004645ac(iVar3,1);
      uVar2 = 1;
    }
  }
  return uVar2;
}

