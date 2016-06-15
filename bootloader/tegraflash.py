#!/usr/bin/env python
#
# Copyright (c) 2014-2016, NVIDIA Corporation.  All Rights Reserved.
#
# NVIDIA Corporation and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA Corporation is strictly prohibited.
#

import sys
import os
from os.path import expanduser

# insert current working directory
sys.path.insert(1, os.getcwd())

import getopt
import collections
import subprocess
import shutil
import string
import cmd
import errno
import tegraflash_internal
from tegraflash_internal import cmd_environ, paths
from tegraflash_internal import tegraflash_exception, tegraflash_os_path, tegraflash_abs_path
from tegraflash_internal import tegraflash_flash, tegraflash_read, tegraflash_write, tegraflash_test, tegraflash_parse, tegraflash_reboot, tegraflash_dump, tegraflash_rcmbl, tegraflash_rcmboot, tegraflash_sign, tegraflash_sign_binary, tegraflash_secureflash, tegraflash_burnfuses, tegraflash_readfuses, tegraflash_provision_rollback, tegraflash_readmrr, tegraflash_symlink, tegraflash_blowfuses, tegraflash_flush_sata, tegraflash_sata_fwdownload

try:
    input = raw_input
except NameError:
    pass

cmd_environ.update(os.environ.copy())

paths.update({'OUT':None, 'BIN':None, 'SCRIPT':None, 'TMP':None, 'WD':os.getcwd()})

exports = {
            "--bct":None, "--key":'None', "--cfg":None, "--bl":None,
            "--board":None, "--eeprom":None, "--cmd":None, "--instance":None,
            "--hostbin":None, "--applet":None, "--bldtb":None, "--kerneldtb":None, "--chip":None,
            "--out":None, "--nct":None, "--fb":None, "--odmdata":None,
            "--lnx":None, "--tos":None, "--eks":None, "--boardconfig":None,
            "--skipuid":False, "--securedev":False, "--keyindex":None,
            "--wb":None, "--bl-load":None, "--bins":None, "--dev_params":None,
            "--sdram_config":None, "--misc_config":None, "--mb1_bct":None,
            "--pinmux_config":None, "--pmc_config":None, "--pmic_config":None,
            "--scr_config":None, "--br_cmd_config":None, "--applet-cpu":None,
            "--bpf":None,
          }

exit_on_error = False

def usage():
    print( '\n'.join([
    '  Usage: tegraflash [--bct <file] [--cfg <file>] [--bl <file>] [--instance <number>]',
    '                    [--chip <number>] [--bldtb <file>] [--kerneldtb <file>] [--key <file>] [--cmd \"commands\"]',
    '                    [--applet <file>] [--nct <file>] [--hostbin <dir>] [--out <dir>]',
    '                    [--boardconfig <file>] [--skipuid] [--securedev] [--keyindex <number>]',
    '                    [--bl-load <addr>] [--dev_params <file>] [--sdram_config <file>]',
    '                    [--bins <image_type> <file> [load_address][;...]]',
    '                    [--misc_config <file>] [--mb1_bct <file>]',
    '                    [--pinmux_config <file>] [--pmc <file>] [--scr_config <file>]',
    '                    [--pmic_config <file>] [--br_cmd_config <file>]',
    '   ',
    '   --bct           : Bootrom Boot Config Table file',
    '   --cfg           : Partition layout configuration file',
    '   --bl            : Command line bootloader',
    '   --bl-load       : Bootloader load/entry address',
    '   --chip          : Chip Id',
    '   --bldtb     : DTB file to be used by cboot',
    '   --kerneldtb : DTB file to be used by kernel',
    '   --key           : Key for signing required files',
    '   --applet        : Applet to be sent to BootRom',
    '   --nct           : NCT file',
    '   --boardconfig   : File containing board configuration',
    '   --skipuid       : Skip reading Chip UID',
    '   --securedev     : path for flashing fused devices',
    '   --keyindex      : FSKP key index',
    '   --cmd           : List of comma(;) separated commands',
    '   --dev_params    : Boot device parameters',
    '   --sdram_config  : Sdram configuration',
    '   --bins          : List of binaries to be downloaded separated by commad(;)',
    '   --misc_config   : Misc BCT configuration',
    '   --pinmux_config : Pinmux BCT configuration',
    '   --scr_config    : SCR BCT configuration',
    '   --pmc_onfig     : Pad voltage - DPD BCT configuration',
    '   --pmic_config   : PMIC - Rails MMIO/I2C Commands BCT configuration',
    '   --br_cmd_config : BootROM MMIO/I2C Commands BCT configuration',
    '   --mb1_bct       : MB1 BCT file',
    '   --hostbin       : Directory contaning host binaries',
    '   --out           : Directory containing device files',
    '   '
    ]))

