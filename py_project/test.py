import random
import copy
import sys
import tkinter  # //GUI模块
import threading
from functools import reduce

# 参数
'''
ALPHA:信息启发因子，值越大，则蚂蚁选择之前走过的路径可能性就越大
      ，值越小，则蚁群搜索范围就会减少，容易陷入局部最优
BETA:Beta值越大，蚁群越就容易选择局部较短路径，这时算法收敛速度会
     加快，但是随机性不高，容易得到局部的相对最优
'''
(ALPHA, BETA, RHO, Q) = (1.0, 2.0, 0.5, 100.0)
# 城市数，蚁群
(city_num, ant_num) = (10, 10)


distance_x = [
    185, 185, 185, 196, 211, 228, 238, 238, 238, 238, 238, 238, 238, 238, 238]
for i, v in enumerate(distance_x):
    distance_x[i] = v * 2
distance_y = [
    65, 80, 100, 125, 140, 155, 180, 198, 220, 245, 270, 320, 352, 395,430]
for i, v in enumerate(distance_y):
    distance_y[i] = v * 2-100
#第二条地铁线的(x,y)坐标
erhaoxian_x = [
    185, 165, 160, 145, 128, 110, 93, 76, 76, 76, 76, 76, 76, 76, 76, 76]
for i, v in enumerate(erhaoxian_x):
    erhaoxian_x[i] = v * 2
erhaoxian_y = [
    100,120,137,152,167,185,203,234,255,285,304,320,355,381,400,430
]
for i, v in enumerate(erhaoxian_y):
    erhaoxian_y[i] = v * 2-100

threehaoxian_x = [
    76, 100, 124, 135, 188, 205, 205, 240, 302, 322, 350, 372, 396
]
for i, v in enumerate(threehaoxian_x):
    threehaoxian_x[i] = v * 2
threehaoxian_y = [
    255, 278, 285, 285, 285, 320, 340, 352, 352, 352, 352, 352, 352
]
for i, v in enumerate(threehaoxian_y):
    threehaoxian_y[i] = v * 2-100

fourhaoxian_x = [
    76, 118, 158,198, 240, 275, 305, 336, 365, 396]
for i, v in enumerate(fourhaoxian_x):
    fourhaoxian_x[i] = v * 2

fourhaoxian_y = [
    430, 430,430, 430, 430, 430, 430, 430, 430, 430]
for i, v in enumerate(fourhaoxian_y):
    fourhaoxian_y[i] = v * 2-100


fivehaoxian_x = [
    396, 396]
for i, v in enumerate(fivehaoxian_x):
    fivehaoxian_x[i] = v * 2
fivehaoxian_y = [
    352, 430]
for i, v in enumerate(fivehaoxian_y):
    fivehaoxian_y[i] = v * 2-100

# 城市距离和信息素
distance_graph = [[0.0 for col in range(city_num)] for raw in range(city_num)]
pheromone_graph = [[1.0 for col in range(city_num)] for raw in range(city_num)]


