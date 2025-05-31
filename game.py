import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

class MarketSimulator:
    def __init__(self):
        # Market parameters
        self.base_demand = 100       # Base demand quantity
        self.base_supply = 100       # Base supply quantity
        self.demand_elasticity = -3.0  # Demand elasticity
        self.supply_elasticity = 3.0   # Supply elasticity
        self.tax_rate = 0.0          # Initial tax rate
        self.equilibrium_price = 10.0  # Initial equilibrium price
        self.equilibrium_quantity = 100 # Initial equilibrium quantity
        self.history = []             # History records
        
        # Calculate demand curve intercept (maximum willingness to pay)
        self.demand_intercept = self.equilibrium_price - self.base_demand / self.demand_elasticity
        
        # Calculate supply curve intercept (minimum acceptable price)
        self.supply_intercept = self.equilibrium_price - self.base_supply / self.supply_elasticity
        
    def demand_function(self, price):
        """Demand function calculation"""
        return self.base_demand + self.demand_elasticity * (price - self.equilibrium_price)
    
    def supply_function(self, price):
        """Supply function calculation"""
        return self.base_supply + self.supply_elasticity * (price - self.equilibrium_price)
    
    def find_equilibrium(self):
        """Find market equilibrium point"""
        # Iterative method to find equilibrium
        price = self.equilibrium_price
        for _ in range(100):
            demand = self.demand_function(price)
            # Supply considers after-tax price
            supply = self.supply_function(price - self.tax_rate)
            
            if abs(demand - supply) < 0.1:
                break
                
            # Adjust price
            if demand > supply:
                price *= 1.01  # Demand > supply, price increases
            else:
                price *= 0.99  # Supply > demand, price decreases
                
        quantity = min(demand, supply)
        return price, quantity
    
    def calculate_welfare(self, price, quantity):
        """Calculate social welfare (with deadweight loss)"""
        # 1. Calculate producer's actual price
        producer_price = price - self.tax_rate
        
        # 2. Calculate tax revenue
        tax_revenue = self.tax_rate * quantity
        
        # 3. Calculate consumer surplus
        consumer_surplus = 0.5 * (self.demand_intercept - price) * quantity
        
        # 4. Calculate producer surplus
        producer_surplus = 0.5 * (producer_price - self.supply_intercept) * quantity
        
        # 5. Calculate total welfare
        total_welfare = consumer_surplus + producer_surplus + tax_revenue
        
        # 6. Calculate deadweight loss
        # Get zero-tax equilibrium quantity
        zero_tax_price, zero_tax_quantity = self.find_zero_tax_equilibrium()
        deadweight_loss = 0.5 * self.tax_rate * (zero_tax_quantity - quantity)
        
        return consumer_surplus, producer_surplus, tax_revenue, total_welfare, deadweight_loss
    
    def find_zero_tax_equilibrium(self):
        """Find equilibrium with zero tax"""
        # Save current tax rate
        original_tax = self.tax_rate
        # Set tax rate to 0
        self.tax_rate = 0
        # Calculate equilibrium
        price, quantity = self.find_equilibrium()
        # Restore original tax rate
        self.tax_rate = original_tax
        return price, quantity

