
undefined8 FUN_004d46e8(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  FUN_004d47fa(param_1);
  uVar1 = xTaskGetCurrentTaskHandle();
  FUN_004420d0();
  iVar2 = *(int *)(param_1 + 4);
  *(undefined4 *)(param_1 + 4) = 0;
  if (iVar2 == 0) {
    *(undefined4 *)(param_1 + 8) = uVar1;
  }
  FUN_004420e8();
  if (iVar2 == 0) {
    FUN_00455afc(0,1,0xffffffff);
  }
  return CONCAT44(param_4,1);
}

