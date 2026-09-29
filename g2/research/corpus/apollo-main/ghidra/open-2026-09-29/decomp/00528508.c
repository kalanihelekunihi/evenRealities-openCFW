
undefined8
raccess_guess_apple_double
          (undefined4 param_1,int param_2,undefined4 param_3,undefined4 *param_4,undefined4 *param_5
          )

{
  undefined4 uVar1;
  undefined4 local_10;
  
  *param_4 = 0;
  if (param_2 == 0) {
    uVar1 = 0x51;
    local_10 = param_4;
  }
  else {
    local_10 = param_5;
    uVar1 = raccess_guess_apple_generic();
  }
  return CONCAT44(local_10,uVar1);
}

