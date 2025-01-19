from flask import Flask, render_template, request
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')  # Use the 'Agg' backend to avoid GUI issues
from matplotlib.collections import LineCollection
from matplotlib.colorbar import ColorbarBase  # Import ColorbarBase
import numpy as np
import fastf1 as ff1
import io
import base64
from fastf1.plotting._constants import Constants
from flask import session as flask_session




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
            fig.suptitle(f'{weekend.name} {year} - {driver} - Speed', size=5, y=0.47)  # Adjust title size

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
            cbaxes = fig.add_axes([0.10, 0.05, 0.25, 0.10])
            normlegend = plt.Normalize(vmin=color.min(), vmax=color.max())
            legend = ColorbarBase(cbaxes, norm=normlegend, cmap='plasma', orientation='horizontal')

            # Save the plot to a BytesIO object
            img = io.BytesIO()
            plt.savefig(img, format='png', dpi=150, bbox_inches="tight")
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
        session_name = ""
        try:
            print(wknd)
            session = ff1.get_session(year, int(wknd), ses)
            session.load()
            drivers = session.drivers
            drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]
            laps = session.laps
            
            session_name = session.event['EventName']
            
            compound_colors = {
                "SOFT": "#FF3333",  # Red for Soft
                "MEDIUM": "#FFFF66",  # Yellow for Medium
                "HARD": "#0033FF",  # Blue for Hard
                "INTERMEDIATE": "#33CC33",  # Green for Intermediate
                "WET": "#3399FF"  # Blue for Wet
            }
            
            stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
            stints = stints.groupby(["Driver", "Stint", "Compound"])
            stints = stints.count().reset_index()
            stints = stints.rename(columns={"LapNumber": "StintLength"})
            
            
            fig, ax = plt.subplots(figsize=(3.5, 5))
            plt.subplots_adjust(left=0.3, right=0.95, top=0.9, bottom=0.1)
            
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
                        fill=True,
                        height=0.8
                    )

                    # Update where the next stint should start
                    previous_stint_end += row["StintLength"]

            plt.title(session_name, fontsize=12)
            plt.xlabel("Lap Number", fontsize=12)
            plt.xticks(fontsize=10)
            plt.yticks(fontsize=10)
            plt.grid(False)
            plt.tight_layout()
            
            ax.invert_yaxis()  # Place drivers in reverse order (top = best finisher)

            # Aesthetics for cleaner output
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)

            
            
            
            img = io.BytesIO()
            plt.savefig(img, format='png', dpi=200, bbox_inches=None)
            img.seek(0)
            plt.close()

            # Encode the image to base64 for embedding in HTML
            plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    
            return render_template('tire-strategy.html', plot_url=plot_url)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            return render_template('tire-strategy.html', error_message=error_message)

    return render_template('tire-strategy.html', plot_url=None)


@app.route('/colormap', methods=['GET'])
def get_colormap():
    n = len(Constants)  # total number of years

    # dynamically adjust figure size depending on number of required subplots
    fig = plt.figure(figsize=(10, 3 * n))

    # slightly paranoid, sort years explicitly (order is not necessarily
    # guaranteed in the internal code)
    years_sorted = [str(year) for year in
                    sorted((int(year) for year in Constants.keys()), reverse=True)]

    print(years_sorted)
    # generate one axis/graphic for each year
    for i, year in enumerate(years_sorted):
        teams = Constants[year].Teams

        ax = fig.add_subplot(n, 1, i + 1)

        x_labels = list()
        x_ranges = list()
        default_colors = list()
        official_colors = list()

        for j, (name, team) in enumerate(teams.items()):
            x_labels.append(team.ShortName)
            default_colors.append(team.TeamColor.FastF1)
            official_colors.append(team.TeamColor.Official)

            x_ranges.append((j + 0.5, 1))

        # draw color rectangles as horizontal bar graph
        ax.broken_barh(x_ranges, (0.5, 0.9), facecolors=official_colors)
        ax.broken_barh(x_ranges, (1.5, 0.9), facecolors=default_colors)

        # configure y axis and label
        ax.set_ylim((0.5, 2.5))
        ax.set_yticks([1, 2])
        ax.set_yticklabels(['official', 'default'])

        # configure x axis and label
        ax.set_xlim((0.5, len(x_ranges) + 0.5))
        ax.set_xticks(range(1, len(x_labels) + 1))
        ax.set_xticklabels(x_labels)

        # disable frame around axis
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # disable tick markers everywhere, label x axis at the top
        ax.tick_params(top=False, labeltop=True, bottom=False, labelbottom=False,
                    left=False, labelleft=True, right=False, labelright=False)

        # set tick label text color (grey, so it works on light and dark theme and
        # isn't too distracting next to the colors)
        ax.tick_params(colors='#787878')

        # set background color within axes
        # (transparent, fallback white if transparency not supported)
        ax.set_facecolor('#ffffff00')

        # set axes title (grey, so it works on light and dark theme and
        # isn't too distracting next to the colors)
        ax.set_title(year, color='#787878')

    # set background color for figure/margins around axes
    # (transparent, fallback white if transparency not supported)
    fig.patch.set_facecolor('#ffffff00')

    # adjust margins between and around axes
    plt.subplots_adjust(top=0.95, bottom=0.05, left=0.1, right=0.95, hspace=0.5)

    

    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=200, bbox_inches=None)
    img.seek(0)
    plt.close()
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return render_template('colormap.html', plot_url=plot_url)

    




    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
