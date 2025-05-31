import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.gridspec as gridspec


class MarketSimulator:
    def __init__(self, demand_elasticity=-3.0, supply_elasticity=3.0):
        # Market parameters
        self.base_demand = 100  # Base demand quantity
        self.base_supply = 100  # Base supply quantity
        self.demand_elasticity = demand_elasticity  # Demand elasticity
        self.supply_elasticity = supply_elasticity  # Supply elasticity
        self.tax_rate = 0.0  # Initial tax rate
        self.history = []  # History records

        # Calculate initial curves and equilibrium
        self.update_curves()

    def update_curves(self):
        """Update curves when elasticity or tax changes"""
        # Calculate demand curve intercept (maximum willingness to pay)
        # Using equilibrium condition at base point (P=10, Q=100)
        self.demand_intercept = 10 - 100 / self.demand_elasticity

        # Calculate supply curve intercept (minimum acceptable price)
        self.supply_intercept = 10 - 100 / self.supply_elasticity

        # Find current equilibrium
        self.find_equilibrium()

    def demand_function(self, price):
        """Demand function calculation"""
        return self.demand_elasticity * (price - self.demand_intercept)

    def supply_function(self, price):
        """Supply function calculation"""
        return self.supply_elasticity * (price - self.supply_intercept)

    def taxed_supply_function(self, price):
        """Taxed supply function calculation"""
        # Price received by producers is consumer price minus tax
        producer_price = price - self.tax_rate
        return self.supply_elasticity * (producer_price - self.supply_intercept)

    def find_equilibrium(self):
        """Find market equilibrium point"""
        # Find where demand equals taxed supply
        # Solve: demand_elasticity * (P - demand_intercept) = supply_elasticity * ((P - tax_rate) - supply_intercept)

        # Analytical solution
        numerator = (self.supply_elasticity * (self.tax_rate + self.supply_intercept)
                     - self.demand_elasticity * self.demand_intercept)
        denominator = self.supply_elasticity - self.demand_elasticity

        # Calculate equilibrium price and quantity
        self.equilibrium_price = numerator / denominator
        self.equilibrium_quantity = self.demand_function(self.equilibrium_price)

        # Ensure non-negative quantity
        self.equilibrium_quantity = max(0, self.equilibrium_quantity)

        return self.equilibrium_price, self.equilibrium_quantity

    def calculate_welfare(self):
        """Calculate social welfare"""
        # Consumer price is equilibrium price
        consumer_price = self.equilibrium_price
        # Producer price is consumer price minus tax
        producer_price = consumer_price - self.tax_rate
        quantity = self.equilibrium_quantity

        # 1. Consumer surplus (triangle under demand curve and above price)
        consumer_surplus = 0.5 * (self.demand_intercept - consumer_price) * quantity

        # 2. Producer surplus (triangle above supply curve and below price)
        producer_surplus = 0.5 * (producer_price - self.supply_intercept) * quantity

        # 3. Tax revenue
        tax_revenue = self.tax_rate * quantity

        # 4. Total welfare
        total_welfare = consumer_surplus + producer_surplus + tax_revenue

        # 5. Deadweight loss - difference from zero-tax welfare
        # Calculate zero-tax welfare
        original_tax = self.tax_rate
        self.tax_rate = 0
        zero_tax_price, zero_tax_quantity = self.find_equilibrium()
        zero_tax_cs = 0.5 * (self.demand_intercept - zero_tax_price) * zero_tax_quantity
        zero_tax_ps = 0.5 * (zero_tax_price - self.supply_intercept) * zero_tax_quantity
        zero_tax_total = zero_tax_cs + zero_tax_ps

        # Restore actual tax rate
        self.tax_rate = original_tax

        deadweight_loss = max(0, zero_tax_total - total_welfare)

        return consumer_surplus, producer_surplus, tax_revenue, total_welfare, deadweight_loss


