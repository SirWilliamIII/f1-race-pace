from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend to avoid GUI issues
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colorbar import ColorbarBase  # Import ColorbarBase
import numpy as np
import fastf1 as ff1
import io
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user inputs
        year = 2024
        wknd = int(request.form['wknd'])
        ses = request.form['ses']
        driver = request.form['driver']

        try:
            # Load session data
            session = ff1.get_session(year, wknd, ses)
            weekend = session.event
            session.load()
            lap = session.laps.pick_driver(driver).pick_fastest()
            

            # Get telemetry data
            x = lap.telemetry['X']              # values for x-axis
            y = lap.telemetry['Y']              # values for y-axis
            color = lap.telemetry['Speed']      # value to base color gradient on

            # Create line segments
            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
            # Create the plot with a smaller size
            fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(3.56, 2.2))  # Shrunk by 70%
            fig.suptitle(f'{weekend.name} {year} - {driver} - Speed', size=10, y=0.97)  # Adjust title size

            # Adjust margins and turn off axis
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
            ax.axis('off')

            # Create background track line
            ax.plot(lap.telemetry['X'], lap.telemetry['Y'],
                    color='black', linestyle='-', linewidth=6, zorder=0)  # Adjust linewidth

            # Create a continuous norm to map from data points to colors
            norm = plt.Normalize(color.min(), color.max())
            lc = LineCollection(segments, cmap='plasma', norm=norm,
                                linestyle='-', linewidth=4)  # Adjust linewidth

            # Set the values used for colormapping
            lc.set_array(color)

            # Merge all line segments together
            line = ax.add_collection(lc)

            # Create a color bar as a legend
            cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
            normlegend = plt.Normalize(vmin=color.min(), vmax=color.max())
            legend = ColorbarBase(cbaxes, norm=normlegend, cmap='plasma',
                                  orientation="horizontal")

            # Save the plot to a BytesIO object
            img = io.BytesIO()
            plt.savefig(img, format='png', dpi=300, bbox_inches=None)
            img.seek(0)
            plt.close()

            # Encode the image to base64 for embedding in HTML
            plot_url = base64.b64encode(img.getvalue()).decode('utf8')

            return render_template('index.html', plot_url=plot_url)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            return render_template('index.html', error_message=error_message)

    return render_template('index.html', plot_url=None)


@app.route('/tire-strategy', methods=['GET', 'POST'])
def tire_strategy():
    if request.method == 'POST':
        # Get user inputs
        year = 2024
        wknd = request.form['wknd']
        ses = 'R'

        try:
            session = ff1.get_session(year, wknd, ses)
            session.load()
            drivers = session.drivers
            drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]
            laps = session.laps
            

            compound_colors = {
                "SOFT": "#FF3333",  # Red for Soft
                "MEDIUM": "#FFFF66",  # Yellow for Medium
                "HARD": "#0000FF",  # White for Hard
                "INTERMEDIATE": "#33CC33",  # Green for Intermediate
                "WET": "#3399FF"  # Blue for Wet
            }
            
            stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
            stints = stints.groupby(["Driver", "Stint", "Compound"])
            stints = stints.count().reset_index()
            stints = stints.rename(columns={"LapNumber": "StintLength"})
            
            
            fig, ax = plt.subplots(figsize=(3.5, 5))
            
            for driver in drivers:                    
                driver_stints = stints.loc[stints["Driver"] == driver]
                previous_stint_end = 0  # Track where the previous stint ended
                
                for idx, row in driver_stints.iterrows():
                    # Use the predefined color for the compound
                    c = compound_colors[row['Compound']]

                    # Plot the stint as a horizontal bar
                    plt.barh(
                        y=driver, 
                        width=row["StintLength"], 
                        left=previous_stint_end, 
                        color=c, 
                        edgecolor="black",
                        fill=True
                    )

                    # Update where the next stint should start
                    previous_stint_end += row["StintLength"]
                
            plt.title("2022 Hungarian Grand Prix Strategies")
            plt.xlabel("Lap Number")
            plt.grid(False)
            ax.invert_yaxis()  # Place drivers in reverse order (top = best finisher)

            # Aesthetics for cleaner output
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)

            plt.tight_layout()
            img = io.BytesIO()
            plt.savefig(img, format='png', dpi=300, bbox_inches=None)
            img.seek(0)
            plt.close()

            # Encode the image to base64 for embedding in HTML
            plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    
            return render_template('tire-strategy.html', plot_url=plot_url)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            return render_template('index.html', error_message=error_message)

    return render_template('index.html', plot_url=None)

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
