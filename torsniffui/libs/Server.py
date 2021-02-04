from multiprocessing import Process
from flask import Flask, request, render_template, make_response, redirect
from torsniffui.libs import Database
import dateutil.parser

try:
    import simplejson as json
except ImportError:
    import json


class Server(Process):
    def __init__(self, db: Database, host="0.0.0.0", port=1668, debug=True):
        Process.__init__(self)
        self.app = Flask(__name__)
        self.db = db
        self.host = host
        self.port = port
        self.debug = debug

        def render(tpl, **kwargs):
            return make_response(render_template(tpl, **kwargs))

        def get_json() -> dict:
            return request.get_json(force=True)

        def has_keys(d: dict, keys: list[str]) -> bool:
            for k in keys:
                if k not in d.keys():
                    return False
            return True

        def api(keys: list[str], func, default_data: dict = None):
            j = get_json()
            data = {"error": True}
            if default_data:
                data.update(default_data)
            if has_keys(j, keys):
                data["error"] = False
                data.update(func(j))
            return make_response(json.dumps(data))

        @self.app.route("/")
        def root():
            return redirect("/dashboard")

        @self.app.route("/dashboard")
        def dashboard():
            return render("dashboard.html")

        @self.app.route("/search")
        def search():
            return render("search.html",
                          searchableKeys=self.db.get_columns("torrents"),
                          searchableFilters=[
                              "contains", "after", "startswith", "endswith"
                          ])  # todo make filter stuff work

        @self.app.route("/api/v1/db/table/count", methods=["POST"])
        def api_v1_db_table_count():
            def f(jo: dict):
                return {
                    "count": self.db.size(jo["table"])
                }
            return api(["table"], f)

        @self.app.route("/api/v1/db/table/new", methods=["POST"])
        def api_v1_db_table_new():
            def f(jo: dict):
                r = []
                for i in self.db.get_after(jo["table"], dateutil.parser.parse(jo["after"]), jo["count"]):
                    r.append(i.__dict__)
                return {
                    "items": r
                }
            return api(["table", "after", "count"], f)

        @self.app.route("/api/v1/db/table/find", methods=["POST"])
        def api_v1_db_table_search():
            def f(jo: dict):
                r = {
                    "items": [],
                    "error": False
                }
                tbl = "torrents"
                q = jo["query"]
                c = jo["column"]
                f = jo["filter"]
                if f == "contains":
                    d = self.db.get_ilike(tbl, c, "%{}%".format(q))
                elif f == "after":
                    d = self.db.get_after(tbl, c, q)
                elif f == "startswith":
                    d = self.db.get_startswith(tbl, c, q)
                elif f == "endswith":
                    d = self.db.get_endswith(tbl, c, q)
                else:
                    d = []
                    r["error"] = False
                for i in d:
                    r["items"].append(i.__dict__)
                return r
            return api(["query", "column", "filter"], f)

    def run(self) -> None:
        self.app.run(self.host, self.port, self.debug, threaded=True)
