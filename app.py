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
            
            
            
            ################## Add the following code ##################
            
            
            
            
            
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
            print(f"Plot URL: {plot_url}")  # Debugging line

            return render_template('index.html', plot_url=plot_url)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            return render_template('index.html', error_message=error_message)

    return render_template('index.html', plot_url=None)

if __name__ == '__main__':
    app.run(debug=True)