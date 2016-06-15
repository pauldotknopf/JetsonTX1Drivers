#

# Copyright (c) 2014-2016, NVIDIA Corporation.  All Rights Reserved.
#
# NVIDIA Corporation and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA Corporation is strictly prohibited.
#

from __future__ import print_function

import subprocess
import os.path
import time
import sys
import shutil
import math
from xml.etree import ElementTree
import struct

cmd_environ = { }
paths = { }

start_time = time.time()
values = { }
tegrarcm_values = { '--list':'rcm_list.xml', '--signed_list':'rcm_list_signed.xml',
                    '--storage_info':'storage_info.bin', '--board_info':'board_info.bin',
                    '--chip_info':'chip_info.bin', '--rollback_data':'rollback_data.bin',
                    '--blowfuse_info': 'blow_fuse_data.bin',
                  }
tegrabct_values = { '--bct':None, '--list':'bct_list.xml', '--signed_list':'bct_list_signed.xml', '--mb1_bct':None }
tegrasign_values = { '--pubkeyhash':'pub_key.key', '--mode':'None'}
tegraparser_values = { '--pt':None, }
tegrahost_values = { '--list':'images_list.xml', '--signed_list':'images_list_signed.xml', }

tegraflash_binaries_t18x = { 'tegrabct':'tegrabct_v2', 'tegrahost':'tegrahost_v2', 'tegrasign':'tegrasign_v2', 'tegrarcm':'tegrarcm_v2', 'tegradevflash':'tegradevflash_v2', 'tegraparser':'tegraparser_v2'}

tegraflash_binaries = { 'tegrabct':'tegrabct', 'tegrahost':'tegrahost', 'tegrasign':'tegrasign', 'tegrarcm':'tegrarcm', 'tegradevflash':'tegradevflash', 'tegraparser':'tegraparser'}

# Functions private to this module
# Although they are accessible, please dont use them outside this module
def _parse_fuses(filename):
    with open(filename, 'rb') as f:
        # TID shall be the first 4 bytes of fuses.bin
        tid = struct.unpack('>I',  f.read(4))[0] # Expected to be read in Big Endian format
        info_print('TID Read from Device: %x\n' % tid)

