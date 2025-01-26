from flask import Blueprint, render_template, request
import io, base64
import matplotlib.pyplot as plt
import fastf1 as ff1


positions_bp = Blueprint('positions', __name__)


@positions_bp.route('/positions', methods=['GET', 'POST'])
def get_positions():
	if request.method == 'POST':
		try:
			year = 2024
			wknd = int(request.form['wknd'])
			session = ff1.get_session(year, wknd, 'R')
			session.load()

			fig, ax = plt.subplots(figsize=(8.0, 4.9))

			for drv in session.drivers:
				drv_laps = session.laps.pick_drivers(drv)

				abb = drv_laps['Driver'].iloc[0]
				style = ff1.plotting.get_driver_style(identifier=abb, style=['color', 'linestyle'], session=session)

				ax.plot(drv_laps['LapNumber'], drv_laps['Position'], label=abb, **style)

			ax.set_ylim([20.5, 0.5])
			ax.set_yticks([1, 5, 10, 15, 20])
			ax.set_xlabel('Lap')
			ax.set_ylabel('Position')

			ax.legend(bbox_to_anchor=(1.0, 1.02))

			plt.tight_layout()

			img = io.BytesIO()
			plt.savefig(img, format='png', dpi=150, bbox_inches="tight")
			img.seek(0)
			plt.close()

			plot_url = base64.b64encode(img.getvalue()).decode('utf8')
			return render_template('positions.html', plot_url=plot_url)

		except Exception as e:
			return render_template('positions.html', error_message=f"Error: {str(e)}")

	return render_template('positions.html', plot_url=None)
