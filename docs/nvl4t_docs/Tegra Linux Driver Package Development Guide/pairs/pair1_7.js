var pairs =
{
"lauterbach":{"debugging":1,"scripts":1,"add":1}
,"debugging":{"scripts":1}
,"scripts":{"lauterbach":1,"supplied":1,"$t32sys":1,"physical_setup.cmm":1,"t32.cmm":1,"environment":1,"detailed":1,"from":1}
,"supplied":{"release":1}
,"release":{"include":1}
,"include":{"script":1}
,"script":{"description":1,"install_scripts":1,"variables":1,"copy":1}
,"description":{"axi_attach.cmm":1}
,"axi_attach.cmm":{"sets":1}
,"sets":{"cpu":1,"paths":1,"common":1,"user-specific":1,"commands":1}
,"cpu":{"axi":1,"tegra":1,"various":1,"cpu_dcc_swi_setup.cmm":1,"mmu":1,"kernel":1,"monitor":1,"complex":1,"u-boot":1,"apertures":1,"start":1}
,"axi":{"access":1}
,"access":{"config_coredump.t32":1}
,"config_coredump.t32":{"provides":1}
,"provides":{"environment":1,"windows":1}
,"environment":{"variable":1,"variables":1,"four":1,"execute":1}
,"variable":{"settings":1}
,"settings":{"driver":1,"config_cpu.t32":1,"config_cpu_win.t32":1,"cpu_attach.cmm":1,"cpu_uboot-attach.cmm":1,"t21x\u002Ft21x_axi_attach.cmm":1}
,"driver":{"settings":1}
,"config_cpu.t32":{"provides":1}
,"config_cpu_win.t32":{"provides":1}
,"cpu_attach.cmm":{"attaches":1}
,"attaches":{"cpu":1}
,"tegra":{"<platform>":1}
,"<platform>":{"bsp":1}
,"bsp":{"kernel":1,"ethernet":1}
,"kernel":{"cpu_boot_attach.cmm":1,"symbols":1,"image":1,"windows.cmm":1}
,"cpu_boot_attach.cmm":{"attaches":1}
,"ethernet":{"boot":1}
,"boot":{"cpu_boot_sdram_noload.cmm":1,"loader":1}
,"cpu_boot_sdram_noload.cmm":{"boots":1}
,"boots":{"cpu":1}
,"various":{"configurations":1}
,"configurations":{"cpu_dcc_setup.cmm":1}
,"cpu_dcc_setup.cmm":{"configures":1}
,"configures":{"dcc":1}
,"dcc":{"cpu":1,"using":1}
,"cpu_dcc_swi_setup.cmm":{"configures":1}
,"using":{"swi":1}
,"swi":{"method":1}
,"method":{"cpu_disable_mmu.cmm":1}
,"cpu_disable_mmu.cmm":{"disables":1}
,"disables":{"cpu":1}
,"mmu":{"caches":1}
,"caches":{"cpu_kernel_attach.cmm":1}
,"cpu_kernel_attach.cmm":{"attaches":1}
,"symbols":{"loaded":1}
,"loaded":{"cpu_kernel_load.cmm":1,"cpu_mp_attach.cmm":1}
,"cpu_kernel_load.cmm":{"loads":1}
,"loads":{"kernel":1}
,"image":{"via":1,"vmlinux":1}
,"via":{"jtag":1}
,"jtag":{"loader":1}
,"loader":{"cpu_menu_setup.cmm":1,"physical":1}
,"cpu_menu_setup.cmm":{"installs":1}
,"installs":{"cpu-side":1,"scripts":1,"lauterbach":1}
,"cpu-side":{"menu":1}
,"menu":{"buttons":1}
,"buttons":{"cpu_monitor_attach.cmm":1}
,"cpu_monitor_attach.cmm":{"attaches":1}
,"monitor":{"symbols":1}
,"cpu_mp_attach.cmm":{"sets":1}
,"complex":{"core\u002Fmultiprocessor":1}
,"core\u002Fmultiprocessor":{"settings":1}
,"cpu_uboot-attach.cmm":{"boots":1}
,"u-boot":{"already":1}
,"already":{"present":1}
,"present":{"sdram":1}
,"sdram":{"csite_cpu.cmm":1}
,"csite_cpu.cmm":{"dumps":1}
,"dumps":{"coresight":1}
,"coresight":{"cpu":1}
,"apertures":{"install_customer_scripts":1}
,"install_customer_scripts":{"installs":1}
,"$t32sys":{"(android)":1}
,"(android)":{"c:\u005Ct32":1}
,"c:\u005Ct32":{"(windows)":1}
,"(windows)":{"directory":1}
,"directory":{"prompts":1,"following":1,"$sudo":1}
,"prompts":{"user":1}
,"user":{"customize":1}
,"customize":{"configuration":1}
,"configuration":{"script":1}
,"install_scripts":{"installs":1}
,"physical_setup.cmm":{"reconfigures":1}
,"reconfigures":{"boot":1,"virtual":1}
,"physical":{"addressing":1}
,"addressing":{"mode":1}
,"mode":{"setup_customer_environment.cmm":1,"kernel":1}
,"setup_customer_environment.cmm":{"sets":1}
,"paths":{"global":1,"image":1}
,"global":{"environment":1}
,"variables":{"used":1,"virtual_setup.cmm":1,"~\u002F.bashrc":1}
,"used":{"scripts":1}
,"t32.cmm":{"initializes":1}
,"initializes":{"trace32":1}
,"trace32":{"t32_customer.cmm":1,"t32cpu.bat":1,"instance":1,"t21x\u002Ft21x_cpu_jtag_setup.cmm":1,"t21x\u002Ft21x_cpu_mp_jtag_setup.cmm":1,"t21x\u002Ft21x_init_cpu.cmm":1,"setting":1,"install":1}
,"t32_customer.cmm":{"default":1}
,"default":{"startup":1}
,"startup":{"program":1}
,"program":{"trace32":1}
,"t32cpu.bat":{"specifies":1}
,"specifies":{"trace32":1}
,"instance":{"cpu":1}
,"start":{"toolbar_setup.cmm":1}
,"toolbar_setup.cmm":{"sets":1}
,"common":{"toolbar":1}
,"toolbar":{"items":1}
,"items":{"user_config_customer.cmm":1}
,"user_config_customer.cmm":{"sets":1,"script":1,"\u002Fopt\u002Ft32\u002Fuser_config.cmm":1}
,"user-specific":{"parameters":1}
,"parameters":{"such":1,"trace32":1}
,"such":{"script":1}
,"virtual_setup.cmm":{"reconfigures":1}
,"virtual":{"addressing":1}
,"windows.cmm":{"provides":1}
,"windows":{"settings":1}
,"t21x\u002Ft21x_axi_attach.cmm":{"sets":1}
,"t21x\u002Ft21x_cpu_jtag_setup.cmm":{"sets":1}
,"t21x\u002Ft21x_cpu_mp_jtag_setup.cmm":{"sets":1}
,"t21x\u002Ft21x_init_cpu.cmm":{"sets":1}
,"setting":{"lauterbach":1}
,"four":{"sets":1}
,"commands":{"run":1,"device":1}
,"run":{"environment":1,"lauterbach":1}
,"execute":{"lauterbach":1,"following":1}
,"detailed":{"below":1}
,"below":{"setup":1}
,"setup":{"run":1,"user_config_customer.cmm":1}
,"add":{"variables":1}
,"~\u002F.bashrc":{"$export":1}
,"$export":{"t32sys=<directory":1,"t32tmp=\u002Ftmp":1,"t32id=t32":1,"path=$path:$t32sys\u002Fbin\u002Fpc_linux64:$t32sys":1,"tegra_top=$(pwd)":1,"target_board=t210ref":1,"target_os_subtype=gnu_linux":1}
,"t32sys=<directory":{"chose":1}
,"chose":{"your":1}
,"your":{"trace32":1,"build":1,"t32":1}
,"install":{"directory>":1}
,"directory>":{"$export":1}
,"t32tmp=\u002Ftmp":{"$export":1}
,"t32id=t32":{"$export":1}
,"path=$path:$t32sys\u002Fbin\u002Fpc_linux64:$t32sys":{"your":1}
,"build":{"directory":1}
,"following":{"$export":1,"command":1,"commands":1}
,"tegra_top=$(pwd)":{"$export":1}
,"target_board=t210ref":{"$export":1}
,"target_os_subtype=gnu_linux":{"download":1}
,"download":{"tar":1}
,"tar":{"ball":1}
,"ball":{"lauterbach":1}
,"from":{"link":1}
,"link":{"downloads":1}
,"downloads":{"button":1}
,"button":{"extract":1}
,"extract":{"correct":1}
,"correct":{"paths":1}
,"vmlinux":{"setup":1}
,"copy":{"required":1}
,"required":{"files":1}
,"files":{"your":1}
,"t32":{"directory":1}
,"$sudo":{".\u002Finstall_customer_scripts":1}
,".\u002Finstall_customer_scripts":{"$cp":1}
,"$cp":{"user_config_customer.cmm":1,".\u002Fsetup_customer_environment.cmm":1}
,"\u002Fopt\u002Ft32\u002Fuser_config.cmm":{"$cp":1}
,".\u002Fsetup_customer_environment.cmm":{".\u002Fsetup_environment.cmm":1}
,".\u002Fsetup_environment.cmm":{"execute":1}
,"command":{"host":1}
,"host":{"system":1}
,"system":{"$t32cpu-64":1}
,"$t32cpu-64":{"&execute":1}
,"&execute":{"following":1}
,"device":{"$echo":1}
,"$echo":{"\u002Fsys\u002Fdevices\u002Fsystem\u002Fcpu\u002Fcpuquiet\u002Ftegra_cpuquiet\u002Fenable":1,"\u002Fsys\u002Fkernel\u002Fdebug\u002Fcpuidle_t210\u002Ffast_cluster_states_enable":1,"\u002Fsys\u002Fkernel\u002Fdebug\u002Fcpuidle_t210\u002Fslow_cluster_states_enable":1}
,"\u002Fsys\u002Fdevices\u002Fsystem\u002Fcpu\u002Fcpuquiet\u002Ftegra_cpuquiet\u002Fenable":{"$echo":1}
,"\u002Fsys\u002Fkernel\u002Fdebug\u002Fcpuidle_t210\u002Ffast_cluster_states_enable":{"$echo":1}
}
;Search.control.loadWordPairs(pairs);