class tegraflash_exception(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def tegraflash_os_path(path):
    newpath = path
    newpath = os.path.expanduser(newpath)
    newpath = os.path.normpath(newpath)

    # convert cygwin path to windows path
    if sys.platform == 'cygwin':
        process = subprocess.Popen(['cygpath', '-w', newpath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if process.wait() != 0:
            raise tegraflash_exception("Path conversion failed " + newpath)
        newpath = process.communicate()[0]

    newpath = newpath.rstrip('\n')

    if sys.platform == 'win32' or sys.platform == 'cygwin':
        newpath = newpath.replace('/', '\\')

    return newpath

def tegraflash_abs_path(file_path):
    new_path = file_path
    new_path = os.path.expanduser(new_path)

    if not os.path.isabs(new_path):
        new_path = os.path.join(paths['WD'], new_path)

    new_path = tegraflash_os_path(new_path)

    return new_path

def info_print(string):
    diff_time = time.time() - start_time
    print('[ %8.4f ] %s' % (diff_time, string))

def print_process(process) :
    print_time = True
    diff_time = time.time() - start_time

    while process.poll() is None:
        output = process.stdout.read(1)
        outputchar = output.decode('ascii')
        if outputchar == '\n' :
            diff_time = time.time() - start_time
            print_time = True
        elif outputchar == '\r' :
            print_time = True
        elif outputchar:
            if print_time:
                print('[ %8.4f ] ' % diff_time, end="")
                print_time = False

        sys.stdout.write(outputchar)
        sys.stdout.flush()

    for string in process.communicate()[0].decode('utf-8').split('\n'):
        if print_time:
            diff_time = time.time() - start_time
            print('[ %8.4f ] ' % diff_time, end='')
        print(string)
        print_time = True


def run_command(cmd):
    info_print(' '.join(cmd))

    use_shell = False
    if sys.platform == 'win32':
        use_shell = True

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=use_shell, env=cmd_environ)

    print_process(process)
    return_code = process.wait()

    if return_code != 0:
        raise tegraflash_exception('Return value ' + str(return_code) +
                '\nCommand ' + ' '.join(cmd))

def tegraflash_flash(args):
    global start_time
    start_time = time.time()
    values.update(args)

    if values['--bl'] is None:
        print('Error: Command line bootloader is not specified')
        return 1

    if values['--cfg'] is None:
        print('Error: Partition configuration is not specified')
        return 1

    if values['--chip'] is None:
        print('Error: chip is not specified')
        return 1

    tegraflash_get_key_mode()
    tegraflash_generate_rcm_message()
    tegraflash_parse_partitionlayout()
    tegraflash_sign_images()
    tegraflash_generate_bct()
    tegraflash_update_images()
    tegraflash_update_bfs_images()
    tegraflash_send_tboot(tegrarcm_values['--signed_list'])
    args['--skipuid'] = False
    tegraflash_send_bct()
    tegraflash_send_bootloader()
    tegraflash_get_storage_info()
    tegraflash_boot('recovery')
    tegraflash_flash_partitions()
    tegraflash_flash_bct()
    info_print('Flashing completed\n')

def tegraflash_rcmbl(args):
    global start_time
    start_time = time.time()
    values.update(args)

    if values['--chip'] is None:
        print('Error: chip is not specified')
        return 1

    if values['--applet'] is None:
        print('Error: applet is not specified')
        return 1

    if values['--bct'] is None:
        print('Error: BCT is not specified')
        return 1

    if values['--bldtb'] is None:
        print('Error: Bootloader DTB is not specified')
        return 1

    if values['--applet-cpu'] is None:
        print('Error: CPU-side pre-bootloader binary is not specified')
        return 1

    if values['--bl'] is None:
        print('Error: Command line bootloader is not specified')
        return 1

    if values['--securedev']:
        tegrabct_values['--bct'] = values['--bct']
        tegraflash_update_boardinfo()
        tegraflash_update_odmdata()
        tegraflash_send_tboot(args['--applet'])
    else:
        tegraflash_generate_rcm_message()
        tegraflash_parse_partitionlayout()
        tegraflash_sign_images()
        tegraflash_generate_bct()
        tegraflash_update_images()
        tegraflash_send_tboot(tegrarcm_values['--signed_list'])
    args['--skipuid'] = False
    tegraflash_send_bct()
    tegraflash_send_bootimages()
    tegraflash_send_bootloader()
    tegraflash_boot('recovery')
    info_print('RCM-bl started\n')

def tegraflash_rcmboot(args):
    global start_time
    start_time = time.time()
    values.update(args)

    if values['--bct'] is None:
        print('Error: BCT is not specified')
        return 1

    if values['--bl'] is None:
        print('Error: Command line bootloader is not specified')
        return 1

    if values['--chip'] is None:
        print('Error: chip is not specified')
        return 1

    if values['--bldtb'] is None:
        print('Error: bl dtb is not specified')
        return 1

    if values['--kerneldtb'] is None:
        print('Error: bl dtb is not specified')
        return 1

    tegrabct_values['--bct'] = values['--bct']
    tegrabct_values['--mb1_bct'] = values['--mb1_bct']
    tegraflash_update_boardinfo()
    tegraflash_update_odmdata()
    tegraflash_send_tboot(args['--applet'])
    args['--skipuid'] = False
    tegraflash_send_bct()
    if int(values['--chip'], 0) != 0x18:
        tegraflash_send_bootimages()
    tegraflash_send_bootloader(False)
    tegraflash_boot('rcm')
    info_print('RCM-boot started\n')

def tegraflash_secureflash(args):
    values.update(args)
    tegrabct_values['--bct'] = values['--bct']
    tegraflash_parse_partitionlayout()
    tegraflash_send_tboot(args['--applet'])
    args['--skipuid'] = False
    if  values['--odmdata'] is not None:
        info_print('Updating Odmdata')
        command = exec_file('tegrabct')
        command.extend(['--bct', tegrabct_values['--bct']])
        command.extend(['--chip', values['--chip']])
        command.extend(['--updatefields', 'Odmdata = ' + values['--odmdata']])
        run_command(command)
    tegraflash_send_bct()
    tegraflash_get_storage_info()
    tegraflash_send_bootloader()
    tegraflash_boot('recovery')
    tegraflash_flash_partitions()
    tegraflash_flash_bct()
    info_print('Flashing completed\n')

def tegraflash_read(args, partition_name, filename):
    values.update(args)

    if values['--bl'] is None:
        print('Error: Command line bootloader is not specified')
        return 1

    if values['--securedev']:
        tegrabct_values['--bct'] = values['--bct']
        if values['--cfg'] is not None:
            tegraflash_parse_partitionlayout()
        tegraflash_send_tboot(args['--applet'])
        args['--skipuid'] = False
        tegraflash_get_storage_info()
        if values['--bct'] is not None:
            tegraflash_send_bct()

    else:
        tegraflash_generate_rcm_message()
        tegraflash_send_tboot(tegrarcm_values['--signed_list'])
        args['--skipuid'] = False
        tegraflash_get_storage_info()

        if values['--cfg'] is not None:
            tegraflash_parse_partitionlayout()
            tegraflash_sign_images()

        if values['--bct'] is None:
            info_print('Reading BCT from device for further operations')
        else:
            info_print('Send BCT from Host')
            tegraflash_generate_bct()
            tegraflash_send_bct()

    if partition_name == 'bct':
        tegraflash_read_partition('tegrarcm', partition_name, filename)
    else:
        tegraflash_send_bootloader()
        tegraflash_boot('recovery')
        tegraflash_read_partition('tegradevflash', partition_name, filename)

def tegraflash_write(args, partition_name, filename):
    values.update(args)

    if values['--bl'] is None:
        print('Error: Command line bootloader is not specified')
        return 1

    if values['--securedev']:
        tegrabct_values['--bct'] = values['--bct']
        tegraflash_send_tboot(args['--applet'])
        args['--skipuid'] = False
    else:
        tegraflash_generate_rcm_message()
        tegraflash_send_tboot(tegrarcm_values['--signed_list'])
        args['--skipuid'] = False

    tegraflash_send_bootloader()
    tegraflash_boot('recovery')
    tegraflash_write_partition(partition_name, filename)

def tegraflash_test(args, test_args):
    values.update(args)

    if values['--securedev']:
        tegraflash_send_tboot(args['--applet'])
    else:
        tegraflash_generate_rcm_message()
        tegraflash_send_tboot(tegrarcm_values['--signed_list'])

    args['--skipuid'] = False

    if test_args[0] == 'sdram':
        tegraflash_verify_sdram(test_args[1:])
    elif test_args[0] == 'emmc':
        tegraflash_verify_emmc(test_args[1:])
    elif test_args[0] == 'eeprom':
        tegraflash_verify_eeprom(test_args[1:])
    else:
        raise tegraflash_exception(test_args[0] + " is not supported")

def tegraflash_parse(args, parse_args):
    values.update(args)

    if parse_args[0] == 'fusebypass':
        tegraflash_parse_fuse_bypass(parse_args[1:])
        args['--skipuid'] = False
    else:
        raise tegraflash_exception(parse_args[0] + " is not supported")

def tegraflash_get_key_mode():
    if int(values['--chip'], 0) != 0x18:
        return

    command = exec_file('tegrasign')
    command.extend(['--key', values['--key']])
    command.extend(['--getmode', 'mode.txt'])
    run_command(command)

    with open('mode.txt') as mode_file:
        tegrasign_values['--mode'] = mode_file.read()

def tegraflash_parse_fuse_bypass(fb_args):
    auto = False
    forcebypass = False

    if len(fb_args) < 2:
        raise tegraflash_exception("Invalid arguments")

    auto = (fb_args[1] == 'auto')

    command = exec_file('tegraparser')
    command.extend(['--fuseconfig', fb_args[0]])
    command.extend(['--sku', fb_args[1]])

    if len(fb_args) == 3:
        if fb_args[2] != 'forcebypass':
            raise tegraflash_exception('Invalid ' + fb_args[2])

        command.extend([fb_args[2]])
        forcebypass = True

    if auto or not forcebypass:
        tegraflash_generate_rcm_message()
        tegraflash_send_tboot(tegrarcm_values['--signed_list'])
        values['--skipuid'] = False
        tegraflash_fetch_chip_info()
        command.extend(['--chipinfo', tegrarcm_values['--chip_info']])

    if auto:
        tegraflash_fetch_board_info()
        command.extend(['--boardinfo', tegrarcm_values['--board_info']])

    info_print('Parsing fuse bypass information')
    run_command(command)

def tegraflash_sign_binary(exports, args):
    info_print('Generating signature')
    command = exec_file('tegrasign')
    if not '--key' in args:
        args.extend(['--key', exports['--key']])
    else:
        file_name_index = args.index('--key') + 1
        args[file_name_index] = tegraflash_abs_path(args[file_name_index])

    os.chdir(paths['WD']);
    file_name_index = args.index('--file') + 1
    args[file_name_index] = tegraflash_abs_path(args[file_name_index])

    command.extend(args)
    try:
        run_command(command)
    except tegraflash_exception as e:
        raise e
    finally:
        os.chdir(paths['TMP']);

def tegraflash_sign(exports):
    values.update(exports)
    cfg_file = values['--cfg']
    signed_files = [ ]

    tegraflash_get_key_mode()

    output_dir = tegraflash_abs_path('signed')
    images_to_sign = ['mts_preboot', 'mts_bootpack', 'mb2_bootloader']
    binaries = []
    tegraflash_generate_rcm_message()

    if values['--cfg'] is not None :
        tegraflash_parse_partitionlayout()
        tegraflash_sign_images()
        tegraflash_generate_bct()
        tegraflash_update_images()

    if values['--bins'] is not None:
        bins = values['--bins'].split(';')
        for binary in bins:
            binary = binary.strip(' ')
            binary = binary.replace('  ', ' ')
            tags = binary.split(' ')
            if (len(tags) < 2):
                raise tegraflash_exception('invalid format ' + binary)

            if tags[0] in images_to_sign:
                tags[1] = tegraflas_oem_sign_file(tags[1])

            binaries.extend([tags[1]])

    if int(values['--chip'], 0) == 0x18 and values['--bl']:
        values['--bl'] = tegraflas_oem_sign_file(values['--bl'])
        binaries.extend([values['--bl']])

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    info_print("Copying signed file in " + output_dir)
    signed_files.extend(tegraflash_copy_signed_binaries(tegrarcm_values['--signed_list'], output_dir))

    if values['--cfg'] is not None :
        signed_files.extend(tegraflash_copy_signed_binaries(tegrahost_values['--signed_list'], output_dir))
        shutil.copyfile(tegrabct_values['--bct'], output_dir + "/" + tegrabct_values['--bct'])
        tegraflash_update_cfg_file(signed_files, cfg_file, output_dir)

    if tegrabct_values['--mb1_bct'] is not None:
        shutil.copyfile(tegrabct_values['--mb1_bct'], output_dir + "/" + tegrabct_values['--mb1_bct'])

    for signed_binary in binaries:
        shutil.copyfile(signed_binary, output_dir + "/" + signed_binary)

def tegraflash_update_cfg_file(signed_files, cfg_file, output_dir):
    signed_files = dict(zip(signed_files[::2], signed_files[1::2]))
    with open(cfg_file, 'r') as file:
        xml_tree = ElementTree.parse(file)

    root = xml_tree.getroot()

    for node in root.findall('.//filename'):
        file_name = node.text.strip()
        if file_name in signed_files:
            node.text = " " + signed_files[file_name] + " "

    with open (output_dir + "/" + cfg_file, 'wb+') as file:
        file.write(ElementTree.tostring(root))

def tegraflash_copy_signed_binaries(xml_file, output_dir):
    signed_files = [ ]
    with open(xml_file, 'rt') as file:
        xml_tree = ElementTree.parse(file)

    mode = xml_tree.getroot().get('mode')
    if mode == "pkc":
        list_text = "signed_file"
    else:
        list_text = "encrypt_file"

    for file_nodes in xml_tree.getiterator('file'):
        file_name = file_nodes.get('name')
        signed_file = file_nodes.find(mode).get(list_text)
        shutil.copyfile(signed_file, output_dir + "/" + signed_file)
        signed_files.extend([file_name, signed_file])

    return signed_files

def tegraflash_boot(boot_type):
    command = exec_file('tegrarcm')
    command.extend(['--boot', boot_type])
    run_command(command)

    if int(values['--chip'], 0) == 0x18:
        time.sleep(25)

def tegraflash_fetch_board_info():
    info_print('Retrieving board information')
    command = exec_file('tegrarcm')
    command.extend(['--oem', 'platformdetails', 'eeprom', tegrarcm_values['--board_info']])
    run_command(command)

def tegraflash_fetch_chip_info():
    info_print('Retrieving board information')
    command = exec_file('tegrarcm')
    command.extend(['--oem', 'platformdetails', 'chip', tegrarcm_values['--chip_info']])
    try:
        run_command(command)
    except tegraflash_exception as e:
        command[0] = 'tegradevflash'
        run_command(command)

def tegraflash_dump(args, dump_args):
    values.update(args)
    if values['--securedev']:
        tegraflash_send_tboot(args['--applet'])
    else:
        tegraflash_generate_rcm_message()
        tegraflash_send_tboot(tegrarcm_values['--signed_list'])
    args['--skipuid'] = False

    if dump_args[0] == 'ram':
        tegraflash_dumpram(dump_args[1:])
    elif dump_args[0] == 'ptm':
        tegraflash_dumpptm(dump_args[1:])
    elif dump_args[0] == 'custinfo':
        tegraflash_read(args, 'bct', 'tmp.bct')
        tegraflash_dumpcustinfo(dump_args[1:])
    else:
        raise tegraflash_exception(dump_args[0] + " is not supported")

def tegraflash_dumpcustinfo(dump_args):
    info_print('Dumping customer Info')
    command = exec_file('tegrabct')
    command.extend(['--bct', 'tmp.bct'])
    command.extend(['--chip', values['--chip']])
    if len(dump_args) > 0:
        file_path = tegraflash_abs_path(dump_args[0])
    else:
        file_path = tegraflash_abs_path("custinfo.bin")

    command.extend(['--custinfo', file_path])
    run_command(command)

def tegraflash_tboot_reset(args):
    if args[0] == 'coldboot':
        info_print('Coldbooting the device')
    elif args[0] == 'recovery':
        info_print('Rebooting to recovery mode')
    else:
        raise tegraflash_exception(args[0] + " is not supported")

    command = exec_file('tegrarcm')
    command.extend(['--reboot', args[0]])
    run_command(command)
    time.sleep(2)

def tegraflash_dumpram(dump_args):
    separator = '---------------------------------------------------'
    info_print('Dumping Ram - Checking if requested region is valid')
    info_print(separator)
    command = exec_file('tegrarcm')
    command.extend(['--oem', 'checkdumpramrequest'])
    command.extend([dump_args[0]])
    command.extend([dump_args[1]])
    run_command(command)

    if len(dump_args[0]) > 0 and len(dump_args[1]) > 0 and len(dump_args) > 2:
        boundary = int(dump_args[0], 0) + int(dump_args[1], 0) - 1
        if boundary <= 0xFFFFFFFF:
            info_print('Dumping Ram - Dump region within 2GB Memory boundary')
            info_print(separator)
            command = exec_file('tegrarcm')
            command.extend(['--oem', 'dumpram'])
            command.extend([dump_args[0]])
            command.extend([dump_args[1]])
            file_path = tegraflash_abs_path(dump_args[2])
            command.extend([file_path])
            run_command(command)
            resettype = ['coldboot']
            tegraflash_tboot_reset(resettype)
        elif boundary > 0xFFFFFFFF and int(dump_args[0], 0) <= 0xFFFFFFFF:
            tempfilenames = ['temp1.bin', 'temp2.bin']
            info_print('Dumping Ram - Dump region spanning across 2GB Memory boundary')
            info_print(separator)
            info_print('Saving dump of memory region requested < 2GB')
            command = exec_file('tegrarcm')
            command.extend(['--oem', 'dumpram'])
            command.extend([dump_args[0]])
            memoryleft = 0x100000000 - int(dump_args[0], 0)
            command.extend(['' + hex(memoryleft)])
            file_path = tempfilenames[0]
            command.extend([file_path])
            run_command(command)

            info_print('Loading TBoot-CPU to initialize SMMU')
            tegraflash_dumpram_load_tboot_cpu()

            info_print('Saving dump of memory region requested > 2GB')
            command = exec_file('tegrarcm')
            command.extend(['--oem', 'dumpram'])
            command.extend(['0x100000000'])
            memorydumped = 0x100000000 - int(dump_args[0], 0)
            memoryleft = int(dump_args[1], 0) - memorydumped
            command.extend(['' + hex(memoryleft)])
            file_path = tempfilenames[1]
            command.extend([file_path])
            run_command(command)
            resettype = ['coldboot']
            tegraflash_tboot_reset(resettype)
            #merge files by reading 10MB blocks
            blocksize = 10485760
            info_print('Merging temp files into :' + tegraflash_abs_path(dump_args[2]))
            fout = file(tegraflash_abs_path(dump_args[2]),'wb')
            for a in tempfilenames:
                fin = file(a,'rb')
                while True:
                    data = fin.read(blocksize)
                    if not data:
                        break
                    fout.write(data)
                fin.close()
            fout.close()
        else:
            info_print('Dumping Ram - Dump region entirely beyond 2GB Memory boundary')
            info_print(separator)
            info_print('Loading TBoot-CPU to initialize SMMU')

            tegraflash_dumpram_load_tboot_cpu()
            info_print('Saving dump of memory > 2GB')
            command = exec_file('tegrarcm')
            command.extend(['--oem', 'dumpram'])
            command.extend([dump_args[0]])
            command.extend([dump_args[1]])
            file_path = tegraflash_abs_path(dump_args[2])
            command.extend([file_path])
            run_command(command)
            resettype = ['coldboot']
            tegraflash_tboot_reset(resettype)

def tegraflash_dumpram_load_tboot_cpu():
    info_print('Sending Tboot-CPU')
    command = exec_file('tegrarcm')
    command.extend(['--download', 'tbc', 'nvtboot_cpu.bin', '0', '0'])
    run_command(command)

def tegraflash_dumpptm(dump_args):
    info_print('Dumping PTM')
    command = exec_file('tegrarcm')
    command.extend(['--oem', 'dumpptm'])

    if len(dump_args) > 0:
        command.extend([dump_args[0]])

    run_command(command)

def tegraflash_burnfuses(exports):
    values.update(exports)

    info_print('Burning fuses')

    if values['--chip'] is None:
        print('Error: chip is not specified')
        return 1

    if values['--securedev']:
        tegraflash_send_tboot(exports['--applet'])
    else:
        tegraflash_generate_rcm_message()
        tegraflash_send_tboot(tegrarcm_values['--signed_list'])

    command = exec_file('tegrarcm')
    command.extend(['--oem', 'burnfuses'])
    run_command(command)

def tegraflash_blowfuses(exports, args):
    values.update(exports)

    if args is None:
        print('Error: require an argument')
        return 1

    filename = os.path.splitext(args[0])
    if filename[1] != '.xml':
        print('Error: not an xml file')
        return 1

    info_print('Parsing fuse info as per xml file')
    command = exec_file('tegraparser')
    command.extend(['--blowfuse_info', args[0], tegrarcm_values['--blowfuse_info']])
    run_command(command)

    if values['--chip'] is None:
        print('Error: chip is not specified')
        return 1

    if values['--securedev']:
        tegraflash_send_tboot(exports['--applet'])
    else:
        tegraflash_generate_rcm_message()
        tegraflash_send_tboot(tegrarcm_values['--signed_list'])

    info_print('Blowing fuses')

    command = exec_file('tegrarcm')
    command.extend(['--oem', 'blowfuses'])
    command.extend([tegrarcm_values['--blowfuse_info']])

    run_command(command)

def tegraflash_readfuses(args, filename):
    values.update(args)

    info_print('Reading fuses')
    if values['--securedev']:
        tegraflash_send_tboot(args['--applet'])
    else:
        tegraflash_generate_rcm_message()
        tegraflash_send_tboot(tegrarcm_values['--signed_list'])

    command = exec_file('tegrarcm')
    command.extend(['--oem', 'readfuses', filename])

    run_command(command)
    _parse_fuses(filename)
    resettype = ['recovery']
    tegraflash_tboot_reset(resettype)

def tegraflash_provision_rollback(exports):
    values.update(exports)

    info_print('Provision Rollback key')

    if values['--chip'] is None:
        print('Error: chip is not specified')
        return 1

    if values['--bct'] is not None:

        if values['--nct'] is None:
            print('Error: NCT file is not specified')
            return 1

        tegraflash_generate_rcm_message()
        tegraflash_generate_bct()
        if values['--securedev']:
            tegraflash_send_tboot(exports['--applet'])
        else:
            tegraflash_send_tboot(tegrarcm_values['--signed_list'])
        tegraflash_send_bct()
        tegraflash_get_storage_info()

    else:
        tegraflash_generate_rcm_message()
        if values['--securedev']:
            tegraflash_send_tboot(exports['--applet'])
        else:
            tegraflash_send_tboot(tegrarcm_values['--signed_list'])

    # generate rollback key
    command = exec_file('tegrarcm')
    command.extend(['--oem', 'getrollback', tegrarcm_values['--rollback_data']])
    run_command(command)

    # provision rollback key
    tegraflash_send_bootloader()
    tegraflash_boot('recovery')
    command = exec_file('tegradevflash')
    command.extend(['--oem', 'setrollback', tegrarcm_values['--rollback_data']])
    run_command(command)

def tegraflash_verify_sdram(test_args):
    if values['--bct'] is not None:
        tegraflash_generate_bct()
        tegraflash_send_bct()

    info_print('Verifying SDRAM')
    command = exec_file('tegrarcm')
    command.extend(['--oem', 'verifysdram'])
    command.extend(test_args)
    run_command(command)

def tegraflash_symlink(srcfile, destfile):
    srcfile = tegraflash_os_path(srcfile)
    destfile = tegraflash_os_path(destfile)

    if sys.platform == 'win32' or sys.platform == 'cygwin':
        process = subprocess.Popen(['cmd', '/c', 'mklink /H ' + destfile + ' ' + srcfile], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait();
    else:
        os.symlink(srcfile, destfile)

def tegraflas_oem_sign_file(in_file):
    filename = os.path.basename(in_file)
    mode = tegrasign_values['--mode']
    command = exec_file('tegrahost')
    command.extend(['--align', in_file])
    run_command(command)

    if not os.path.exists(filename):
        tegraflash_symlink(in_file, filename)

    if mode == 'pkc':
        mode = 'oem-rsa'

    command = exec_file('tegrahost')
    command.extend(['--appendsigheader', filename, mode])
    run_command(command)
    filename = os.path.splitext(filename)[0] + '_sigheader' + os.path.splitext(filename)[1]

    root = ElementTree.Element('file_list')
    comment = ElementTree.Comment('Auto generated by tegraflash.py')
    root.append(comment)
    child = ElementTree.SubElement(root, 'file')
    child.set('name', filename)
    child.set('offset', '384')
    sbk = ElementTree.SubElement(child, 'sbk')
    sbk.set('encrypt', '1')
    sbk.set('sign', '1')
    sbk.set('encrypt_file', filename + '.encrypt')
    sbk.set('hash', filename + '.hash')
    pkc = ElementTree.SubElement(child, 'pkc')
    pkc.set('signature', filename + '.sig')
    pkc.set('signed_file', filename + '.signed')
    sign_tree = ElementTree.ElementTree(root);
    sign_tree.write(filename + '_list.xml')

    command = exec_file('tegrasign')
    command.extend(['--key', values['--key']])
    command.extend(['--list', filename + '_list.xml'])
    run_command(command)

    sign_xml_file = filename + '_list_signed.xml'

    with open(sign_xml_file, 'rt') as file:
        xml_tree = ElementTree.parse(file)

    mode = xml_tree.getroot().get('mode')
    if mode == "pkc":
        sig_type = "oem_rsa"
        list_text = "signed_file"
        sig_file = "signature"
    else:
        list_text = "encrypt_file"
        sig_type = "zerosbk"
        sig_file = "hash"

    signed_file = filename
    for file_nodes in xml_tree.getiterator('file'):
        signed_file = file_nodes.find(mode).get(list_text)
        sig_file = file_nodes.find(mode).get(sig_file)

    command = exec_file('tegrahost')
    command.extend(['--updatesigheader', signed_file, sig_file, sig_type])

    run_command(command)

    signed_file = os.path.splitext(signed_file)[0] + '_signed' + os.path.splitext(signed_file)[1]

    return signed_file

def tegraflash_verify_emmc(test_args):
    info_print('Verifying EMMC')
    command = exec_file('tegrarcm')
    command.extend(['--oem', 'verifyemmc'])
    command.extend(test_args)
    run_command(command)

def tegraflash_verify_eeprom(test_args):
    info_print('Verifying EEPROM')
    command = exec_file('tegrarcm')
    command.extend(['--oem', 'verifyeeprom'])
    command.extend(test_args)
    run_command(command)

def tegraflash_readmrr(args, test_args):
    info_print('Reading MRR')

    values.update(args)

    if values['--securedev']:
        tegraflash_send_tboot(args['--applet'])
    else:
        tegraflash_generate_rcm_message()
        tegraflash_send_tboot(tegrarcm_values['--signed_list'])

    args['--skipuid'] = False

    if values['--bct'] is not None:
        tegraflash_generate_bct()
        tegraflash_send_bct()

    command = exec_file('tegrarcm')
    command.extend(['--oem', 'readmrr'])
    run_command(command)

def tegraflash_write_partition(partition_name, filename):
    info_print('Writing partition')
    command = exec_file('tegradevflash')
    command.extend(['--write', partition_name, filename])
    run_command(command)

def tegraflash_read_partition(executable, partition_name, filename):
    info_print('Reading partition')
    command = exec_file(executable)
    command.extend(['--read', partition_name, filename])
    run_command(command)

def exec_file(name):
    bin_name = ''
    if int(values['--chip'], 0) == 0x18:
        bin_name = tegraflash_binaries_t18x[name]
    else:
        bin_name = tegraflash_binaries[name]

    use_shell = False
    if sys.platform == 'win32':
        use_shell = True

    try:
        subprocess.Popen([bin_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=use_shell, env=cmd_environ)
    except OSError as e:
        raise tegraflash_exception('Could not find ' + bin_name)

    supports_instance = ['tegrarcm', 'tegradevflash']
    if values['--instance'] is not None and name in supports_instance:
        bin_name = [bin_name, '--instance', values['--instance']]
    else:
        bin_name = [bin_name]

    return bin_name

def tegraflash_send_tboot(file_name):
    info_print('Boot Rom communication')
    command = exec_file('tegrarcm')
    command.extend(['--chip', values['--chip']])
    command.extend(['--rcm', file_name])

    if values['--skipuid']:
        command.extend(['--skipuid'])
        values['--skipuid'] = False

    run_command(command)

    if int(values['--chip'], 0) == 0x18:
        time.sleep(5)

def tegraflash_send_bct():
    info_print('Sending BCTs')
    command = exec_file('tegrarcm')
    if int(values['--chip'], 0) == 0x18:
        command.extend(['--download', 'bct_bootrom', tegrabct_values['--bct']])
        command.extend(['--download', 'bct_mb1', tegrabct_values['--mb1_bct']])
    else:
        command.extend(['--download', 'bct', tegrabct_values['--bct']])

    run_command(command)

def tegraflash_get_storage_info():
    info_print('Retrieving storage infomation')
    try:
        command = exec_file('tegrarcm')
        command.extend(['--oem', 'platformdetails', 'storage', tegrarcm_values['--storage_info']])
        run_command(command)
    except tegraflash_exception as e:
        command = exec_file('tegradevflash')
        command.extend(['--oem', 'platformdetails', 'storage', tegrarcm_values['--storage_info']])
        run_command(command)

def tegraflash_send_bootimages():
    info_print('Sending boot.img and required binaries')
    command = exec_file('tegrarcm')

    if values['--fb'] is not None:
        command.extend(['--download', 'fb', values['--fb'], '0', '0'])

    if values['--lnx'] is not None:
        command.extend(['--download', 'lnx', values['--lnx'], '0', '0'])

    if not (values['--tos'] is None):
        command.extend(['--download', 'tos', values['--tos'], '0', '0'])
        if  not (values['--eks'] is None):
            command.extend(['--download', 'eks', values['--eks'], '0', '0'])

    if values['--wb'] is not None:
        command.extend(['--download', 'wb0', values['--wb'], '0', '0'])

    if values['--kerneldtb'] is not None:
        command.extend(['--download', 'dtb', values['--kerneldtb'], '0'])

    if values['--bpf'] is not None:
        command.extend(['--download', 'bpf', values['--bpf'], '0'])

    run_command(command)

def tegraflash_generate_blob(sign_images):
    bins=''
    info_print('Generating blob')
    root = ElementTree.Element('file_list')
    root.set('mode', 'blob')
    comment = ElementTree.Comment('Auto generated by tegraflash.py')
    root.append(comment)
    child = ElementTree.SubElement(root, 'file')
    filename = os.path.basename(values['--bl'])

    if not os.path.exists(filename):
        tegraflash_symlink(values['--bl'], filename)

    tegraflash_symlink(filename, 'blob_' + filename)
    filename = 'blob_' + filename;

    if sign_images:
        filename = tegraflas_oem_sign_file(filename)

    child.set('name', filename)
    child.set('type', 'bootloader')

    images_to_sign = ['mts_preboot', 'mts_bootpack', 'mb2_bootloader']

    if values['--bins']:
        bins = values['--bins'].split(';')

    for binary in bins:
        binary = binary.strip(' ')
        binary = binary.replace('  ', ' ')
        tags = binary.split(' ')
        child = ElementTree.SubElement(root, 'file')
        if (len(tags) < 2):
            raise tegraflash_exception('invalid format ' + binary)

        child.set('type', tags[0])

        filename = os.path.basename(tags[1])
        if not os.path.exists(filename):
            tegraflash_symlink(tags[1], filename)

        tegraflash_symlink(filename, 'blob_' + filename)
        filename = 'blob_' + filename;

        if sign_images and tags[0] in images_to_sign:
            filename = tegraflas_oem_sign_file(filename)

        child.set('name', filename)

        if (len(tags) > 2):
            child.set('load_address', tags[2])

    blobtree = ElementTree.ElementTree(root);
    blobtree.write('blob.xml')

    command = exec_file('tegrahost')
    command.extend(['--generateblob', 'blob.xml', 'blob.bin'])

    run_command(command)

def tegraflash_send_bootloader(sign_images = True):
    if int(values['--chip'], 0) == 0x18:
        tegraflash_generate_blob(sign_images)

    info_print('Sending bootloader and pre-requisite binaries')
    command = exec_file('tegrarcm')

    if int(values['--chip'], 0) == 0x18:
        command.extend(['--download', 'blob', 'blob.bin'])
    else:
        command.extend(['--download', 'ebt', values['--bl']])
        if values['--bl-load'] is not None:
            bl_load = values['--bl-load']
        else:
            bl_load = '0'
        command.extend([bl_load, bl_load])

    if values['--applet-cpu'] is not None:
        command.extend(['--download', 'tbc', values['--applet-cpu'], '0', '0'])

    if values['--bldtb'] is not None:
        command.extend(['--download', 'rp1', values['--bldtb'], '0'])

    run_command(command)

def tegraflash_flash_partitions():
    info_print('Flashing the device')

    if int(values['--chip'], 0) == 0x18:
        command = exec_file('tegraparser')
        command.extend(['--storageinfo', tegrarcm_values['--storage_info']])
        command.extend(['--generategpt', '--pt', tegraparser_values['--pt']])
        run_command(command)

    command = exec_file('tegradevflash')
    command.extend(['--pt', tegraparser_values['--pt']])

    if int(values['--chip'], 0) != 0x18:
        command.extend(['--storageinfo', tegrarcm_values['--storage_info']])

    command.extend(['--create']);
    run_command(command)

def tegraflash_reboot(args):
    if args[0] == 'coldboot':
        info_print('Coldbooting the device')
    elif args[0] == 'recovery':
        info_print('Rebooting to recovery mode')
    else:
        raise tegraflash_exception(args[0] + " is not supported")

    command = exec_file('tegradevflash')
    command.extend(['--reboot', args[0]])
    run_command(command)
    time.sleep(2)

def tegraflash_flush_sata(args):
    info_print("Start cleaning up SATA HDD internal cache (up to 10min)...")
    command = exec_file('tegradevflash')
    command.extend(['--flush_sata'])
    run_command(command)

def tegraflash_sata_fwdownload(filename):
    command = exec_file('tegradevflash')
    if filename is None:
        command.extend(['--sata_fwdownload'])
    else:
        command.extend(['--sata_fwdownload', filename])
    run_command(command)

def tegraflash_flash_bct():
    command = exec_file('tegradevflash')
    command.extend(['--write', 'BCT', tegrabct_values['--bct']]);
    run_command(command)

    if int(values['--chip'], 0) == 0x18:
        command = exec_file('tegradevflash')
        command.extend(['--write', 'MB1_BCT', tegrabct_values['--mb1_bct']]);
        run_command(command)

def tegraflash_sign_images():
    if values['--fb'] is not None:
        info_print('Updating warmboot with fusebypass information')
        command = exec_file('tegrahost')
        command.extend(['--chip', values['--chip']])
        command.extend(['--partitionlayout', tegraparser_values['--pt']])
        command.extend(['--updatewbfuseinfo', values['--fb']])
        run_command(command)

    info_print('Creating list of images to be signed')
    command = exec_file('tegrahost')
    command.extend(['--chip', values['--chip']])
    command.extend(['--partitionlayout', tegraparser_values['--pt']]);

    command.extend(['--list', tegrahost_values['--list']])
    if int(values['--chip'], 0) == 0x18:
        mode = tegrasign_values['--mode']

        if mode == 'pkc':
            mode = 'oem-rsa'

        command.extend([mode])

    run_command(command)

    info_print('Generating signatures')
    command = exec_file('tegrasign')
    command.extend(['--key', values['--key']])
    command.extend(['--list', tegrahost_values['--list']])
    command.extend(['--pubkeyhash', tegrasign_values['--pubkeyhash']])
    run_command(command)

def tegraflash_update_images():
    info_print('Copying signatures')
    command = exec_file('tegrahost')
    command.extend(['--chip', values['--chip']])
    command.extend(['--partitionlayout', tegraparser_values['--pt']])
    command.extend(['--updatesig', tegrahost_values['--signed_list']])

    if os.path.isfile(tegrasign_values['--pubkeyhash']):
        command.extend(['--pubkeyhash', tegrasign_values['--pubkeyhash']])

    run_command(command)

def tegraflash_update_bfs_images():
    info_print('Updating BFS information')
    command = exec_file('tegrabct')
    command.extend(['--bct', tegrabct_values['--bct']])
    command.extend(['--chip', values['--chip']])
    command.extend(['--updatebfsinfo', tegraparser_values['--pt']])
    if os.path.isfile(tegrasign_values['--pubkeyhash']):
        command.extend(['--pubkeyhash', tegrasign_values['--pubkeyhash']])
    run_command(command)

def tegraflash_update_boardinfo():
    if values['--nct'] is not None:
        info_print('Updating board information into bct')
        command = exec_file('tegraparser')
        command.extend(['--nct', values['--nct']])
        command.extend(['--chip', values['--chip']])
        command.extend(['--updatecustinfo', tegrabct_values['--bct']])
        run_command(command)
    elif values['--boardconfig'] is not None:
        info_print('Updating board information from board config into bct')
        command = exec_file('tegraparser')
        command.extend(['--boardconfig', values['--boardconfig']])
        command.extend(['--chip', values['--chip']])
        command.extend(['--updatecustinfo', tegrabct_values['--bct']])
        run_command(command)

def tegraflash_update_odmdata():
    if  values['--odmdata'] is not None:
        info_print('Updating Odmdata')
        command = exec_file('tegrabct')

        if int(values['--chip'], 0) == 0x18:
            command.extend(['--brbct', tegrabct_values['--bct']])
        else:
            command.extend(['--bct', tegrabct_values['--bct']])

        command.extend(['--chip', values['--chip']])
        command.extend(['--updatefields', 'Odmdata = ' + values['--odmdata']])
        run_command(command)

def tegraflash_generate_bct():
    command = exec_file('tegrabct')

    if values['--bct'] is None and int(values['--chip'], 0) == 0x18:
        values['--bct'] = 'br_bct.cfg'

    if int(values['--chip'], 0) == 0x18:
        brbct_arg = '--brbct'
        command.extend(['--dev_param', values['--dev_params']])
        command.extend(['--brbct', values['--bct']])
        tegrabct_values['--bct'] = os.path.splitext(values['--bct'])[0] + '_BR.bct'
    else:
        brbct_arg = '--bct'
        command.extend(['--bct', values['--bct']])
        tegrabct_values['--bct'] = os.path.splitext(values['--bct'])[0] + '.bct'

    command.extend(['--chip', values['--chip']])
    run_command(command)

    if tegraparser_values['--pt'] is not None:
        if int(values['--chip'], 0) != 0x18:
            info_print('Updating boot device parameters')
            command = exec_file('tegrabct')
            command.extend(['--bct', tegrabct_values['--bct']])
            command.extend(['--chip', values['--chip']])
            command.extend(['--updatedevparam', tegraparser_values['--pt']])
            run_command(command)

        info_print('Updating bl info')
        command = exec_file('tegrabct')
        command.extend([brbct_arg, tegrabct_values['--bct']])
        command.extend(['--chip', values['--chip']])
        command.extend(['--updateblinfo', tegraparser_values['--pt']])
        command.extend(['--updatesig', tegrahost_values['--signed_list']])
        run_command(command)

        if int(values['--chip'], 0) != 0x18:
            info_print('Updating secondary storage information into bct')
            command = exec_file('tegraparser')
            command.extend(['--pt', tegraparser_values['--pt']])
            command.extend(['--chip', values['--chip']])
            command.extend(['--updatecustinfo', tegrabct_values['--bct']])
            run_command(command)

    tegraflash_update_boardinfo()
    tegraflash_update_odmdata()

    info_print('Get Signed section bct')
    command = exec_file('tegrabct')
    command.extend([brbct_arg, tegrabct_values['--bct']])
    command.extend(['--chip', values['--chip']])
    command.extend(['--listbct', tegrabct_values['--list']])
    run_command(command)

    info_print('Signing BCT')
    command = exec_file('tegrasign')
    command.extend(['--key', values['--key']])
    command.extend(['--list', tegrabct_values['--list']])
    command.extend(['--pubkeyhash', tegrasign_values['--pubkeyhash']])
    run_command(command)

    info_print('Updating BCT with signature')
    command = exec_file('tegrabct')
    command.extend([brbct_arg, tegrabct_values['--bct']])
    command.extend(['--chip', values['--chip']])
    command.extend(['--updatesig', tegrabct_values['--signed_list']])

    if os.path.isfile(tegrasign_values['--pubkeyhash']):
        command.extend(['--pubkeyhash', tegrasign_values['--pubkeyhash']])

    run_command(command)

    if int(values['--chip'], 0) == 0x18:
        info_print('Generating mb1-bct')

        if values['--mb1_bct'] is None:
            values['--mb1_bct'] = 'mb1_bct.cfg'
        command = exec_file('tegrabct')
        command.extend(['--chip', values['--chip']])
        command.extend(['--mb1bct', values['--mb1_bct']])
        command.extend(['--sdram', values['--sdram_config']])
        command.extend(['--misc', values['--misc_config']])
        if values['--pinmux_config'] is not None:
            command.extend(['--pinmux', values['--pinmux_config']])
        if values['--scr_config'] is not None:
            command.extend(['--scr', values['--scr_config']])
        if values['--pmc_config'] is not None:
            command.extend(['--pmc', values['--pmc_config']])
        if values['--pmic_config'] is not None:
            command.extend(['--pmic', values['--pmic_config']])
        if values['--br_cmd_config'] is not None:
            command.extend(['--brcommand', values['--br_cmd_config']])
        run_command(command)
        tegrabct_values['--mb1_bct'] = os.path.splitext(values['--mb1_bct'])[0] + '_MB1.bct'

        if tegraparser_values['--pt'] is not None:
            info_print('Updating mb1-bct with firmware information')
            command = exec_file('tegrabct')
            command.extend(['--chip', values['--chip']])
            command.extend(['--mb1bct', tegrabct_values['--mb1_bct']])
            command.extend(['--updatefwinfo', tegraparser_values['--pt']])
            run_command(command)

        tegrabct_values['--mb1_bct'] = tegraflas_oem_sign_file(tegrabct_values['--mb1_bct'])

def tegraflash_parse_partitionlayout():
    info_print('Parsing partition layout')
    command = exec_file('tegraparser')
    command.extend(['--pt', values['--cfg']])
    tegraparser_values['--pt'] = os.path.splitext(values['--cfg'])[0] + '.bin'
    run_command(command)

def tegraflash_generate_rcm_message():
    info_print('Generating RCM messages')
    command = exec_file('tegrarcm')
    command.extend(['--listrcm', tegrarcm_values['--list']])
    command.extend(['--chip', values['--chip']])
    if values['--keyindex'] is not None:
        command.extend(['--keyindex', values['--keyindex']])

    if int(values['--chip'], 0) == 0x13:
        command.extend(['--download', 'rcm', 'mts_preboot_si', '0x4000F000'])

    command.extend(['--download', 'rcm', values['--applet'], '0', '0'])
    run_command(command)

    info_print('Signing RCM messages')
    command = exec_file('tegrasign')
    command.extend(['--key', values['--key']])
    command.extend(['--list', tegrarcm_values['--list']])
    command.extend(['--pubkeyhash', tegrasign_values['--pubkeyhash']])
    run_command(command)

    info_print('Copying signature to RCM mesages')
    command = exec_file('tegrarcm')
    command.extend(['--chip', values['--chip']])
    command.extend(['--updatesig', tegrarcm_values['--signed_list']])

    if os.path.isfile(tegrasign_values['--pubkeyhash']):
        command.extend(['--pubkeyhash', tegrasign_values['--pubkeyhash']])

    run_command(command)

