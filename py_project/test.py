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
(city_num, ant_num) = (53, 15)
san_hao_xian_zhan = ["人和","龙归","嘉禾望岗","白云大道北","永泰","同和","京溪南方医院","梅花园","燕塘","广州东站","林和西","体育西路","珠江新城","广州塔","客村"];

er_hao_xian_zhan=["嘉禾望岗","黄边","江夏","萧岗","白云文化广场","白云公园","飞翔公园","三元里","广州火车站","越秀公园","纪念堂","公园前","海珠广场","市二宫","江南西","昌岗"]

wu_hao_xian_zhan=["广州火车站","小北","淘金","区庄","动物园","杨箕","五羊邨","珠江新城","猎德","潭村","员村","科韵路","车陂南"]

ba_hao_xian_zhan=["昌岗","晓港","中大","鹭江","客村","赤岗","磨碟沙","新港东","琶洲","万胜围"]

si_hao_xian_zhan=["车陂南","万胜围"]
distance_x = [
    185, 185, 185, 196, 211, 228, 238, 238, 238, 238, 238, 238, 238, 238, 238]
distance_y = [
    65, 80, 100, 125, 140, 155, 180, 198, 220, 245, 270, 320, 352, 395,430]

#第二条地铁线的(x,y)坐标
erhaoxian_x = [
    185, 165, 160, 145, 128, 110, 93, 76, 76, 76, 76, 76, 76, 76, 76, 76]

erhaoxian_y = [
    100,120,137,152,167,185,203,234,255,285,304,320,355,381,400,430]


threehaoxian_x = [
    76, 100, 124, 135, 188, 205, 205, 238, 302, 322, 350, 372, 396]

threehaoxian_y = [
    255, 278, 285, 285, 285, 320, 340, 352, 352, 352, 352, 352, 352]


fourhaoxian_x = [
    76, 118, 158,198, 238, 275, 305, 336, 365, 396]


fourhaoxian_y = [
    430, 430,430, 430, 430, 430, 430, 430, 430, 430]



fivehaoxian_x = [
    396, 396]
fivehaoxian_y = [
    352, 430]

#珠江新城选择的两条路径距离
#换乘两个站点
zhujiang = 0
for i in range(7,12):
    sum = pow((threehaoxian_x[i+1] - threehaoxian_x[i]), 2) + pow((threehaoxian_y[i+1] - threehaoxian_y[i]), 2)
    sum = pow(sum, 0.5)
    zhujiang += sum
zhujiang = zhujiang +  pow(pow(396 - 396, 2) + pow(352 - 430, 2),0.5)

#换乘一个站点
kecun = 0
for i in range(12,14):
    sum = pow((distance_x[i+1] - distance_x[i]), 2) + pow((distance_y[i+1] - distance_y[i]), 2)
    sum = pow(sum, 0.5)
    kecun += sum
for i in range(4,9):
    sum = pow((fourhaoxian_x[i+1] - fourhaoxian_x[i]), 2) + pow((fourhaoxian_y[i+1] - fourhaoxian_y[i]), 2)
    sum = pow(sum, 0.5)
    kecun += sum


#广州火车站到珠江新城距离
huochezhanjuli = 0
for i in range(0,9):
    sum = pow((erhaoxian_x[i+1] - erhaoxian_x[i]), 2) + pow((erhaoxian_y[i+1] - erhaoxian_y[i]), 2)
    sum = pow(sum, 0.5)
    huochezhanjuli += round(sum,2)
for i in range(0,8):
    sum = pow((threehaoxian_x[i+1] - threehaoxian_x[i]), 2) + pow((threehaoxian_y[i+1] - threehaoxian_y[i]), 2)
    sum = pow(sum, 0.5)
    huochezhanjuli += round(sum,2)



#嘉禾望岗到珠江新城距离
jiahewanggang = 0
for i in range(0,13):
    sum = pow((distance_x[i+1] - distance_x[i]), 2) + pow((distance_y[i+1] - distance_y[i]), 2)
    sum = pow(sum, 0.5)
    jiahewanggang += round(sum,2)

#珠江新城信息素
pheromone_zhujiang = 1.0
#客村信息素
pheromone_kecun = 1.0