# ----------- 蚂蚁 -----------
class Ant(object):

    # 初始化
    def __init__(self, ID):

        self.ID = ID  # ID
        self.__clean_data()  # 随机初始化出生点

    # 初始数据
    def __clean_data(self):

        self.path = []  # 当前蚂蚁的路径
        self.total_distance = 0.0  # 当前路径的总距离
        self.move_count = 0  # 移动次数
        self.current_city = -1  # 当前停留的城市
        self.open_table_city = [True for i in range(city_num)]  # 探索城市的状态

        city_index = 0
        self.current_city = city_index
        self.path.append(city_index)
        self.open_table_city[city_index] = False
        self.move_count = 1

    # 选择下一个城市
    def __choice_next_city(self):

        next_city = -1
        select_citys_prob = [0.0 for i in range(city_num)]  # 存储去下个城市的概率
        total_prob = 0.0

        # 获取去下一个城市的概率
        for i in range(city_num):
            if self.open_table_city[i]:
                try:
                    # 计算概率：与信息素浓度成正比，与距离成反比
                    select_citys_prob[i] = pow(pheromone_graph[self.current_city][i], ALPHA) * pow(
                        (1.0 / distance_graph[self.current_city][i]), BETA)
                    total_prob += select_citys_prob[i]
                except ZeroDivisionError as e:
                    print('Ant ID: {ID}, current city: {current}, target city: {target}'.format(ID=self.ID,
                                                                                                current=self.current_city,
                                                                                                target=i))
                    sys.exit(1)

        # 轮盘选择城市
        if total_prob > 0.0:
            # 产生一个随机概率,0.0-total_prob
            temp_prob = random.uniform(0.0, total_prob)
            for i in range(city_num):
                if self.open_table_city[i]:
                    # 轮次相减
                    temp_prob -= select_citys_prob[i]
                    if temp_prob < 0.0:
                        next_city = i
                        break

        # 未从概率产生，顺序选择一个未访问城市
        # if next_city == -1:
        #     for i in range(city_num):
        #         if self.open_table_city[i]:
        #             next_city = i
        #             break

        if (next_city == -1):
            next_city = random.randint(0, city_num - 1)
            while ((self.open_table_city[next_city]) == False):  # if==False,说明已经遍历过了
                next_city = random.randint(0, city_num - 1)

        # 返回下一个城市序号
        return next_city

    # 计算路径总距离
    def __cal_total_distance(self):

        temp_distance = 0.0

        for i in range(1, city_num):
            start, end = self.path[i], self.path[i - 1]
            temp_distance += distance_graph[start][end]

        # 回路
        end = self.path[0]
        temp_distance += distance_graph[start][end]
        self.total_distance = temp_distance

    # 移动操作
    def __move(self, next_city):

        self.path.append(next_city)
        self.open_table_city[next_city] = False
        self.total_distance += distance_graph[self.current_city][next_city]
        self.current_city = next_city
        self.move_count += 1

    # 搜索路径
    def search_path(self):

        # 初始化数据
        self.__clean_data()

        # 搜素路径，遍历完所有城市为止
        while self.move_count < city_num:
            # 移动到下一个城市
            next_city = self.__choice_next_city()
            self.__move(next_city)

        # 计算路径总长度
        self.__cal_total_distance()


# ----------- TSP问题 -----------



