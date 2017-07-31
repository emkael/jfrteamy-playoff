import traceback
from jfr_playoff.settings import PlayoffSettings
from jfr_playoff.generator import PlayoffGenerator
from jfr_playoff.filemanager import PlayoffFileManager

def main():

    try:
        s = PlayoffSettings()

        generator = PlayoffGenerator(s)
        content = generator.generate_content()

        file_manager = PlayoffFileManager(s)
        file_manager.write_content(content)
        file_manager.copy_scripts()
        file_manager.send_files()
    except:
        print traceback.format_exc()
    finally:
        if s.interactive:
            raw_input('Press any key to continue...')

if __name__ == '__main__':
    main()
