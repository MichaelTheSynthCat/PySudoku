from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import copy
import csv
import os
import random
import time
from squareboard_class import *  # custom classes
from edgeboard_class import *
from cornerboard_class import *

# constants defining sizes of UI in different levels of sudoku
ui_size = {2: {'sqdimension': 60, 'linewidth': 10, 'charsize': 55},
           3: {'sqdimension': 45, 'linewidth': 5, 'charsize': 38},
           4: {'sqdimension': 30, 'linewidth': 4, 'charsize': 22},
           5: {'sqdimension': 20, 'linewidth': 3, 'charsize': 14},
           6: {'sqdimension': 15, 'linewidth': 2, 'charsize': 10}}
ui_font = 'Arial', 14


class ControllerButton(Button): # digit selector button 
    def __init__(self, master, c, r, eraser=False):
        Button.__init__(self, master, text=str(r*game.chartsize+c+1), command=self.pressed, font=('Arial', 30), width=2)
        if eraser:
            self['text'] = 'Erase'
            self['width'] = 6
            self.num = 0
            self.grid(column=c, row=r, columnspan=10)
        else:
            self.num = r*game.chartsize+c+1
            self.grid(column=c+40, row=1+r)

    def pressed(self): 
        controller.reset_buttons()
        controller.selected_num = self.num # sets selected digit
        self['relief'] = 'sunken'

    def set_relief(self):
        self['relief'] = 'raised'


class AskSize(Toplevel): # window asking for size of sudoku square x*x, classic sudoku has 3*3
    def __init__(self):
        global ask
        try:
            ask.cancel()
        except NameError:
            pass
        Toplevel.__init__(self, main)
        ask = self
        self.title('Enter size')
        self.value = StringVar(value=generatesize)
        Label(self, text='Region size').grid(column=0, row=0)
        spin = Spinbox(self, textvariable=self.value, width=7, from_=2, to=6)
        spin.grid(column=1, row=0)
        spin.focus()
        Label(self, text='After entering a new size,\ngenerate a new level').grid(column=0, row=50, columnspan=2)
        Button(self, text='Cancel', command=self.cancel).grid(column=0, row=100)
        Button(self, text='Confirm', command=self.confirm).grid(column=1, row=100)

        self.bind('<Return>', lambda e: self.confirm())

    def confirm(self):
        global generatesize
        value = int(self.value.get())
        if value > 6:
            value = 6
        if value < 2:
            value = 2
        generatesize = value
        self.destroy()
        del self

    def cancel(self):
        self.destroy()
        del self


class Timer(Label):
    def __init__(self, master):
        Label.__init__(self, master, bg="#c0c0c0", font=ui_font)
        self.showtime = StringVar(value='00:00')
        self['textvariable'] = self.showtime
        self.time = 0
        self.starttime = 0
        self.time_process = 0
        self.reset()

    def reset(self):
        self.starttime = time.perf_counter()
        self.time_process = self.after(100, self.count_time)

    def count_time(self):
        self.time = time.localtime(time.perf_counter() - self.starttime)
        text = str(self.time.tm_min).zfill(2)+':'+str(self.time.tm_sec).zfill(2)
        self.showtime.set(text)
        self.time_process = self.after(100, self.count_time)

    def __del__(self):
        self.after_cancel(self.time_process)


class Main(Frame):  # mainframe
    def __init__(self):
        Frame.__init__(self, tk, bg="#c0c0c0")
        self.grid(column=0, row=0)


