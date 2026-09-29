
void FUN_005b845c(char param_1,code *param_2,undefined4 param_3)

{
  if ((*(char *)(DAT_005b89bc + 8) == param_1) && (param_2 != (code *)0x0)) {
    (*param_2)(DAT_005b89bc,param_3);
  }
  if ((*(char *)(DAT_005b89c0 + 8) == param_1) && (param_2 != (code *)0x0)) {
    (*param_2)(DAT_005b89c0,param_3);
  }
  return;
}

