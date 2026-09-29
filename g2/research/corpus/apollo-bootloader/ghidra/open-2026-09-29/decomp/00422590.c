
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00422590(char *param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == (char *)0x0) {
    param_1 = s_constraint_handler__bad_message_004225af + 1;
  }
  if ((code *)*_DAT_004225ac == (code *)0x0) {
    FUN_00417c28(param_1);
  }
  else {
    (*(code *)*_DAT_004225ac)(param_1,0,0x22);
  }
  return CONCAT44(unaff_r7,0x22);
}

