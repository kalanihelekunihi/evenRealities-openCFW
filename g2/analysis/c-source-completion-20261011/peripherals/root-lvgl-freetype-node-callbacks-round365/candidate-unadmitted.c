
/* Complete native node comparator4b2342..4b239c90bytes.
 * Byte fields are reread after comparison as in native instructions. */
int32_t audio_uart_ft_node_compare_4b2342(const void *left,const void *right)
{
 const volatile uint8_t *a=left,*b=right;
 if(a[5]!=b[5]){uint32_t rhs=b[5],lhs=a[5];return lhs>rhs?1:-1;}
 if(a[4]!=b[4]){uint32_t rhs=b[4],lhs=a[4];return lhs>rhs?1:-1;}
 const char *rhs=(const char *)(uintptr_t)*(const volatile uint32_t *)right;
 const char *lhs=(const char *)(uintptr_t)*(const volatile uint32_t *)left;
 int32_t result=audio_uart_lv_string_compare_4547be(lhs,rhs);
 return result==0?0:result>0?1:-1;
}
