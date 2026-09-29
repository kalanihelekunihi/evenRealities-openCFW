
undefined8 FUN_0055b35a(int param_1,undefined4 param_2,undefined1 param_3)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_1 == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = (**(code **)(param_1 + 4))(3,param_2,param_3);
  }
  return CONCAT44(unaff_r7,uVar1);
}