def create_interactive_game():
    """Create interactive game interface"""
    # Initialize simulator
    sim = MarketSimulator()
    
    # Create figure
    fig = plt.figure(figsize=(10, 8))
    fig.suptitle("Tax Welfare Analysis Game", fontsize=16, fontweight='bold')
    
    # Create two subplots (vertical arrangement)
    ax = plt.subplot(2, 1, 1)  # Top: Supply and demand curves
    ax2 = plt.subplot(2, 1, 2) # Bottom: Welfare analysis
    
    # Adjust layout
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.22, top=0.9, hspace=0.4)
    
    # Create price range
    prices = np.linspace(0, 25, 200)
    # Calculate demand curve
    demand = [sim.demand_function(p) for p in prices]
    # Calculate supply curve
    supply = [sim.supply_function(p) for p in prices]
    
    # Plot supply and demand curves
    demand_line, = ax.plot(prices, demand, 'b-', label='Demand Curve', linewidth=2.5)
    supply_line, = ax.plot(prices, supply, 'r-', label='Supply Curve', linewidth=2.5)
    
    # Calculate initial equilibrium
    eq_price, eq_quantity = sim.find_equilibrium()
    # Plot equilibrium point
    eq_point, = ax.plot(eq_price, eq_quantity, 'go', markersize=10, 
                       markerfacecolor='gold', markeredgecolor='black', 
                       label='Equilibrium')
    
    # Add concise equilibrium point label
    eq_label = ax.text(eq_price + 0.5, eq_quantity + 10, 
                      f"P={eq_price:.2f}, Q={eq_quantity:.2f}",
                      fontsize=10, bbox=dict(facecolor='white', alpha=0.9))
    
    # If tax exists, plot taxed supply curve
    if sim.tax_rate > 0:
        supply_tax = [sim.supply_function(p - sim.tax_rate) for p in prices]
        supply_tax_line, = ax.plot(prices, supply_tax, 'r--', label='Taxed Supply', 
                                  linewidth=2.0)
        ax.legend(loc='best', fontsize=9)
    
    # Set chart properties
    ax.set_title('Supply and Demand Curves', fontsize=14)
    ax.set_xlabel('Price', fontsize=12)
    ax.set_ylabel('Quantity', fontsize=12)
    ax.set_xlim(0, 25)
    ax.set_ylim(0, 250)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Welfare analysis chart (without value labels)
    welfare_labels = ['Consumer Surplus', 'Producer Surplus', 'Tax Revenue', 'Total Welfare', 'Deadweight Loss']
    welfare_data = sim.calculate_welfare(eq_price, eq_quantity)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#d62728']
    welfare_bars = ax2.bar(welfare_labels, welfare_data, color=colors, alpha=0.85)
    ax2.set_title('Social Welfare Analysis', fontsize=14)
    ax2.set_ylabel('Value', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Set welfare labels
    ax2.tick_params(axis='x', rotation=0)
    
    # Add tax rate slider (range 0-10)
    tax_ax = plt.axes([0.25, 0.14, 0.55, 0.03])
    tax_slider = Slider(
        ax=tax_ax, label='Tax Rate', 
        valmin=0, valmax=10, valinit=sim.tax_rate,
        valstep=0.1, color='#2ca02c'
    )
    
    # Add reset button
    reset_ax = plt.axes([0.4, 0.06, 0.2, 0.03])
    reset_button = Button(reset_ax, 'Reset Market', color='#1f77b4')
    
    # Add status panel (shorter width)
    status_box = plt.axes([0.15, 0.01, 0.7, 0.05])  # Narrower status box
    status_box.set_axis_off()
    status_text = status_box.text(0.5, 0.5, '', fontsize=10, 
                                ha='center', va='center',
                                bbox=dict(facecolor='#f7f7f7', alpha=0.9))
    
    def update_status():
        """Update status text"""
        # Calculate welfare metrics
        cs, ps, tr, total, dwl = sim.calculate_welfare(eq_price, eq_quantity)
        
        # Create status message
        status = (
            f"Price={eq_price:.2f}, Qty={eq_quantity:.2f} | "
            f"Tax: {sim.tax_rate:.2f} | "
            f"CS={cs:.2f}, PS={ps:.2f}, TR={tr:.2f}, Total={total:.2f}, DWL={dwl:.2f}"
        )
        
        # Update text object
        status_text.set_text(status)
    
    def update(val):
        """Update charts"""
        nonlocal eq_price, eq_quantity
        
        # Update tax rate
        sim.tax_rate = tax_slider.val
        
        # Calculate new equilibrium
        eq_price, eq_quantity = sim.find_equilibrium()
        
        # Update supply and demand curves
        demand_line.set_ydata([sim.demand_function(p) for p in prices])
        supply_line.set_ydata([sim.supply_function(p) for p in prices])
        
        # Update equilibrium point and label
        eq_point.set_data([eq_price], [eq_quantity])
        eq_label.set_text(f"P={eq_price:.2f}, Q={eq_quantity:.2f}")
        eq_label.set_position((eq_price + 0.5, eq_quantity + 10))
        
        # Clear previous taxed supply curves
        for line in ax.lines[2:]:
            if line.get_label() == 'Taxed Supply':
                line.remove()
        
        # Replot taxed supply curve (if tax exists)
        if sim.tax_rate > 0:
            supply_tax = [sim.supply_function(p - sim.tax_rate) for p in prices]
            ax.plot(prices, supply_tax, 'r--', label='Taxed Supply', linewidth=2.0)
            ax.legend(loc='best', fontsize=9)
        
        # Update welfare chart
        welfare_data = sim.calculate_welfare(eq_price, eq_quantity)
        for i, bar in enumerate(welfare_bars):
            bar.set_height(welfare_data[i])
        
        # Adjust Y-axis range to fit new data
        max_value = max(welfare_data) * 1.2
        ax2.set_ylim(0, max_value)
        
        # Update status
        update_status()
        
        # Record history
        sim.history.append({
            'tax': sim.tax_rate,
            'price': eq_price,
            'quantity': eq_quantity,
            'welfare': welfare_data[3]
        })
        
        fig.canvas.draw_idle()
    
    def reset(event):
        """Reset market"""
        nonlocal sim
        sim = MarketSimulator()
        tax_slider.set_val(0)
        update(None)
        fig.canvas.draw()
    
    # Set callback functions
    tax_slider.on_changed(update)
    reset_button.on_clicked(reset)
    
    # Initial update
    update_status()
    update(None)
    
    plt.show()

# Run the game
if __name__ == "__main__":
    create_interactive_game()
