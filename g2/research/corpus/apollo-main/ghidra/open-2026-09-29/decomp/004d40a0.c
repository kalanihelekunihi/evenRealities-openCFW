
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004d40a0(char *param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == (char *)0x0) {
    param_1 = s_constraint_handler__bad_message_004d40bf + 1;
  }
  if ((code *)*_DAT_004d40bc == (code *)0x0) {
    FUN_00541b74(param_1);
  }
  else {
    (*(code *)*_DAT_004d40bc)(param_1,0,0x22);
  }
  return CONCAT44(unaff_r7,0x22);
}

