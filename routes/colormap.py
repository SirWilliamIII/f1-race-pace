from flask import Blueprint, render_template
import io, base64
import matplotlib.pyplot as plt
from fastf1.plotting._constants import Constants


colormap_bp = Blueprint('colormap', __name__)


@colormap_bp.route('/colormap', methods=['GET'])
def get_colormap():
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        years = sorted(Constants.keys(), reverse=True)

        for i, year in enumerate(years):
            teams = Constants[year].Teams
            x_labels = []
            colors = []
            for name, team in teams.items():
                x_labels.append(name)
                colors.append(team.TeamColor.Official)

            ax.barh(year, len(teams), color=colors, edgecolor="black")

        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=150, bbox_inches="tight")
        img.seek(0)
        plt.close()

        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        return render_template('colormap.html', plot_url=plot_url)

    except Exception as e:
        return render_template('colormap.html', error_message=f"Error: {str(e)}")

