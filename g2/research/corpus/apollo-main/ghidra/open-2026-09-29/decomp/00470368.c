
undefined8 FUN_00470368(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  for (uVar3 = 0; uVar3 < 200; uVar3 = uVar3 + 1) {
    iVar1 = FUN_004702d8();
    if (iVar1 == 0) {
      uVar2 = 0;
      goto LAB_004703b8;
    }
    FUN_00491102(5);
  }
  uVar3 = 0;
  do {
    if (param_1 <= uVar3) {
      uVar2 = 1;
LAB_004703b8:
      return CONCAT44(param_4,uVar2);
    }
    iVar1 = osKernelGetState();
    if (iVar1 == 2) {
      osDelay(1);
    }
    else {
      FUN_00491102(1000);
    }
    iVar1 = FUN_004702d8();
    if (iVar1 == 0) {
      uVar2 = 0;
      goto LAB_004703b8;
    }
    uVar3 = uVar3 + 1;
  } while( true );
}

