from PyQt5 import Qt, QtCore, QtWidgets as QW
import sys
import random
from itertools import product
from functools import reduce
import traceback  # Для отладки
import os  # Для отладки
from pathlib import Path  # Для отладки
from threading import Timer


MSIZES = ((9, 9), (16, 16), (16, 30))
FLAGS_CHARS_D = {'': 32, 'f': int('1f6a9', 16), '?': 63}
FLAGS = ('', 'f', '?')
MINE_CHAR = int('1F4A3', 16)
MINES_QUANT = {(9, 9): 10, (16, 16): 40, (16, 30): 99}
NUM_CLRS = {1: 'blue', 2: 'green', 3: 'red', 4: 'dark blue', 5: 'brown', 6: 'turquoise', 7: 'black', 8: 'white'}


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# Функция выводит название вызвавшей ее функции
def say_my_name():
    stack = traceback.extract_stack()
    print(stack[-2][-2])


class Game:
    def __init__(self):
        self.want_new_game = False
        self.mainw = False
        self.new_game()

    def change_want_new_game(self, state):
        self.want_new_game = state

    def new_game(self):
        if self.mainw:
            msize = self.mainw.get_msize()
            self.mainw.close()
            self.mainw = None
        self.mainw = MainW(self)


class MainW(QW.QWidget):
    def __init__(self, parent=None, game_n=0, msize=MSIZES[0]):
        self.game_n = game_n
        if not self.game_n:
            super().__init__()
            self.parent = parent
            self.btns = {}  # Словарь кнопок
        
        self.game_stop = False
        self.msize = msize
        self.mines_quant = MINES_QUANT[self.msize]
        # КНОПКИ 1
        self.turns = 0
        self.time = 0
        if not self.game_n:
            self.initUI()
            self.new_msize()
            self.create_timer()
        else:
            self.reinit_game_menu()
        self.game_n += 1

    def reinit_game_menu(self):
        self.found_mines_qlcd.display(self.mines_quant)
        self.timer_qlcd.display(0)
##        self.gen_crds_btns()
        
    def initUI(self):
        self.setWindowTitle('Сапёр')
        
        # <РАЗМЕТКА СТРАНИЦЫ
        self.main_vlayout = QW.QVBoxLayout()
        self.setLayout(self.main_vlayout)

        self.game_menu_hlayout = QW.QHBoxLayout()
        self.main_vlayout.insertLayout(0, self.game_menu_hlayout)
                
        self.game_grid = QW.QGridLayout()
        self.main_vlayout.insertLayout(1, self.game_grid)
        
        self.gamer_hlayout = QW.QHBoxLayout()
        self.main_vlayout.insertLayout(2, self.gamer_hlayout)
        # >РАЗМЕТКА СТРАНИЦЫ
        
        # <ОФОРМЛЕНИЕ ПРЕДСТАВЛЕНИЯ ИГРОВОЙ ИНФОРМАЦИИ
        lcd_font = Qt.QFont('Arial', pointSize=20, weight=Qt.QFont.Bold)
        
        # Кол-во мин
        self.found_mines_qlcd = QW.QLCDNumber(3)
        self.found_mines_qlcd.setFont(lcd_font)
        self.game_menu_hlayout.addWidget(self.found_mines_qlcd)
        self.found_mines_qlcd.display(self.mines_quant)

        # Кнопка начала новой игры
        self.start_btn = QW.QPushButton(chr(128578))
        self.start_btn.setFixedSize(50, 50)
##        self.start_btn.setMask(Qt.QRegion(0, 0, 50, 50, Qt.QRegion.Ellipse))
        self.start_btn.setStyleSheet('Text-align: center; background: rgb(240, 240, 240); border-color: rgb(240, 240, 240);')
##        game.mainw.palette().color(Qt.QPalette.Background)
        self.start_btn.setFont(Qt.QFont('Arial', pointSize=20, weight=Qt.QFont.Bold))
        self.start_btn.setFlat(True)
        self.game_menu_hlayout.addWidget(self.start_btn)
        
        # Таймер
        self.timer_qlcd = QW.QLCDNumber(3)
        self.timer_qlcd.setFont(lcd_font)
        self.game_menu_hlayout.addWidget(self.timer_qlcd)
        # >ОФОРМЛЕНИЕ ПРЕДСТАВЛЕНИЯ ИГРОВОЙ ИНФОРМАЦИИ
        
        self.game_grid.setSpacing(2)
        # КНОПКИ 2
        # Сгенерировать новый набор Кнопок и добавить их в Разметку
        self.gen_crds_btns()
        # Отобразить Осн.окно
        self.show()
        # Открыть окно выбора размера поля для получения новых размеров мин.поля
        self.start_btn.clicked.connect(self.new_msize)

        # Установка аватара игрока
