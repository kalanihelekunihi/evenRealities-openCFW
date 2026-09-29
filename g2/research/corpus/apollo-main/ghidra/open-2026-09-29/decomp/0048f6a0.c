
undefined8 FUN_0048f6a0(int param_1,char param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_2 == '\0') {
    uVar1 = FUN_0048f628();
  }
  else if (param_2 == '\x01') {
    uVar1 = FUN_0048f3be(param_1,0,8);
  }
  else if (param_2 == '\x02') {
    uVar1 = FUN_0048f64c();
  }
  else if (param_2 == '\x05') {
    uVar1 = FUN_0048f3be(param_1,0,4);
  }
  else {
    uVar1 = DAT_00490118;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar1 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar1;
    uVar1 = 0;
  }
  return CONCAT44(unaff_r7,uVar1);
}

