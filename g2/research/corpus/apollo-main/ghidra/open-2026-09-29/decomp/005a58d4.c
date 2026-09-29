
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 atAlsReadHandler(void)

{
  undefined4 uVar1;
  undefined1 auStack_6c [100];
  
  uVar1 = als_function_09();
  FUN_0044b728(auStack_6c,100,PTR_DAT_005a5970,uVar1,*(undefined4 *)(_DAT_005a596c + 0x28));
  at_core_output(auStack_6c);
  return 1;
}