##        self.avatar = Qt.QPixmap('E:\\YD\\YandexDisk\\Backup\\OneDrive_LysVM\\MyDocs\\ME\\avatar.jpg')
##        self.avatar = self.avatar.scaled(150, 150)
##        self.show_avatar = QW.QLabel(self)
##        self.show_avatar.setPixmap(self.avatar)
##
##        self.game_grid.addWidget(self.show_avatar, self.msize[0] + 2, 0, self.msize[0] + 2, 6)
##        self.select_avatar = QW.QPushButton('Ввести имя')
##        self.grid.addWidget(self.select_avatar, self.msize[0] + 2, 7, self.msize[0] + 2, 10)
##        self.select_avatar.clicked.connect(self.select_avatar_window)
        self.setSizePolicy(Qt.QSizePolicy.Preferred, Qt.QSizePolicy.Preferred)
        
##    def select_avatar_window(self):
##        self.years = QW.QInputDialog.getInt(self, 'Ввод возраста',
##                                                  'Сколько тебе лет?',
##                                                  5, 4, 130, 1)[0]
##        self.avatar = Qt.QPixmap(self.fname)
##        self.avatar = self.avatar.scaled(150, 150)
##        self.show_avatar.setText(str(self.years))

    def new_msize(self):
        self.msizew = SelectMSizeW(self)
    
    def get_msize(self):
        return self.msize

    def create_timer(self):
        self.timer = Timer(1, self.renew_timer_qlcd)
        self.timer.start()

    def renew_timer_qlcd(self):
        if self.turns:
            self.time += 1
            self.timer_qlcd.display(self.time)
            if not self.game_stop:
                self.create_timer()
    
    # Получить размер поля от пользователя из внешнего окна
    def set_msize(self):
        self.mines_quant = MINES_QUANT[self.msize]
        # Пересоздание матрицы
        self.msizew.close()
        # КНОПКИ 3
        # Сгенерировать новый набор Кнопок и добавить их в Разметку
        self.__init__(game_n=self.game_n, msize=self.msizew.get_msize())
        self.gen_crds_btns()
        self.sizeHint()

    # КНОПКИ 4
    # Сгенерировать новое Игровое поле
    def gen_crds_btns(self):
        # Опустошить словарь
        for btn in self.btns:
            self.btns[btn].setParent(None)
        self.btns = {}
        # Очистить Разметку
        for i in range(self.game_grid.count()):
            self.game_grid.removeItem(self.game_grid.itemAt(i))

        # Изменяя диапазон генерируемых i, можно менять координаты кнопок
        # Добавить в разметку новый набор Кнопок
        for i in range(self.msize[0]):
            for j in range(self.msize[1]):
                # КНОПКИ 5
                # Формирование словаря типа Координаты: Кнопка
                self.btns[(i, j)] = MineButton((i, j), self)
                self.btns[(i, j)].setFixedSize(25, 25)
                self.game_grid.addWidget(self.btns[(i, j)], i, j)
        # ВОТ ОНО - минимальный фиксированный размер!!!
        self.main_vlayout.setSizeConstraint(Qt.QLayout.SetFixedSize)

    def mousePress(self):
        self.found_mines_qlcd.display(len(self.get_found_mines()))

    def plus_turn(self):
        self.turns += 1

    def seq_minus(self, seq1, seq2):
        return list(set(seq1) - set(seq2))

    def seqs_union(self, seq_seq):
        return list(set([el for seq in seq_seq for el in seq]))

    def seqs_conj(self, *seqs):
        seqs = list(map(set, seqs))
        return reduce(set.intersection, seqs)

    def get_empty_crds(self):
        # КНОПКИ 6
        return list(filter(lambda x: not self.btns[x].mine, list(self.btns.keys())))

    def get_mines_crds(self):
        # КНОПКИ 7
        return list(filter(lambda x: self.btns[x].mine, list(self.btns.keys())))

    def get_near_crds(self, xy):
        x, y = xy
        x_m1 = (x - 1) if (x > 0) else (x)
        x_p1 = (x + 1) if (x < self.msize[0] - 1) else (x)
        y_m1 = (y - 1) if (y > 0) else (y)
        y_p1 = (y + 1) if (y < self.msize[1] - 1) else (y)
        return self.seq_minus(list(product(range(x_m1, x_p1 + 1),
                                      range(y_m1, y_p1 + 1))), [xy])

    def get_near_empty_crds(self, xy):
        return self.seq_minus(self.get_near_crds(xy), self.get_mines_crds())

    def get_near_mines_crds(self, xy):
        return self.seq_minus(self.get_near_crds(xy), self.get_empty_crds())

    def have_common_els(self, *seqs):
        return list(reduce(set.intersection, map(set, seqs)))

    def get_found_mines(self):
        return list(filter(lambda x: not self.btns[x].flag ==
                           FLAGS[1], self.get_mines_crds()))

    # Получение расстояния между координатами
    def crds_distance(self, crds1, crds2):
        return max(abs(crds1[0] - crds2[0]), abs(crds1[1] - crds2[1]))

    def mine_demine_seq(self, crds_seq, is_mine):
        
        for crds in crds_seq:
            # КНОПКИ 8
            self.btns[crds].mine = is_mine

    def gen_mines(self, pressed_btn):

        def get_isolated_sets_empty_crds():
            
            # <Получить список изолированных наборов связанных координат пустых ячеек
            empty_crds_isolated_sets = []
            # Словарь - координаты ячейки: координаты рядом стоящих пустых ячеек
            near_empty_crds_dict = dict((crds,
                                         self.get_near_empty_crds(crds))
                                        for crds in self.get_empty_crds())
            while near_empty_crds_dict:
                key, val = near_empty_crds_dict.popitem()
                keys_cntd_crds = [key]
                vals_cntd_near_crds = val
                new_cntd_near_crds = True
                while new_cntd_near_crds:
                    
                    # <<Отфильтровать ключи словаря 'near_empty_crds_dict' (координаты), значения которых
                    # (рядом стоящие ячейки) имеют общие координаты с формируемым набором
                    # связанных пустых ячеек 'vals_cntd_near_crds'
                    new_cntd_near_crds = list(filter
                                              (lambda x: self.have_common_els
                                               (near_empty_crds_dict[x] + [x],
                                                vals_cntd_near_crds),
                                               near_empty_crds_dict.keys()))
                    # >>Отфильтровать ключи словаря 'near_empty_crds_dict' (координаты)

                    # <<Объединить отфильтрованные координаты (ключи и значения
                    # (рядом стоящие пустые ячейки)) с формируемым изолированным набором
                    # (keys_cntd_crds, vals_cntd_near_crds)
                    for k in new_cntd_near_crds:
                        keys_cntd_crds += [k]
                        vals_cntd_near_crds += near_empty_crds_dict.pop(k)
                    # <<Объединить отфильтрованные координаты (ключи и значения
                    
                empty_crds_isolated_sets.append(keys_cntd_crds)
            return empty_crds_isolated_sets
            # >Получить список изолированных наборов связанных координат пустых ячеек
            
        # Получить список возможных координат для расстановки мин
        all_possible_mines_crds = self.seq_minus(self.get_empty_crds(), [pressed_btn.crds])  # без открытой ячейки

        while not self.get_mines_crds():
            # <Расставить мины
            mines_crds = random.sample(all_possible_mines_crds, self.mines_quant)  # без открытой ячейки
            self.mine_demine_seq(mines_crds, True)
            # >Расставить мины

            # Получить список изолированных наборов пустых ячеек - ВЫЗОВ ФУНКЦИИ МЕТОДА
            empty_crds_isolated_sets = get_isolated_sets_empty_crds()
            if len(empty_crds_isolated_sets) > 1:
                self.mine_demine_seq(mines_crds, False)

    def check_win(self):
        # КНОПКИ 9
        empty_open_cells_quant = len(list(filter(lambda x:
                                                 self.btns[x].open,
                                                 self.get_empty_crds())))
        if empty_open_cells_quant == len(self.get_empty_crds()):
            self.game_win()

    def game_win(self):
        # КНОПКИ 10
        # Получить неоткрытые ячейки с минами без флагов
        self.game_stop = True
        clsd_mines_crds = filter(lambda x: not self.btns[x].open, self.get_mines_crds())
        wout_flags_clsd_mines_crds = filter(lambda x: not (self.btns[x].flag == FLAGS[1]), clsd_mines_crds)
        for crds in list(wout_flags_clsd_mines_crds):
            self.btns[crds].change_flag(FLAGS[1])
        self.endgw = EndGW('win', self)
        self.endgw.show()

    def game_lose(self):
        self.game_stop = True
        self.endgw = EndGW('lose', self)
        self.endgw.show()


