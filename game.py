import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import random

class MarketSimulator:
    def __init__(self):
        # 初始市场参数
        self.base_demand = 100      # 基础需求量
        self.base_supply = 100      # 基础供给量
        self.demand_elasticity = -1.5  # 需求弹性系数
        self.supply_elasticity = 1.2   # 供给弹性系数
        self.tax_rate = 0.0         # 初始税率
        self.equilibrium_price = 10.0  # 初始均衡价格
        self.equilibrium_quantity = 100 # 初始均衡数量
        self.history = []            # 历史记录
        
    def demand_function(self, price):
        """计算需求函数"""
        return self.base_demand + self.demand_elasticity * (price - self.equilibrium_price)
    
    def supply_function(self, price):
        """计算供给函数"""
        return self.base_supply + self.supply_elasticity * (price - self.equilibrium_price)
    
    def find_equilibrium(self):
        """计算市场均衡点"""
        # 使用迭代法寻找均衡
        price = self.equilibrium_price
        for _ in range(100):
            demand = self.demand_function(price)
            supply = self.supply_function(price - self.tax_rate)  # 供给考虑税后价格
            
            if abs(demand - supply) < 0.1:
                break
                
            # 调整价格
            if demand > supply:
                price *= 1.01  # 需求大于供给，价格上涨
            else:
                price *= 0.99  # 供给大于需求，价格下降
                
        quantity = min(demand, supply)
        return price, quantity
    
    def calculate_welfare(self, price, quantity):
        """计算社会福利"""
        # 消费者剩余 (三角形面积)
        max_willingness = self.demand_function(0)
        consumer_surplus = 0.5 * (max_willingness - self.demand_function(price)) * quantity
        
        # 生产者剩余
        min_willingness = self.supply_function(0)
        producer_surplus = 0.5 * (price - min_willingness) * quantity
        
        # 政府税收
        tax_revenue = quantity * self.tax_rate
        
        total_welfare = consumer_surplus + producer_surplus + tax_revenue
        return consumer_surplus, producer_surplus, tax_revenue, total_welfare
    
    def apply_random_shock(self):
        """应用随机市场冲击"""
        shock_type = random.choice(['demand', 'supply'])
        
        if shock_type == 'demand':
            # 需求冲击 (如: 消费者偏好变化)
            self.base_demand *= random.uniform(0.8, 1.2)
            self.demand_elasticity *= random.uniform(0.9, 1.1)
        else:
            # 供给冲击 (如: 生产成本变化)
            self.base_supply *= random.uniform(0.8, 1.2)
            self.supply_elasticity *= random.uniform(0.9, 1.1)
        
        # 更新均衡点
        self.equilibrium_price, self.equilibrium_quantity = self.find_equilibrium()
        return shock_type

def create_interactive_game():
    """创建交互式游戏界面"""
    # 初始化模拟器
    sim = MarketSimulator()
    
    # 创建图表
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    plt.subplots_adjust(left=0.1, bottom=0.3)
    
    # 初始数据
    prices = np.linspace(0, 20, 100)
    demand = [sim.demand_function(p) for p in prices]
    supply = [sim.supply_function(p) for p in prices]
    
    # 绘制供需曲线
    demand_line, = ax.plot(prices, demand, 'b-', label='需求')
    supply_line, = ax.plot(prices, supply, 'r-', label='供给')
    
    # 绘制均衡点
    eq_price, eq_quantity = sim.find_equilibrium()
    eq_point, = ax.plot(eq_price, eq_quantity, 'go', markersize=10)
    
    # 绘制税收影响
    if sim.tax_rate > 0:
        supply_tax = [sim.supply_function(p - sim.tax_rate) for p in prices]
        supply_tax_line, = ax.plot(prices, supply_tax, 'r--', label='税后供给')
        ax.legend()
    
    # 设置图表属性
    ax.set_title('市场供需曲线')
    ax.set_xlabel('价格')
    ax.set_ylabel('数量')
    ax.set_ylim(0, 200)
    ax.grid(True)
    
    # 福利图表
    welfare_labels = ['消费者剩余', '生产者剩余', '政府税收', '总福利']
    welfare_data = sim.calculate_welfare(eq_price, eq_quantity)
    welfare_bars = ax2.bar(welfare_labels, welfare_data, color=['blue', 'red', 'green', 'purple'])
    ax2.set_title('社会福利分析')
    ax2.set_ylabel('价值')
    
    # 添加税率滑块
    ax_tax = plt.axes([0.1, 0.15, 0.8, 0.03])
    tax_slider = Slider(
        ax=ax_tax, label='税率', 
        valmin=0, valmax=5, valinit=sim.tax_rate,
        valstep=0.1
    )
    
    # 添加随机冲击按钮
    ax_shock = plt.axes([0.1, 0.05, 0.3, 0.04])
    shock_button = Button(ax_shock, '应用市场冲击')
    
    # 添加重置按钮
    ax_reset = plt.axes([0.6, 0.05, 0.3, 0.04])
    reset_button = Button(ax_reset, '重置市场')
    
    # 添加状态文本
    status_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12,
                         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    def update_status():
        """更新状态文本"""
        status = (
            f"均衡价格: {eq_price:.2f}\n"
            f"均衡数量: {eq_quantity:.2f}\n"
            f"税率: {sim.tax_rate:.2f}\n"
            f"需求弹性: {sim.demand_elasticity:.2f}\n"
            f"供给弹性: {sim.supply_elasticity:.2f}"
        )
        status_text.set_text(status)
    
    def update(val):
        """更新图表"""
        nonlocal eq_price, eq_quantity
        
        # 更新税率
        sim.tax_rate = tax_slider.val
        
        # 计算新均衡
        eq_price, eq_quantity = sim.find_equilibrium()
        
        # 更新供需曲线
        demand_line.set_ydata([sim.demand_function(p) for p in prices])
        supply_line.set_ydata([sim.supply_function(p) for p in prices])
        
        # 更新均衡点
        eq_point.set_data([eq_price], [eq_quantity])
        
        # 更新税收曲线
        for line in ax.lines[2:]:
            line.remove()
        
        if sim.tax_rate > 0:
            supply_tax = [sim.supply_function(p - sim.tax_rate) for p in prices]
            ax.plot(prices, supply_tax, 'r--', label='税后供给')
            ax.legend()
        
        # 更新福利图表
        welfare_data = sim.calculate_welfare(eq_price, eq_quantity)
        for i, bar in enumerate(welfare_bars):
            bar.set_height(welfare_data[i])
        ax2.set_ylim(0, max(welfare_data) * 1.2)
        
        # 更新状态
        update_status()
        
        # 记录历史
        sim.history.append({
            'tax': sim.tax_rate,
            'price': eq_price,
            'quantity': eq_quantity,
            'welfare': welfare_data[3]
        })
        
        fig.canvas.draw_idle()
    
    def apply_shock(event):
        """应用市场冲击"""
        shock_type = sim.apply_random_shock()
        update_status()
        update(None)
        
        # 显示冲击信息
        ax.set_title(f"市场供需曲线 - {shock_type}冲击发生!")
        plt.pause(1)
        ax.set_title('市场供需曲线')
    
    def reset(event):
        """重置市场"""
        nonlocal sim
        sim = MarketSimulator()
        tax_slider.set_val(0)
        update(None)
    
    # 设置回调函数
    tax_slider.on_changed(update)
    shock_button.on_clicked(apply_shock)
    reset_button.on_clicked(reset)
    
    # 初始更新
    update_status()
    update(None)
    
    plt.show()

# 运行游戏
if __name__ == "__main__":
    create_interactive_game()