class TSP(object):


    def __init__(self, root, width=1024, height=1024, n=city_num):


        # 创建画布
        self.root = root
        self.width = width
        self.height = height
        # 城市数目初始化为city_num
        self.n = n
        # tkinter.Canvas
        self.canvas = tkinter.Canvas(
            root,
            width=self.width,
            height=self.height,
            bg="#EBEBEB",  # 背景白色
            xscrollincrement=1,
            yscrollincrement=1
        )
        self.canvas.pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.title("智能交通选择(n:初始化 e:开始搜索 s:停止搜索 q:退出程序)")
        self.__r = 5
        self.__lock = threading.RLock()  # 线程锁

        self.__bindEvents()
        self.new()

        # 计算城市之间的距离
        for i in range(city_num):
            for j in range(city_num):
                temp_distance = pow((distance_x[i] - distance_x[j]), 2) + pow((distance_y[i] - distance_y[j]), 2)
                temp_distance = pow(temp_distance, 0.5)
                distance_graph[i][j] = float(int(temp_distance + 0.5))

    # 按键响应程序
    def __bindEvents(self):

        self.root.bind("q", self.quite)  # 退出程序
        self.root.bind("n", self.new)  # 初始化
        self.root.bind("e", self.search_path)  # 开始搜索
        self.root.bind("s", self.stop)  # 停止搜索

    # 更改标题
    def title(self, s):

        self.root.title(s)

    # 初始化
    def new(self, evt=None):

        # 停止线程
        self.__lock.acquire()
        self.__running = False
        self.__lock.release()

        self.clear()  # 清除信息
        self.nodes = []  # 第一条地铁线节点
        self.nodes2 = []  # 第一条地铁线节点对象

        self.twoNodes = []  # 第二条地铁线节点坐标
        self.twoNodes2 = []  # 第二条地铁线节点对象

        self.threeNodes = []  # 第三条地铁线节点坐标
        self.threeNodes2 = []  # 第三条地铁线节点对象

        self.fourNodes = []  # 第四条地铁线节点坐标
        self.fourNodes2 = []  # 第四条地铁线节点对象

        self.fiveNodes = []  # 第五条地铁线节点坐标
        self.fiveNodes2 = []  # 第四条地铁线节点对象
        # 初始化第一条节点
        for i in range(len(distance_x)):
            # 在画布上随机初始坐标
            x = distance_x[i]
            y = distance_y[i]
            self.nodes.append((x, y))
            # 生成节点椭圆，半径为self.__r
            node = self.canvas.create_oval(x - self.__r,
                                           y - self.__r, x + self.__r, y + self.__r,
                                           fill="#ff0000",  # 填充红色
                                           outline="#000000",  # 轮廓白色
                                           tags="node",
                                           )
            self.nodes2.append(node)
            # 显示坐标
            self.canvas.create_text(x, y - 10,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text='(' + str(x) + ',' + str(y) + ')',  # 所绘制文字的内容
                                    fill='black'  # 所绘制文字的颜色为灰色
                                    )

        # 顺序连接城市

        self.line(range(len(distance_x)))

        # 初始化第二条城市节点
        for i in range(len(erhaoxian_x)):
            # 在画布上随机初始坐标
            x = erhaoxian_x[i]
            y = erhaoxian_y[i]
            self.twoNodes.append((x, y))
            # 生成节点椭圆，半径为self.__r
            node = self.canvas.create_oval(x - self.__r,
                                           y - self.__r, x + self.__r, y + self.__r,
                                           fill="#ff0000",  # 填充红色
                                           outline="#000000",  # 轮廓白色
                                           tags="node",
                                           )
            self.twoNodes2.append(node)
            # 显示坐标
            self.canvas.create_text(x, y - 10,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text='(' + str(x) + ',' + str(y) + ')',  # 所绘制文字的内容
                                    fill='black'  # 所绘制文字的颜色为灰色
                                    )

        # 顺序连接城市

        self.line_two(range(len(erhaoxian_x)))

        # 初始化第三条城市节点
        for i in range(len(threehaoxian_x)):
            # 在画布上随机初始坐标
            x = threehaoxian_x[i]
            y = threehaoxian_y[i]
            self.threeNodes.append((x, y))
            # 生成节点椭圆，半径为self.__r
            node = self.canvas.create_oval(x - self.__r,
                                           y - self.__r, x + self.__r, y + self.__r,
                                           fill="#ff0000",  # 填充红色
                                           outline="#000000",  # 轮廓白色
                                           tags="node",
                                           )
            self.threeNodes2.append(node)
            # 显示坐标
            self.canvas.create_text(x, y - 10,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text='(' + str(x) + ',' + str(y) + ')',  # 所绘制文字的内容
                                    fill='black'  # 所绘制文字的颜色为灰色
                                    )

        # 顺序连接城市
        self.line_three(range(len(threehaoxian_x)))

        # 初始化第四条城市节点
        for i in range(len(fourhaoxian_x)):
            # 在画布上随机初始坐标
            x = fourhaoxian_x[i]
            y = fourhaoxian_y[i]
            self.fourNodes.append((x, y))
            # 生成节点椭圆，半径为self.__r
            node = self.canvas.create_oval(x - self.__r,
                                           y - self.__r, x + self.__r, y + self.__r,
                                           fill="#ff0000",  # 填充红色
                                           outline="#000000",  # 轮廓白色
                                           tags="node",
                                           )
            self.fourNodes2.append(node)
            # 显示坐标
            self.canvas.create_text(x, y - 10,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text='(' + str(x) + ',' + str(y) + ')',  # 所绘制文字的内容
                                    fill='black'  # 所绘制文字的颜色为灰色
                                    )

        # 顺序连接城市

        self.line_four(range(len(fourhaoxian_x)))

        # 初始化第五条城市节点
        for i in range(len(fivehaoxian_x)):
            # 在画布上随机初始坐标
            x = fivehaoxian_x[i]
            y = fivehaoxian_y[i]
            self.fiveNodes.append((x, y))
            # 生成节点椭圆，半径为self.__r
            node = self.canvas.create_oval(x - self.__r,
                                           y - self.__r, x + self.__r, y + self.__r,
                                           fill="#ff0000",  # 填充红色
                                           outline="#000000",  # 轮廓白色
                                           tags="node",
                                           )
            self.fiveNodes2.append(node)
            # 显示坐标
            self.canvas.create_text(x, y - 10,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text='(' + str(x) + ',' + str(y) + ')',  # 所绘制文字的内容
                                    fill='black'  # 所绘制文字的颜色为灰色
                                    )

        # 顺序连接城市

        self.line_five(range(len(fivehaoxian_x)))

        # 初始城市之间的距离和信息素
        for i in range(city_num):
            for j in range(city_num):
                pheromone_graph[i][j] = 1.0

        self.ants = [Ant(ID) for ID in range(ant_num)]  # 初始蚁群
        self.best_ant = Ant(-1)  # 初始最优解
        self.best_ant.total_distance = 1 << 31  # 初始最大距离
        self.iter = 1  # 初始化迭代次数

    # 将节点按order顺序连线
    def line(self, order):
        # 删除原线
        self.canvas.delete("line")
        print(order)
        def line2(i1, i2):
            p1, p2 = self.nodes[i1], self.nodes[i2]
            self.canvas.create_line(p1, p2, width=6, fill="yellow", tags="line")
            return i2

        # order[-1]为初始值
        reduce(line2, order, order[0])

    def line_two(self, order):
        # 删除原线
        print(order)

        def line2(i1, i2):
            p1, p2 = self.twoNodes[i1], self.twoNodes[i2]
            self.canvas.create_line(p1, p2, width=6, fill="blue", tags="line")
            return i2

        # order[-1]为初始值
        reduce(line2, order, order[0])


    def line_five(self, order):
        # 删除原线
        print(order)

        def line2(i1, i2):
            p1, p2 = self.fiveNodes[i1], self.fiveNodes[i2]
            self.canvas.create_line(p1, p2, width=6, fill="blue", tags="line")
            return i2

        # order[-1]为初始值
        reduce(line2, order, order[0])

    def line_three(self, order):
        # 删除原线
        print(order)

        def line2(i1, i2):
            p1, p2 = self.threeNodes[i1], self.threeNodes[i2]
            self.canvas.create_line(p1, p2, width=6, fill="red", tags="line")
            return i2

        # order[-1]为初始值
        reduce(line2, order, order[0])



    def line_four(self, order):
        # 删除原线
        print(order)

        def line2(i1, i2):
            p1, p2 = self.fourNodes[i1], self.fourNodes[i2]
            self.canvas.create_line(p1, p2, width=6, fill="green", tags="line")
            return i2

        # order[-1]为初始值
        reduce(line2, order, order[0])


    # 清除画布
    def clear(self):
        for item in self.canvas.find_all():
            self.canvas.delete(item)

    # 退出程序
    def quite(self, evt):
        self.__lock.acquire()
        self.__running = False
        self.__lock.release()
        self.root.destroy()
        print(u"\n程序已退出...")
        sys.exit()

    # 停止搜索
    def stop(self, evt):
        self.__lock.acquire()
        self.__running = False
        self.__lock.release()

    # 开始搜索
    def search_path(self, evt=None):

        # 开启线程
        self.__lock.acquire()
        self.__running = True
        self.__lock.release()

        while self.__running:
            # 遍历每一只蚂蚁
            for ant in self.ants:
                # 搜索一条路径
                ant.search_path()
                # 与当前最优蚂蚁比较
                if ant.total_distance < self.best_ant.total_distance:
                    # 更新最优解
                    self.best_ant = copy.deepcopy(ant)
            # 更新信息素
            self.__update_pheromone_gragh()
            print(u"迭代次数：", self.iter, u"最佳路径总距离：", int(self.best_ant.total_distance))
            # 连线
            self.line(self.best_ant.path)
            # 设置标题
            self.title("TSP蚁群算法(n:随机初始 e:开始搜索 s:停止搜索 q:退出程序) 迭代次数: %d" % self.iter)
            # 更新画布
            self.canvas.update()
            self.iter += 1

    # 更新信息素
    def __update_pheromone_gragh(self):

        # 获取每只蚂蚁在其路径上留下的信息素
        temp_pheromone = [[0.0 for col in range(city_num)] for raw in range(city_num)]
        for ant in self.ants:
            for i in range(1, city_num):
                start, end = ant.path[i - 1], ant.path[i]
                # 在路径上的每两个相邻城市间留下信息素，与路径总距离反比
                temp_pheromone[start][end] += Q / ant.total_distance
                temp_pheromone[end][start] = temp_pheromone[start][end]

        # 更新所有城市之间的信息素，旧信息素衰减加上新迭代信息素
        for i in range(city_num):
            for j in range(city_num):
                pheromone_graph[i][j] = pheromone_graph[i][j] * RHO + temp_pheromone[i][j]

    # 主循环
    def mainloop(self):
        self.root.mainloop()


# ----------- 程序的入口处 -----------

if __name__ == '__main__':
    print(u""" 
--------------------------------------------------------

-------------------------------------------------------- 
    """)
    print(pheromone_graph)
    TSP(tkinter.Tk()).mainloop()
