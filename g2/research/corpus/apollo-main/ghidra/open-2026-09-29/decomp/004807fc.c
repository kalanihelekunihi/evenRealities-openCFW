
undefined8 FUN_004807fc(int param_1,uint *param_2,uint param_3,uint param_4)

{
  undefined4 uVar1;
  
  do {
    if ((*param_2 & param_3) == param_4) {
      uVar1 = 0;
LAB_00480824:
      return CONCAT44(param_4,uVar1);
    }
    if (param_1 == 0) {
      uVar1 = 4;
      goto LAB_00480824;
    }
    FUN_004807a0(1);
    param_1 = param_1 + -1;
  } while( true );
}

