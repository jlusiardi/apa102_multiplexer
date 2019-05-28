import os
import jinja2
import argparse


def run_integration(script_file, entity):
    parser = argparse.ArgumentParser()
    parser.add_argument('--map-only', dest='map_only', action='store_true')
    parser.add_argument('--skip-programming', dest='skip_programming', action='store_true')
    parser.add_argument('--permanent', dest='permanent', action='store_true', help='write into Serial Flash')
    args = parser.parse_args()

    # calculate entity name
    entity_name = os.path.splitext(os.path.basename(script_file))[0]

    # create path for integration test for entity
    path = os.path.join('..', 'integration_tests', entity_name)
    try:
        os.stat(path)
    except FileNotFoundError:
        os.mkdir(path)

    # convert entity to VHDL
    entity.convert(hdl='VHDL', path=path, name=entity_name, initial_values=True)

    # create qsf file from template
    with open('template.qsf', 'r') as template_file:
        template = jinja2.Template(template_file.read())
        with open(os.path.join(path, entity_name + '.qsf'), 'w') as project_file:
            project_file.write(template.render(ENITIYNAME=entity_name))

    import subprocess

    a = subprocess.run(['quartus_map', '--64bit', entity_name], cwd=path)
    if a.returncode != 0:
        exit(a.returncode)
    if args.map_only:
        return
    a = subprocess.run(['quartus_fit', '--64bit', entity_name], cwd=path)
    if a.returncode != 0:
        exit(a.returncode)
    a = subprocess.run(['quartus_asm', '--64bit', entity_name], cwd=path)
    if a.returncode != 0:
        exit(a.returncode)
    a = subprocess.run(['quartus_sta', '--64bit', entity_name], cwd=path)
    if a.returncode != 0:
        exit(a.returncode)

    path = os.path.join('..', 'integration_tests', entity_name, 'output_files')
    try:
        os.stat(path)
    except FileNotFoundError:
        os.mkdir(path)

    if not args.skip_programming:
        if not args.permanent:
            # create cdf file from template
            with open('template.cdf', 'r') as template_file:
                template = jinja2.Template(template_file.read())
                with open(os.path.join(path, entity_name + '.cdf'), 'w') as project_file:
                    project_file.write(template.render(ENITIYNAME=entity_name))
            a = subprocess.run(
                ['quartus_pgm', '--64bit', '-c', 'USB-Blaster(Altera)', '{entity}.cdf'.format(entity=entity_name)],
                cwd=path)
            if a.returncode != 0:
                exit(a.returncode)
        else:
            # write cdf file for flashing the serial eeprom
            with open('template_AS.cdf', 'r') as template_file:
                template = jinja2.Template(template_file.read())
                with open(os.path.join(path, entity_name + '_as.cdf'), 'w') as project_file:
                    project_file.write(template.render(ENITIYNAME=entity_name))
            a = subprocess.run(
                ['quartus_pgm', '--64bit', '-c', 'USB-Blaster(Altera)', '{entity}.cdf'.format(entity=entity_name)],
                cwd=path)
            if a.returncode != 0:
                exit(a.returncode)

