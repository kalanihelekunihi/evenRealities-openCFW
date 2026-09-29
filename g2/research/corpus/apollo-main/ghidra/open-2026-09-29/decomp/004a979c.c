
undefined4 ui_onboarding_main_sub_004A979C(int param_1,int param_2,undefined1 *param_3)

{
  undefined4 uVar1;
  
  if ((param_1 == 0) || (param_3 == (undefined1 *)0x0)) {
    uVar1 = 0xffffffff;
  }
  else {
    *param_3 = *(undefined1 *)(param_1 + param_2);
    param_3[1] = *(undefined1 *)(param_1 + param_2 + 1);
    param_3[2] = *(undefined1 *)(param_1 + param_2 + 2);
    *(uint *)(param_3 + 4) =
         CONCAT13(*(undefined1 *)(param_1 + param_2 + 6),
                  CONCAT12(*(undefined1 *)(param_1 + param_2 + 5),
                           CONCAT11(*(undefined1 *)(param_1 + param_2 + 4),
                                    *(undefined1 *)(param_1 + param_2 + 3))));
    uVar1 = 0;
  }
  return uVar1;
}

