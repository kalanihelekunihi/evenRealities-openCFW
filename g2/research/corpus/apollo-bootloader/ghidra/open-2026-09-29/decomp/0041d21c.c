
undefined8 delay_status_change(int param_1,uint *param_2,uint param_3,uint param_4)

{
  undefined4 uVar1;
  
  do {
    if ((*param_2 & param_3) == param_4) {
      uVar1 = 0;
LAB_0041d244:
      return CONCAT44(param_4,uVar1);
    }
    if (param_1 == 0) {
      uVar1 = 4;
      goto LAB_0041d244;
    }
    delay_us(1);
    param_1 = param_1 + -1;
  } while( true );
}