#广州火车站-珠江新城信息素
pheromone_huochezhan = 1.0
#广州火车站-万胜围信息素
pheromone_changgang = 1.0

#嘉禾-珠江信息素
jiahezhujiang = 1.0
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
        self.path.append((distance_x[city_index],distance_y[city_index]))
        self.open_table_city[city_index] = False
        self.move_count = 1

        self.kecun = False
        self.zhujiang = False
        self.chepeinan = False
        self.huochezhan = False
    # 选择下一个城市
    def __choice_next_city(self,path):

        next_city = -1
        select_citys_prob = [0.0 for i in range(city_num)]  # 存储去下个城市的概率
        total = 0.0
        result = ()
        for i in range(15):
            if (i == 2 and path == (185, 100)):

                zhujiangxinchenggailv = pow(jiahezhujiang, ALPHA) * pow(1.0 /jiahewanggang , BETA)
                guangzhouhuochezhangailv = pow(pheromone_huochezhan, ALPHA) * pow(1.0 /huochezhanjuli, BETA)

                total = zhujiangxinchenggailv + guangzhouhuochezhangailv
                if total > 0.0:
                    # 产生一个随机概率,0.0-total_prob
                    temp_prob = random.uniform(0.0, total)

                    for i in range(2):
                        # 轮次相减
                        if i == 0:
                            temp_prob -= zhujiangxinchenggailv
                        elif i == 1:
                            temp_prob -= guangzhouhuochezhangailv
                        if temp_prob < 0.0:
                            if (i == 0):
                                result = (196, 125)
                                self.open_table_city[3] = False

                                return result
                            elif i == 1:
                                result = (165, 120)
                                self.open_table_city[25] = False
                                self.huochezhan = True
                                return result


                    break

            if( i==13 and path == (238,352) ):
                #轮盘赌算法开始
                #1、计算概率
                #2、计算概率和
                #3
                zhujiang_gailv =  pow(pheromone_zhujiang, ALPHA) * pow(1.0 / zhujiang, BETA)

                kecun_gailv =  pow(pheromone_kecun, ALPHA) * pow(1.0 / kecun, BETA)
                total = zhujiang_gailv + kecun_gailv
                if total > 0.0:
                    # 产生一个随机概率,0.0-total_prob
                    temp_prob = random.uniform(0.0, total)

                    for i in range(2):
                        # 轮次相减
                        if i== 0:
                            temp_prob -= zhujiang_gailv
                        elif i == 1:
                            temp_prob -= kecun_gailv
                        if temp_prob < 0.0:
                            if (i == 0):
                                result = (302,352)
                                self.open_table_city[20] = False

                                return result
                            elif i == 1:
                                result = (238,395)
                                self.open_table_city[13] = False

                                return result


                    break
            if self.huochezhan:
                break
            if self.open_table_city[i]:
                next_city = i
                result = (distance_x[i], distance_y[i])
                self.open_table_city[i]=False
                break
        #嘉禾望岗换乘点选择
        if( path == (165,120) or self.huochezhan == True):
            self.huochezhan = True
            if path == (165,120):
                self.total_distance = self.total_distance + 10
            for i in range(2,9):
                if self.open_table_city[ 24+i]:
                    result = (erhaoxian_x[i],erhaoxian_y[i])
                    self.open_table_city[ 24 + i] = False
                    return result
            self.total_distance = self.total_distance + 10
            for i in range(1,8):
                if self.open_table_city[ 32+i]:
                    result = (threehaoxian_x[i],threehaoxian_y[i])
                    self.open_table_city[ 32 + i] = False
                    return result
                if(i==7):
                    result = (238, 352)
                    for i in range(3, 14):
                        self.open_table_city[i] = False
                    self.huochezhan = False
                    return result



        #客村新城换乘点选择
        if( path == (238,430) or self.kecun == True):
            self.kecun = True
            if path == (238,430):
                self.total_distance = self.total_distance + 10
            for i in range(5,10):
                if self.open_table_city[ 10+i]:
                    result = (fourhaoxian_x[i],fourhaoxian_y[i])
                    self.open_table_city[ 10 + i] = False
                    break

        # 珠江新城新城换乘点选择
        if (path == (302,352) or self.zhujiang == True):
            self.zhujiang = True
            if path == (302,352):
                self.total_distance = self.total_distance + 10
            for i in range(9, 13):
                if self.open_table_city[12+i]:
                    result = (threehaoxian_x[i], threehaoxian_y[i])
                    self.open_table_city[12 +i] = False
                    break
        #客村最后一个换乘点
        if (path == (396, 352) or self.chepeinan == True):
            self.total_distance = self.total_distance + 10
            self.chepeinan = True
            result = (396,430)


        return result



    # 计算路径总距离
    def __cal_total_distance(self):

        temp_distance = 0.0

        for i in range(len(self.path)-1):
            sum  = 0
            sum = pow((self.path[i][0] - self.path[i+1][0]), 2) + pow((self.path[i][1] - self.path[i+1][1]), 2)
            sum = round(pow(sum, 0.5),2)
            temp_distance += sum
        self.total_distance = self.total_distance + temp_distance

    # 移动操作
    def __move(self, next_city):

        self.path.append(next_city)

        sum = 0
        sum = pow((self.path[len(self.path)-1][0] - self.path[len(self.path)-2][0]), 2) + pow((self.path[len(self.path)-1][1] - self.path[len(self.path)-2][1]), 2)
        sum = round(pow(sum, 0.5), 2)
        self.total_distance += sum
        self.current_city = self.move_count
        self.move_count += 1

    # 搜索路径
    def search_path(self):

        # 初始化数据
        self.__clean_data()

        # 搜素路径，遍历完所有城市为止
        while (self.path[len(self.path)-1][0]   != 396 & self.path[len(self.path)-1][1] != 430) :
            # 移动到下一个城市
            next_city = self.__choice_next_city(self.path[len(self.path)-1])
            self.__move(next_city)

        # 计算路径总长度
        self.__cal_total_distance()