class Menubar(Menu):  # menubar class
    def __init__(self):
        Menu.__init__(self, tk)
        tk['menu'] = self
        tk.option_add('*tearOff', FALSE)
        self.tabs = {'Main': Menu(self), 'Play': Menu(self), 'Editor': Menu(self), 'Options': Menu(self)}
        for x in iter(self.tabs):
            self.add_cascade(menu=self.tabs[x], label=x)
        self.dif = StringVar(value=difficulty)
        self.rtc = StringVar(value='False')
        self.tabs['Main'].add_command(label='Restart', command=game.restart)
        self.tabs['Main'].add_command(label='Quicksave', command=game.save_quicksave)
        self.tabs['Main'].add_command(label='Load quicksave', command=game.load_quicksave)
        self.tabs['Main'].add_command(label='Find solution', command=game.show_solution)
        self.tabs['Main'].add_command(label='Exit', command=tk.destroy)
        self.tabs['Play'].add_command(label='Open', command=file_open)
        self.tabs['Play'].add_command(label='Save', command=file_save)
        self.tabs['Play'].add_command(label='Generate', command=lambda: game.generate_level(generatesize, difficulty))
        self.tabs['Play'].add_checkbutton(label='Real time check', variable=self.rtc, onvalue='True', offvalue='False', command= self.set_rtcheck)
        self.tabs['Editor'].add_command(label='Create empty level template', command=lambda: game.design_new_level(generatesize))
        self.tabs['Editor'].add_command(label='Open level template', command=lambda: game.open_level_template())
        self.tabs['Editor'].add_command(label='Save level template', command=lambda: game.save_level_template())
        self.tabs['Editor'].add_command(label='Generate solved level', command=lambda: game.generate_solved_level(generatesize, start=True))
        self.tabs['Editor'].add_command(label='Play current level template', command=lambda: game.play_current_design())
        self.tabs['Options'].add_command(label='Set sudoku size', command=AskSize)
        self.difset = Menu(self.tabs['Options'])
        self.tabs['Options'].add_cascade(menu=self.difset, label='Generation difficulty')
        self.difset.add_radiobutton(label='Easy', variable=self.dif, value=0.4, command=self.set_difficulty)
        self.difset.add_radiobutton(label='Normal', variable=self.dif, value=0.55, command=self.set_difficulty)
        self.difset.add_radiobutton(label='Hard', variable=self.dif, value=0.65, command=self.set_difficulty)
        self.difset.add_radiobutton(label='Extreme', variable=self.dif, value=0.75, command=self.set_difficulty)
        self.difset.add_radiobutton(label='Impossible', variable=self.dif, value=0.85, command=self.set_difficulty)
        self.add_command(label='Help', command=help_dialog)

    def set_difficulty(self):
        global difficulty
        difficulty = float(self.dif.get())

    def set_rtcheck(self):
        game.rtcheck = eval(self.rtc.get())
        controller.provide_status()


class DataBank:  # data storage class
    def __init__(self, columns, rows,
                 colors={'squares': '#ffffff', 'edges': '#000000', 'corners': '#000000', 'background': '#ffffff'},
                 symbol='Char'):
        # create storage classes for squares, edges and corners
        self.squareboard = SquareBoard(columns, rows, color=colors['squares'], background=colors['background'], symbol=symbol)
        self.edgeboard_horizontal = Edgeboard(columns, rows+1, orient="horizontal", color=colors['edges'])
        self.edgeboard_vertical = Edgeboard(columns+1, rows, orient="vertical", color=colors['edges'])
        self.cornerboard = Cornerboard(columns+1, rows+1, color=colors['corners'])
        self.types = {'s': self.squareboard, 'he': self.edgeboard_horizontal,
                      've': self.edgeboard_vertical, 'c': self.cornerboard}
        self.chart = [columns, rows]
        self.redesign()

    def redesign(self): # apply color theme
        for r in range(self.chart[1]+1):
            for c in range(self.chart[0]):
                if r % game.chartsize != 0:
                    self.edgeboard_horizontal.data[r][c].color = 'grey'
        for r in range(self.chart[1]):
            for c in range(self.chart[0]+1):
                if c % game.chartsize != 0:
                    self.edgeboard_vertical.data[r][c].color = 'grey'


