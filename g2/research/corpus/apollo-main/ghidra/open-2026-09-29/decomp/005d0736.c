
char * FUN_005d0736(undefined4 *param_1,char *param_2)

{
  char *local_10;
  
  for (local_10 = (char *)*param_1; local_10 < param_2; local_10 = local_10 + 1) {
    if ((((*local_10 != ' ') && (*local_10 != '\r')) && (*local_10 != '\n')) &&
       (((*local_10 != '\t' && (*local_10 != '\f')) && (*local_10 != '\0')))) {
      if (*local_10 != '%') break;
      FUN_005d071c(&local_10,param_2);
    }
  }
  *param_1 = local_10;
  return local_10;
}

