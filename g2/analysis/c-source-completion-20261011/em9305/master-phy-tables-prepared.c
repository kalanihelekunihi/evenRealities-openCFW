/* Native master PHY five-state/eight-action tables. All executable entries
 * are typed genuine function relocations; no native literal code aliases. */
extern uint32_t opencfw_em9305_phy_action_31592c(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315a0c(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315c64(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315e60(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315e84(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315f0c(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_31634c(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_3163a4(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_3164a8(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_316550(uintptr_t);
const opencfw_em9305_phy_action_fn opencfw_em9305_phy_actions_33522c[40]={
 opencfw_em9305_phy_action_315a0c,0,opencfw_em9305_phy_action_315e60,0,0,opencfw_em9305_phy_action_31592c,opencfw_em9305_phy_action_31592c,0,
 opencfw_em9305_phy_action_31634c,0,opencfw_em9305_phy_action_3163a4,0,0,0,0,opencfw_em9305_phy_action_3164a8,
 opencfw_em9305_phy_action_31634c,opencfw_em9305_phy_action_315e84,opencfw_em9305_phy_action_3163a4,opencfw_em9305_phy_action_315f0c,opencfw_em9305_phy_action_315c64,0,0,0,
 opencfw_em9305_phy_action_31634c,0,opencfw_em9305_phy_action_3163a4,0,0,0,0,opencfw_em9305_phy_action_316550,
 opencfw_em9305_phy_action_31634c,0,opencfw_em9305_phy_action_3163a4,0,opencfw_em9305_phy_action_315c64,0,0,0,
};
const uint8_t opencfw_em9305_phy_transitions_3352cc[40]={
 1u,0u,3u,0u,0u,1u,3u,0u,
 1u,1u,1u,1u,1u,1u,1u,2u,
 2u,4u,2u,0u,0u,2u,2u,2u,
 3u,3u,3u,3u,3u,3u,3u,4u,
 4u,4u,4u,0u,0u,4u,4u,4u,
};
_Static_assert(sizeof(opencfw_em9305_phy_actions_33522c)==160u,"native ARC action table width");
