import sys

from gym_trading_env.renderer import Renderer

sys.path.append("./src")

renderer = Renderer(render_logs_dir="render_logs")

# # Add Custom Lines (Simple Moving Average)
# renderer.add_line(name="sma10",
#                   function=lambda df: df["close"].rolling(10).mean(),
#                   line_options={"width" : 1, "color": "purple"})
# renderer.add_line(name= "sma20",
#                   function=lambda df: df["close"].rolling(20).mean(),
#                   line_options = {"width" : 1, "color": "blue"})

# # Add Custom Metrics (Annualized metrics)
# amr = 100 * ( (df['close'].iloc[-1] / df['close'].iloc[0])
#                   **(pd.Timedelta(days=365) / (df.index.values[-1] - df.index.values[0]))
#                   - 1 )
# renderer.add_metric(name="Annual Market Return",
#                     function=lambda df: f"{amr:0.2f}%"
# )

# apr = 100 * ( (df['portfolio_valuation'].iloc[-1] / df['portfolio_valuation'].iloc[0])
#                   **(pd.Timedelta(days=365) / (df.index.values[-1] - df.index.values[0]))
#                   - 1 )

# renderer.add_metric(name="Annual Portfolio Return",
#                     function=lambda df: f"{apr:0.2f}%"
# )

renderer.run()
