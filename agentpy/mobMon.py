import tkinter as tk
import tkinter.ttk as ttk
import copy
import math

class MonitorWin:
    def __init__(self, configs=None, mode=None, on_config_update=None):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.quit_callback)
        self.win = tk.Frame(master=self.root, width=500, height=300)
        self.win.winfo_toplevel().title("Config")
        # self.win.title('Agent Config')
        # self.win.bind("<Button-1>", self.click_callback)
        # self.win.protocol("WM_DELETE_WINDOW", self.onMonitorWindowClose)
        self.win.pack()
        self.label_map = {}
        self.default_configs = copy.deepcopy(configs)
        self.configs = copy.deepcopy(configs)
        self.notebook = None
        self.current_mode = mode
        self.on_config_update = on_config_update
        self.__create_tabs(self.win, self.configs, mode)

    def __del__(self):
        self.win.destroy()

    def __create_tabs(self, parent_win, configs, default_mode):
        """Create a tab for each config"""
        labelFrame = tk.LabelFrame(parent_win, text='', padx=2, pady=2)
        labelFrame.pack(fill='x', padx=4, pady=4)
        notebook = ttk.Notebook(labelFrame)
        default_tab = 0
        for idx, mode in enumerate(configs):
            if mode == default_mode:
                default_tab = idx
            f = tk.Frame(notebook)
            notebook.add(f, text=mode)
            row = 0
            for k, v in configs[mode].items():
                self.__create_sliders(f, mode, k, v, row)
                row += 1
        notebook.select(default_tab)
        notebook.bind('<<NotebookTabChanged>>', self.tab_changed)
        notebook.pack()
        self.notebook = notebook

    # def __get_current_tab_mode(self):
    #     tab_id = self.notebook.index(self.notebook.select())
    #     return list(self.default_configs.keys())[tab_id]

    def tab_changed(self, _):
        selected_mode = self.notebook.tab('current')['text']
        if selected_mode != self.current_mode:
            self.on_config_update(self.configs, selected_mode)
            self.current_mode = selected_mode

    def __get_config_key(self, config_name, config_key):
        return config_name + ':' + config_key

    def __format_value(self, value):
        # return '%8.3f' % (value)
        return '{:06.2f}'.format(value)

    def __create_sliders(self, parent, config_name, config_key, value, row):
        tk.Label(parent, text=config_key).grid(row=row, column=0, sticky=tk.E)
        if type(value) is not str:
            label = tk.Label(parent, text=self.__format_value(value))
            label.grid(row=row, column=1, sticky=tk.W, pady=5)
            slider = tk.Scale(parent, from_=0, to=20, length=150, orient=tk.HORIZONTAL, showvalue=0, 
                command=lambda v: self.slider_callback(v, config_name, config_key))
            slider.set(10)
            slider.grid(row=row, column=2, sticky=tk.W, pady=5)
            self.label_map[self.__get_config_key(config_name, config_key)] = label
        else:
            label = tk.Label(parent, text=value)
            label.grid(row=row, column=2, sticky=tk.W, pady=5)

    def slider_callback(self, value, config_name, key):
        self.configs[config_name][key] = self.default_configs[config_name][key] * math.pow(1.2, int(value) - 10)
        self.label_map[self.__get_config_key(config_name, key)].config(text=self.__format_value(self.configs[config_name][key]))
        if self.on_config_update is not None:
            self.on_config_update(self.configs, self.current_mode)

    def update(self):
        try:
            self.win.update()
        except:
            print('dialog error')

    def position(self, x, y):
        """ Move monitor window to the given location. """
        self.win.lift()
        self.win.minsize(450, 100)
        self.win.geometry('+%d+%d'%(x, y))
        self.win.update()

    def quit_callback(self):
        pass

