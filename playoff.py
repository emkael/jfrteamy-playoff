import traceback

from jfr_playoff.filemanager import PlayoffFileManager
from jfr_playoff.generator import PlayoffGenerator
from jfr_playoff.settings import PlayoffSettings


def main():

    interactive = False

    try:
        import argparse
        arg_parser = argparse.ArgumentParser(
            description='Generate play-off HTML for JFR Teamy tournaments')
        output_args = arg_parser.add_mutually_exclusive_group()
        output_args.add_argument('-v', '--verbose', action='store_true',
                                 help='display info on STDERR')
        output_args.add_argument('-vv', '--debug', action='store_true',
                                 help='display debug info on STDERR')
        output_args.add_argument('-q', '--quiet', action='store_true',
                                 help='suppress warnings on STDERR')
        arg_parser.add_argument('config_file', metavar='JSON_FILE',
                                help='path to config JSON file',
                                type=str, nargs='?', default=None)
        arguments = arg_parser.parse_args()

        settings = PlayoffSettings(arguments.config_file)
        interactive = settings.interactive

        generator = PlayoffGenerator(settings)
        content = generator.generate_content()

        file_manager = PlayoffFileManager(settings)
        file_manager.write_content(content)
        file_manager.copy_scripts()
        file_manager.send_files()
    except SystemExit:
        interactive = False
        raise
    except:
        print traceback.format_exc()
    finally:
        if interactive:
            raw_input('Press any key to continue...')

if __name__ == '__main__':
    main()