class GraphicEngine(Canvas):  # engine for viewing squareboards
    def __init__(self, columns, rows, sqdimension=50, linewidth=7, charsize=None):
        width = linewidth*(columns+1)+columns*sqdimension+10
        height = linewidth*(rows+1)+rows*sqdimension+10
        Canvas.__init__(self, main, width=width, height=height)
        self.grid(column=20, row=0, columnspan=10, rowspan=50, padx=10, pady=10)
        self.chart = [columns, rows]  # number of columns and rows
        self.dimensions = [width, height]  # width and height in pixels
        self.sqdimension = sqdimension  # dimension of a square in pixels
        self.linewidth = linewidth  # width of a line in pixels
        if charsize is None:
            self.charsize = self.sqdimension
        else:
            self.charsize = charsize

        tk.bind('<KeyPress>', lambda event: controller.insert_number(event))
        self.bind('<1>', lambda event: controller.left_click(event))
        self.bind('<2>', lambda event: controller.middle_click(event))
        self.bind('<3>', lambda event: controller.right_click(event))
        self.bind('<MouseWheel>', lambda event: controller.mousewheel(event))
        self.bind('<Motion>', lambda event: self.highlight_cursor(event))

    def render(self):  # render the squareboard
        self.delete('last')
        # squares
        for r in range(self.chart[1]):
            for c in range(self.chart[0]):
                if data.squareboard.data[r][c].symbol == 'None':
                    self.create_rectangle(self.linewidth + c * (self.sqdimension + self.linewidth) + 5,
                                          self.dimensions[1] - self.linewidth - r * (self.sqdimension + self.linewidth) - 5,
                                          (c + 1) * (self.sqdimension + self.linewidth) + 5,
                                          self.dimensions[1] - (r + 1) * (self.sqdimension + self.linewidth) - 5,
                                          fill=data.squareboard.data[r][c].color,
                                          outline=data.squareboard.data[r][c].color, tags='last')
                else:
                    self.create_rectangle(self.linewidth + c * (self.sqdimension + self.linewidth) + 5,
                                          self.dimensions[1]-self.linewidth-r*(self.sqdimension+self.linewidth) - 5,
                                          (c + 1) * (self.sqdimension + self.linewidth) + 5,
                                          self.dimensions[1] - (r + 1) * (self.sqdimension + self.linewidth) - 5,
                                          fill=data.squareboard.data[r][c].background,
                                          outline=data.squareboard.data[r][c].background, tags='last')
        self.render_chars()
        # horizontal edges
        for r in range(self.chart[1]+1):
            for c in range(self.chart[0]):
                for e in range(self.linewidth):
                    self.create_line(self.linewidth+c*(self.sqdimension+self.linewidth)+5,
                                     self.dimensions[1]-r*(self.sqdimension+self.linewidth)-e-5,
                                     (c+1)*(self.sqdimension+self.linewidth)+5,
                                     self.dimensions[1]-r*(self.sqdimension+self.linewidth)-e-5,
                                     fill=data.edgeboard_horizontal.data[r][c].color, tags='last')
        # vertical edges
        for r in range(self.chart[1]):
            for c in range(self.chart[0]+1):
                for e in range(self.linewidth):
                    self.create_line(c*(self.sqdimension+self.linewidth)+e+5,
                                     self.dimensions[1]-self.linewidth-r*(self.sqdimension+self.linewidth)-5,
                                     c*(self.sqdimension+self.linewidth)+e+5,
                                     self.dimensions[1]-(r+1)*(self.sqdimension+self.linewidth)-5,
                                     fill=data.edgeboard_vertical.data[r][c].color, tags='last')
        # corners
        for r in range(self.chart[1]+1):
            for c in range(self.chart[0]+1):
                self.create_rectangle(c*(self.sqdimension+self.linewidth)+5,
                                      self.dimensions[1]-r*(self.sqdimension+self.linewidth)-5,
                                      c*(self.sqdimension+self.linewidth)+self.linewidth-1+5,
                                      self.dimensions[1]-r*(self.sqdimension+self.linewidth)-self.linewidth+1-5,
                                      fill=data.cornerboard.data[r][c].color,
                                      outline=data.cornerboard.data[r][c].color, tags='last')
        self.tag_raise('char')

    def render_chars(self):
        self.delete('char', 'select', 'solution')
        for r in range(self.chart[1]):
            for c in range(self.chart[0]):
                if data.squareboard.data[r][c].symbol == 'Char':
                    if game.chart[r][c][-1] == 'd':
                        color = 'black'
                    else:
                        color = 'blue'
                    char = game.chart[r][c][:-1]
                    if char == '0':
                        continue
                    self.create_text(self.linewidth + c * (self.sqdimension + self.linewidth) + 5 + self.sqdimension//2,
                                     self.dimensions[1] - (r + 1) * (self.sqdimension + self.linewidth) - 5 + self.sqdimension//2+self.sqdimension//25,
                                     text=char, fill=color, font=('Arial', self.charsize),
                                     tags=('last', 'char', 'p'+str(c)+'-'+str(r)))

    def char(self, char, color, c, r, tag):
        self.create_text(self.linewidth + c * (self.sqdimension + self.linewidth) + 5 + self.sqdimension//2,
                         self.dimensions[1] - (r + 1) * (self.sqdimension + self.linewidth) - 5 + self.sqdimension//2+self.sqdimension//25,
                         text=char, fill=color, font=('Arial', self.charsize),
                         tags=('last', 'char', 'p'+str(c)+'-'+str(r), tag))

    def show_select(self, c, r):
        self.delete('select')
        self.create_rectangle(self.linewidth + c * (self.sqdimension + self.linewidth) + 5,
                              self.dimensions[1]-self.linewidth-r*(self.sqdimension+self.linewidth) - 5,
                              (c + 1) * (self.sqdimension + self.linewidth) + 5,
                              self.dimensions[1] - (r + 1) * (self.sqdimension + self.linewidth) - 5,
                              outline='yellow', width=3, tags=('last', 'select'))

    def highlight_cursor(self, event):
        pos = find_square(event)
        if pos is None:
            self.delete('pointed')
            return
        c, r = pos[0], pos[1]
        if legal_edit(c, r):
            color = 'cyan'
        else:
            color = 'blue'
        self.delete('pointed')
        self.create_rectangle(self.linewidth + c * (self.sqdimension + self.linewidth) + 5,
                              self.dimensions[1]-self.linewidth-r*(self.sqdimension+self.linewidth) - 5,
                              (c + 1) * (self.sqdimension + self.linewidth) + 5,
                              self.dimensions[1] - (r + 1) * (self.sqdimension + self.linewidth) - 5,
                              outline=color, width=3, tags=('last', 'pointed'))
        self.tag_raise('select')