# ----------- TSP问题 -----------



class TSP(object):


    def __init__(self, root, width=800, height=600, n=city_num):


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
            if (i in range(3,12) or i==0 or i == 1 or i == 13):
                self.canvas.create_text(x+40, y ,  # 使用create_text方法在坐标（302，77）处绘制文字
                                        text='(' + san_hao_xian_zhan[i] + ')',  # 所绘制文字的内容
                                        fill='black'  # 所绘制文字的颜色为灰色
                                        )
            else:
                self.canvas.create_text(x, y - 10,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text='('+san_hao_xian_zhan[i]+')',  # 所绘制文字的内容
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
            if( i in range(1,8) or i in range(9,15) ):

                self.canvas.create_text(x-30, y ,  # 使用create_text方法在坐标（302，77）处绘制文字
                                        text='(' + er_hao_xian_zhan[i] + ')',  # 所绘制文字的内容
                                        fill='black'  # 所绘制文字的颜色为灰色
                                        )
            else:
                self.canvas.create_text(x, y - 10,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text='(' + er_hao_xian_zhan[i] + ')',  # 所绘制文字的内容
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
            if (i == 1 or i==2 or i==9 or i ==11):
                self.canvas.create_text(x, y + 15,  # 使用create_text方法在坐标（302，77）处绘制文字
                                        text='(' + wu_hao_xian_zhan[i] + ')',  # 所绘制文字的内容
                                        fill='black'  # 所绘制文字的颜色为灰色
                                        )
            elif (i == 5 or i ==6):
                self.canvas.create_text(x-30, y ,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text='(' + wu_hao_xian_zhan[i] + ')',  # 所绘制文字的内容
                                    fill='black'  # 所绘制文字的颜色为灰色
                                    )
            else:
                self.canvas.create_text(x, y - 10,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text='(' + wu_hao_xian_zhan[i] + ')',  # 所绘制文字的内容
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
            if (i == 6 or i == 8):
                self.canvas.create_text(x, y +20,  # 使用create_text方法在坐标（302，77）处绘制文字
                                        text='(' + ba_hao_xian_zhan[i] + ')',  # 所绘制文字的内容
                                        fill='black'  # 所绘制文字的颜色为灰色

                                        )
            else:
                self.canvas.create_text(x, y - 10,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text='(' + ba_hao_xian_zhan[i]+ ')',  # 所绘制文字的内容
                                    fill='black' # 所绘制文字的颜色为灰色

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
                                    text='(' + si_hao_xian_zhan[i] + ')',  # 所绘制文字的内容
                                    fill='black'  # 所绘制文字的颜色为灰色
                                    )

        # 顺序连接城市

        self.line_five(range(len(fivehaoxian_x)))

        # 初始城市之间的距离和信息素
        # for i in range(city_num):
        #     for j in range(city_num):
        #         pheromone_graph[i][j] = 1.0

        self.ants = [Ant(ID) for ID in range(30)]  # 初始蚁群
        self.best_ant = Ant(-1)  # 初始最优解
        self.best_ant.total_distance = 1 << 31  # 初始最大距离
        self.iter = 1  # 初始化迭代次数

    # 将节点按order顺序连线
    def line(self, order):
        # 删除原线
        self.canvas.delete("line")

        def line2(i1, i2):
            p1, p2 = self.nodes[i1], self.nodes[i2]
            self.canvas.create_line(p1, p2, width=6, fill="yellow", tags="line")
            return i2

        # order[-1]为初始值
        reduce(line2, order, order[0])

    def line_two(self, order):
        # 删除原线


        def line2(i1, i2):
            p1, p2 = self.twoNodes[i1], self.twoNodes[i2]
            self.canvas.create_line(p1, p2, width=6, fill="blue", tags="line")
            return i2

        # order[-1]为初始值
        reduce(line2, order, order[0])


    def line_five(self, order):
        # 删除原线


        def line2(i1, i2):
            p1, p2 = self.fiveNodes[i1], self.fiveNodes[i2]
            self.canvas.create_line(p1, p2, width=6, fill="green", tags="line")
            return i2

        # order[-1]为初始值
        reduce(line2, order, order[0])

    def line_three(self, order):
        # 删除原线


        def line2(i1, i2):
            p1, p2 = self.threeNodes[i1], self.threeNodes[i2]
            self.canvas.create_line(p1, p2, width=6, fill="red", tags="line")
            return i2

        # order[-1]为初始值
        reduce(line2, order, order[0])



    def line_four(self, order):
        # 删除原线


        def line2(i1, i2):
            p1, p2 = self.fourNodes[i1], self.fourNodes[i2]
            self.canvas.create_line(p1, p2, width=6, fill="#9400D3", tags="line")
            return i2

        # order[-1]为初始值
        reduce(line2, order, order[0])

    def display(self,path):
        self.canvas.delete("line")
        for i in range(len(path)-1):
            self.canvas.create_line(path[i], path[i+1], width=6, fill="green", tags="line")

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
                if ant.total_distance <= self.best_ant.total_distance:
                    # 更新最优解
                    self.best_ant = copy.deepcopy(ant)
            # 更新信息素
            self.__update_pheromone_gragh(self.best_ant.path)

            print(u"迭代次数：", self.iter, u"最佳路径总距离：", int(self.best_ant.total_distance),"站数",self.best_ant.move_count-1)
            # 连线
            self.display(self.best_ant.path)
            # 设置标题
            self.title("TSP蚁群算法(n:随机初始 e:开始搜索 s:停止搜索 q:退出程序) 迭代次数: %d" % self.iter)
            # 更新画布
            self.canvas.update()
            self.iter += 1

    # 更新信息素
    def __update_pheromone_gragh(self,path):
        if ((302,351) in path):
            global pheromone_zhujiang
            for ant in self.ants:
                pheromone_zhujiang =  (pheromone_zhujiang)  * 0.5 + Q / ant.total_distance
        if ((238,395) in path):
            global pheromone_kecun
            for ant in self.ants:
                pheromone_kecun =  (pheromone_kecun)  * 0.5 + Q / ant.total_distance


    # 主循环
    def mainloop(self):
        self.root.mainloop()


# ----------- 程序的入口处 -----------

if __name__ == '__main__':
    print(u""" 
--------------------------------------------------------

-------------------------------------------------------- 
    """)
    # print(pheromone_graph)
    TSP(tkinter.Tk()).mainloop()