class SelectMSizeW(QW.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        # Окно будет блокировать все окна приложения
        self.setWindowModality(2)
        self.parent = parent
        self.msize = self.parent.get_msize()
        self.setFont(Qt.QFont('Arial', pointSize=12, weight=Qt.QFont.Bold))
        self.initUI()
        self.show()

    def initUI(self):
        # Определить параметры окна
        self.setWindowTitle('Выбор размера поля')
        self.setFixedSize(210, 120)
        #### Окно->Группа->Контейнер-сетка->Переключатели
        # Создать в Окне Группу для переключателей, определить выравнивание надписи
        self.grb = QW.QGroupBox('Выбор размера поля:', self)
        self.grb.setAlignment(QtCore.Qt.AlignHCenter)
        # Создать Контейнер-сетку
        self.grb_grid = QW.QGridLayout()
        # Создать Переключатели и кнопку
        self.grb_grid_rbtn1 = QW.QRadioButton('9*9')
        self.grb_grid_rbtn2 = QW.QRadioButton('16*16')
        self.grb_grid_rbtn3 = QW.QRadioButton('16*30')
        self.grb_btn1 = QW.QPushButton('OK')
        # КНОПКИ 11
        # Список Переключателей
        self.grb_grid_rbtns = [self.grb_grid_rbtn1,
                                    self.grb_grid_rbtn2,
                                    self.grb_grid_rbtn3]
        # Добавить Переключатели в 'QButtonGroup'
        self.qbtn_gr = QW.QButtonGroup()
        # КНОПКИ 12
        for i in range(len(self.grb_grid_rbtns)):
            self.qbtn_gr.addButton(self.grb_grid_rbtns[i])
        # Добавить Переключатели в Контейнер-сетку
        # КНОПКИ 13
        for i in range(len(self.grb_grid_rbtns)):
            self.grb_grid.addWidget(self.grb_grid_rbtns[i], 0, i)
        self.grb_grid_rbtns[MSIZES.index(self.msize)].setChecked(True)  # Включить Переключатель по-умолчанию
        self.grb_grid.addWidget(self.grb_btn1, 1, 0, 1, 3,
                                alignment=QtCore.Qt.AlignHCenter)

        # При нажатии на Переключатель вызвать метод 'self.get_selected_msize'
        self.qbtn_gr.buttonClicked.connect(self.set_selected_msize)
        # При нажатии на кнопку 'OK' вызвать метод 'self.ret_msize'
        self.grb_btn1.clicked.connect(self.ret_msize)
        # Установить Контейнер-сетку в качестве разметки Группы переключателей
        self.grb.setLayout(self.grb_grid)
        
    def set_selected_msize(self):
        
        # Присвоить внутр.переменной msize значение из MSIZES по индексу выбранного Переключателя
        # в списке Переключателей
##        self.label.setText(str(self.qbtn_gr.checkedButton()))
        # КНОПКИ 14
        self.msize = MSIZES[self.grb_grid_rbtns.index(self.qbtn_gr.checkedButton())]
        
    def ret_msize(self):
        
        # Присвоить переменной родительского объекта 'parent.msize' значение внутренней
        # переменной 'self.msize' через метод
        self.parent.set_msize()

    def get_msize(self):
        return self.msize


class EndGW(QW.QWidget):
    def __init__(self, result, parent=None):
        
        super().__init__()
        # Окно будет блокировать все окна приложения
        self.setWindowModality(2)
        self.result = result
        self.parent = parent
        self.setFont(Qt.QFont('Arial', pointSize=12, weight=Qt.QFont.Bold))
        self.initUI()

    def initUI(self):
        # Определить параметры окна
        if self.result == 'win':
            title = 'Победа!'
            text = 'Вы разминировали все мины,\nи Ваш отряд победил!'
        elif self.result == 'lose':
            title = 'Вы подорвались'
            text = 'В результате неаккуратной попытки разминирования\nВы подорвались и попали в госпиталь'
        self.setWindowTitle(title)
        self.setFixedSize(500, 200)
        #### Окно->Контейнер-сетка->Элементы управления
        # Создать Контейнер-сетку
        self.grid = QW.QGridLayout()
        # Создать Надпись и кнопку
        self.grid_label = QW.QLabel(text)
        self.pbtn = QW.QPushButton('OK')
        # Добавить Переключатели в Контейнер-сетку
        self.grid.addWidget(self.grid_label, 0, 0,
                            alignment=QtCore.Qt.AlignHCenter)
        self.grid.addWidget(self.pbtn, 1, 0,
                            alignment=QtCore.Qt.AlignHCenter)
        
        # При нажатии на кнопку 'OK' вызвать метод 'self.close'
        self.pbtn.clicked.connect(self.close)
        # Установить Контейнер-сетку в качестве разметки Группы переключателей
        self.setLayout(self.grid)



class MineButton(QW.QPushButton):
    
    def __init__(self, crds, parent=None):
        super().__init__()
        self.setStyleSheet('background: #D3D3D3;')
        self.parent = parent
        # Атрибуты игры
        self.crds = crds
        self.mine = False
        self.flag = FLAGS[0]
        self.open = False
        # Дизайн
        self.setCheckable(True)
        self.setFont(Qt.QFont('Arial', pointSize=13, weight=Qt.QFont.Black))

    # Это - инкапсулированный обработчик!
    def mousePressEvent(self, e):
        if not self.parent.game_stop:
            # То факт, что после вызова операции 'super' label-виджет основного окна
            # начинает отображать значения, присваиваемые методом 'mainw.mousePressEvent',
            # говорит о том, что метод 'mousePressEvent', вызываемый операцией 'super',
            # выполняется с возвращением значения, которое методом подкласса не возвращается
    ##        super().mousePressEvent(e)
            mouse_button = e.button()
            if mouse_button == Qt.Qt.LeftButton:
                # Нажатие левой кнопки (открытие ячейки)
                self.open_cell(True)
            elif mouse_button == Qt.Qt.RightButton:
                self.change_flag()
            self.parent.mousePress()

    def open_cell(self, click=False):
##        
        # При первом открытии выполнить генерацию мин
        if not self.parent.turns:
            self.parent.gen_mines(self)
            self.parent.create_timer()
        if not (self.isChecked() or self.open or self.flag):
            self.setChecked(True)  # Визуальное нажатие кнопки
            self.open = True  # Статус переменной, отражающей состояние кнопки
            if click:
                self.parent.plus_turn()
            # Если МИНА - ПРОИГРЫШ
            if self.mine:
                self.setStyleSheet('background-color: #FF0000;')
                self.setText(chr(MINE_CHAR))  # Отображение мины
                self.parent.game_lose()
            # Если ПУСТАЯ ЯЧЕЙКА - ОТКРЫТИЕ ЯЧЕЙКИ
            else:
                near_mines = len(self.parent.get_near_mines_crds(self.crds))
                if near_mines:
                    self.setStyleSheet(f'color: {Qt.QColor(NUM_CLRS[near_mines]).name()}; background: #D3D3D3;')
                self.setText(str(near_mines) if near_mines else '')
                near_empty_crds = self.parent.get_near_empty_crds(self.crds)
                # КНОПКИ 15
                for near_crds in near_empty_crds:
                    near_crds_near_mines = len(self.parent.get_near_mines_crds(near_crds))
                    if (not near_mines) or (not near_crds_near_mines):
                        self.parent.btns[near_crds].open_cell()
                self.parent.check_win()

    def change_flag(self, new_flag=False):
        
        if not (self.isChecked() or self.open):
            if not new_flag:
                self.flag = FLAGS[(FLAGS.index(self.flag) + 1) % 3]
            else:
                self.flag = new_flag
            self.setText(chr(FLAGS_CHARS_D[self.flag]))


if __name__ == '__main__':
    app = QW.QApplication([])
    game = Game()
    sys.excepthook = except_hook
    sys.exit(app.exec())
