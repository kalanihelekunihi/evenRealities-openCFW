
undefined4 FUN_005814d4(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  undefined4 local_90;
  undefined1 local_8c [128];
  
  local_90 = 0;
  uVar1 = FUN_005848fc(param_3,1,&local_90);
  iVar2 = FUN_0058143a(uVar1);
  if (iVar2 == 0) {
    FUN_004733ee(DAT_00581714,param_3,uVar1);
  }
  else {
    FUN_004733ee(DAT_0058170c,uVar1);
    uVar3 = FUN_0044a43c(uVar1);
    iVar2 = FUN_00581462(uVar1,local_8c);
    if (iVar2 == 0) {
      for (iVar2 = 0; iVar2 < (int)(uVar3 >> 1); iVar2 = iVar2 + 1) {
        FUN_004733ee(PTR_s__02X_005816f0,local_8c[iVar2]);
      }
      FUN_004733ee(&LAB_00581640);
      APP_BleRingSendDataMsg(local_8c,uVar3 >> 1 & 0xffff);
    }
    else {
      FUN_004733ee(DAT_00581710);
    }
  }
  return 0;
}

