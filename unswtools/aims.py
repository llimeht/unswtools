import json
import requests

from unswtools.login import load_credentials


login_url = "https://aims.unsw.edu.au/page.php?pg=common.Login"
auth_url = "https://aims.unsw.edu.au/_basic/auth/doLogin.php"

portfolio_url = "https://aims.unsw.edu.au/page.php?pg=common.Portfolio"
service_url = "https://aims.unsw.edu.au/service.php"

course_pdf_url_template = ("https://aims.unsw.edu.au/page.php?"
                           "pg=master.PrintPage&r=%s&o=pdf")


def login(credentials=None):
    session = requests.session()

    session.get(login_url)

    username, password = load_credentials(credentials)

    payload = {
        'submit': 'submit',
        'username': username,
        'password': password
    }

    session.post(auth_url, data=payload)

    return Aims(session)


class Aims:
    def __init__(self, session):
        self.session = session

    def course(self, course_code=None, course_id=None):
        return Course(self, course_code, course_id)


class Course:
    def __init__(self, aims, course_code=None, course_id=None):
        self.aims = aims
        self.course_code = course_code
        self._course_id = course_id
        self._record_id = None

    def search_course_data(self):
        payload = [
            {
                "srv": "record.RecordService.runPortfolioSearch",
                "data": {
                    "searchTerm": self.course_code,
                    "type": "course",
                    "from": "any",
                    "org": "",
                    "author": "",
                    "career": "all",
                    "updated": "all",
                    "incl_backcat": "f",
                    "sortCol": "last_upd_sort",
                    "sortDir": "desc",
                    "numPerPage": "20",
                    "page": "1",
                    "inactive": "f",
                    "searchAdmin": "f",
                },
                "seq": 2,
            }
        ]
        search = self.aims.session.post(service_url,
                                        data={'_req_': json.dumps(payload)})
        data = json.loads(search.text)
        records = data[0]['result']['results']

        try:
            return records[0]
        except IndexError:
            raise ValueError("Course %s not found!" % self.course_code)

    def course_id(self):
        if not self._course_id:
            record = self.search_course_data()
            self._course_id = record['id']
        return self._course_id

    def fetch_pdf(self, filename=None):
        if filename is None:
            filename = "%s.pdf" % self.course_code

        course_pdf_url = course_pdf_url_template % self.course_id()

        with open(filename, "wb") as fh:
            response = self.aims.session.get(course_pdf_url)
            fh.write(response.content)

    def record_id(self):
        if not self._record_id:
            record = self.search_course_data()
            self._record_id = record['inst_id']
        return self._record_id

    def _fetch_records(self):
        payload = [
            {
                "srv": "record.RecordService.getRecordData",
                "data": {
                    "instanceId": self.record_id(),
                    "timestamp": None,
                },
                "seq": 2,
            }
        ]
        search = self.aims.session.post(service_url,
                                        data={'_req_': json.dumps(payload)})
        return json.loads(search.text)

    def course_record(self):
        rec = self._fetch_records()
        return rec[0]['result']['data']

    def make_html_report(self):
        # FIXME move this to a separate function that accepts a course and then formats it
        data = self.course_record()

        # FIXME: make methods or properties for each of these?
        course_aims = data['course_aims']
        course_description = data['course_description']

        clos = json.loads(data['cour_learning_outcomes'])
        clo_items = {}
        for c in clos:
            clo_items[c['id']] = ('<p>{sequence}. {text}</p>'.format(**c))

        clo_map = data['assessmentItems_and_mapping']['AIMapCLO']
        clo_map_items = {}
        for c in clo_map:
            clo_map_items[c['id']] = [e['id'] for e in c['mappings']]

        assessments = data['assessment_items']
        assmt_items = []
        for a in assessments:
            clos = clo_map_items[a['id']]
            a['clos'] = "".join(sorted(clo_items[clo_id] for clo_id in clos))
            assmt_items.append('''\
                <tr>
                    <td>{title}</td>
                    <td>{type_descr}</td>
                    <td>{weight}</td>
                    <td>{clos}</td>
                </tr>'''.format(**a))

        hours = json.loads(data['standard_hour'])['data']
        hour_items = ["<tr><td>{name}</td><td>{hours}</td></tr>".format(**e)
                      for e in hours]

        # FIXME: use jinja templates instead
        entry = [
            "<h2>Course aims</h2>",
            course_aims if course_aims else "None specified",
            "<h2>Course description</h2>",
            course_description if course_description else "None specified",
            "<h2>Course Learning Outcomes</h2>",
            "<ol>",
            "\n".join(sorted(clo_items.values())),
            "</ol>",
            "<h2>Assessments</h2>",
            "<table>",
            "<tr><th>Name</th><th>Type</th><th>Weight</th><th>CLOs</th></tr>",
            "\n".join(assmt_items),
            "</table>",
            "<h2>Teaching activities per week in old semester</h2>",
            "<table>",
            "<tr><th>Activity</th><th>Hours/week 2018</th></tr>",
            "\n".join(hour_items),
            "</table>",
        ]

        return "\n".join(entry)

    def export_course_summary(self, filename=None):
        html = self.make_html_report()
        save_report(html, self.course_code, filename)


def display_report(html):
    from IPython.display import HTML, display
    display(HTML(html))


def save_report(html, course, filename=None):
    if filename is None:
        filename = "%s.html" % course

    with open(filename, 'w') as fh:
        fh.write("""\
<html>
<head>
  <title>{title}</title>
  <meta charset="utf-8"/>
</head>
<style>
table, td, th {{
    border: 1px solid black;
    border-collapse: collapse;
}}
body {{
    font-family: sans;
}}
</style>
<body>
<h1>Summary for {title}</h1>

{entry}
</body>
</html>
        """.format(title=course, entry=html))
