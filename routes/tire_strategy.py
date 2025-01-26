from flask import Blueprint, render_template, request
import io, base64
import matplotlib.pyplot as plt
import fastf1 as ff1

# Create a Blueprint for the tire strategy route
tire_strategy_bp = Blueprint('tire_strategy', __name__)


@tire_strategy_bp.route('/tire-strategy', methods=['GET', 'POST'])
def tire_strategy():
    if request.method == 'POST':
        try:
            year = 2024
            wknd = int(request.form['wknd'])
            session = ff1.get_session(year, wknd, 'R')
            session.load()

            laps = session.laps
            drivers = [session.get_driver(driver)["Abbreviation"] for driver in session.drivers]

            stints = laps.groupby(["Driver", "Stint", "Compound"])["LapNumber"].count().reset_index()
            stints = stints.rename(columns={"LapNumber": "StintLength"})

            fig, ax = plt.subplots(figsize=(10, 6))
            compound_colors = {
                "SOFT": "#FF3333",
                "MEDIUM": "#FFFF66",
                "HARD": "#0033FF",
                "INTERMEDIATE": "#33CC33",
                "WET": "#3399FF"
            }

            for driver in drivers:
                driver_stints = stints[stints["Driver"] == driver]
                previous_lap = 0
                for _, stint in driver_stints.iterrows():
                    ax.barh(driver, stint["StintLength"], left=previous_lap, color=compound_colors[stint["Compound"]])
                    previous_lap += stint["StintLength"]

            plt.xlabel("Laps")
            plt.title("Tire Strategy")
            ax.invert_yaxis()

            img = io.BytesIO()
            plt.savefig(img, format='png', dpi=150, bbox_inches="tight")
            img.seek(0)
            plt.close()

            plot_url = base64.b64encode(img.getvalue()).decode('utf8')
            return render_template('tire-strategy.html', plot_url=plot_url)

        except Exception as e:
            return render_template('tire-strategy.html', error_message=f"Error: {str(e)}")

    return render_template('tire-strategy.html', plot_url=None)