import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

class MarketSimulator:
    def __init__(self):
        # Initial market parameters with increased elasticity
        self.base_demand = 100       # Base demand quantity
        self.base_supply = 100       # Base supply quantity
        self.demand_elasticity = -2.5  # Increased demand elasticity (more responsive)
        self.supply_elasticity = 2.5   # Increased supply elasticity (more responsive)
        self.tax_rate = 0.0          # Initial tax rate
        self.equilibrium_price = 10.0  # Initial equilibrium price
        self.equilibrium_quantity = 100 # Initial equilibrium quantity
        self.history = []             # History records
        
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
            supply = self.supply_function(price - self.tax_rate)  # Supply considers after-tax price
            
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
        """Calculate social welfare with corrected producer surplus"""
        # Consumer surplus (triangle area under demand curve)
        max_willingness = self.demand_function(0)
        consumer_surplus = 0.5 * (max_willingness - self.demand_function(price)) * quantity
        
        # Producer surplus (triangle area above supply curve)
        p0 = self.equilibrium_price - self.base_supply/self.supply_elasticity
        producer_surplus = 0.5 * (price - p0) * quantity
        
        # Government tax revenue
        tax_revenue = quantity * self.tax_rate
        
        total_welfare = consumer_surplus + producer_surplus + tax_revenue
        return consumer_surplus, producer_surplus, tax_revenue, total_welfare

def create_interactive_game():
    """Create interactive game interface with enhanced visuals"""
    # Initialize simulator
    sim = MarketSimulator()
    
    # Create figure with adjusted size
    fig = plt.figure(figsize=(10, 8.5))
    
    # Create two subplots vertically with adjusted spacing
    ax = plt.subplot(2, 1, 1)  # Top plot for supply and demand
    ax2 = plt.subplot(2, 1, 2) # Bottom plot for welfare analysis
    
    # Adjust spacing between subplots and bottom margin
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.22, top=0.95, hspace=0.45)
    
    # Initial data with extended price range
    prices = np.linspace(0, 25, 200)  # Extended price range
    demand = [sim.demand_function(p) for p in prices]
    supply = [sim.supply_function(p) for p in prices]
    
    # Plot thicker and more distinct supply and demand curves
    demand_line, = ax.plot(prices, demand, 'b-', label='Demand', linewidth=3, alpha=0.9)
    supply_line, = ax.plot(prices, supply, 'r-', label='Supply', linewidth=3, alpha=0.9)
    
    # Plot equilibrium point with enhanced visual
    eq_price, eq_quantity = sim.find_equilibrium()
    eq_point, = ax.plot(eq_price, eq_quantity, 'go', markersize=12, 
                       markerfacecolor='gold', markeredgecolor='black', 
                       markeredgewidth=1.5, label='Equilibrium')
    
    # Add equilibrium point annotation with larger font
    eq_label = ax.text(eq_price + 0.5, eq_quantity + 10, 
                      f"Eq: P={eq_price:.2f}, Q={eq_quantity:.2f}",
                      fontsize=11, fontweight='bold',
                      bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray'))
    
    # Plot tax impact with dashed line
    if sim.tax_rate > 0:
        supply_tax = [sim.supply_function(p - sim.tax_rate) for p in prices]
        supply_tax_line, = ax.plot(prices, supply_tax, 'r--', label='Supply with Tax', 
                                  linewidth=2.5, alpha=0.8)
        ax.legend(loc='best', fontsize=10)
    
    # Set chart properties with enhanced visuals
    ax.set_title('Supply and Demand Curves', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Price', fontsize=13, labelpad=10)
    ax.set_ylabel('Quantity', fontsize=13, labelpad=10)
    ax.set_xlim(0, 25)
    ax.set_ylim(0, 250)  # Increased y-axis range
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.tick_params(axis='both', which='major', labelsize=11)
    
    # Welfare chart with enhanced visuals and horizontal labels
    welfare_labels = ['Consumer Surplus', 'Producer Surplus', 'Tax Revenue', 'Total Welfare']
    welfare_data = sim.calculate_welfare(eq_price, eq_quantity)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd']
    welfare_bars = ax2.bar(welfare_labels, welfare_data, color=colors, alpha=0.85)
    ax2.set_title('Social Welfare Analysis', fontsize=16, fontweight='bold', pad=15)
    ax2.set_ylabel('Value', fontsize=13, labelpad=10)
    ax2.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Set horizontal labels for welfare analysis
    ax2.tick_params(axis='x', rotation=0, labelsize=11)  # Changed rotation to 0 (horizontal)
    ax2.tick_params(axis='y', labelsize=11)
    
    # Add tax rate slider with better positioning and styling
    tax_ax = plt.axes([0.25, 0.14, 0.55, 0.03])
    tax_slider = Slider(
        ax=tax_ax, label='Tax Rate', 
        valmin=0, valmax=5, valinit=sim.tax_rate,
        valstep=0.1, color='#2ca02c',
        track_color='#c7e9c0'
    )
    tax_ax.tick_params(labelsize=11)
    
    # Add reset button with better styling
    reset_ax = plt.axes([0.4, 0.06, 0.2, 0.03])
    reset_button = Button(reset_ax, 'Reset Market', 
                         color='#1f77b4', hovercolor='#4d94d6')
    reset_button.label.set_fontsize(11)
    
    # Add enhanced status panel with centered text
    status_box = plt.axes([0.05, 0.01, 0.9, 0.05])
    status_box.set_axis_off()
    status_text = status_box.text(0.5, 0.5, '', fontsize=12, 
                                ha='center', va='center',  # Center alignment
                                bbox=dict(boxstyle='round', facecolor='#f7f7f7', 
                                         alpha=0.9, edgecolor='#d9d9d9'))
    
    def update_status():
        """Update status text with detailed welfare information"""
        consumer_surplus, producer_surplus, tax_revenue, total_welfare = sim.calculate_welfare(eq_price, eq_quantity)
        
        # Create formatted status message
        status = (
            f"Market: Price={eq_price:.2f}, Quantity={eq_quantity:.2f} | "
            f"Tax Rate: {sim.tax_rate:.2f} | "
            f"Welfare: CS={consumer_surplus:.2f}, PS={producer_surplus:.2f}, "
            f"TR={tax_revenue:.2f}, Total={total_welfare:.2f}"
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
        eq_label.set_text(f"Eq: P={eq_price:.2f}, Q={eq_quantity:.2f}")
        eq_label.set_position((eq_price + 0.5, eq_quantity + 10))
        
        # Clear previous tax curves
        for line in ax.lines[2:]:
            if line.get_label() == 'Supply with Tax':
                line.remove()
        
        # Replot tax curve
        if sim.tax_rate > 0:
            supply_tax = [sim.supply_function(p - sim.tax_rate) for p in prices]
            ax.plot(prices, supply_tax, 'r--', label='Supply with Tax', linewidth=2.5, alpha=0.8)
            ax.legend(loc='best', fontsize=10)
        
        # Update welfare chart
        welfare_data = sim.calculate_welfare(eq_price, eq_quantity)
        for i, bar in enumerate(welfare_bars):
            bar.set_height(welfare_data[i])
        ax2.set_ylim(0, max(welfare_data) * 1.2)
        
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
        ax.set_title('Supply and Demand Curves', color='black')
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
