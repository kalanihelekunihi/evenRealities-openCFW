
undefined8 FUN_004207a2(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  for (uVar3 = 0; uVar3 < 200; uVar3 = uVar3 + 1) {
    iVar1 = FUN_0042074e();
    if (iVar1 == 0) {
      uVar2 = 0;
      goto LAB_004207f2;
    }
    FUN_0041f9e6(5);
  }
  uVar3 = 0;
  do {
    if (param_1 <= uVar3) {
      uVar2 = 1;
LAB_004207f2:
      return CONCAT44(param_4,uVar2);
    }
    iVar1 = FUN_00416088();
    if (iVar1 == 2) {
      bl_runtime_notify(1);
    }
    else {
      FUN_0041f9e6(1000);
    }
    iVar1 = FUN_0042074e();
    if (iVar1 == 0) {
      uVar2 = 0;
      goto LAB_004207f2;
    }
    uVar3 = uVar3 + 1;
  } while( true );
}

