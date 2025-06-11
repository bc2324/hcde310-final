from flask import Flask, render_template, request, redirect, url_for
import json
from functions import geocode, get_route, latest_eq, route_safe

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        origin_addr = request.form["origin"]
        dest_addr   = request.form["dest"]

        origin = geocode(origin_addr)
        dest   = geocode(dest_addr)
        if not origin or not dest:
            return redirect(url_for("index"))

        quake  = latest_eq()
        route  = get_route(origin, dest)
        safe   = route_safe(route["coords"], quake)

        return render_template(
            "results.html",
            origin=origin_addr,
            dest=dest_addr,
            route=route,
            coords_json=json.dumps(route["coords"]),
            quake=quake,
            safe=safe,
        )
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)



