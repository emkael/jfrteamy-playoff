from PyInstaller.utils.hooks import collect_submodules
hiddenimports = (
    collect_submodules('jfr_playoff.data.tournament') +
    collect_submodules('jfr_playoff.data.match')
)
