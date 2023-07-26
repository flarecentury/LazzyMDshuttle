from ipylab import JupyterFrontEnd


def jupyter_command(x):
    # method 1
    list_commands = ['completer:invoke',
                     'completer:select',
                     'tooltip:dismiss',
                     'apputils:activate-command-palette',
                     'apputils:load-statedb',
                     'apputils:reset',
                     'apputils:reset-on-load',
                     'apputils:print',
                     'apputils:run-first-enabled',
                     'apputils:run-all-enabled',
                     'docmanager:clone',
                     'docmanager:rename',
                     'docmanager:delete',
                     'docmanager:show-in-file-browser',
                     'docmanager:delete-file',
                     'docmanager:new-untitled',
                     'docmanager:open',
                     'docmanager:reload',
                     'docmanager:restore-checkpoint',
                     'docmanager:save',
                     'docmanager:save-all',
                     'docmanager:save-as',
                     'docmanager:toggle-autosave',
                     '__internal:context-menu-info',
                     'application:close',
                     'application:close-other-tabs',
                     'application:close-right-tabs',
                     'application:activate-next-tab',
                     'application:activate-previous-tab',
                     'application:activate-next-tab-bar',
                     'application:activate-previous-tab-bar',
                     'application:close-all',
                     'application:toggle-left-area',
                     'application:toggle-right-area',
                     'application:toggle-presentation-mode',
                     'application:set-mode',
                     'application:toggle-mode',
                     'apputils:toggle-header',
                     'launcher:create',
                     'statusbar:toggle',
                     'documentsearch:start',
                     'documentsearch:startWithReplace',
                     'documentsearch:highlightNext',
                     'documentsearch:highlightPrevious',
                     'help:about',
                     'help:launch-classic-notebook',
                     'help:jupyter-forum',
                     'apputils:change-theme',
                     'apputils:theme-scrollbars',
                     'apputils:change-font',
                     'apputils:incr-font-size',
                     'apputils:decr-font-size',
                     'docmanager:download',
                     'docmanager:open-browser-tab',
                     'htmlviewer:trust-html',
                     'imageviewer:zoom-in',
                     'imageviewer:zoom-out',
                     'imageviewer:reset-image',
                     'imageviewer:rotate-clockwise',
                     'imageviewer:rotate-counterclockwise',
                     'imageviewer:flip-horizontal',
                     'imageviewer:flip-vertical',
                     'imageviewer:invert-colors',
                     'rendermime:handle-local-link',
                     'inspector:open',
                     'extensionmanager:toggle',
                     'markdownviewer:open',
                     'markdownviewer:edit',
                     'settingeditor:open-json',
                     'settingeditor:revert',
                     'settingeditor:save',
                     'workspace-ui:save-as',
                     'workspace-ui:save',
                     'filebrowser:share-main',
                     'filebrowser:download',
                     'filebrowser:copy-download-link',
                     'filebrowser:activate',
                     'filebrowser:hide-main',
                     'filebrowser:open-browser-tab',
                     'filebrowser:open-url',
                     'settingeditor:open',
                     'filebrowser:delete',
                     'filebrowser:copy',
                     'filebrowser:cut',
                     'filebrowser:duplicate',
                     'filebrowser:go-to-path',
                     'filebrowser:go-up',
                     'filebrowser:open-path',
                     'filebrowser:open',
                     'filebrowser:paste',
                     'filebrowser:create-new-directory',
                     'filebrowser:create-new-file',
                     'filebrowser:create-new-markdown-file',
                     'filebrowser:rename',
                     'filebrowser:copy-path',
                     'filebrowser:shutdown',
                     'filebrowser:toggle-main',
                     'filebrowser:create-main-launcher',
                     'filebrowser:toggle-navigate-to-current-directory',
                     'filebrowser:toggle-last-modified',
                     'filebrowser:toggle-hidden-files',
                     'filebrowser:search',
                     'editmenu:undo',
                     'editmenu:redo',
                     'editmenu:clear-current',
                     'editmenu:clear-all',
                     'editmenu:go-to-line',
                     'filemenu:close-and-cleanup',
                     'filemenu:create-console',
                     'filemenu:shutdown',
                     'filemenu:logout',
                     'kernelmenu:interrupt',
                     'kernelmenu:reconnect-to-kernel',
                     'kernelmenu:restart',
                     'kernelmenu:restart-and-clear',
                     'kernelmenu:change',
                     'kernelmenu:shutdown',
                     'kernelmenu:shutdownAll',
                     'runmenu:run',
                     'runmenu:run-all',
                     'runmenu:restart-and-run-all',
                     'viewmenu:line-numbering',
                     'viewmenu:match-brackets',
                     'viewmenu:word-wrap',
                     'tabsmenu:activate-by-id',
                     'tabsmenu:activate-previously-used-tab',
                     'editmenu:open',
                     'filemenu:open',
                     'kernelmenu:open',
                     'runmenu:open',
                     'viewmenu:open',
                     'settingsmenu:open',
                     'tabsmenu:open',
                     'helpmenu:open',
                     'mainmenu:open-first',
                     'help:open',
                     'notebook:run-cell-and-select-next',
                     'notebook:run-cell',
                     'notebook:run-cell-and-insert-below',
                     'notebook:run-all-cells',
                     'notebook:run-all-above',
                     'notebook:run-all-below',
                     'notebook:render-all-markdown',
                     'notebook:restart-kernel',
                     'notebook:close-and-shutdown',
                     'notebook:trust',
                     'notebook:restart-clear-output',
                     'notebook:restart-and-run-to-selected',
                     'notebook:restart-run-all',
                     'notebook:clear-all-cell-outputs',
                     'notebook:clear-cell-output',
                     'notebook:interrupt-kernel',
                     'notebook:change-cell-to-code',
                     'notebook:change-cell-to-markdown',
                     'notebook:change-cell-to-raw',
                     'notebook:cut-cell',
                     'notebook:copy-cell',
                     'notebook:paste-cell-below',
                     'notebook:paste-cell-above',
                     'notebook:paste-and-replace-cell',
                     'notebook:delete-cell',
                     'notebook:split-cell-at-cursor',
                     'notebook:merge-cells',
                     'notebook:merge-cell-above',
                     'notebook:merge-cell-below',
                     'notebook:insert-cell-above',
                     'notebook:insert-cell-below',
                     'notebook:move-cursor-up',
                     'notebook:move-cursor-down',
                     'notebook:extend-marked-cells-above',
                     'notebook:extend-marked-cells-top',
                     'notebook:extend-marked-cells-below',
                     'notebook:extend-marked-cells-bottom',
                     'notebook:select-all',
                     'notebook:deselect-all',
                     'notebook:move-cell-up',
                     'notebook:move-cell-down',
                     'notebook:toggle-all-cell-line-numbers',
                     'notebook:enter-command-mode',
                     'notebook:enter-edit-mode',
                     'notebook:undo-cell-action',
                     'notebook:redo-cell-action',
                     'notebook:change-kernel',
                     'notebook:reconnect-to-kernel',
                     'notebook:change-cell-to-heading-1',
                     'notebook:change-cell-to-heading-2',
                     'notebook:change-cell-to-heading-3',
                     'notebook:change-cell-to-heading-4',
                     'notebook:change-cell-to-heading-5',
                     'notebook:change-cell-to-heading-6',
                     'notebook:hide-cell-code',
                     'notebook:show-cell-code',
                     'notebook:hide-all-cell-code',
                     'notebook:show-all-cell-code',
                     'notebook:hide-cell-outputs',
                     'notebook:show-cell-outputs',
                     'notebook:hide-all-cell-outputs',
                     'notebook:toggle-render-side-by-side-current',
                     'notebook:set-side-by-side-ratio',
                     'notebook:show-all-cell-outputs',
                     'notebook:enable-output-scrolling',
                     'notebook:disable-output-scrolling',
                     'notebook:select-last-run-cell',
                     'notebook:replace-selection',
                     'Collapsible_Headings:Toggle_Collapse',
                     'Collapsible_Headings:Collapse_All',
                     'Collapsible_Headings:Expand_All',
                     'notebook:create-new',
                     'help:licenses',
                     'help:licenses-refresh',
                     'help:license-report',
                     'terminal:create-new',
                     'terminal:open',
                     'terminal:refresh',
                     'terminal:increase-font',
                     'terminal:decrease-font',
                     'terminal:set-theme',
                     'notebook:toggle-autoclosing-brackets',
                     'completer:invoke-notebook',
                     'completer:select-notebook',
                     'logconsole:open',
                     'logconsole:add-checkpoint',
                     'logconsole:clear',
                     'logconsole:set-level',
                     'notebook:export-to-format',
                     'notebook:create-output-view',
                     'notebook:create-console',
                     'notebook:run-in-console',
                     'notebook:copy-to-clipboard',
                     'tooltip:launch-notebook',
                     'console:toggle-autoclosing-brackets',
                     'console:open',
                     'console:create',
                     'console:clear',
                     'console:run-unforced',
                     'console:run-forced',
                     'console:linebreak',
                     'console:replace-selection',
                     'console:interrupt-kernel',
                     'console:restart-kernel',
                     'console:close-and-shutdown',
                     'console:inject',
                     'console:change-kernel',
                     'console:interaction-mode',
                     '@jupyter-widgets/jupyterlab-manager:saveWidgetState',
                     'completer:invoke-console',
                     'completer:select-console',
                     'console:toggle-show-all-kernel-activity',
                     'tooltip:launch-console',
                     'fileeditor:change-font-size',
                     'fileeditor:toggle-line-numbers',
                     'fileeditor:toggle-line-wrap',
                     'fileeditor:change-tabs',
                     'fileeditor:toggle-match-brackets',
                     'fileeditor:toggle-autoclosing-brackets',
                     'fileeditor:toggle-autoclosing-brackets-universal',
                     'fileeditor:replace-selection',
                     'fileeditor:create-console',
                     'fileeditor:run-code',
                     'fileeditor:run-all',
                     'fileeditor:markdown-preview',
                     'fileeditor:create-new',
                     'fileeditor:create-new-markdown-file',
                     'fileeditor:undo',
                     'fileeditor:redo',
                     'fileeditor:cut',
                     'fileeditor:copy',
                     'fileeditor:paste',
                     'fileeditor:select-all',
                     'codemirror:change-theme',
                     'codemirror:change-keymap',
                     'codemirror:find',
                     'codemirror:go-to-line',
                     'codemirror:change-mode',
                     'completer:invoke-file',
                     'completer:select-file',
                     'tooltip:launch-file',
                     'toc:run-cells',
                     'debugger:restart-debug',
                     'debugger:inspect-variable',
                     'debugger:render-mime-variable',
                     'debugger:evaluate',
                     'debugger:continue',
                     'debugger:terminate',
                     'debugger:next',
                     'debugger:stepIn',
                     'debugger:stepOut',
                     'debugger:pause',
                     'jupyterlab-translation:en',
                     'sidebar:switch',
                     'help-menu-conda-env-MDa-py:banner',
                     'help-menu-conda-env-MDa-py:Python Reference',
                     'help-menu-conda-env-MDa-py:IPython Reference',
                     'help-menu-conda-env-MDa-py:NumPy Reference',
                     'help-menu-conda-env-MDa-py:SciPy Reference',
                     'help-menu-conda-env-MDa-py:Matplotlib Reference',
                     'help-menu-conda-env-MDa-py:SymPy Reference',
                     'help-menu-conda-env-MDa-py:pandas Reference',
                     'help-menu-conda-env-pycharm-MDAnalysis-py:banner',
                     'help-menu-conda-env-pycharm-MDAnalysis-py:Python Reference',
                     'help-menu-conda-env-pycharm-MDAnalysis-py:IPython Reference',
                     'help-menu-conda-env-pycharm-MDAnalysis-py:NumPy Reference',
                     'help-menu-conda-env-pycharm-MDAnalysis-py:SciPy Reference',
                     'help-menu-conda-env-pycharm-MDAnalysis-py:Matplotlib Reference',
                     'help-menu-conda-env-pycharm-MDAnalysis-py:SymPy Reference',
                     'help-menu-conda-env-pycharm-MDAnalysis-py:pandas Reference',
                     'help-menu-conda-env-structurefactor_spme-py:banner',
                     'help-menu-conda-env-structurefactor_spme-py:Python Reference',
                     'help-menu-conda-env-structurefactor_spme-py:IPython Reference',
                     'help-menu-conda-env-structurefactor_spme-py:NumPy Reference',
                     'help-menu-conda-env-structurefactor_spme-py:SciPy Reference',
                     'help-menu-conda-env-structurefactor_spme-py:Matplotlib Reference',
                     'help-menu-conda-env-structurefactor_spme-py:SymPy Reference',
                     'help-menu-conda-env-structurefactor_spme-py:pandas Reference']
    app = JupyterFrontEnd()
    if x == 'list':
        for i in list_commands:
            print(i)
    else:
        app.commands.execute(x)