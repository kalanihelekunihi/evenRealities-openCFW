#include <stdint.h>

struct FT_Module_Class;
struct FT_Driver_ClassRec;
struct FT_Renderer_Class;

extern const struct FT_Module_Class autofit_module_class;
extern const struct FT_Driver_ClassRec tt_driver_class;
extern const struct FT_Driver_ClassRec cff_driver_class;
extern const struct FT_Module_Class psaux_module_class;
extern const struct FT_Module_Class psnames_module_class;
extern const struct FT_Module_Class pshinter_module_class;
extern const struct FT_Module_Class sfnt_module_class;
extern const struct FT_Renderer_Class ft_smooth_renderer_class;
extern const struct FT_Renderer_Class ft_smooth_lcd_renderer_class;
extern const struct FT_Renderer_Class ft_smooth_lcdv_renderer_class;
extern uint32_t audio_uart_ft_add_module_52729c(void *, const void *);

/* Exact recovered ten-class order, source owned; class objects remain imports. */
static const void *const ft405_default_modules[] = {
    &autofit_module_class,
    &tt_driver_class,
    &cff_driver_class,
    &psaux_module_class,
    &psnames_module_class,
    &pshinter_module_class,
    &sfnt_module_class,
    &ft_smooth_renderer_class,
    &ft_smooth_lcd_renderer_class,
    &ft_smooth_lcdv_renderer_class,
    0
};

/* Whole native FT_Add_Default_Modules body at 0x5242fc, 28 bytes. */
void audio_uart_ft_add_default_modules_5242fc(void *library)
{
    for (const void *const *current = ft405_default_modules; *current != 0; ++current)
        (void)audio_uart_ft_add_module_52729c(library, *current);
}
