from flask import Blueprint, render_template, request
import io, base64
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colorbar import ColorbarBase
import fastf1 as ff1

# Create a Blueprint for the index route
index_bp = Blueprint('index', __name__)


def get_inputs():
    inputs = {}
    if request.method == 'POST':
        # Get user inputs
        inputs['year'] = 2024
        inputs['wknd'] = int(request.form['wknd'])
        inputs['ses'] = 'R'
        inputs['driver'] = request.form['driver']
    return inputs


@index_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Extract inputs
            inputs = get_inputs()
            year = inputs['year']
            wknd = inputs['wknd']
            ses = inputs['ses']
            driver = inputs['driver']

            # Load session and telemetry data
            session = ff1.get_session(year, wknd, ses)
            session.load()
            lap = session.laps.pick_driver(driver).pick_fastest()

            x = lap.telemetry['X']
            y = lap.telemetry['Y']
            speed = lap.telemetry['Speed']

            # Create plot
            fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(3.56, 2.2))
            fig.suptitle(f'{wknd} {year} - {driver} - Speed', size=5, y=0.47)
            ax.plot(x, y, color='black', linewidth=0.5)
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
            ax.axis('off')
            ax.plot(lap.telemetry['X'], lap.telemetry['Y']
                    , color='black', linewidth=0.5)

            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            norm = plt.Normalize(speed.min(), speed.max())
            lc = LineCollection(segments, cmap='plasma', norm=norm)
            lc.set_array(speed)
            ax.add_collection(lc)
            ax.autoscale()
            plt.axis('off')

            # Save to a BytesIO buffer
            img = io.BytesIO()
            plt.savefig(img, format='png', dpi=150, bbox_inches="tight")
            img.seek(0)
            plt.close()

            # Convert to base64 for embedding in HTML
            plot_url = base64.b64encode(img.getvalue()).decode('utf8')
            positions_url = base64.b64encode(img.getvalue()).decode('utf8')
            return render_template('index.html', plot_url=plot_url, positions_url=positions_url)

        except Exception as e:
            return render_template('index.html', error_message=f"Error: {str(e)}")

    return render_template('index.html', plot_url=None)