def tegraflash_err(Errcode):
    if( exit_on_error):
        sys.exit(Errcode)

class tegraflashcmds(cmd.Cmd):
    prompt = 'tegraflash~> '

    def __init__(self):
        print('\n'.join([
            'Welcome to Tegra Flash',
            'version 1.0.0',
            'Type ? or help for help and q or quit to exit',
            'Use ! to execute system commands',
            ' '
            ]))
        cmd.Cmd.__init__(self)

    def do_quit(self, params):
        return True;

    def do_shell(self, params):
        os.system(params)

    def emptyline(self):
        pass

    def default(self,line):
        print('unknown command:' + line)
        tegraflash_err(1)

    def do_q(self, params):
        return True;

    def do_flash(self, param):
        tegraflash_update_env()
        params = param.replace('  ', ' ')
        args = param.split(' ')
        exports.update(dict(zip(args[::2], args[1::2])))
        compulsory_args = ['--cfg', '--bl', '--chip', '--applet']

        for required_arg in compulsory_args:
            if exports[required_arg] is None:
                exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

        try:
            tegraflash_flash(exports)

        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)

    def help_flash(self):
        print('\n'.join([
        ' ',
        '------------------------------------------------------',
        '  Usage: flash --bct <file> --cfg <file> [--key <file>]',
        '               --applet <file>',
        '------------------------------------------------------',
        '   --bct    : Boot configuration Table',
        '   --cfg    : Partition layout configuration',
        '   --bl     : Command line bootloader',
        '   --key    : Key file',
        '   --applet : Applet to be sent to BootRom',
        '------------------------------------------------------',
        ' ',
        ]))

    def do_secureflash(self, param):
        tegraflash_update_env()
        params = param.replace('  ', ' ')
        args = param.split(' ')
        exports.update(dict(zip(args[::2], args[1::2])))
        compulsory_args = ['--bct', '--cfg', '--bldtb', '--bl', '--applet']

        for required_arg in compulsory_args:
            if exports[required_arg] is None:
                exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

        try:
            tegraflash_secureflash(exports)

        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)

    def help_secureflash(self):
        print('\n'.join([
        ' ',
        '------------------------------------------------------',
        '  Usage: secureflash --bct <file> --cfg <file> --applet <file>',
        '         --bldtb <file> --bl <file>',
        '------------------------------------------------------',
        '   --bct    : Boot configuration Table',
        '   --cfg    : Partition layout configuration',
        '   --bl     : Command line bootloader',
        '   --applet : Applet to be sent to BootRom',
        '   --bldtb  : DTB file for recovery boot',
        '------------------------------------------------------',
        ' ',
        ]))

    def do_rcmbl(self, param):
        print ("\n Entering RCM bootloader\n")
        tegraflash_update_env()
        compulsory_args = ['--chip', '--applet', '--bct', '--bldtb',
            '--applet-cpu',  '--bl']

        for required_arg in compulsory_args:
            if exports[required_arg] is None:
                exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

        try:
            tegraflash_rcmbl(exports)
        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)

    def help_rcmbl(self):
        print('\n'.join([
        ' ',
        '------------------------------------------------------',
        '  Usage: rcmbl --chip <chip> --applet <file> --bct <file>',
        '               --bldtb <dtb> --applet-cpu <file>',
        '               --bl <file> [--bl-load <load-addr>]',
        '               [--odmdata <data>] [--boardconfig <file>]',
        '               [--key <file>] [--eks <file>]',
        '------------------------------------------------------',
        '   --chip        : Chip ID',
        '   --applet      : Applet to be sent to Boot ROM',
        '   --bct         : Boot Configuration Table',
        '   --bldtb       : Bootloader DTB file to pass to bootloader',
        '   --applet-cpu  : CPU-side pre-bootloader binary',
        '   --bl          : Command line bootloader',
        '   --bl-load     : Bootloader load address',
        '   --odmdata     : ODMDATA to write into BCT',
        '   --boardconfig : Board config to write into BCT',
        '   --key         : Key file',
        '   --eks         : eks.dat file',
        '------------------------------------------------------',
        ' ',
        ]))

    def do_rcmboot(self, param):
        print ("\n Entering RCM boot\n")
        tegraflash_update_env()
        compulsory_args = ['--bct', '--bl', '--chip', '--applet']

        for required_arg in compulsory_args:
            if exports[required_arg] is None:
                exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

        try:
            tegraflash_rcmboot(exports)

        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)

    def help_rcmboot(self):
        print('\n'.join([
        ' ',
        '------------------------------------------------------',
        '  Usage: rcmboot --bct <file> --cfg <file> [--key <file>]',
        '                 --lnx <file> [--tos <file>] [--eks <file>]',
        '                 --bl <file> --applet <file> ',
        '------------------------------------------------------',
        '   --bct    : Boot configuration Table',
        '   --cfg    : Partition layout configuration',
        '   --key    : Key file',
        '   --lnx    : boot.img file used during rcmboot',
        '   --tos    : tos.img file used during rcmboot',
        '   --eks    : eks.dat file used during rcmboot',
        '   --bl     : Command line bootloader',
        '   --applet : Applet to be sent to BootRom',
        '------------------------------------------------------',
        ' ',
        ]))

    def do_read(self, params):
        params = params.replace('  ', ' ')
        args = params.split(' ')
        if len(args) == 2:
            tegraflash_update_env()

            compulsory_args = ['--bl', '--chip', '--applet']

            for required_arg in compulsory_args:
                if exports[required_arg] is None:
                    exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

            try:
                file_path = tegraflash_abs_path(args[1])
                tegraflash_read(exports, args[0], file_path)

            except tegraflash_exception as e:
                print('Error: '+ e.value)
        else:
            self.help_read()

    def help_read(self):
        print('\n'.join([
        ' ',
        '-------------------------------------------',
        '  Usage: read <name> <file>',
        '-------------------------------------------',
        ' ',
        ]))

    def do_write(self, params):
        params = params.replace('  ', ' ')
        args = params.split(' ')
        if len(args) == 2:
            tegraflash_update_env()
            compulsory_args = ['--bl', '--chip', '--applet']

            for required_arg in compulsory_args:
                if exports[required_arg] is None:
                    exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

            try:
                file_path = tegraflash_abs_path(args[1])
                tegraflash_write(exports, args[0], file_path)

            except tegraflash_exception as e:
                print('Error: '+ e.value)
                tegraflash_err(1)

        else:
            self.help_write()

    def help_write(self):
        print('\n'.join([
        ' ',
        '--------------------------------------------',
        '  Usage: write <name> <file>',
        '--------------------------------------------',
        '   ',
        ]))

    def do_reboot(self, param):
        param = param.replace('  ', ' ')
        args = param.split(' ')

        try:
            if not args[0]:
                args[0] = "coldboot"

            tegraflash_reboot(args)

        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)

    def help_reboot(self):
        print('\n'.join([
        ' ',
        '--------------------------------------------',
        '  Usage: reboot [coldboot | recovery]',
        '--------------------------------------------',
        '   ',
        ]))

    def do_sign(self, params):
        tegraflash_update_env()
        args = { }
        if not params == "":
            params = params.replace('  ', ' ')
            args = params.split(' ')

        try:
            if not '--file' in args:
                if not params == "":
                    args = dict(zip(args[::2], args[1::2]))
                    exports.update(args)

                compulsory_args = ['--chip', '--key']

                for required_arg in compulsory_args:
                    if exports[required_arg] is None:
                        exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

                tegraflash_sign(exports)
            else:
                tegraflash_sign_binary(exports, args)

        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)

    def help_sign(self):
        print('\n'.join([
        ' ',
        '----------------------------------------------------------------------',
        '  Usage: sign --key <file> [--file <file>] [--offset <number>]',
        '              [--length <number>] [--pubkeyhash <file>]',
        '----------------------------------------------------------------------',
        '   --key        : File containing key',
        '   --file       : File containing data to be signed',
        '   --offset     : Start of data which is to be signed',
        '   --length     : Length of data to be signed',
        '   --pubkeyhash : Save public key hash in file for input PKC key',
        '----------------------------------------------------------------------',
        ' 1. For SBK encrypted data will be saved in <filename>_encrypt.<ext>',
        '    format and hash in <filename>.hash format',
        ' 2. For PKC signature will be saved in <filename>.sig format',
        ' ',
        ' If --file is not specified then binaries will be signed based on',
        ' partition layout',
        '----------------------------------------------------------------------',
        ' ',
        ]))

    def do_test(self, params):
        params = params.replace('  ', ' ')
        args = params.split(' ')

        if args[0] != '':
            if len(args) > 1 or args[0] == 'eeprom':
                tegraflash_update_env()

                compulsory_args = ['--chip', '--applet']

                for required_arg in compulsory_args:
                    if exports[required_arg] is None:
                        exports[required_arg] = input('Input ' + required_arg[2:] + ': ')
                try:
                    tegraflash_test(exports, args)
                except tegraflash_exception as e:
                    print('Error: '+ e.value)
                    tegraflash_err(1)
            else:
                self.help_test()
        else:
            self.help_test()

    def help_test(self):
        print('\n'.join([

        ' ',
        '----------------------------------------------------------------------',
        '  Usage: test <test_name> [parameters]',
        '----------------------------------------------------------------------',
        '  Supported tests',
        ' ',
        '  sdram <mode> [size]  : Mode and size in Mb',
        '                         Verifies sdram by writing and reading specified',
        '                         size. Supported modes are 0: soft Test, 1: Hard Test',
        '                         2: Bus Test',
        ' ',
        '  emmc [loop]          : how many loops will be executed',
        '                         Verifies emmc by reading EXT_CSD in 8 bit data width',
        '                         and comparing to reading EXT_CSD in initial state in 1',
        '                         bit data width',
        ' ',
        '  eeprom               : Verifies the eeprom by reading the CRC value',
        '                         that is stored in byte 255 of eeprom and',
        '                         compares it to a value that is calculated in',
        '                         s/w. This ensure that the data path to and',
        '                         from the EEPROM is good as well as verifies',
        '                         data integrity',
        '----------------------------------------------------------------------',
        ' '
        ]))

    def do_parse(self, params):
        params = params.replace('  ', ' ')
        args = params.split(' ')
        if len(args) > 1:
            tegraflash_update_env()

            compulsory_args = ['--chip', '--applet']

            for required_arg in compulsory_args:
                if exports[required_arg] is None:
                    exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

            try:
                tegraflash_parse(exports, args)
            except tegraflash_exception as e:
                print('Error: '+ e.value)
                tegraflash_err(1)
        else:
            self.help_parse()

    def help_parse(self):
        print('\n'.join([
        ' ',
        '---------------------------------------------------------',
        ' Usage: parse <parser> [options]',
        '---------------------------------------------------------',
        ' ',
        ]))

    def do_dump(self, params):
        params = params.replace('  ', ' ')
        args = params.split(' ')
        if len(args) > 0 and len(params) > 0:
            tegraflash_update_env()

            compulsory_args = ['--chip', '--applet']

            for required_arg in compulsory_args:
                if exports[required_arg] is None:
                    exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

            try:
                tegraflash_dump(exports, args)
            except tegraflash_exception as e:
                print('Error: '+ e.value)
                tegraflash_err(1)
        else:
            self.help_dump()

    def help_dump(self):
        print('\n'.join([
        ' ',
        '----------------------------------------------------------------------',
        '  Usage: dump <type> [options]',
        '----------------------------------------------------------------------',
        '  Following types can be dumped',
        ' ',
        '  ram [<start offset> <size>] [file] : Dumps the complete ram if start offset and',
        '                                       size are not specified.',
        '  ptm [file]                         : Dumps only the PTM traces.',
        '  custinfo [file]                    : Dumps customer information',
        '----------------------------------------------------------------------',
        ' '
        ]))

    def do_burnfuses(self, params):
        params = params.replace('  ', ' ')
        args = params.split(' ')
        tegraflash_update_env()
        compulsory_args = ['--chip', '--applet']

        for required_arg in compulsory_args:
            if exports[required_arg] is None:
                exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

        try:
            tegraflash_burnfuses(exports)
        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)

    def help_burnfuses(self):
        print('\n'.join([
        ' ',
        '----------------------------------------------------------------------',
        '  Usage: burnfuses ',
        '----------------------------------------------------------------------',
        '  The command burns a specific set of fuses like TID/LID/SBK/DK/PKC ',
		'  This is unlike the blowfuses command, which takes requests to set ',
		'  values for arbitrary fuses, via an xml file input '
        '----------------------------------------------------------------------',
        ]))

    def do_blowfuses(self, params):
        params = params.replace('  ', ' ')
        args = params.split(' ')
        tegraflash_update_env()
        compulsory_args = ['--chip', '--applet']

        for required_arg in compulsory_args:
            if exports[required_arg] is None:
                exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

        try:
            tegraflash_blowfuses(exports, args)
        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)

    def help_blowfuses(self):
        print('\n'.join([
        ' ',
        '----------------------------------------------------------------------',
        '  Usage: blowfuses <filename.xml>',
        '----------------------------------------------------------------------',
        '  Takes requests to set values for arbitrary fuses via an xml file input ',
		'  This is unlike the burnfuses command, which sets hard coded fuses ',
		'  like TID/LID/SBK/DK/PKC to mentioned values '
        '----------------------------------------------------------------------',
        ]))

    def do_readfuses(self, params):
        params = params.replace('  ', ' ')
        args = params.split(' ')
        if len(args) > 0 and len(params) > 0:
            tegraflash_update_env()
        compulsory_args = ['--chip', '--applet']

        for required_arg in compulsory_args:
            if exports[required_arg] is None:
                exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

        try:
            if not args[0]:
                args[0] = "dut_fuses.bin"
            file_path = tegraflash_abs_path(args[0])
            tegraflash_readfuses(exports, file_path)
        except tegraflash_exception as e:
            print('Error: '+ e.value)

    def help_readfuses(self):
        print('\n'.join([
        ' ',
        '----------------------------------------------------------------------',
        '  Usage: readfuses [outputfile]',
        '----------------------------------------------------------------------',
        ]))

    def do_flush_sata(self, params):
        tegraflash_update_env()
        try:
            tegraflash_flush_sata(args)
        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)

    def help_flush_sata(self):
        print('\n'.join([
        ' ',
        '--------------------------------------------',
        '  Usage: flush_sata',
        '--------------------------------------------',
        '   ',
        ]))

    def do_sata_fwdownload(self, params):
        tegraflash_update_env()
        args = params.split()
        try:
            file_path = tegraflash_abs_path(args[0]) if len(args) >= 1 else None
            tegraflash_sata_fwdownload(file_path)
        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)

    def help_sata_fwdownload(self):
        print('\n'.join([
        ' ',
        '--------------------------------------------',
        '  Usage: sata_fwdownload <file>',
        '--------------------------------------------',
        '   ',
        ]))


    def do_setrollback(self, params):
        params = params.replace('  ', ' ')
        args = params.split(' ')
        tegraflash_update_env()
        compulsory_args = ['--chip', '--applet', '--bl']

        for required_arg in compulsory_args:
            if exports[required_arg] is None:
                exports[required_arg] = input('Input ' + required_arg[2:] + ': ')

        try:
            tegraflash_provision_rollback(exports)
        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)

    def help_setrollback(self):
        print('\n'.join([
        ' ',
        '----------------------------------------------------------------------',
        '  Usage: setrollback ',
        '----------------------------------------------------------------------',
        ]))

    def do_show(self, params):
        args = params.split()
        if len(args) > 1:
            print("Error: More than one arguments")
        elif len(args) == 0:
            for key, value in exports.iteritems():
                print(key[2:] + ' = ' + str(value or 'None'))
        elif len(args) == 1:
            var = '--' + args[0]
            if var in exports:
                val = exports[var]
                if val is None:
                    val = "None"
                print(args[0] + ' = ' + val)
            else:
                print("Invalid " + args[0])

    def help_show(self):
        print('\n'.join([
        ' ',
        '--------------------------------------------------',
        '   Usage: show [variable]',
        '--------------------------------------------------',
        ' '
        ]))

    def do_export(self, params):
        args = params.split()
        if len(args) == 2:
            exports.update({'--'+args[0]:args[1]})
        else:
            print("Error: Invalid number of arguments")

    def do_interact(self, param):
        self.cmdloop()

    def help_export(self):
        print('\n'.join([
            ' ',
            '---------------------------------------------------',
            '  Usage: export <variable> <value>',
            '---------------------------------------------------',
            ' Following variables can be exported',
            '   bct    : Boot Config Table file',
            '   bl     : Command line bootloader',
            '   cfg    : Partition configuration layout',
            '   key    : Key for signing',
            '----------------------------------------------------'
            ' '
        ]))

    def do_readmrr(self, params):
        params = params.replace('  ', ' ')
        args = params.split(' ')
        tegraflash_update_env()

        compulsory_args = ['--chip', '--applet']

        for required_arg in compulsory_args:
            if exports[required_arg] is None:
                exports[required_arg] = input('Input ' + required_arg[2:] + ': ')
        try:
            tegraflash_readmrr(exports, args)
        except tegraflash_exception as e:
            print('Error: '+ e.value)
            tegraflash_err(1)


    def do_help(self, param):
        if (len(param) > 1):
            cmd.Cmd.do_help(self, param)
        else:
            print("");
            print("Commonly used tegraflash Commands")
            print("------------------------------------------")
            print("   flash         : Flash the device")
            print("   secureflash   : Flash device with pre-signed binaries")
            print("   read          : Read a partition")
            print("   write         : Write a partition")
            print("   dump          : Dump data from device")
            print("   test          : Run basic tests")
            print("   reboot        : Reboot the device")
            print("   rcmbl         : Boot bootloader without flashing")
            print("   rcmboot       : Boot kernel without flashing")
            print("   sign          : Sign binaries")
            print("   export        : Export variables")
            print("   show          : List export variables")
            print("------------------------------------------")
            print(" help <command> gives help on command")
            print(" q or quit to quit terminal")
            print("")