class Game:
    def __init__(self):
        self.type = ''
        self.chartsize = 0
        self.chart = []
        self.quicksave = []
        self.rtcheck = False  # real time check

    def load(self, path): # load a level file
        self.change_type('Play')
        self.chart = []
        self.quicksave = []
        with open(path, 'r', newline='') as file:
            reader = csv.reader(file)
            self.chartsize = int(next(reader)[0])
            recreate_environment(self.chartsize)
            for r in range(self.dim()):
                line = next(reader)
                row = []
                for c in range(self.dim()):
                    row.append(line[c])
                self.chart.append(row)
        try:
            workspace.render_chars()
        except NameError:
            pass
        change_title(self.type, path)
        workspace.render()
        self.save_quicksave()
        timer.reset()
        controller.provide_status()

    def save(self, path): # save a level file
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.chartsize])
            for r in range(self.dim()):
                writer.writerow(self.chart[r])

    def restart(self):
        self.quicksave = []
        for r in range(self.dim()):
            for c in range(self.dim()):
                if self.chart[r][c][-1] == 'i':
                    self.chart[r][c] = '0i'
        workspace.render_chars()
        controller.selected_square = None
        timer.reset()
        controller.provide_status()

    def save_quicksave(self):
        self.quicksave = copy.deepcopy(self.chart)
        controller.provide_status()

    def load_quicksave(self):
        self.chart = copy.deepcopy(self.quicksave)
        workspace.render_chars()

    def generate_level(self, size, empty):
        if not self.generate_solved_level(size, start=True):
            return
        self.change_type('Play')

        places = int(empty*self.dim()**2)
        full = []
        for r in range(self.dim()):
            for c in range(self.dim()):
                full.append(r*self.dim()+c)
        random.shuffle(full)
        for x in range(places):
            r, c = full[x]//self.dim(), full[x] % self.dim()
            self.chart[r][c] = '0i'

        change_title(self.type)
        workspace.render_chars()
        self.save_quicksave()
        timer.reset()
        controller.provide_status()

    def design_new_level(self, size):
        self.change_type('Edit')
        self.quicksave = []
        self.chartsize = size
        self.change_type('Edit')
        self.chart = []
        for r in range(self.dim()):
            row = []
            for c in range(self.dim()):
                row.append('0d')
            self.chart.append(row)

        change_title(self.type)
        recreate_environment(size)
        workspace.render()
        timer.reset()
        controller.provide_status()

    def open_level_template(self):
        path = filedialog.askopenfilename(initialdir=cwd,
                                          filetypes=(("All files", "*.*"),
                                                     ("PySudoku Level Template *.pslt", "*.pslt")))
        if path != '':
            self.change_type('Edit')
            self.quicksave = []
            self.chart = []
            with open(path, 'r', newline='') as file:
                reader = csv.reader(file)
                self.chartsize = int(next(reader)[0])
                recreate_environment(self.chartsize)
                for r in range(self.dim()):
                    line = next(reader)
                    row = []
                    for c in range(self.dim()):
                        row.append(line[c])
                    self.chart.append(row)
                workspace.render()
            change_title(self.type, path)
            timer.reset()
            controller.provide_status()

    def save_level_template(self):
        path = filedialog.asksaveasfilename(initialdir=cwd,
                                            filetypes=(("All files", "*.*"),
                                                       ("PySudoku Level Template *.pslt", "*.pslt")))
        if path != '':
            if path[-5:] != '.pslt':
                path += '.pslt'
            for r in range(self.dim()):
                for c in range(self.dim()):
                    if self.chart[r][c][0] == '0':
                        self.chart[r][c] = '0i'
            with open(path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([self.chartsize])
                for r in range(self.dim()):
                    writer.writerow(self.chart[r])

    def generate_solved_level(self, size, start=False):
        if size > 4 and start:
            ans = messagebox.askyesno(message='Size is too big, it may take a long time.\nDo you want to continue?',
                                      icon='question', title='Warning')
            if not ans:
                return False
        self.chartsize = size
        chart = []
        for r in range(self.dim()):
            row = []
            for c in range(self.dim()):
                row.append(0)
            chart.append(row)

        # create diagonal matrixes
        for i in range(size):
            nums = [x for x in range(1, self.dim()+1)]
            random.shuffle(nums)
            for j in range(self.dim()):
                chart[i*size+j//size][i*size+j % size] = nums[j]
        self.change_type('Edit')
        self.quicksave = []
        solved = Solver(chart)
        solved.find_solution(0, 0)
        self.chart = solved.convert_to_game()
        for r in range(self.dim()):
            for c in range(self.dim()):
                if self.chart[r][c][0] == '?':
                    self.generate_solved_level(size)
                    return True
        change_title(self.type)
        recreate_environment(size)
        workspace.render()
        timer.reset()
        controller.provide_status()
        return True

    def play_current_design(self):
        for r in range(self.dim()):
            for c in range(self.dim()):
                if self.chart[r][c][0] == '0':
                    self.chart[r][c] = '0i'
        self.change_type('Play')
        self.save_quicksave()
        change_title(self.type)
        timer.reset()

    def show_solution(self):
        if game.chartsize > 3:
            ans = messagebox.askyesno(message='Size is too big, it may take a long time.\nDo you want to continue?',
                                      icon='question', title='Warning')
            if not ans:
                return False
        chart = copy.deepcopy(self.chart)
        for r in range(self.dim()):
            for c in range(self.dim()):
                if chart[r][c][-1] == 'i':
                    chart[r][c] = '0i'
        solved = Solver(chart, convert=True)
        solved.find_solution(0, 0)
        chart = solved.convert_to_game()
        for r in range(self.dim()):
            for c in range(self.dim()):
                if self.chart[r][c][-1] == 'i':
                    workspace.char(chart[r][c][:-1], 'green', c, r, 'solution')

    def change_type(self, _type):
        if _type == 'Play':
            self.type = 'Play'
            tk.menu.tabs['Main'].entryconfigure(0, state=NORMAL)
            tk.menu.tabs['Main'].entryconfigure(1, state=NORMAL)
            tk.menu.tabs['Main'].entryconfigure(2, state=NORMAL)
            tk.menu.tabs['Main'].entryconfigure(3, state=NORMAL)
            tk.menu.tabs['Play'].entryconfigure(1, state=NORMAL)
            tk.menu.tabs['Editor'].entryconfigure(2, state=DISABLED)
            tk.menu.tabs['Editor'].entryconfigure(4, state=DISABLED)
        if _type == 'Edit':
            self.type = 'Edit'
            tk.menu.tabs['Main'].entryconfigure(0, state=DISABLED)
            tk.menu.tabs['Main'].entryconfigure(1, state=DISABLED)
            tk.menu.tabs['Main'].entryconfigure(2, state=DISABLED)
            tk.menu.tabs['Main'].entryconfigure(3, state=DISABLED)
            tk.menu.tabs['Play'].entryconfigure(1, state=DISABLED)
            tk.menu.tabs['Editor'].entryconfigure(2, state=NORMAL)
            tk.menu.tabs['Editor'].entryconfigure(4, state=NORMAL)

    def numtype(self):
        if self.type == 'Play':
            return 'i'
        if self.type == 'Edit':
            return 'd'

    def dim(self):
        return self.chartsize**2


class Controller(Frame): # handles user input
    def __init__(self):
        Frame.__init__(self, main, bg="#c0c0c0")
        self.grid(column=40, row=0)
        self.selected_num = None
        self.selected_square = None
        self.empty_places = 0
        self.buttons = []

    def create_buttons(self, size):
        if len(self.buttons) > 0:
            for x in self.buttons:
                x.destroy()
        self.buttons = []
        self.buttons.append(ControllerButton(self, c=40, r=0, eraser=True))
        for r in range(size):
            for c in range(size):
                self.buttons.append(ControllerButton(self, c=c, r=r))

    def insert_number(self, event):
        if self.selected_square is None:
            return
        if event.keysym_num in (65535, 65288):
            game.chart[self.selected_square[1]][self.selected_square[0]] = '0'+game.numtype()
        if 48 <= event.keysym_num <= 57:
            game.chart[self.selected_square[1]][self.selected_square[0]] = chr(event.keysym_num)+game.numtype()
        workspace.render_chars()
        self.selected_square = None
        self.provide_status()

    def left_click(self, event):
        pos = find_square(event)
        if pos is None:
            return
        if legal_edit(pos[0], pos[1]):
            self.selected_square = pos
            workspace.show_select(pos[0], pos[1])

    def right_click(self, event):
        pos = find_square(event)
        if pos is None:
            return
        if self.selected_num is None:
            return
        if legal_edit(pos[0], pos[1]):
            game.chart[pos[1]][pos[0]] = str(self.selected_num)+game.numtype()
            workspace.render_chars()
        self.selected_square = None
        self.provide_status()

    def middle_click(self, event):
        pos = find_square(event)
        if pos is None:
            return
        if legal_edit(pos[0], pos[1]):
            game.chart[pos[1]][pos[0]] = '0'+game.numtype()
            workspace.render_chars()
        self.selected_square = None
        self.provide_status()

    def mousewheel(self, event):
        pos = find_square(event)
        if pos is None:
            return
        if legal_edit(pos[0], pos[1]):
            num = int(game.chart[pos[1]][pos[0]][:-1])
            if event.delta > 0:
                num += 1
                if num > game.dim():
                    num = 0
            else:
                num -= 1
                if num < 0:
                    num = game.dim()
            game.chart[pos[1]][pos[0]] = str(num)+game.numtype()
            workspace.render_chars()
        self.selected_square = None
        self.provide_status()

    def count_empty_places(self):
        self.empty_places = 0
        for r in range(game.dim()):
            for c in range(game.dim()):
                if game.chart[r][c][-1] == 'i':
                    self.empty_places += 1

    def provide_status(self):
        if game.type == 'Play':
            self.count_empty_places()
            empty = 0
            for r in range(game.dim()):
                for c in range(game.dim()):
                    if game.chart[r][c] == '0i':
                        empty += 1
            try:
                statusframe.progressbar['value'] = (self.empty_places-empty)/self.empty_places
                solver = Solver(game.chart, convert=True)
                if solver.check_grid():
                    messagebox.showinfo(message='You won!')
            except ZeroDivisionError:
                messagebox.showinfo(message='Already completed level!')
        else:
            statusframe.progressbar['value'] = 1

    def reset_buttons(self):
        for x in self.buttons:
            x.set_relief()


class Status(Frame):
    def __init__(self):
        global timer
        Frame.__init__(self, main, bg="#c0c0c0")
        self.grid(column=40, row=10)
        Label(self, text='Elapsed time:', bg="#c0c0c0", font=ui_font).grid(column=40, row=10, sticky=W)
        timer = Timer(self)
        timer.grid(column=41, row=10, sticky=E)
        Label(self, text='Progress:', bg="#c0c0c0", font=ui_font).grid(column=40, row=11, sticky=W)
        self.progress = StringVar(value=0)
        self.progressbar = ttk.Progressbar(self, orient=HORIZONTAL, length=150,
                                           mode='determinate', maximum=1, value=0)
        self.progressbar.grid(column=40, row=12, columnspan=2)


class Solver: # checks whether digits inserted by user correspond to sudoku's rules and solves sudoku level
    def __init__(self, chart, convert=False):
        self.chart = copy.deepcopy(chart)
        self.dim = len(self.chart)
        self.chartsize = int(self.dim**(1/2))
        self.status_window = None
        if convert:
            self.convert_to_solver()

    def find_solution(self, r, c):
        if c >= self.dim:
            c = 0
            r += 1
        if r >= self.dim:
            return True
        if self.chart[r][c] == 0:
            nums = [x for x in range(1, self.dim+1)]
            random.shuffle(nums)
            for n in nums:
                if self.check_matrix(n, r, c) and self.check_row(n, r, c) and self.check_column(n, r, c):
                    self.chart[r][c] = n
                    if self.find_solution(r, c+1):
                        return True
                    else:
                        self.chart[r][c] = 0
            return False
        else:
            if self.find_solution(r, c+1):
                return True
            else:
                return False

    def check_grid(self):
        ok = True
        for r in range(self.dim):
            for c in range(self.dim):
                num = self.chart[r][c]
                if not (self.check_matrix(num, r, c) and self.check_row(num, r, c) and self.check_column(num, r, c)):
                    ok = False
                    if num != 0 and game.chart[r][c][-1] == 'i' and game.rtcheck:
                        workspace.char(num, 'red', c, r, 'mistake')
        return ok

    def check_matrix(self, num, r, c):
        i, j = r // self.chartsize, c // self.chartsize
        for x in range(self.chartsize):
            for y in range(self.chartsize):
                if i*self.chartsize+x == r and j*self.chartsize+y == c:
                    continue
                if self.chart[i*self.chartsize+x][j*self.chartsize+y] == num:
                    return False
        return True

    def check_row(self, num, r, ic):
        for c in range(self.dim):
            if ic == c:
                continue
            if self.chart[r][c] == num:
                return False
        return True

    def check_column(self, num, ir, c):
        for r in range(self.dim):
            if ir == r:
                continue
            if self.chart[r][c] == num:
                return False
        return True

    def convert_to_solver(self):
        for r in range(self.dim):
            for c in range(self.dim):
                self.chart[r][c] = int(self.chart[r][c][:-1])

    def convert_to_game(self):
        chart = copy.deepcopy(self.chart)
        for r in range(self.dim):
            for c in range(self.dim):
                chart[r][c] = str(chart[r][c])+'d'
        return chart


def recreate_environment(size):
    global data, workspace
    controller.create_buttons(size)
    size = size**2
    try:
        workspace.destroy()
        del data, workspace
    except NameError:
        pass
    data = DataBank(size, size)
    workspace = GraphicEngine(data.chart[0], data.chart[1], sqdimension=ui_size[game.chartsize]['sqdimension'],
                              linewidth=ui_size[game.chartsize]['linewidth'],
                              charsize=ui_size[game.chartsize]['charsize'])


def legal_edit(c, r):
    if game.type == 'Edit':
        return True
    if game.chart[r][c][1] == 'd':
        return False
    else:
        return True


def find_square(event):  # calculate at which object cursor is pointing
    fx = event.x
    fy = workspace.dimensions[1] - event.y
    if fx > workspace.dimensions[0]-5 or fx < 5 or fy > workspace.dimensions[1]-5 or fy < 5:
        return None
    fx -= 5
    fy -= 5

    c = fx // (workspace.linewidth + workspace.sqdimension)
    r = fy // (workspace.linewidth + workspace.sqdimension)
    x = fx % (workspace.linewidth+workspace.sqdimension)
    y = fy % (workspace.linewidth+workspace.sqdimension)
    if y <= workspace.linewidth:
        xline = True
    else:
        xline = False
    if x <= workspace.linewidth:
        yline = True
    else:
        yline = False
    if xline and yline:
        _type = 'c'
    elif xline:
        _type = 'he'
    elif yline:
        _type = 've'
    else:
        _type = 's'
        return [c, r]


def console_info(chart):
    print()
    for row in chart:
        for column in row:
            print(str(column)+' ', end='')
        print()


def file_open():
    path = filedialog.askopenfilename(initialdir=cwd,
                                      filetypes=(("All files", "*.*"),
                                                 ("PySudoku Level Template *.pslt", "*.pslt"),
                                                 ('PySudoku Level Save *.psls', '*.psls')))
    if path != '':
        game.load(path=path)


def file_save():
    path = filedialog.asksaveasfilename(initialdir=cwd,
                                        filetypes=(("All files", "*.*"),
                                                   ('PySudoku Level Save *.psls', '*.psls')))
    if path != '':
        if path[-5:] != '.psls':
            path += '.psls'
        game.save(path=path)


def change_title(mode, path=None):
    title = 'PySudoku - '+mode
    if path is not None:
        suffix = path.rpartition('/')
        title += ': '+suffix[2]
    tk.title(title)


def help_dialog():
    global winhelp
    try:
        winhelp.destroy()
    except NameError:
        pass
    winhelp = Toplevel(tk)
    winhelp.title("PySudoku - Help")
    winhelp.resizable(False, False)
    text = Text(winhelp, height=40, width=110)
    text.grid()
    text.insert('1.0', """The Japanese Sudoku game generator, editor and solver for Windows and Linux.

--- How to play ---
I think I don't have to explain to you how sudoku works but rather how work with this application.
There are 3 different methods how to insert digits:
  1. LMB and Keypad
    Click with left mouse button on the desired cell, the cell should be in a yellow frame.
    Then enter a digit with your keyboard. DEL deletes the inserted number.
  2. RMB and virtual keypad
    Choose the desired digit on the virtual keypad on the right.
    Then click with right mouse button on the cell which should contain the digit.
  3. Mousewheel
    Point with the mouse cursor at the cell which should be filled.
    Scroll with the mouse wheel until the wanted digit is displayed.

--- Realtime check and auto-solve ---
You can turn on realtime check in on the menubar in section Play. With this option enabled, the collinding
cells will be highlighted. The level can also be automatically solved by the computer if you want to.
Check the Find solution button in Main menu.

--- Level generation ---
PySudoku can generate a whole new level. Search it on the menubar in section Play.

--- Level Editor ---
Make your own sudoku using the Editor on the menubar.

--- Looking for challenge ---
Sudoku veterans can turn on higher difficulty or play on bigger scale (4x4, 5x5, 6x6)!
Set it in Options and than generate or create a new level.

--- Quicksave --- 
You can make a quicksave at any time in the Main menu and come back to it when you screw up.

--- License and author ---
Author: Michal Krulich
License: GNU GPL 3.0
Github repository: https://github.com/MichaelTheSynthCat/PySudoku
""")
    text['state'] = DISABLED


if __name__ == '__main__':
    cwd = os.getcwd()
    generatesize = 3
    difficulty = 0.55
    game = Game()
    tk = Tk()
    tk.title("PySudoku")
    tk.resizable(False, False)
    tk.menu = Menubar()
    main = Main()
    controller = Controller()
    statusframe = Status()
    try:
        game.load(path='3x3 levels/3x3 level 1.pslt')
    except FileNotFoundError:
        game.generate_level(generatesize, difficulty)
    tk.mainloop()
