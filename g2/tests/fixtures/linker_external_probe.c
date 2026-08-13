extern void open_cfw_unresolved_external(void);

__attribute__((used, noinline))
void open_cfw_external_probe(void)
{
    open_cfw_unresolved_external();
}