def tegraflash_run_commands():
    global exit_on_error
    commands = exports['--cmd'].split(';')
    interpreter = tegraflashcmds()
    exit_on_error = True
    for command in commands:
        interpreter.onecmd(command)

def tegraflash_update_env():
    path_separator = ":"
    if sys.platform == 'win32':
        path_separator = ";"

    cmd_environ["PATH"] = paths['BIN'] + path_separator + paths['WD'] + path_separator + paths['OUT'] \
                                  + path_separator + paths['SCRIPT'] + path_separator + paths['TMP'] + path_separator + os.environ["PATH"]
if __name__ == '__main__':
    options = ["skipuid", "bct=", "cfg=", "bl=", "hostbin=", "cmd=", "key=", "instance=",
               "out=", "chip=", "bldtb=", "kerneldtb=", "nct=", "applet=", "fb=", "odmdata=",
               "lnx=", "tos=", "eks=", "boardconfig=", "securedev", "keyindex=", "wb=",
               "bl-load=", "bins=", "dev_params=", "sdram_config=", "misc_config=",
               "mb1_bct=", "pinmux_config=", "scr_config=", "pmc_config=",
               "pmic_config=", "br_cmd_config=", "applet-cpu=", "bpf="]

    try:
      opts, args = getopt.getopt(sys.argv[1:], "h", options)
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    exports.update(dict(opts))

    if '--skipuid' in sys.argv[1:]:
        exports['--skipuid'] = True

    if '--securedev' in sys.argv[1:]:
        exports['--securedev'] = True

    abs_path = ['--bct', '--cfg', '--bl', '--hostbin', '--key', '--out', '--bldtb', '--kerneldtb',
                '--nct', '--applet', '--fb', '--lnx', '--tos', '--eks', '--wb',
                '--boardconfig', '--applet-cpu', '--bpf']
    for path in abs_path:
        if exports[path] is not None:
            if os.path.dirname(exports[path]):
                exports[path] = os.path.abspath(exports[path])
                exports[path] = tegraflash_os_path(exports[path])

    paths['SCRIPT'] =  os.path.abspath(os.path.dirname(__file__))
    paths['OUT'] = os.getcwd()
    if exports['--hostbin'] is None:
        paths['BIN'] = os.path.abspath(os.path.dirname(__file__))
    else:
        paths['BIN'] = os.path.abspath(exports['--hostbin'])

    if exports['--out'] is not None:
        paths['OUT'] = os.path.abspath(exports['--out'])

    sys.path.insert(1, paths['OUT'])

    # Create a tmporary directory with pid as name
    # Create symlinks for all the files in current directory
    paths['TMP'] = os.path.abspath(paths['OUT'] + "/" + str(os.getpid()))

    try:
        os.makedirs(paths['TMP'])
    except OSError as e:
        paths['TMP'] = expanduser("~") + '/' + str(os.getpid())
        os.makedirs(paths['TMP'])
    retries = 2

    while retries > 0:
        os.chdir(paths['TMP']);
        try:
            for files in os.listdir(paths['OUT']):
                if os.path.isfile(paths['OUT'] + '/' + files):
                    tegraflash_symlink(paths['OUT'] + '/' + files, files)
            retries = 0;
        except OSError as e:
            shutil.rmtree(paths['TMP'])
            paths['TMP'] = expanduser("~") + '/' + str(os.getpid())
            os.makedirs(paths['TMP'])
            retries = retries - 1

    try:
        if exports["--cmd"] is None:
            tegraflashcmds().cmdloop()
        else:
            tegraflash_run_commands()

    except tegraflash_exception as e:
        print('Error: '+ e.value)

    finally:
        # Delete the temporary directory created
        os.chdir(paths['WD']);
        shutil.rmtree(paths['TMP'])