def create_interactive_game():
    """Create interactive game interface with adjustable elasticities"""
    # Initialize simulator
    sim = MarketSimulator()

    # Create figure with custom grid layout
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle("Tax Welfare Analysis", fontsize=16, fontweight='bold', y=0.98)  # 提高主标题位置

    # Use GridSpec for better layout control
    gs = gridspec.GridSpec(2, 2, height_ratios=[3, 1], width_ratios=[3, 1])

    # Create axes
    ax = plt.subplot(gs[0, 0])  # Supply and demand curves (main plot)
    ax2 = plt.subplot(gs[1, 0])  # Welfare analysis (bottom left)
    ax_controls = plt.subplot(gs[0:2, 1])  # Controls panel (right column)
    ax_controls.set_axis_off()  # We'll create our own axes for controls

    # Adjust layout with more space at the top
    plt.subplots_adjust(left=0.08, right=0.92, bottom=0.1, top=0.92,
                        hspace=0.3, wspace=0.3)

    # Create quantity range (x-axis)
    quantities = np.linspace(0, 200, 200)  # Reasonable quantity range

    # Calculate and plot demand curve (price as function of quantity)
    demand_prices = [q / sim.demand_elasticity + sim.demand_intercept for q in quantities]
    demand_line, = ax.plot(quantities, demand_prices, 'b-', linewidth=2.0)

    # Calculate and plot supply curve
    supply_prices = [q / sim.supply_elasticity + sim.supply_intercept for q in quantities]
    supply_line, = ax.plot(quantities, supply_prices, 'r-', linewidth=2.0)

    # Find initial equilibrium
    consumer_price, quantity = sim.find_equilibrium()

    # Plot equilibrium point with a label
    eq_point, = ax.plot(quantity, consumer_price, 'go', markersize=10,
                        markerfacecolor='gold', markeredgecolor='black', zorder=10)

    # 平衡点标签 - 美化版本
    eq_label = ax.annotate(
        f'Price: {consumer_price:.2f}\nQuantity: {quantity:.2f}',
        xy=(quantity, consumer_price),
        xytext=(quantity, consumer_price + 2.5),  # 在点上方的固定位置
        textcoords='data',
        ha='center',
        va='bottom',
        fontsize=10,
        bbox=dict(
            boxstyle='round,pad=0.5',
            fc='#FFF8DC',  # 浅米色背景
            ec='#DAA520',  # 金色边框
            lw=1.5,
            alpha=0.95
        )
    )

    # Create taxed supply curve (always visible in legend)
    taxed_supply_prices = [q / sim.supply_elasticity + sim.supply_intercept + sim.tax_rate for q in quantities]
    supply_tax_line, = ax.plot(quantities, taxed_supply_prices, 'r--', linewidth=1.5)

    # Add legend with all elements including taxed supply
    ax.legend([demand_line, supply_line, supply_tax_line, eq_point],
              ['Demand', 'Supply', 'Taxed Supply', 'Equilibrium'],
              loc='upper right', fontsize=9, framealpha=0.9)

    # 图表标题居中显示，有合适间距
    ax.set_title("Supply and Demand Curves", fontsize=12, pad=10, y=1.0)  # 居中位置
    ax.title.set_position([0.5, 1.0])  # 确保标题在图表上方居中

    # Set chart properties
    ax.set_xlabel('Quantity', fontsize=11)
    ax.set_ylabel('Price', fontsize=11)
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 20)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Welfare analysis chart
    welfare_labels = ['CS', 'PS', 'Tax', 'Total', 'DWL']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#d62728']
    welfare_data = sim.calculate_welfare()
    welfare_bars = ax2.bar(welfare_labels, welfare_data, color=colors, alpha=0.85)
    ax2.set_ylabel('Value', fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.7, axis='y')

    # 福利图表标题居中显示
    ax2.set_title("Welfare Analysis", fontsize=12, pad=10, y=1.0)  # 居中位置
    ax2.title.set_position([0.5, 1.0])  # 确保标题在图表上方居中

    # 美化右侧控制面板
    # 添加控制面板标题 - 位置调整
    control_title = plt.figtext(0.85, 0.88, "Market Parameters",
                                fontsize=12, fontweight='bold', ha='center')

    # Add control sliders in the right panel with improved styling
    # Create axes for controls with relative positioning
    tax_ax = fig.add_axes([0.75, 0.85, 0.2, 0.03])
    tax_slider = Slider(
        ax=tax_ax, label='Tax Rate',
        valmin=0, valmax=10, valinit=sim.tax_rate,
        valstep=0.1, color='#2ca02c',
        track_color='#e0f2e0',  # 浅绿色轨道
    )
    tax_ax.set_facecolor('#f8f8f8')  # 设置背景色

    # Add elasticity controls
    demand_ax = fig.add_axes([0.75, 0.80, 0.2, 0.03])
    demand_elasticity_slider = Slider(
        ax=demand_ax, label='Demand Elasticity',
        valmin=-5.0, valmax=-0.5, valinit=sim.demand_elasticity,
        valstep=0.1, color='#1f77b4',
        track_color='#e0e8f0'  # 浅蓝色轨道
    )
    demand_ax.set_facecolor('#f8f8f8')  # 设置背景色

    supply_ax = fig.add_axes([0.75, 0.75, 0.2, 0.03])
    supply_elasticity_slider = Slider(
        ax=supply_ax, label='Supply Elasticity',
        valmin=0.5, valmax=5.0, valinit=sim.supply_elasticity,
        valstep=0.1, color='#ff7f0e',
        track_color='#f8e8d0'  # 浅橙色轨道
    )
    supply_ax.set_facecolor('#f8f8f8')  # 设置背景色

    # 添加重置按钮 - 使用更美观的样式
    reset_ax = fig.add_axes([0.75, 0.70, 0.2, 0.05])
    reset_button = Button(reset_ax, 'Reset Market', color='#1f77b4', hovercolor='#4a90d9')
    reset_ax.set_facecolor('#f8f8f8')  # 设置背景色

    # 美化福利指标表格
    # 创建福利指标表格 - 添加标题和边框
    table_ax = fig.add_axes([0.75, 0.05, 0.2, 0.55])
    table_ax.set_axis_off()

    # 添加表格标题 - 位置调整
    table_title = plt.figtext(0.85, 0.60, "Welfare Metrics",
                              fontsize=12, fontweight='bold', ha='center')

    # 初始化表格数据
    welfare_metrics = [
        ("Equilibrium Price", f"{consumer_price:.2f}"),
        ("Equilibrium Quantity", f"{quantity:.2f}"),
        ("Consumer Surplus", f"{welfare_data[0]:.2f}"),
        ("Producer Surplus", f"{welfare_data[1]:.2f}"),
        ("Tax Revenue", f"{welfare_data[2]:.2f}"),
        ("Total Welfare", f"{welfare_data[3]:.2f}"),
        ("Deadweight Loss", f"{welfare_data[4]:.2f}")
    ]

    # 创建表格 - 使用更大的边界框和边框
    table = table_ax.table(
        cellText=welfare_metrics,
        colLabels=["Metric", "Value"],
        cellLoc='center',
        loc='center',
        bbox=[0.1, 0.1, 0.85, 0.85],
        edges='closed'  # 添加表格边框
    )

    # 表格样式优化以适应内容
    table.auto_set_font_size(False)
    table.set_fontsize(10)  # 使用稍大的字体
    table.auto_set_column_width([0, 1])  # 自动调整列宽

    # 设置标题行样式
    for (row, col), cell in table.get_celld().items():
        if row == 0:  # 标题行
            cell.set_facecolor('#4a7b9d')
            cell.set_text_props(color='white', weight='bold')
            cell.set_edgecolor('#2a5a7d')  # 更深的边框颜色
        elif row % 2 == 1:  # 交替行颜色
            cell.set_facecolor('#f5f5f5')  # 更浅的灰色
        # 设置所有单元格的边框
        cell.set_edgecolor('#d0d0d0')

    # 存储参考线用于更新
    ref_lines = {
        'supply_tax_line': supply_tax_line,
        'table': table,
        'eq_label': eq_label,
        'eq_point': eq_point
    }

    def update_elasticity():
        """更新弹性值并重新计算曲线"""
        # 更新弹性值
        sim.demand_elasticity = demand_elasticity_slider.val
        sim.supply_elasticity = supply_elasticity_slider.val

        # 更新曲线
        sim.update_curves()

    def update(val):
        """更新图表"""
        nonlocal consumer_price, quantity, welfare_data

        # 更新税率
        sim.tax_rate = tax_slider.val

        # 找到新的均衡点
        consumer_price, quantity = sim.find_equilibrium()

        # 重新计算福利
        welfare_data = sim.calculate_welfare()

        # 更新供需曲线
        demand_prices = [q / sim.demand_elasticity + sim.demand_intercept for q in quantities]
        demand_line.set_ydata(demand_prices)
        supply_prices = [q / sim.supply_elasticity + sim.supply_intercept for q in quantities]
        supply_line.set_ydata(supply_prices)

        # 更新均衡点和标签 - 标签随点一起移动
        ref_lines['eq_point'].set_data([quantity], [consumer_price])
        ref_lines['eq_label'].xy = (quantity, consumer_price)
        ref_lines['eq_label'].set_position((quantity, consumer_price + 2.5))
        ref_lines['eq_label'].set_text(f'Price: {consumer_price:.2f}\nQuantity: {quantity:.2f}')

        # 更新含税供给曲线
        taxed_supply_prices = [q / sim.supply_elasticity + sim.supply_intercept + sim.tax_rate for q in quantities]
        ref_lines['supply_tax_line'].set_ydata(taxed_supply_prices)

        # 更新福利图表
        for i, bar in enumerate(welfare_bars):
            bar.set_height(welfare_data[i])

        # 调整Y轴范围以适应新数据
        max_value = max(welfare_data) * 1.2
        ax2.set_ylim(0, max_value)

        # 使用新值更新表格
        new_metrics = [
            ("Equilibrium Price", f"{consumer_price:.2f}"),
            ("Equilibrium Quantity", f"{quantity:.2f}"),
            ("Consumer Surplus", f"{welfare_data[0]:.2f}"),
            ("Producer Surplus", f"{welfare_data[1]:.2f}"),
            ("Tax Revenue", f"{welfare_data[2]:.2f}"),
            ("Total Welfare", f"{welfare_data[3]:.2f}"),
            ("Deadweight Loss", f"{welfare_data[4]:.2f}")
        ]

        # 更新表格数据
        for i, (metric, value) in enumerate(new_metrics):
            ref_lines['table'].get_celld()[(i + 1, 0)].get_text().set_text(metric)
            ref_lines['table'].get_celld()[(i + 1, 1)].get_text().set_text(value)

        fig.canvas.draw_idle()

    def update_elasticity_and_chart(val):
        """更新弹性并更新图表"""
        update_elasticity()
        update(val)

    def reset(event):
        """将市场重置为初始状态"""
        nonlocal sim, consumer_price, quantity, welfare_data

        # 重置为初始值
        sim = MarketSimulator()

        # 更新滑块
        tax_slider.set_val(0)
        demand_elasticity_slider.set_val(-3.0)
        supply_elasticity_slider.set_val(3.0)

        # 获取初始值
        consumer_price, quantity = sim.find_equilibrium()
        welfare_data = sim.calculate_welfare()

        # 更新图表
        update(None)
        fig.canvas.draw()

    # 设置回调函数
    tax_slider.on_changed(update)
    demand_elasticity_slider.on_changed(update_elasticity_and_chart)
    supply_elasticity_slider.on_changed(update_elasticity_and_chart)
    reset_button.on_clicked(reset)

    # 初始更新
    update(None)

    # 添加美学改进
    fig.patch.set_facecolor('#f5f5f5')
    ax.set_facecolor('#ffffff')
    ax2.set_facecolor('#ffffff')
    table_ax.set_facecolor('#f9f9f9')

    plt.show()


# 运行游戏
if __name__ == "__main__":
    create_interactive_game()
